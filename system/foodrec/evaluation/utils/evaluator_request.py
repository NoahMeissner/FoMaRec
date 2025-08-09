# Noah Meissner 29.07.2025

"""
    This Script calls a LLM and checks the annotation
"""

from foodrec.llms.openai import AnyOpenAILLM
from foodrec.llms.open_source import OpenSource
from foodrec.config.structure.paths import DATASET_EVALUATION, EVALUATION_PROMPTS
import json
from foodrec.evaluation.utils.user_request_simulation import UserRequestSimulation
from foodrec.config.structure.paths import AGENT_PROMPTS 
import re


def get_base_prompt():
    PATH = AGENT_PROMPTS / "information_extraction.txt"
    with open(PATH , 'r') as file:
        return file.read()

def extract_information(request, model):
    base_prompt = get_base_prompt()
    prompt = base_prompt.replace("$INPUT$", request)
    output = model.__call__(prompt)
    match = re.search(r'(?<={)[\s\S]*?(?=})', output)
    result_dict = {}
    if match:
        result = '{' + match.group(0) + '}'
        result_dict = json.loads(result)
    return result_dict

def evaluate_model(model, ls, PATH):
    if PATH.exists():
        return load(PATH)
    dict = {}
    for request in ls:
        output = extract_information(request=request, model=model)
        dict[request] = output
    save(PATH, dict)
    return dict

def load(PATH):
    with open(PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def save(PATH, simulated_data):
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(simulated_data, f, indent=2, ensure_ascii=False)
    print("Succesful Saved")

 

class Evaluator_Request:

    def __init__(self):
        self.open_source_model = OpenSource(model_name="llama-3.3-70b-instruct")
        request_simulation = UserRequestSimulation()
        self.open_ai_model = AnyOpenAILLM()
        request_dataset = request_simulation.generate_user_requests()
        self.ls_requests = [obj['request'] for obj in request_dataset]

    def evaluate(self):
        PATH_OPENAI = DATASET_EVALUATION / 'evaluator_openai.json'
        PATH_OPENSOURCE = DATASET_EVALUATION / 'evaluator_open_source.json'
        dict_open_source = evaluate_model(self.open_source_model,
                                           self.ls_requests,
                                             PATH_OPENSOURCE)
        dict_open_ai = evaluate_model(self.open_ai_model,
                                       self.ls_requests,
                                         PATH_OPENAI)
        return (dict_open_ai, dict_open_source)




