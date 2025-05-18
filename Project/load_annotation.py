#@Noah Meißner 18.05.2025

import json

PATH = "Data/admin.jsonl"

def load_json(PATH):
    jsonl_data = []
    with open(PATH, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            jsonl_data.append(obj)
    return jsonl_data

def swap_format(data):
    text = data['text']
    labels = data['label']
    ls = []
    for label in labels:
        start = label[0]
        end = label[1]
        annotation = label[2]
        ls.append((start,end,annotation))
    return (text, {"entities": ls})

def load_dataset():
    ls_raw = load_json(PATH)
    ls = []
    for obj in ls_raw:
        ls.append(swap_format(obj))
    return ls
    