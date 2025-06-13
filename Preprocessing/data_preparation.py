#@Noah Meißner 15.05.2025

import pandas as pd
import os
from request.request_database import get_raw
from clean_dataset import DataClean
from data_structure.paths import RAW_SET
'''
This class checks if the Dataset is already in the DataFolder. If so he uses the data there.
If the data is missing, the dataset will be downloaded from the Server
After that the preprocessing is started
'''
PATH = RAW_SET

def get_data(preprocessing=True, new=False):
    df = None
    if not os.path.exists(PATH) or new:
        new = True
        df = get_raw()
    else:
        df = pd.read_csv(PATH)
    
    if preprocessing:
        data_obj = DataClean(df)
        df = data_obj.preprocess_data()
    print(df)
    # TODO Feature Extraction


    
