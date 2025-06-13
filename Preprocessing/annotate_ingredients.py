# 3.06.2025 @Noah Meissner

from request.request_gemini import request
import pandas as pd
from DataLoader_Ingredients import DataLoader
from prompts import ingredients_extraction
import json
import tqdm
import os
import ast
from data_structure.DataType import DataType
from data_structure.model_name import ModelName
from loader.load_ner import  ner_loader, ner_safer
import re
from data_structure.paths import RAW_SET, NER_TRA, NER_PRE

def pack_twenty(data, existing_keys):
    filtered = [item for item in data if str(item) not in existing_keys]
    return [filtered[i:i+20] for i in range(0, len(filtered), 20)]


def clean_model_output(str):
    match = re.search(r'\[(.*)\]', str, re.DOTALL)
    if match:
        cleaned_json = "[" + match.group(1).strip() + "]"
    try:
        parsed_data = ast.literal_eval(cleaned_json)
        return parsed_data
    except Exception as e:
        print("Fehler beim Parsen:", e)

def convert_list_to_dict(data_list):
    result = {}
    for item in data_list:
        for key, value in item.items():
            result[key] = value
    return result

def load_json_from_folder(folder_path):
    data_list = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    data_list.append(convert_list_to_dict(data))
                except json.JSONDecodeError:
                    print(f"Warning: File {filename} is not a valid JSON file.")
    
    return data_list



def label_data():
    df_whole = pd.read_csv(RAW_SET)
    loader_obj = DataLoader(df_whole)
    train, test = loader_obj.get_set()
    combined = load_json_from_folder(NER_PRE)
    merged = {k: v for d in combined for k, v in d.items()}
    if not os.path.exists(NER_TRA/"Gemini.json"):
        packages = pack_twenty(train, set(merged.keys()))
        res = []
        prompt = ingredients_extraction.prompt_ingredients
        for idx, p in enumerate(tqdm(packages, desc="Verarbeite Pakete")):
            try:
                new_prompt = prompt.replace("$DATA$", str(p))
                output = request(new_prompt)
                cleaned = clean_model_output(output)
                res.extend(cleaned)
                if idx % 20 == 0:
                    ner_safer(id={id},type=DataType.pre,data=res)
            except Exception as e:
                print(f"Model Error bei Paket {idx + 1}: {output}")
        ner_safer(ModelName.Gemini,DataType.train,res)
    return ner_loader(ModelName.Gemini,DataType.train,res)