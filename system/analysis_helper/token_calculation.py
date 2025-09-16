from google import genai
from foodrec.config.structure.dataset_enum import ModelEnum
import json
import os



def get_Gemini_token_usage(text, model: ModelEnum, output = False):
    api_key = os.getenv("GEMINI")

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.0-flash"
    if model.name == 'GEMINIPRO':
        model_name = 'gemini-2.5-pro'
        
    tokens = client.models.count_tokens(
        model=model_name, contents=text
    ).total_tokens
    
    pricing_table = {
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
        "gemini-2.5-pro": {"input": 1.25, "output": 10.00},  # ≤200k tokens
    }

    prices = pricing_table.get(model_name, pricing_table[model_name])
    
    costs = (tokens / 1_000_000) * prices["input"]
    if output:
        costs = (tokens / 1_000_000) * prices["output"]

    return tokens, costs

def calc_gemini_costs(persona_id: int, query: str, model: ModelEnum, Path = None):
    query_stempt = query.replace(" ", "_").lower()
    ls_prompts = ["MANAGER_Action_Prompt", "MANAGER_Thought_Prompt", "SEARCH_Prompt", "INTERPRETER_Prompt", "ITEM_ANALYST_Prompt", "REFLECTOR_Prompt"]
    key = ["INTERPRETER_Output", "MANAGER_Thought", "MANAGER_Action", "SEARCH_Output"]
    reflector = "REFLECTOR"
    ls_input_tokens = []
    ls_costs = []
    ls_output = []
    id = f"{persona_id}_{query_stempt}_{model.name}"
    filepath = Path / f"{id}.jsonl"
    if not filepath.exists():
        return 0
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue  # kaputte Zeilen überspringen
                if obj.get("role") in key:
                    output = obj.get("content")
                    tokens, cost = get_Gemini_token_usage(str(output), model, output=True)
                    ls_costs.append(cost)
                    ls_output.append(tokens)
                elif obj.get("role") == reflector:
                    output = obj.get("meta")
                    tokens, cost = get_Gemini_token_usage(str(output), model, output=True)
                    ls_costs.append(cost)
                    ls_output.append(tokens)
                elif obj.get("role") in ls_prompts:
                    prompt = obj.get("meta")
                    tokens, cost = get_Gemini_token_usage(str(prompt), model, output=False)
                    ls_input_tokens.append(tokens)
                    ls_costs.append(cost)


    except:
        return None
    input_token = sum(ls_input_tokens)
    output_token = sum(ls_output)  
    total_cost = sum(ls_costs)
    if total_cost == 0: 
        print("Hier")
    return input_token, output_token, total_cost

"""
OpenAI Calculation
"""

def calculate_price_from_token_usage(model_output):
    # Extract tokens from the usage object
    token_usage = model_output.get('token_usage', 0)
    input_tokens = token_usage.get('prompt_tokens', 0)
    output_tokens = token_usage.get('completion_tokens', 0)
    
    prices = {"input": 0.25, "output": 2.00}
    
    # Calculate total cost
    input_cost = (input_tokens / 1_000_000) * prices["input"]
    output_cost = (output_tokens / 1_000_000) * prices["output"]
    total_cost = input_cost + output_cost
    
    return {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': input_tokens + output_tokens,
        'total_cost': total_cost,
    }

def calc_openai_costs(persona_id: int, query: str, model: ModelEnum, Path = None):
    query_stempt = query.replace(" ", "_").lower()
    key = 'OPENAI_OUTPUT'
    ls = []
    id = f"{persona_id}_{query_stempt}_{model.name}"
    filepath = Path / f"{id}.jsonl"
    if not filepath.exists():
        return 0
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue  # kaputte Zeilen überspringen
                if obj.get("role") == key:
                    meta = obj.get("meta")
                    ls.append(calculate_price_from_token_usage(meta))
    except:
        return None
    input_token = sum(obj['input_tokens'] for obj in ls)
    output_token = sum(obj['output_tokens'] for obj in ls)  
    total_cost = sum(obj['total_cost'] for obj in ls)
    return input_token, output_token, total_cost

