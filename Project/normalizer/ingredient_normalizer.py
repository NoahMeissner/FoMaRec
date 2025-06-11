# 11.06.2025 @Noah Meissner

"""
In this file we write the normalizer which normalize ingredients
to make it able to compare it with other recipes
"""

from request.request_gemini import request
from data_structure.model_name import ModelName
from data_structure.DataType import DataType
from loader.load_normalization import save_response
import re
import ast
from tqdm import tqdm
from request.recipe_api import request_api
from request.request_modern_bert import Bert
from prompts.ingredients_normalization import prompt_ingredients_normalization
from normalizer.ingredient_cleaner import clean

def get_ingredients(ls):
    res = []
    for classification in ls:
        if classification[1].lower() == 'ingredients':
            res.append(classification[0])
    return res

def api_request(txt):
    output = request_api(txt)
    detailed_info = output.get("detailed_info", [])
    
    if detailed_info and len(detailed_info) > 0 and detailed_info[0] and len(detailed_info[0]) > 0:
        erkannte_zutat = detailed_info[0][0].get("erkannteZutat", "")
    else:
        erkannte_zutat = "" 
    
    return erkannte_zutat


def get_ner(bert, item):
    try:
        result = bert.predict_and_return(str(item))
        return {"original":item, "ner":result}
    except Exception as e:
        print("Model Error:", e)

def is_number(token):
    token = token.strip()
    return re.fullmatch(r'\d+([.,]\d+)?', token) is not None

def clean_model_output(str):
    match = re.search(r'\[(.*)\]', str, re.DOTALL)
    if match:
        cleaned_json = "[" + match.group(1).strip() + "]"
    try:
        parsed_data = ast.literal_eval(cleaned_json)
        return parsed_data
    except Exception as e:
        print("Fehler beim Parsen:", e)

def prepare_over(ingredient, length_ner):
    dict_spices = clean(ingredient)
    cleaned = dict_spices['cleaned']
    spices = dict_spices['spices']
    split_cleaned = [part.strip() for part in re.split(r'[%|]', cleaned)]
    ls_ingredient = []
    for i in split_cleaned:
        ls_ingredient.append((i,api_request(i)))
    ls_ingredient.extend(spices)
    if len(ls_ingredient)>length_ner:
        return ls_ingredient
    else:
        return None

def normalize_ingredients(ls_ing):
    ls = []
    prompt = prompt_ingredients_normalization
    try:
        over = [(prepare_over(value, len(ls_ing)), value) for value in ls_ing]
        split = [(api_request(value),value) for value in ls_ing]
        split.extend(over)
        final = []
        gemini_ls = []
        for index in range(0,len(over)):
            over_item = over[index]
            split_item = split[index]
            try:
                if (over_item[0] == 'Nicht erkannt' or over_item[0] is None) and (split_item[0] == 'Nicht erkannt' or split_item[0] is None):
                    gemini_ls.append(ls_ing[index])
                elif (over_item[0] == 'Nicht erkannt' or over_item[0] is None) and (split_item[0] != 'Nicht erkannt' or split_item[0] is not None):
                    final.append((split_item[1], split_item[0].upper()))
                else:
                    final.append((over_item[1], over_item[0].upper()))
            except Exception as e:
                a = 1
        try:
            if len(gemini_ls)> 0:
                final.extend(clean_model_output(str(request(prompt.replace("$DATA$",str(gemini_ls))))))
        except Exception as e:
            print("API ERROR",e)
        ls.extend(final)
    except Exception as e:
        print("Annotation error",e)
    return [value[1] for value in ls]


    


