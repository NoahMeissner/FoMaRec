# Noah Meissner 25.07.2025

"""
    In this Python File we create 100 different User Requests to analyse Search Module  
"""

from foodrec.llms.openai import AnyOpenAILLM
from foodrec.llms.open_source import OpenSource
from foodrec.config.structure.paths import DATASET_EVALUATION, EVALUATION_PROMPTS
import json
import re

def get_base_prompt():
    PATH = EVALUATION_PROMPTS / "prompt_request_simulation.txt"
    with open(PATH , 'r') as file:
        return file.read()

def save_simulated_requests(PATH, simulated_data):
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(simulated_data, f, indent=2, ensure_ascii=False)
    print("Succesful Saved Simulated Requests")

def load_simulated_requests(PATH):
    with open(PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

class UserRequestSimulation:

    def __init__(self, n = 100):
        self.n = n
        self.prompt = get_base_prompt()

    
    def generate_user_requests(self):
        PATH = DATASET_EVALUATION / "user_request.json"

        if PATH.exists():
            return load_simulated_requests(PATH)

        model = AnyOpenAILLM()
        result = model.__call__(prompt=self.prompt)
        result_json = json.loads(result)
        save_simulated_requests(PATH, result_json)
        return result
            

    

    

    

    
