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
from analysis_helper.most_common_path import most_common_path

def calc_time(persona_id: int, query: str, model: ModelEnum, Path = None):
    query_stempt = query.replace(" ", "_").lower()
    id = f"{persona_id}_{query_stempt}_{model.name}"
    ls_search = []
    filepath = Path / f"{id}.jsonl"
    if not filepath.exists():
        return 0
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            num = 0
            lines = [line.strip() for line in f if line.strip()]
            if not lines:
                return 0

            first_obj = json.loads(lines[0])
            last_obj = json.loads(lines[-1])
            time_first = first_obj.get("ts")
            time_last = last_obj.get("ts")
            fmt = "%Y-%m-%dT%H:%M:%S%z"
            dt1 = datetime.strptime(time_first.replace("Z", "+00:00"), fmt)
            dt2 = datetime.strptime(time_last.replace("Z", "+00:00"), fmt)
            time = (dt2 - dt1).total_seconds()
            return time
    except Exception as e:
        print(e)
        return 0
    
    return 0

def calc_mean_time(df, paths, model_name: ModelEnum):
    def calc_median_time(df, model:ModelEnum, Path):
        ls = []
        for index, row in df.iterrows():
            persona_id = row["id"]
            query = row["query"]
            ls.append(calc_time(persona_id=persona_id, query=query, model=model, Path=Path))
        return np.mean(ls)
    print("Mean Time No Biase:", calc_median_time(df, model_name, paths['PATH_NO_BIASE']))
    print("Mean Time System Biase:", calc_median_time(df, model_name, paths['PATH_SYSTEM_BIASE']))
    print("Mean Time Search Biase:", calc_median_time(df, model_name, paths['PATH_SEARCH_BIASE']))
    print("Mean Both Biase:", calc_median_time(df, model_name, paths['PATH_BOTH']))
