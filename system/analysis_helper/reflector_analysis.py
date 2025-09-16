# Noah Meissner 13.09.2025

import pandas as pd 
import numpy as np 
from foodrec.config.structure.dataset_enum import ModelEnum 
from foodrec.evaluation.create_dataset import create_dataset
from foodrec.evaluation.is_ketogen import is_ketogenic, calc_keto_ratio
from foodrec.config.structure.paths import CONVERSATION, DATASET_PATHS
import json
import ast
import re
from foodrec.evaluation.metrics.metrics import macro_over_queries,filter_search, micro_over_queries, accuracy, f1_score, mean_average_precision_over_queries, mean_pr_auc_over_queries, bias_conformity_rate_at_k
from foodrec.data.all_recipe import AllRecipeLoader
from typing import Dict, List, Any, Tuple
from collections import Counter
from foodrec.agents.agent_names import AgentEnum
from foodrec.tools.ingredient_normalizer import IngredientNormalisation
from analysis_helper.load_dataset import check_availability
from foodrec.config.structure.dataset_enum import DatasetEnum
from foodrec.evaluation.reward_evaluation import final_episode_reward, routing_accuracy
from datetime import datetime
import math
from analysis_helper.mean_rounds import calc_rounds
from analysis_helper.query_analysis import calc_other_recommendation_parameters
from analysis_helper.calc_routing_reward import get_reward_set, reward_average_calculation

def extract_recommended_recipes(text: str):
    # 1) Position direkt vor der öffnenden eckigen Klammer finden
    m = re.search(r'Recommended Recipes:\s*\[', text)
    if not m:
        return None  # nichts gefunden
    i = m.end() - 1  # Index der '['

    # 2) Bis zur schließenden ']' der Liste laufen (Strings & Escapes beachten)
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
        return None  # keine schließende Klammer gefunden

    list_str = text[i:end]

    # 3) In echte Python-Strukturen umwandeln
    # (sicherer als eval; unterstützt Literale, None, True/False usw.)
    return ast.literal_eval(list_str)


def cals_reflector_accuracy(persona_id: int, query: str, model: ModelEnum, Path = None):
    query_stempt = query.replace(" ", "_").lower()
    id = f"{persona_id}_{query_stempt}_{model.name}"
    key = "REFLECTOR_Prompt"
    filepath = Path / f"{id}.jsonl"
    if not filepath.exists():
        return 0
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            num = 0
            for line in f:
                
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue  # kaputte Zeilen überspringen
                if obj.get("role") == key:
                    text = obj.get("content")
                    match = extract_recommended_recipes(text)
                    recipe = match[0]
                    return calc_keto_ratio(recipe.get("proteins"), recipe.get("carbohydrates"),recipe.get("fat"))
                    
    except Exception as e:
        return 0
    return 0
