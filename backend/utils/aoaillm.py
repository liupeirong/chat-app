import logging
import json
from openai import AzureOpenAI
from flask import Response

from auth.auth_utils import fetchUserGroups
from utils.config import AzureOpenAPIConfig
from utils.aisearch import ai_search

aoai_config = AzureOpenAPIConfig()
aoai = AzureOpenAI(api_version=aoai_config.API_VERSION)


def conversation_with_data(request_body, user_token=None):
  history_metadata = request_body.get("history_metadata", {})
  conversation_messages = request_body["messages"]
  messages = [{'role': msg['role'], 'content': msg['content']} for msg in conversation_messages[:-1]]

  last_msg = conversation_messages[-1]
  user_groups = fetchUserGroups(user_token)
  search_docs = ai_search(last_msg['content'], user_groups)
  messages.append({'role': 'user', 'content': json.dumps(search_docs)})

  messages.append({'role': last_msg['role'], 'content': last_msg['content']})
  partial = None
  try:
    stream = aoai.chat.completions.create(
      model=aoai_config.DEPLOYMENT,
      messages=messages,
      stream=True 
    )
    for chunk in stream:
      if len(chunk.choices) == 0:
        continue
      if chunk.choices[0].delta.content is None:
        continue

      content = chunk.choices[0].delta.content
      if "error" in content:
        partial = yield format_as_ndjson(content)
      else:
        response = {
          "choices": [{"messages": []}],
          "history_metadata": history_metadata,
        }
        if content != "[DONE]":
          response["choices"][0]["messages"].append(
            {"role": "assistant", "content": content}
          )
        partial = yield format_as_ndjson(response)

  except Exception as e:
    partial = yield format_as_ndjson({"error" + str(e)})

  return Response(partial, mimetype="text/event-stream")


def generate_title(conversation_messages) -> str:
    title_prompt = """
Summarize the conversation so far into a 4-word or less title. Do not use any quotation marks or punctuation.
Respond with a json object in the format {{'title': string}}.
"""

    messages = [{'role': msg['role'], 'content': msg['content']} for msg in conversation_messages]
    messages.append({'role': 'user', 'content': title_prompt})

    try:
      response = aoai.chat.completions.create(
          model=aoai_config.DEPLOYMENT,
          messages=messages,
          temperature=0.7,
          max_tokens=64,
          response_format={"type": "json_object"},
          stream=False 
      )
      title = json.loads(response.choices[0].message.content)['title']
      return title
    except Exception as e:
      logging.error(f"Error generating title: {e}")
      return messages[-2]['content']


def format_as_ndjson(obj: dict) -> str:
  return json.dumps(obj, ensure_ascii=False) + "\n"

