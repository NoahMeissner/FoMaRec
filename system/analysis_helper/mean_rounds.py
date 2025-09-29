import json
from foodrec.config.structure.dataset_enum import ModelEnum
from analysis_helper.load_dataset import get_file_path

def calc_rounds(persona_id: int, query: str, model: ModelEnum, Path = None):
    """Calculate the number of REFLECTOR rounds in the conversation"""
    filepath = get_file_path(Path=Path, query=query, persona_id=persona_id, model=model)
    if filepath is None:
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
                    continue
                if obj.get("role") == "REFLECTOR":
                    num +=1
            return num
    except Exception as e:
        print(e)
        return None
    return 0
