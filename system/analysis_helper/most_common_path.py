import json
from foodrec.config.structure.dataset_enum import ModelEnum
from analysis_helper.load_dataset import get_file_path

def most_common_path(persona_id: int, query: str, model: ModelEnum, Path=None):
    allowed_roles = ["INTERPRETER_Output",
                     "USER_ANALYST",
                     "SEARCH_Output",
                     "ITEM_ANALYST",
                     "REFLECTOR"]
    filepath = get_file_path(Path=Path, query=query, persona_id=persona_id, model=model)
    if filepath is None:
        return []  

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
        return []

    return routing
