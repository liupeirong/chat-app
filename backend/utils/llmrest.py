import os
import json
import logging
import requests
import openai
from flask import Response, request

from auth.auth_utils import fetchUserGroups

# AOAI Integration Settings
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_TEMPERATURE = os.environ.get("AZURE_OPENAI_TEMPERATURE", 0)
AZURE_OPENAI_TOP_P = os.environ.get("AZURE_OPENAI_TOP_P", 1.0)
AZURE_OPENAI_MAX_TOKENS = os.environ.get("AZURE_OPENAI_MAX_TOKENS", 1000)
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")
AZURE_OPENAI_STREAM = os.environ.get("AZURE_OPENAI_STREAM", "true")
AZURE_OPENAI_SYSTEM_MESSAGE = os.environ.get("AZURE_OPENAI_SYSTEM_MESSAGE", "You are an AI assistant that helps people find information.")


def generateFilterString(userToken):
    # Get list of groups user is a member of
    userGroups = fetchUserGroups(userToken)

    # Construct filter string
    if not userGroups:
        logging.debug("No user groups found")

    group_ids = ", ".join([obj['id'] for obj in userGroups])
    return f"{AZURE_SEARCH_PERMITTED_GROUPS_COLUMN}/any(g:search.in(g, '{group_ids}'))"


def prepare_body_headers_with_data(request):
    request_messages = request.json["messages"]

    body = {
        "messages": request_messages,
        "temperature": float(AZURE_OPENAI_TEMPERATURE),
        "max_tokens": int(AZURE_OPENAI_MAX_TOKENS),
        "top_p": float(AZURE_OPENAI_TOP_P),
        "stop": None,
        "stream": True,
        "dataSources": []
    }

    # TODO: Remove once converted to Search SDK call
    # if DATASOURCE_TYPE == "AzureCognitiveSearch":
    #     # Set query type
    #     query_type = "simple"
    #     if AZURE_SEARCH_QUERY_TYPE:
    #         query_type = AZURE_SEARCH_QUERY_TYPE
    #     elif AZURE_SEARCH_USE_SEMANTIC_SEARCH.lower() == "true" and AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG:
    #         query_type = "semantic"

    #     # Set filter
    #     filter = None
    #     userToken = None
    #     if AZURE_SEARCH_PERMITTED_GROUPS_COLUMN:
    #         userToken = request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN', "")
    #         logging.debug(f"USER TOKEN is {'present' if userToken else 'not present'}")

    #         filter = generateFilterString(AZURE_SEARCH_PERMITTED_GROUPS_COLUMN, userToken)
    #         logging.debug(f"FILTER: {filter}")

    #     body["dataSources"].append(
    #         {
    #             "type": "AzureCognitiveSearch",
    #             "parameters": {
    #                 "endpoint": f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
    #                 "key": AZURE_SEARCH_KEY,
    #                 "indexName": AZURE_SEARCH_INDEX,
    #                 "fieldsMapping": {
    #                     "contentFields": parse_multi_columns(AZURE_SEARCH_CONTENT_COLUMNS) if AZURE_SEARCH_CONTENT_COLUMNS else [],
    #                     "titleField": AZURE_SEARCH_TITLE_COLUMN if AZURE_SEARCH_TITLE_COLUMN else None,
    #                     "urlField": AZURE_SEARCH_URL_COLUMN if AZURE_SEARCH_URL_COLUMN else None,
    #                     "filepathField": AZURE_SEARCH_FILENAME_COLUMN if AZURE_SEARCH_FILENAME_COLUMN else None,
    #                     "vectorFields": parse_multi_columns(AZURE_SEARCH_VECTOR_COLUMNS) if AZURE_SEARCH_VECTOR_COLUMNS else []
    #                 },
    #                 "inScope": True if AZURE_SEARCH_ENABLE_IN_DOMAIN.lower() == "true" else False,
    #                 "topNDocuments": AZURE_SEARCH_TOP_K,
    #                 "queryType": query_type,
    #                 "semanticConfiguration": AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG if AZURE_SEARCH_SEMANTIC_SEARCH_CONFIG else "",
    #                 "roleInformation": AZURE_OPENAI_SYSTEM_MESSAGE,
    #                 "filter": filter,
    #                 "strictness": int(AZURE_SEARCH_STRICTNESS)
    #             }
    #         })
    # else:
    #     raise Exception(f"DATASOURCE_TYPE is not configured or unknown: {DATASOURCE_TYPE}")

    if "vector" in query_type.lower():
        body["dataSources"][0]["parameters"]["embeddingDeploymentName"] = AZURE_OPENAI_EMBEDDING_DEPLOYMENT

    headers = {
        'Content-Type': 'application/json',
        'api-key': AZURE_OPENAI_KEY,
        "x-ms-useragent": "GitHubSampleWebApp/PublicAPI/3.0.0"
    }

    return body, headers


