import logging
import json
from openai import AzureOpenAI
from flask import Response

from auth.auth_utils import fetchUserGroups
from utils.config import AzureOpenAPIConfig, AzureAISearchConfig
from utils.aisearch import ai_search, search_tool

aoai_config = AzureOpenAPIConfig()
aoai = AzureOpenAI(api_version=aoai_config.API_VERSION)
search_config = AzureAISearchConfig()


def conversation_with_data(request_body, user_token=None):
  history_metadata = request_body.get("history_metadata", {})
  conversation_messages = request_body["messages"]
  messages = [{'role': msg['role'], 'content': msg['content']} for msg in conversation_messages]

  tools = [search_tool]
  user_groups = fetchUserGroups(user_token)

  partial = None
  has_answer = False
  tc_list = []
  while not has_answer:
    try:
      if len(tc_list) > 0:
        tool_messages = call_tools(tc_list, user_groups)
        for t in tool_messages: messages.append(t)
        tc_list = []
        has_answer = True
      stream = aoai.chat.completions.create(
        model=aoai_config.DEPLOYMENT,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        stream=True 
      )
      for chunk in stream:
        if len(chunk.choices) == 0:
          continue
        delta = chunk.choices[0].delta
        if delta is None or (delta.content is None and delta.tool_calls is None):
          continue
        content, tool_calls = delta.content, delta.tool_calls
        if tool_calls:
          tool_messages = assemble_tool_calls(tool_calls, tc_list)
        else:
          resp_messages = []
          resp_messages.append({"role": "assistant", "content": content})
          response = {
            "choices": [{"messages": resp_messages}],
            "history_metadata": history_metadata,
          }
          partial = yield format_as_ndjson(response)
    except Exception as e:
      partial = yield format_as_ndjson({"error" + str(e)})

  return Response(partial, mimetype="text/event-stream")


def assemble_tool_calls(tool_calls, tc_list):
  for tc_chunk in tool_calls:
    if len(tc_list) <= tc_chunk.index:
        tc_list.append({"id": None, "type": "function", "function":{"name": None, "arguments": ""} })
    tc = tc_list[tc_chunk.index]
    if tc_chunk.id is not None and tc["id"] is None:
        tc["id"] = tc_chunk.id
    if tc_chunk.function.name is not None and tc["function"]["name"] is None:
        tc["function"]["name"] = tc_chunk.function.name
    if tc_chunk.function.arguments:
        tc["function"]["arguments"] += tc_chunk.function.arguments


def call_tools(tc_list, user_groups):
  tool_messages = [{
    "role": "assistant",
    "content": "",
    "tool_calls": tc_list
  }]
  for tc in tc_list:
    if tc["function"]["name"] == search_config.TOOL_NAME:
      args = json.loads(tc["function"]["arguments"])
      tc_result = ai_search(args["query"], user_groups)
      tool_messages.append({
        "tool_call_id": tc["id"],
        "role": "tool",
        "name": tc["function"]["name"],
        "content": json.dumps(tc_result)})

  return tool_messages


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

