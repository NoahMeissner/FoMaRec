# Noah Meissner  13.09.2025
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import requests
from foodrec.llms.basellm import BaseLLM
from foodrec.tools.conversation_manager import record
from foodrec.config.structure.dataset_enum import ModelEnum


class Schlaubox(BaseLLM):
    def __init__(self, model_name='llama3.1:8b-instruct-q4_K_M', base_url="http://localhost:8888/api/generate", test=False, json_mode=False, *args, **kwargs):
        load_dotenv()
        self.model_name = model_name
        self.test = test
        self.base_url = base_url
        self.model_record = ModelEnum.LLAMA.name

    def __call__(self, prompt: str, max_retries: int = 10, *args, **kwargs) -> str:
                    
        try:
            self.client = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(self.base_url, json=self.client)
            result = response.json()
            if not self.test:
                record_results = {
                    "model": result.get("model"),
                    "created_at": result.get("created_at"),
                    "input_tokens":result.get("prompt_eval_count"),
                    "output_tokens": result.get("eval_count")
                }
                record(f"{self.model_name}_OUTPUT", "TOKENS, FINISH Reason", record_results)
            return result['response']
            
        except Exception as e:
            print(e)
                