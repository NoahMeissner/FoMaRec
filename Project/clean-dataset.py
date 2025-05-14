#@Noah Meißner 14.05.2025
import pandas as pd
import numpy as np
import re

'''
Wir erhalten ein Dataframe mit den Columns:
'recipe_href', 'title', 'Bewertungen', 'Kommentare',
'Favorisiert', 'Aufgerufe', 'numstars', 'average', 'furPersonen',
'img_href', 'zutaten', 'zubereitung', 'Schwierigkeitsgrad',
'Zubereitungszeit', 'Preiskategorie', 'kj', 'kcal', 'Eiweiss',
'Kohlenhydrate', 'Fett', 'date', 'for_diabetes'

Ziel des Skripts ist die vereinheitlichung, löschen von unötigen Daten
'''
columns = [['title', 'Bewertungen',
        'Aufgerufe', 'average', 'furPersonen', 'zutaten', 'zubereitung', 'Schwierigkeitsgrad',
       'Zubereitungszeit', 'Preiskategorie', 'kcal', 'Eiweiss',
       'Kohlenhydrate', 'Fett', 'for_diabetes']]

class DataClean:
    def __init__(self, raw_data):
        self.raw_data = self.rename(raw_data[columns])
    
    def rename(self, df):
        return df.rename(columns={
            'title': 'recipe_name',
            'Bewertungen': 'rating_rate',
            'Aufgerufe': 'views',
            'average': 'average_rate',
            'furPersonen': 'persone_number',
            'zutaten': 'ingredients', #TODO vereinheitlichen
            'zubereitung': 'tutorial',
            'Schwierigkeitsgrad': 'difficulty',
            'Zubereitungszeit': 'cooking_time',
            'Preiskategorie': 'price_category', 
            'Eiweiss': 'protein',
            'Kohlenhydrate': 'Carbohydrates',
            'Fett': 'Fat',
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
    
    def edit_cooking_time(self, df):
        max_time = 4000
        return df[df['cooking_time']>max_time]
    
    def edit_protein(self, df):
        max= 1000
        return df[df['protein']>max]
    
    def edit_carbohydrates(self, df):
        max= 2000
        return df[df['Carbohydrates']>max]
    
    def edit_fat(self, df):
        max= 2000
        return df[df['Fat']>max]
    
    def edit_persone_number(self, df):
        df.loc[df['persone_number'] > 30, 'persone_number'] = np.nan
        return df


















        
