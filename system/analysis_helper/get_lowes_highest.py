import json
from foodrec.evaluation.is_ketogen import is_ketogenic, calc_keto_ratio
import numpy as np
from typing import Dict, List, Any, Tuple
from foodrec.config.structure.dataset_enum import ModelEnum 

def take_25_lowest_keto(query_set,paths, model_name:ModelEnum, high=False):
    def get_search_engine(queries: List[str], Path = None):
        filepath = Path
        recipes = []
        if not filepath.exists():
            print("error")
            return 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                obj = json.loads(f.read())
                recipes = [obj.get(query) for query in queries]
                return recipes
        except Exception as e:
            print(e)
            return None
    def calc_keto(recipe):
        proteins = recipe.get("proteins")
        fat = recipe.get("fat")
        carbohydrates = recipe.get("carbohydrates")
        return calc_keto_ratio(protein_g=proteins, fat_g=fat, carbs_g=carbohydrates)
    queries = query_set['query']
    recipes = get_search_engine(queries, paths["PATH_SEARCH_ENGINE"])
    ls = [
        (np.mean([calc_keto(r) for r in recipe if r is not None]) if recipe else np.nan)
        for recipe in recipes
    ]
    arr = np.asarray(ls, dtype=float)

    # 1) Statistiken robust gegen inf/NaN
    finite_mask = np.isfinite(arr)          # True nur für endliche Werte
    arr_finite = arr[finite_mask]
    q25, q75 = np.percentile(arr_finite, [25, 75])
    mean     = np.mean(arr_finite)
    max_val  = np.max(arr_finite)

    print("25%:", q25)
    print("75%:", q75)
    print("Mean:", mean)
    print("Max:", max_val)

    order = np.argsort(arr)                 # sortiert ALLE Indizes nach Wert (inkl. inf)

    if high:
        indices = order[-25:]
    else:
        indices = order[:25]
    print(indices[0])
    q = []
    for i in indices:
        if i < len(queries):
            #print(queries[i], ls[i])
            q.append(queries[i])
    filtered_df = query_set[query_set["query"].isin(q)]

    return filtered_df