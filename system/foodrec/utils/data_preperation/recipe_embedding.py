# Noah Meißner 16.07.2025

"""
This Class is responsible for the calculation of the recipe embeddings based on the dataset
"""

import pandas as pd
import numpy as np
from tqdm import tqdm
tqdm.pandas()
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class RecipeEmbedder:

    def __init__(self, model_name='multi-qa-mpnet-base-dot-v1'):
        self.model = SentenceTransformer(model_name)
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        print("RecipeEmbedder initialised")


    def create_recipe_description(self, recipe_row):
        try:
            """Create comprehensive recipe description using all available data"""
            description_parts = []
            
            # Title
            if pd.notna(recipe_row.get('recipe_name')):
                description_parts.append(f"Recipe: {recipe_row['recipe_name']}")
            
            # Ingredients (most important for similarity)
            if isinstance(recipe_row.get('ingredients_normalized'), (list, np.ndarray, pd.Series)):
                if pd.notna(recipe_row.get('ingredients_normalized')).any():
                    ingredients = str(recipe_row['ingredients_normalized'])
                    description_parts.append(f"Ingredients: {ingredients}")
            
            # Preparation method
            if pd.notna(recipe_row.get('tutorial')):
                prep = str(recipe_row['tutorial'])[:200]
                description_parts.append(f"Preparation: {prep}")
            
            # Nutritional context with better categorization
            nutrition_context = []
            if pd.notna(recipe_row.get('kcal')):
                kcal = recipe_row['kcal']
                if int(kcal) > 500:
                    nutrition_context.append("high calorie hearty filling substantial meal")
                elif int(kcal) < 300:
                    nutrition_context.append("light low calorie diet friendly")
                else:
                    nutrition_context.append("moderate calorie balanced meal")
            
            if pd.notna(recipe_row.get('protein')):
                protein = recipe_row['protein']
                if int(protein) > 25:
                    nutrition_context.append("high protein muscle building fitness")
                elif int(protein) < 10:
                    nutrition_context.append("low protein light")
                else:
                    nutrition_context.append("moderate protein")
            
            if pd.notna(recipe_row.get('fat')):
                fat = recipe_row['fat']
                if int(fat) > 25:
                    nutrition_context.append("high fat rich creamy indulgent")
                elif int(fat) < 10:
                    nutrition_context.append("low fat lean healthy")
                else:
                    nutrition_context.append("moderate fat")
            
            if pd.notna(recipe_row.get('carbohydrates')):
                carbs = recipe_row['carbohydrates']
                if int(carbs) > 50:
                    nutrition_context.append("high carb energy pasta bread rice")
                elif int(carbs) < 15:
                    nutrition_context.append("low carb keto diet")
                else:
                    nutrition_context.append("moderate carb")
            
            if nutrition_context:
                description_parts.append(f"Nutrition: {' '.join(nutrition_context)}")

            if 'description' in recipe_row:
                description_parts.append(recipe_row['description'])
                    
            return " | ".join(description_parts)
        except Exception as e:
            print(e)
    
    def generate_request_embedding(self, request):
        return self.model.encode(request)
    
    def generate_embeddings(self, df):
        print(type(df))
        print(df.columns)
        descriptions = df.progress_apply(self.create_recipe_description, axis=1).tolist()
        id_ls = df['recipe_href'].tolist()
        recipe_embs = self.model.encode(descriptions, show_progress_bar=True)

        return {
            'id':id_ls,
            'text_embeddings': recipe_embs,
            'descriptions': descriptions,
        }
