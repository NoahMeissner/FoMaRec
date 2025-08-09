# Noah Meissner 21.07.2025

'''
In this script we receive the raw data produced from the Information Extraction LLM.
Out Task is to process the data into numeric data, to use it for search
'''

import pandas as pd
import numpy as np
    

def parse_calories(calories):
    '''
    Converts calorie to numeric scale.
    - less (<=400 kcal): 1
    - average (401–700 kcal): 2
    - lot (>700 kcal): 3
    '''
    if isinstance(calories, str):
        calorie_map = {
            "less": [0, 400],
            "average": [400, 700],
            "lot": [700, 4000]
        }
        return calorie_map.get(calories.lower(), None)
    return None

def parse_time(time):
    '''
    Converts time to numeric scale.
    - time (<=400 kcal): 1
    - average (401–700 kcal): 2
    - lot (>700 kcal): 3
    '''
    if isinstance(time, str):
        time_map = {
            "fast": [0,30],
            "slow": [30, 100000],
        }
        print(time)
        return time_map.get(time.lower(), None)
    return None

def process_cuisine(ls):
    def process_cuisine(txt):
        if "latin" == txt:
            return "latin_america"
        if "asia" == txt:
            return "asia"
        if "europe" == txt:
            return "central_europe"
        if "middle_east" == txt:
            return "middle_east"
        return None
    return [process_cuisine(txt) for txt in ls]


        
def process_data(time, cuisine, calories, ingredients_avoid, ingredients_included):
    '''
        time: fast, slow, or []
        cuisine: europe, middle_east, latin, asia
        persons: 1-20 or []
        calories: less, average, lot
    '''

    time = None if time is None or time == [] else parse_time(time)
    cuisine = None if cuisine is None or cuisine == [] else process_cuisine(cuisine)
    calories = None if calories is None or calories == [] else parse_calories(calories)
    ingredients_avoid = None if ingredients_avoid is None or ingredients_avoid == [] else ingredients_avoid
    ingredients_included = None if ingredients_included is None or ingredients_included == [] else ingredients_included

    return {
        "time": time,
        "cuisine": cuisine,
        "calories": calories,
        "include": ingredients_included,
        "avoid": ingredients_avoid
    }






