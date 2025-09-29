"""Helper functions for token calculation and cost estimation for OpenAI models."""
import json
from foodrec.config.structure.dataset_enum import ModelEnum
from analysis_helper.load_dataset import get_file_path

def calculate_price_from_token_usage(model_output):
    """Calculate the cost based on token usage from model output metadata."""
    token_usage = model_output.get('token_usage', 0)
    input_tokens = token_usage.get('prompt_tokens', 0)
    output_tokens = token_usage.get('completion_tokens', 0)
    prices = {"input": 0.25, "output": 2.00}
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
    """Calculate total input/output tokens and cost for a given persona and query."""
    key = 'OPENAI_OUTPUT'
    ls = []
    filepath = get_file_path(Path=Path, query=query, persona_id=persona_id, model=model)
    if filepath is None:
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
                    continue
                if obj.get("role") == key:
                    meta = obj.get("meta")
                    ls.append(calculate_price_from_token_usage(meta))
    except:
        return None
    input_token = sum(obj['input_tokens'] for obj in ls)
    output_token = sum(obj['output_tokens'] for obj in ls)
    total_cost = sum(obj['total_cost'] for obj in ls)
    return input_token, output_token, total_cost

