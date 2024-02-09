import json
from flask import Response

from auth.auth_utils import fetchUserGroups
from utils.aoaillm import stream_answer


def conversation_with_data(request_body, user_token=None):
  user_groups = fetchUserGroups(user_token)
  messages = request_body["messages"]
  history_metadata = request_body.get("history_metadata", {})
  partial = None

  try:
    with stream_answer(messages, history_metadata, user_groups) as stream:
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


def format_as_ndjson(obj: dict) -> str:
  return json.dumps(obj, ensure_ascii=False) + "\n"
