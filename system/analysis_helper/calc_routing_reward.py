import pandas as pd 
import numpy as np 
from foodrec.config.structure.dataset_enum import ModelEnum 
from foodrec.evaluation.create_dataset import create_dataset
from foodrec.evaluation.is_ketogen import is_ketogenic, calc_keto_ratio
from foodrec.config.structure.paths import CONVERSATION, DATASET_PATHS
import json
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

def check_reward(persona_id: int, query: str, model: ModelEnum, Path = None):
    query_stempt = query.replace(" ", "_").lower()
    id = f"{persona_id}_{query_stempt}_{model.name}"
    ls_search = []
    filepath = Path / f"{id}.jsonl"
    if not filepath.exists():
        return None, None
    roles = [AgentEnum.USER_ANALYST.value, AgentEnum.SEARCH.value, AgentEnum.REFLECTOR.value, AgentEnum.FINISH.value, AgentEnum.ITEM_ANALYST.value, AgentEnum.INTERPRETER.value]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            ls = [AgentEnum.START.value]
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue  # kaputte Zeilen überspringen
                try:
                    if obj.get("role") in roles:
                        ls.append(obj.get("role"))
                    if obj.get("role") == "INTERPRETER_Output":
                        ls.append(AgentEnum.INTERPRETER.value)
                    if obj.get("role") == "Search_Results":
                        ls.append(AgentEnum.SEARCH.value)
                    if obj.get("role") == "assistant":
                        ls.append(AgentEnum.FINISH.value)
                except Exception as e:
                    print(f"Error processing line: {line}, Error: {e}")
                    continue
            return ls
    except:
        print(f"Error reading file {filepath}")
        return None
    
    return None

def reward_average_calculation(reward_system):
    gamma = 1
    normalize = True  # auf Wunsch vergleichbar machen

    scores = []
    for i, episode in enumerate(reward_system, start=1):
        score = final_episode_reward(episode, gamma=gamma, normalize=normalize)
        scores.append(score)

    # Optional: Gesamtauswertung
    avg_score = sum(scores) / len(scores) if scores else 0.0
    return f"Score: {avg_score:.4f} bei gamma={gamma}, normalize={normalize}"

def get_reward_set(df, model:ModelEnum, Path):
    ls_res = []
    for index, row in df.iterrows():
        try:
            persona_id = row["id"]
            query = row["query"]
            ls_res.append(check_reward(persona_id=persona_id, query=query, model=model, Path=Path))
        except Exception as e:
            print(query)
            print(e)
    return ls_res