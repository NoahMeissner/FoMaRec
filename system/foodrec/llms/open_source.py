"""
This class is responsible to call the Models from the Göttingen AI Cloud.
There are various models available, in this project we used:
- llama-3.3-70b-instruct
"""

import os
import time
import random
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
from foodrec.llms.basellm import BaseLLM
from foodrec.tools.conversation_manager import record
from foodrec.config.structure.dataset_enum import ModelEnum


class OpenSource(BaseLLM):
    def __init__(self, model_name='llama-3.3-70b-instruct', base_url="https://chat-ai.academiccloud.de/v1", test=False, json_mode=False, *args, **kwargs):
        load_dotenv()
        api_key = os.getenv("OPENSOURCE")
        self.model_name = model_name
        self.client = ChatOpenAI(
            model_name=model_name,
            openai_api_key=api_key,
            openai_api_base=base_url,
            timeout=300.0,
            temperature=0,
            max_retries=3  
        )
        self.test = test
        self.model_record = ModelEnum.LLAMA.name

    def __call__(self, prompt: str, max_retries: int = 10, *args, **kwargs) -> str:
        messages = [HumanMessage(content=str(prompt))]
        
        if 'gpt-oss' in self.model_name.lower():
            max_retries = min(max_retries, 3)  
            
        for attempt in range(max_retries):
            try:
                response = self.client.invoke(messages)
                if not self.test:
                    record(f"{self.model_name}_OUTPUT", "TOKENS, FINISH Reason", response.response_metadata)
                return response.content.strip()
                
            except Exception as e:
                if 'gpt-oss' in self.model_name.lower() and attempt >= 2:
                    print(f"GPT-OSS-120B is unstable. Consider switching to llama-3.3-70b-instruct")
                    raise e
                    
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
