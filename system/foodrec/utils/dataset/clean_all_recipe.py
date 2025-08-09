# Noah Meissner 25.07.2025

from foodrec.utils.dataset.clean import DataClean


columns = ['recipe_id','recipe_name','recipe_description','avg_rating','ingredients_list','recipe_directions','duration','protein','carbohydrates','fat','kcal']

class CleanAllRecipe(DataClean):

    def __init__(self, raw_data):
        self.raw_data = self.rename(raw_data[columns])

    def rename(self, df):
        return df.rename(columns={
            'recipe_id':'recipe_href',
            'recipe_description':'description',
            'avg_rating': 'rating_rate',
            'ingredients_list': 'ingredients_normalized',
            'recipe_directions': 'tutorial',
            'duration': 'cooking_time',
            'protein': 'protein',
            'carbohydrates': 'carbohydrates',
            'fat': 'fat',
            'kcal':'kcal'
        })
    
    def clean_rating(self, df):
        def safe_int(x):
            try:
                return int(x)
            except (ValueError, TypeError):
                return None 

        df['rating_rate'] = df['rating_rate'].map(safe_int)
        return df
    
    def edit_numbers(self, df, number, column):
        return df[df[column]<number]

    
    def edit_carbs(self, df):
        ls = [['cooking_time',4000],['protein',1000],['carbohydrates',2000],['fat',2000]]
        for carb in ls:
            column = carb[0]
            number = carb[1]
            df = self.edit_numbers(df, number, column)
        return df


    def preprocess_data(self):
        raw = self.rename(self.raw_data)
        raw = self.clean_rating(raw)
        raw = self.edit_carbs(raw)
        return raw

