# Noah Meissner 5.09.2025

"""
This class is responsible for the Loaind of the simulated Recommender Tasks
"""

import json
from foodrec.config.structure.dataset_enum import ModelEnum 
from foodrec.evaluation.metrics.metrics import macro_over_queries,filter_search, micro_over_queries, accuracy, f1_score, mean_average_precision_over_queries


def check_availability(persona_id: int, query: str, model: ModelEnum, Path = None):
    query_stempt = query.replace(" ", "_").lower()
    id = f"{persona_id}_{query_stempt}_{model.name}"
    ls_search = []
    ref = {}
    filepath = Path / f"{id}.jsonl"
    if not filepath.exists():
        print(filepath)
        return None, None
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    print(line)
                    continue  # kaputte Zeilen überspringen
                try:
                    if obj.get("role") == "REFLECTOR":
                        ref = obj.get("meta", [])
                    if obj.get("role") == "assistant":
                        ls_search = filter_search(ls_search)
                        return [obj.get("content"), ls_search, ref]
                    if obj.get("role") == "Search_Results":
                        zw_res = obj.get("meta", [])
                        if zw_res!= None and len(zw_res) > len(ls_search):
                            ls_search = zw_res
                except Exception as e:
                    print(f"Error processing line: {line}, Error: {e}")
                    continue
    except:
        print(f"Error reading file {filepath}")
        return None
    
    return None


from foodrec.config.structure.paths import CONVERSATION, DATASET_PATHS
from foodrec.config.structure.dataset_enum import ModelEnum 
import json



def get_search_engine(Path):
    with open(Path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data, data
    
def get_dicts_set(df, model:ModelEnum, Path):
    pred = {}
    gt = {}
    ref = {}
    for index, row in df.iterrows():
        try:
            persona_id = row["id"]
            query = row["query"]
            pred[query], gt[query], ref[query] = check_availability(persona_id=persona_id, query=query, model=model, Path=Path)
        except Exception as e:
            print(query)
            print(e)
    return pred, gt, ref

