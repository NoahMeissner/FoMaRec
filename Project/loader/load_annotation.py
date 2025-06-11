#@Noah Meißner 18.05.2025

import json
import re
from data_structure.paths import NER_TRA

PATH = NER_TRA/"dataset.json"

'''
TRAIN_DATA = [
    ("200g Zucker", {"entities": [(0, 4, "Number"), (5, 11, "Ingredients")]}),
    ("1 TL Salz", {"entities": [(0, 1, "Number"), (2, 4, "Units"), (5, 9, "Ingredients")]}),
]

'''

def load_json(PATH):
    raw_json =[] 
    with open(PATH, "r", encoding="utf-8") as f:
        raw_json = json.load(f)
    return raw_json


def convert_to_spacy_format(raw_data):
    spacy_data = []
    for entry in raw_data:
        for text, info in entry.items():
            try:
                entities = []
                for item in info["entities"]:
                    # Fall 1: (phrase, label)
                    if isinstance(item, (list, tuple)) and len(item) == 2:
                        phrase, label = item
                        matches = list(re.finditer(re.escape(phrase), text))
                        if matches:
                            for match in matches:
                                start, end = match.start(), match.end()
                                entities.append((start, end, label))
                        else:
                            print(f"⚠️ Phrase '{phrase}' nicht in Text gefunden: '{text}'")
                    # Fall 2: spaCy-Format mit start, end, label
                    elif isinstance(item, dict) and {"start", "end", "label"} <= item.keys():
                        start, end, label = item["start"], item["end"], item["label"]
                        # Optional: Validierung, ob start/end im Textbereich liegen
                        if 0 <= start < end <= len(text):
                            entities.append((start, end, label))
                        else:
                            print(f"⚠️ Ungültige Start/Ende-Werte bei Text: '{text}' - {item}")
                    else:
                        print(f"❌ Fehler bei Text: '{text}' - Grund: ungültige Entität: {item}")
                spacy_data.append((text, {"entities": entities}))
            except Exception as e:
                print(f'❌ Fehler bei Text: {text} - Grund: {e}')
    return spacy_data


def load_dataset():
    ls_raw = load_json(PATH)
    converted_ls = convert_to_spacy_format(ls_raw)
    return converted_ls
    
    