#@ Noah Meißner 15.05.2025

import pandas as pd
import numpy as np
from request_gemini import request
import re
from clean_dataset import DataClean
'''
Die Zutaten befinden sich in einer Unstrukturierten Form und müssen daher bereinigt werden bevor sie verwendbar sind.
Aus diesem Grund soll in diesem Skript das Feature Extraction stattfinden, um diese in eine einheitliche Form zu bringen
'''
def simplify_details(txt):
    txt = txt.replace('EL','[el]')
    txt = txt.replace('TL','[tl]')
    txt = re.sub(r'\b(\d{1,3})\s*(g|gr)\b', r'\1[grm]', txt, flags=re.IGNORECASE)
    txt = re.sub(r'\b(\d{1,3})\s*(l)\b', r'\1[ltr]', txt, flags=re.IGNORECASE)
    txt = txt.lower()
    txt = txt.replace('esslöffel','[el]')
    txt = txt.replace('teelöffel','[tl]')
    txt = txt.replace('prise','[p]')
    txt = txt.replace('spritzer','[sp]')
    txt = txt.replace('päckchen','[pk]')
    txt = txt.replace('stück','[stk]')
    txt = txt.replace('stk','[stk]')
    txt = txt.replace('milliliter','[mltr]')
    txt = txt.replace('ml','[mltr]')
    txt = txt.replace('gramm','[grm]')
    txt = txt.replace('Liter','[ltr]')

    
    return txt

def split_single_ingrd(txt):
    simplfd_txt = simplify_details(txt)
    items = re.split(r'\n+', simplfd_txt)
    return items

def extract_feature(df, column):
    df[f'ls_{column}'] = df.apply(lambda x: split_single_ingrd(x[column]), axis=1)




def make_label_set():
    data_obj = DataClean(pd.read_csv('Data/dataset.csv'))
    df = data_obj.preprocess_data()
    ls = []
    for index, row in df.iterrows():
        if index<1000:
            ls.extend(split_single_ingrd(row['ingredients']))
        else:
            break
    ls = list(set(ls))

    with open('Data/labels.txt', 'w', encoding='utf-8') as f:
        for index in range(0,1000):
            f.write(f"{ls[index]}\n")
make_label_set()