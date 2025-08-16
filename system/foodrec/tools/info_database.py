# Noah Meissner 31.07.2025

'''
    This class is responsible for getting the Information about the User
'''

import pandas as pd
from foodrec.config.structure.paths import DATASET_PATHS

# TODO Hier muss noch eine Abfrage rein, ob die Datenbank schon existiert

def demo():
    persona = {
    "id":1,
    "name": "Laura",
    "age": 34,
    "diet": "vegetarian",
    "allergies": ["peanuts"],
    "max_time_per_recipe": 30,
    "favorite_ingredients": ["sweet potato", "chickpeas"],
    "cultural_preferences": ["central_europe", "asia"]
    }
    return pd.DataFrame([persona])



def load_set():
    return pd.read_csv(DATASET_PATHS / "zw_personas.csv")


class InformationDataBase:
    """
        This Class is responsible for overhanding the Persona to the System if needed
    """

    def __init__(self):
        self.dataset = load_set()
    
    def query(self, id):
        print(type(id))
        print(id)
        return self.dataset[self.dataset['id'] == id]['persona']
    

