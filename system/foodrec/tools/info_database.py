# Noah Meissner 31.07.2025

'''
    This class is responsible for getting the Information about the User
'''

import pandas as pd
from foodrec.config.structure.paths import DATASET_PATHS

def load_set():
    return pd.read_csv(DATASET_PATHS / "zw_personas.csv")

class InformationDataBase:
    """
        This Class is responsible for overhanding the Persona to the System if needed
    """

    def __init__(self):
        self.dataset = load_set()
    
    def query(self, id):
        return self.dataset[self.dataset['id'] == id]['persona']
    

