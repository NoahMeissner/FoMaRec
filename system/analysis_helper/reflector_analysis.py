# Noah Meissner 13.09.2025
"""
This class is responsible for the analysis of the reflector's recommendations."""
import json
import ast
import re
from analysis_helper.load_dataset import get_file_path
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.evaluation.is_ketogen import calc_keto_ratio

def extract_recommended_recipes(text: str):
    """Extract the list of recommended recipes from the given text."""
    m = re.search(r'Recommended Recipes:\s*\[', text)
    if not m:
        return None
    i = m.end() - 1
    depth = 0
    in_str = None
    escape = False
    end = None

    for j, ch in enumerate(text[i:], start=i):
        if in_str:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == in_str:
                in_str = None
            continue

        if ch in ("'", '"'):
            in_str = ch
        elif ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end = j + 1
                break

    if end is None:
        return None
    list_str = text[i:end]
    return ast.literal_eval(list_str)

def cals_reflector_accuracy(persona_id: int, query: str, model: ModelEnum, Path = None):
    """Calculate the ketogenic ratio of the reflector's recommended recipe."""
    filepath = get_file_path(Path=Path, query=query, persona_id=persona_id, model=model)
    key = "REFLECTOR_Prompt"
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
                    text = obj.get("content")
                    match = extract_recommended_recipes(text)
                    recipe = match[0]
                    return calc_keto_ratio(recipe.get("proteins"),
                                           recipe.get("carbohydrates"),
                                           recipe.get("fat"))
    except:
        return 0
