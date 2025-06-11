#11.06.2025 @Noah Meissner

"""
In this file we write combine all normalisation processes to one for each ingredient
"""

import pandas as pd
import numpy as np
from request.request_modern_bert import Bert
import re
from normalizer.ingredient_normalizer import normalize_ingredients
from normalizer.unit_number_normalizer import get_units_normalize, get_number_normalized

def get_ner(bert, item):
        try:
            result = bert.predict_and_return(str(item))
            return {"original":item, "ner":result}
        except Exception as e:
            print("Model Error:", e)

def is_number(token):
    token = token.strip()
    return re.fullmatch(r'\d+([.,]\d+)?', token) is not None

def get_label(ls, label):
    res = []
    for classification in ls:
        if classification[1].lower() == label:
            res.append(classification[0])
    return res



class Normalization:

    def __init__(self):
        self.bert = Bert()
        self.equal = 0
        self.under = 0
        self.over = 0
        self.zero = 0

    def calculate_stats(self, ls_ing, ls_normalized_ingredient):
        self.equal += int(len(ls_normalized_ingredient) == len(ls_ing))
        self.under += int(len(ls_normalized_ingredient) < len(ls_ing))
        self.over += int(len(ls_normalized_ingredient) > len(ls_ing))
        self.zero += int(len(ls_normalized_ingredient) == 0)
    
    def normalize(self, item):
        try:
            dict_ner = get_ner(self.bert, item)
            original = dict_ner['original']
            ner_labels = dict_ner['ner'][original]['entities']
            ner_labels = [[token, 'Number'] if is_number(token) else [token, label] for token, label in ner_labels]
            ls_ing = get_label(ner_labels, 'ingredients')
            ls_number = get_label(ner_labels, 'number')
            ls_unit = get_label(ner_labels, 'units')
            ls_normalized_unit = get_units_normalize(ls_unit)
            ls_normalized_number = get_number_normalized(ls_number)
            ls_normalized_ingredient = normalize_ingredients(ls_ing)
            self.calculate_stats(ls_ing, ls_normalized_ingredient)
            return ({item : {"unit":ls_normalized_unit[0], "number":ls_normalized_number[0],"ingredient":ls_normalized_ingredient[0].lower()}}, len(ls_ing))
        except:
            return ({item.upper() : {"unit":"", "number":"", "original":item}}, len(ls_ing))    
    def get_stats(self):
        return {"equal": self.equal, "under": self.under, "over": self.over, "zero":self.zero}


