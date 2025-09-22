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
from analysis_helper.calc_routing_reward import get_reward_set, reward_average_calculation

def most_common_path(df, persona_id: int, query: str, model: ModelEnum, Path=None):
    query_stempt = query.replace(" ", "_").lower()
    allowed_roles = {"INTERPRETER_Output", "USER_ANALYST", "SEARCH_Output", "ITEM_ANALYST", "REFLECTOR"}
    file_id = f"{persona_id}_{query_stempt}_{model.name}"
    filepath = Path / f"{file_id}.jsonl"

    if not filepath.exists():
        return []  # always return a list

    routing = []
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
                role = obj.get("role")
                if role in allowed_roles:
                    routing.append(str(role)[:2].upper())
    except Exception:
        return []  # on any error, return empty list for consistency

    return routing  # list of short codes, possibly empty
