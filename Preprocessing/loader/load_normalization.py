# 3.06.2025 @Noah Meissner

from data_structure.DataType import DataType
from data_structure.model_name import ModelName
import json
from data_structure.paths import NORMALIZATION_DIR


def save_response(approach=ModelName,type=DataType, data=[{}]):
    path = NORMALIZATION_DIR/f"{type.value}/{approach.value}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_response(approach=ModelName, type=DataType):
    path = NORMALIZATION_DIR/f"{type.value}/{approach.value}.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Datei nicht gefunden: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen von JSON: {e}")
        return None