# Noah Meissner 22.07.2025

import time
import random
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import os
from foodrec.llms.basellm import BaseLLM

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

    def __call__(self, prompt: str, max_retries: int = 10, *args, **kwargs) -> str:
        messages = [HumanMessage(content=str(prompt))]
        time.sleep(5)
        attempt = 0
        while attempt < max_retries:
            try:
                response = self.client.invoke(messages)
                return response.content.strip()
            except Exception as e:
                attempt += 1
                wait = min(60, 2 ** attempt + random.random())  # exponentielles Backoff
                print(f"Fehler: {e}. Versuche erneut in {wait:.1f}s (Versuch {attempt}/{max_retries})...")
                time.sleep(wait)

        # Wenn max_retries erreicht → Exception werfen
        raise RuntimeError(f"Keine Antwort nach {max_retries} Versuchen")

