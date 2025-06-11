# 3.06.2025 @Noah Meißner

"""
Wir erhalten die Hand Annotation im folgenden Format:
{"id":1003,"text":"","label":[],"Comments":[]}
und müssen dieses in das Standard Format bringen um es mit den anderen zu Vergleichen
{'2 el:petersilie gehackt, salz': {'entities': [['2', 'Number'],
   ['el', 'Units'],
   ['petersilie', 'Ingredients'],
   ['gehackt, salz', 'Type']]}}
"""

import pandas as pd
import numpy as np
import os
import json
from data_structure.DataType import DataType
from data_structure.model_name import ModelName
from data_structure.paths import INGREDIENTS_DIR

def transform_entry(entry):
    text = entry["text"]
    labels = entry["label"]

    entities = []
    for start, end, category in labels:
        span_text = text[start:end]
        cat_formatted = category.capitalize()
        entities.append([span_text, cat_formatted])

    return {text.strip(): {"entities":entities}}


def load_ground_truth(type, approach):
    path = INGREDIENTS_DIR / f"{type.value}"/ f"{approach.value}.jsonl"
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    dict_res = [{k: v} for value in data for k, v in transform_entry(value).items()]
    return dict_res


def ner_loader(approach=ModelName, type=DataType):
    path = INGREDIENTS_DIR / f"{type.value}"/ f"{approach.value}.json"
    if approach.value == ModelName.GroundTruth.value:
        return load_ground_truth(type, approach)
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

def ner_safer(approach=ModelName, type=DataType, data=[{}], id=None):
    path = ""
    if id!= None:
        path = INGREDIENTS_DIR / {type.value}/f"{id}.json"
    else:
        path = INGREDIENTS_DIR / {type.value}/ f"{approach.value}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
