# Noah Meißner 16.09.2025


"""
This class is responsible for the calculation of the path length
"""
import json
from foodrec.config.structure.dataset_enum import ModelEnum
from analysis_helper.load_dataset import get_file_path

def calc_path_length(persona_id: int, query: str, model: ModelEnum, path = None):
    """Calculate the path length of the conversation"""
    ls_key = ["INTERPRETER_Output", "USER_ANALYST", "SEARCH_Output", "ITEM_ANALYST", "REFLECTOR", ]
    filepath = get_file_path(Path=path, query=query, persona_id=persona_id, model=model)
    if filepath is None:
        return 0
    try:
        with open(filepath, "r", encoding="utf-8") as json_list:
            num = 0
            for line in json_list:

                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("role") in ls_key:
                    num +=1
            return num
    except Exception as exception: #pylint: disable=broad-except
        print(exception)
        return None
    return None
