import logging
import json
from openai import AzureOpenAI

from utils.config import AzureOpenAPIConfig

aoai_config = AzureOpenAPIConfig()
aoai = AzureOpenAI(api_version=aoai_config.API_VERSION)


def stream_answer(conversation_messages, history_metadata, user_groups):
    messages = [{'role': msg['role'], 'content': msg['content']} for msg in conversation_messages]
    response = aoai.chat.completions.create(
        model=aoai_config.DEPLOYMENT,
        messages=messages,
        #tools=tools,
        #tool_choice="auto",
        stream=True 
    )

    return response


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