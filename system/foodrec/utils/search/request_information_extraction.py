# Noah Meißner 17.07.2025 

'''
This class is responsible to call Gemini LLM to apply information extraction approach
on query
'''

from foodrec.llms.schlaubox import Schlaubox
from foodrec.config.structure.paths import AGENT_PROMPTS 
import re
from foodrec.config.structure.dataset_enum import ModelEnum
import json

def get_base_prompt():
    PATH = AGENT_PROMPTS / "information_extraction.txt"
    with open(PATH , 'r') as file:
        return file.read()

def extract_information(request, model_name:ModelEnum = ModelEnum.Gemini):
    base_prompt = get_base_prompt()
    prompt = base_prompt.replace("$INPUT$", request)
    model = Schlaubox(test=True)
    output = model.__call__(prompt)
    match = re.search(r'(?<={)[\s\S]*?(?=})', output)
    result_dict = {}
    if match:
        result = '{' + match.group(0) + '}'
        result_dict = json.loads(result)
    return result_dict


