#@Noah Meißner 18.05.2025

from clean_dataset import DataClean
import random
import os
import re

"""
In dieser File wird ein Trainingsdatensatz generiert, sowie ein Testdatensatz um die Model antworten zu analysieren
"""


class DataLoader:

    def __init__(self, dataset):
        self.dataset = dataset.sample(n=5000, random_state=42)
        self.train_path = 'Data/Ingredients/train_labels.txt'
        self.test_path = 'Data/Ingredients/test_labels.txt'

    def split_single_ingrd(self, txt):
        simplfd_txt = txt.lower()
        items = re.split(r'\n+', simplfd_txt)
        return items



    def make_label_set(self):
        data_obj = DataClean(self.dataset)
        df = data_obj.preprocess_data()
        all_ingredients = []
        id = 0
        for index, row in df.iterrows():
            if id < 13000:
                id+=1
                all_ingredients.extend(self.split_single_ingrd(row['ingredients']))
            else:
                break

        unique_ingredients = list(set(all_ingredients))
        random.shuffle(unique_ingredients) 

        total_needed = 10000 + 1000
        if len(unique_ingredients) < total_needed:
            print(unique_ingredients)
            raise ValueError(f"Nicht genug eindeutige Zutaten gefunden ({len(unique_ingredients)} < {total_needed}){len(all_ingredients)}")

        train_labels = unique_ingredients[:10000]
        test_labels = unique_ingredients[10000:total_needed]

        with open(self.train_path, 'w', encoding='utf-8') as f:
            for label in train_labels:
                f.write(f"{label}\n")

        with open(self.test_path, 'w', encoding='utf-8') as f:
            for label in test_labels:
                f.write(f"{label}\n")
        
        return train_labels, test_labels
    
    def load_txt(self, PATH):
        with open(PATH, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f]

    
    def get_train(self):
        if os.path.exists(self.train_path):
            return self.load_txt(self.train_path)
        else:
            train, test = self.make_label_set()
            return train
            

    def get_test(self):
        if os.path.exists(self.test_path):
            return self.load_txt(self.test_path)
        else:
            train, test = self.make_label_set()
            return test

    def get_set(self):
        if os.path.exists(self.test_path):
            return self.load_txt(self.train_path), self.load_txt(self.test_path)
        else:
            train, test = self.make_label_set()
            return train, test