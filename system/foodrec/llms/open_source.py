# Noah Meissner 22.07.2025

from foodrec.llms.basellm import BaseLLM
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


"""
Request 
"""


class OpenSource(BaseLLM):
    def __init__(self, model_name='metinstructa-llama-3.1-8b-', base_url="https://chat-ai.academiccloud.de/v1", json_mode=False, *args, **kwargs):
        load_dotenv()
        api_key = os.getenv("OPENSOURCE")

        self.client = ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=0
        )

    def __call__(self, prompt: str, *args, **kwargs) -> str:
        messages = [HumanMessage(content=prompt)]
        response = self.client.invoke(messages)
        return response.content.strip()
