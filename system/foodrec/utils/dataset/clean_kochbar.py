#@Noah Meißner 14.05.2025
import pandas as pd
import numpy as np
from foodrec.utils.dataset.clean import DataClean

'''
Wir erhalten ein Dataframe mit den Columns:
'recipe_href', 'title', 'Bewertungen', 'Kommentare',
'Favorisiert', 'Aufgerufe', 'numstars', 'average', 'furPersonen',
'img_href', 'zutaten', 'zubereitung', 'Schwierigkeitsgrad',
'Zubereitungszeit', 'Preiskategorie', 'kj', 'kcal', 'Eiweiss',
'Kohlenhydrate', 'Fett', 'date', 'for_diabetes'

Ziel des Skripts ist die vereinheitlichung, löschen von unötigen Daten
'''
columns = ['title', 'Bewertungen',
        'Aufgerufe', 'numstars', 'furPersonen', 'zutaten', 'zubereitung', 'Schwierigkeitsgrad',
       'Zubereitungszeit', 'Preiskategorie', 'kcal', 'Eiweiss',
       'Kohlenhydrate', 'Fett', 'for_diabetes', 'recipe_href']

class KochbarClean(DataClean):
    def __init__(self, raw_data):
        self.raw_data = self.rename(raw_data[columns])
    
    def rename(self, df):
        return df.rename(columns={
            'title': 'recipe_name',
            'Bewertungen': 'rating_rate',
            'Aufgerufe': 'views',
            'numstars': 'average_rate',
            'furPersonen': 'persone_number',
            'zutaten': 'ingredients', #TODO vereinheitlichen
            'zubereitung': 'tutorial',
            'Schwierigkeitsgrad': 'difficulty',
            'Zubereitungszeit': 'cooking_time',
            'Preiskategorie': 'price_category', 
            'Eiweiss': 'protein',
            'Kohlenhydrate': 'carbohydrates',
            'Fett': 'fat',
            'kcal':'kcal'
        })

    def rename_difficulty(self, df):
        translation = {
            'leicht': 'easy',
            'mittel': 'medium',
            'schwer': 'hard',
            'nicht angegeben': None
        }
        df['difficulty'] = df['difficulty'].map(translation)
        return df
    
    def edit_price_category(self, df):
        translation = {
            1: 1,
            3: 2,
            15: 1,
            5: 3
        }
        df['price_category'] = df['price_category'].map(translation)
        return df
    
    def edit_person_number(self, df):
        df.loc[df['persone_number'] > 30, 'persone_number'] = np.nan
        return df
    
    def edit_numbers(self, df, number, column):
        return df[df[column]<number]
    
    def edit_rating(self, df):
        def safe_int(x):
            try:
                return int(x)
            except (ValueError, TypeError):
                return None 

        df['rating_rate'] = df['rating_rate'].map(safe_int)
        return df
        
    
    def edit_carbs(self, df):
        ls = [['cooking_time',4000],['protein',1000],['carbohydrates',2000],['fat',2000]]
        for carb in ls:
            column = carb[0]
            number = carb[1]
            df = self.edit_numbers(df, number, column)
        return df
    
    def preprocess_data(self):
        df = self.rename(self.raw_data)
        df = self.rename_difficulty(df)
        df = self.edit_price_category(df)
        df = self.edit_carbs(df)
        df = self.edit_rating(df)
        df = self.edit_person_number(df)
        return df
