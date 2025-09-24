# Noah Meissner 5.09.2025

"""
This class is responsible for the Loaind of the simulated Recommender Tasks
"""
import json
from foodrec.config.structure.dataset_enum import ModelEnum
from analysis_helper.metrics import filter_search

def get_file_path(Path,query: str, persona_id: int, model: ModelEnum):
    """Get the file path for a given persona_id, query, and model."""
    query_stempt = query.replace(" ", "_").lower()
    id = f"{persona_id}_{query_stempt}_{model.name}"
    id = id.replace("?", "").replace("\'","")
    filepath = Path / f"{id}.jsonl"
    if not filepath.exists():
        print(filepath)
        return None
    return filepath

def check_availability(persona_id: int, query: str, model: ModelEnum, Path = None):
    """Check if the search results contain recipes and 
    return the assistant's recommendation, search results, and reflector meta."""
    ls_search = []
    ref = {}
    filepath = get_file_path(Path=Path, query=query, persona_id=persona_id, model=model)

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
                        if zw_res is not None and len(zw_res) > len(ls_search):
                            ls_search = zw_res
                except Exception as e:
                    print(f"Error processing line: {line}, Error: {e}")
                    continue
    except:
        print(f"Error reading file {filepath}")
        return None

    return None

def get_search_engine(Path):
    """Get the search engine from the given path."""
    with open(Path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data, data

def get_dicts_set(df, model:ModelEnum, Path):
    """Get the dictionaries for all entries in the dataframe."""
    pred = {}
    gt = {}
    ref = {}
    for index, row in df.iterrows():
        try:
            persona_id = row["id"]
            query = row["query"]
            pred[query], gt[query], ref[query] = check_availability(persona_id=persona_id,
                                                                    query=query,
                                                                    model=model,
                                                                    Path=Path)
        except Exception as e:
            print(query)
            print(e)
    return pred, gt, ref

