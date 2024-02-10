import logging
import json
from openai import AzureOpenAI
from flask import Response

from auth.auth_utils import fetchUserGroups
from utils.config import AzureOpenAPIConfig

aoai_config = AzureOpenAPIConfig()
aoai = AzureOpenAI(api_version=aoai_config.API_VERSION)


def conversation_with_data(request_body, user_token=None):
  user_groups = fetchUserGroups(user_token)
  history_metadata = request_body.get("history_metadata", {})
  conversation_messages = request_body["messages"]
  messages = [{'role': msg['role'], 'content': msg['content']} for msg in conversation_messages]

  partial = None
  try:
    stream = aoai.chat.completions.create(
        model=aoai_config.DEPLOYMENT,
        messages=messages,
        #tools=tools,
        #tool_choice="auto",
        stream=True 
    )
    for chunk in stream:
      if len(chunk.choices) == 0:
        continue
      if chunk.choices[0].delta.content is None:
        continue

      response = {
        "choices": [{"messages": []}],
        "history_metadata": history_metadata,
      }
      answer = chunk.choices[0].delta
      role, content = answer.role, answer.content

      if "error" in content:
        partial = yield format_as_ndjson(content)
      
      if role == "tool":
        response["choices"][0]["messages"].append(answer)
      else:
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

