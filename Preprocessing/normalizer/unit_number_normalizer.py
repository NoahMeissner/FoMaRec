# 11.06.2025 @Noah Meissner

import pandas as pd
import numpy as np
from data_structure.paths import NOR_LABEL_UNITS
import json
from numbers import Number

def load_units():
    with open(NOR_LABEL_UNITS, 'r', encoding='utf-8') as f:
        units = json.load(f)
    return units

def get_units_normalize(ner_labels):
    dict_labels = load_units()
    labels = list(set(dict_labels.values()))

    res = []
    for obj in ner_labels:
        obj_clean = str(obj).strip()
        try:
            res.append(dict_labels[obj_clean])
        except:
            if obj_clean in labels:
                res.append(obj_clean)
            else:
                a=1
                #print(f"label: {obj_clean} Missing")
    return res

def get_number_normalized(ner_labels):
    res = []
    for obj in ner_labels:
        obj_string = str(obj).strip()
        try:
            number = int(obj_string)
            res.append(number)
        except ValueError:
            res.append(obj_string)
    return res

