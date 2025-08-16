# Noah Meissner 15.08.2025

"""
    This file runs all, Querys from the personas
"""

from foodrec.system_request import run_query
from foodrec.config.structure.dataset_enum import ModelEnum
from tqdm import tqdm
import pandas as pd
from foodrec.config.structure.paths import DATASET_PATHS


def simulate_query(query:str, persona_id: int, model=ModelEnum.Gemini, biase_agent:bool=False, biase_search:bool=False):
    query_stempt = query.replace(" ", "_").lower()
    out = run_query(query, chat_id=f"{persona_id}_{query_stempt}_{model.name}",user_id=persona_id, model=model, biase_agents=biase_agent, biase_search=biase_search)
    return out

def run_all_queries(model=ModelEnum.Gemini, biase_agent:bool=False, biase_search:bool=False):
    df = pd.read_json(DATASET_PATHS / "zw_personas.json")
    res = {}
    for index, row in tqdm(df, desc="Running queries"):
        query = row['query']
        persona_id: int = row['id']
        res[query] = simulate_query(query, persona_id=persona_id, model=model, biase_agent=biase_agent, biase_search= biase_search)
    return res

def create_dataset(model=ModelEnum.Gemini, biase_agent:bool=False, biase_search:bool=False):
    print(60* "-")
    print(f"Running Simulation with Model: {model.name}, Biase Agent: {biase_agent}, Biase Search: {biase_search}")
    res = run_all_queries(model=model, biase_agent=biase_agent, biase_search= biase_search)
    return res