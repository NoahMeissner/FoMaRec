# Noah Meissner 15.08.2025

"""
    This file runs all, Querys from the personas
"""

from foodrec.system_request import run_query
from foodrec.config.structure.dataset_enum import ModelEnum
from tqdm import tqdm
import pandas as pd
from elasticsearch import Elasticsearch
from typing import Iterable, Mapping, Any, List, Dict, Optional
from foodrec.search.search_ingredients import Search
from foodrec.config.structure.dataset_enum import DatasetEnum
import json
from uuid import uuid4
from foodrec.config.structure.paths import DATASET_PATHS, CONVERSATION

def check_availability(id: str = ""):
    filepath = CONVERSATION / f"{id}.jsonl"
    if not filepath.exists():
        return None
    
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
                if obj.get("role") == "assistant":
                    return obj.get("content")
    except:
        return None
    
    return None

def _to_number(val: Any, typ=float) -> Optional[float]:
    if val is None:
        return None
    try:
        # handle strings like "123", "123.4", "  99 "
        return typ(str(val).strip())
    except (ValueError, TypeError):
        return None

def _to_list(val: Any) -> List[str]:
    if val is None:
        return []
    if isinstance(val, list):
        # ensure all items are strings
        return [str(x).strip() for x in val if x is not None]
    # sometimes a comma/semicolon-separated string
    s = str(val).strip()
    if not s:
        return []
    # split on commas or semicolons
    parts = [p.strip() for p in s.replace(";", ",").split(",")]
    return [p for p in parts if p]



def parse_search_output( response: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        for hit in response:
            # hit is expected to look like an ES hit: {"_id": "...", "_source": {...}}
            source: Mapping[str, Any] = hit.get("_source", {}) if isinstance(hit, Mapping) else {}

            title = str(source.get("title") or "Kein Titel vorhanden")

            recipe: Dict[str, Any] = {
                "id": hit.get("_id") or str(uuid4()),  # stable if _id exists, otherwise UUID
                "title": title,
                "calories": _to_number(source.get("kcal"), float),
                "cuisine": source.get("cuisine"),
                "rating": _to_number(source.get("rate_average"), float),
                "cooking_time": _to_number(source.get("cooking_time"), int),  # assume minutes
                "ingredients": _to_list(source.get("ingredients")),
                "proteins": _to_number(source.get("protein"), float),
                "fat": _to_number(source.get("fat"), float),
                "carbohydrates": _to_number(source.get("carbohydrates"), float),
            }

            results.append(recipe)

        return results

def simulate_query(query:str, persona_id: int, model, biase_agent:bool=False, biase_search:bool=False, print_output:bool=False):
    if model == None:
        es = Elasticsearch("http://localhost:9200")
        search = Search(es_client=es,dataset_name=DatasetEnum.ALL_RECIPE)
        search_output = search.search(query, biase_search)
        return parse_search_output(search_output)

    query_stempt = query.replace(" ", "_").lower()
    id = f"{persona_id}_{query_stempt}_{model.name}"
    available = check_availability(id)
    if available is not None:
        return available
    out = run_query(query, chat_id=id ,user_id=persona_id, model=model, biase_agents=biase_agent, biase_search=biase_search, print_output=print_output)
    return out

def run_all_queries(model=ModelEnum.Gemini, biase_agent:bool=False, biase_search:bool=False, print_output:bool=False):
    df = pd.read_csv(DATASET_PATHS / "zw_personas.csv")
    res = {}
    for index, row in tqdm(df.iterrows(), desc="Running queries", total=len(df)):
        query = row['query']
        persona_id: int = row['id']
        res[query] = simulate_query(query, persona_id=persona_id, model=model, biase_agent=biase_agent, biase_search= biase_search, print_output=print_output)
        if index % 10 == 0:
            with open(f"{index}.json", "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=2)
    return res

def create_dataset(model, biase_agent:bool=False, biase_search:bool=False, print_output:bool=False):
    print(60* "-")
    print(f"Running Simulation with Model:{model.name if model is not None else 'None'}, Biase Agent: {biase_agent}, Biase Search: {biase_search}")
    res = run_all_queries(model=model, biase_agent=biase_agent, biase_search= biase_search, print_output=print_output)
    with open("res_one.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    return res