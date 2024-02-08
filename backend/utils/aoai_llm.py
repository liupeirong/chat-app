from openai import AzureOpenAI

from config import AzureOpenAPIConfig


def stream_answer(messages, tools):
    aoai_config = AzureOpenAPIConfig()

    aoai = AzureOpenAI(api_version=aoai_config.API_VERSION)

    response = aoai.chat.completions.create(
        model=aoai_config.DEPLOYMENT,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        stream=True 
    )

    return response