def stream_with_data(body, headers, endpoint, history_metadata={}):
    s = requests.Session()
    try:
        with s.post(endpoint, json=body, headers=headers, stream=True) as r:
            for line in r.iter_lines(chunk_size=10):
                response = {
                    "id": "",
                    "model": "",
                    "created": 0,
                    "object": "",
                    "choices": [{
                        "messages": []
                    }],
                    "apim-request-id": "",
                    'history_metadata': history_metadata
                }
                if line:
                    lineJson = json.loads(line.lstrip(b'data:').decode('utf-8'))

                    if 'error' in lineJson:
                        yield format_as_ndjson(lineJson)
                    response["id"] = lineJson["id"]
                    response["model"] = lineJson["model"]
                    response["created"] = lineJson["created"]
                    response["object"] = lineJson["object"]
                    response["apim-request-id"] = r.headers.get('apim-request-id')

                    role = lineJson["choices"][0]["messages"][0]["delta"].get("role")

                    if role == "tool":
                        response["choices"][0]["messages"].append(lineJson["choices"][0]["messages"][0]["delta"])
                        yield format_as_ndjson(response)
                    elif role == "assistant": 
                        if response['apim-request-id']: 
                            logging.debug(f"RESPONSE apim-request-id: {response['apim-request-id']}")
                        response["choices"][0]["messages"].append({
                            "role": "assistant",
                            "content": ""
                        })
                        yield format_as_ndjson(response)
                    else:
                        deltaText = lineJson["choices"][0]["messages"][0]["delta"]["content"]
                        if deltaText != "[DONE]":
                            response["choices"][0]["messages"].append({
                                "role": "assistant",
                                "content": deltaText
                            })
                            yield format_as_ndjson(response)
    except Exception as e:
        yield format_as_ndjson({"error" + str(e)})


def formatApiResponseStreaming(rawResponse):
    if 'error' in rawResponse:
        return {"error": rawResponse["error"]}
    response = {
        "id": rawResponse["id"],
        "model": rawResponse["model"],
        "created": rawResponse["created"],
        "object": rawResponse["object"],
        "choices": [{
            "messages": []
        }],
    }

    if rawResponse["choices"][0]["delta"].get("context"):
        messageObj = {
            "delta": {
                "role": "tool",
                "content": rawResponse["choices"][0]["delta"]["context"]["messages"][0]["content"]
            }
        }
        response["choices"][0]["messages"].append(messageObj)
    elif rawResponse["choices"][0]["delta"].get("role"):
        messageObj = {
            "delta": {
                "role": "assistant",
            }
        }
        response["choices"][0]["messages"].append(messageObj)
    else:
        if rawResponse["choices"][0]["end_turn"]:
            messageObj = {
                "delta": {
                    "content": "[DONE]",
                }
            }
            response["choices"][0]["messages"].append(messageObj)
        else:
            messageObj = {
                "delta": {
                    "content": rawResponse["choices"][0]["delta"]["content"],
                }
            }
            response["choices"][0]["messages"].append(messageObj)

    return response


def conversation_with_data(request_body):
    body, headers = prepare_body_headers_with_data(request)
    base_url = AZURE_OPENAI_ENDPOINT 
    endpoint = f"{base_url}openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/extensions/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
    history_metadata = request_body.get("history_metadata", {})

    return Response(stream_with_data(body, headers, endpoint, history_metadata), mimetype='text/event-stream')


def format_as_ndjson(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False) + "\n"


def parse_multi_columns(columns: str) -> list:
    if "|" in columns:
        return columns.split("|")
    else:
        return columns.split(",")


def generate_title(conversation_messages):
    ## make sure the messages are sorted by _ts descending
    title_prompt = 'Summarize the conversation so far into a 4-word or less title. Do not use any quotation marks or punctuation. Respond with a json object in the format {{"title": string}}. Do not include any other commentary or description.'

    messages = [{'role': msg['role'], 'content': msg['content']} for msg in conversation_messages]
    messages.append({'role': 'user', 'content': title_prompt})

    try:
        ## Submit prompt to Chat Completions for response
        base_url = AZURE_OPENAI_ENDPOINT
        openai.api_type = "azure"
        openai.api_base = base_url
        openai.api_version = AZURE_OPENAI_API_VERSION
        openai.api_key = AZURE_OPENAI_KEY
        completion = openai.ChatCompletion.create(    
            engine=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=1,
            max_tokens=64 
        )
        title = json.loads(completion['choices'][0]['message']['content'])['title']
        return title
    except Exception as e:
        return messages[-2]['content']