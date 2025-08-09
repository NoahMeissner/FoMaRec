# Noah Meissner 25.07.2025

from foodrec.utils.downloader.request_database import request_database
from foodrec.config.structure.paths import ALL_RECIPE, DATASET_PATHS
import pandas as pd
from tqdm import tqdm

tables = ['feature_table','categories','parsed_recipe_ingredients','recipe_profiles','ingredients']
database = 'all_recipe'


def download_all_recipe():
    print("Download")
    for table in tables:
        df = request_database(table_name=table, database_name=database)
        df.to_csv(ALL_RECIPE / table+".csv")

def process_ingredients():
    ingredients_parsed = pd.read_csv("parsed_ingredients.csv")
    parsed_recipe_ingredients = pd.read_csv("parsed_recipe_ingredients_recipes.csv")


    ingredients = ingredients_parsed[['new_ingredient_id','name_after_processing']]
    ingredients['parsed_ingredient_id'] = ingredients['new_ingredient_id']
    recipe_ingredients = parsed_recipe_ingredients[['recipe_id','parsed_ingredient_id']]

    recipe_ingredient_dict = {}

    # tqdm um iterrows()
    for index, row in tqdm(recipe_ingredients.iterrows(), total=len(recipe_ingredients), desc="Verarbeite Rezepte"):
        recipe_id = row['recipe_id']
        ingredient_id = row['parsed_ingredient_id']
        
        # Holen des Zutaten-Namens als String (nicht Series!)
        name_series = ingredients[ingredients['parsed_ingredient_id'] == ingredient_id]['name_after_processing']
        if name_series.empty:
            continue  # falls Ingredient fehlt – optional
        ingredient_name = name_series.iloc[0]
        
        if recipe_id not in recipe_ingredient_dict:
            recipe_ingredient_dict[recipe_id] = [ingredient_name]
        else:
            recipe_ingredient_dict[recipe_id].append(ingredient_name)

    # Umwandeln in DataFrame
    df_ingredients = pd.DataFrame({
        'recipe_id': list(recipe_ingredient_dict.keys()),
        'ingredients_list': list(recipe_ingredient_dict.values())
    })

    df_ingredients.to_csv(ALL_RECIPE / "df_ingredient.csv")

def merge_all_recipe():
    feature_table = pd.read_csv("feature_table.csv")
    parsed_recipe_ingredients = pd.read_csv("parsed_recipe_ingredients_recipes.csv")
    recipe_profiles = pd.read_csv("recipe_profiles.csv")
    categories = pd.read_csv("categories.csv")
    ingredients = pd.read_csv("df_ingredient.csv")

    recipe_profile = recipe_profiles[['recipe_id','recipe_description']]
    data_feature_table = feature_table[['recipe_id','cook_id','kcal','protein','carbohydrates','fat','duration','preperation_steps','servings','ingredients','avg_rating']]
    recipe_profiles = recipe_profiles[['recipe_name','recipe_directions','recipe_id']]
    recipe_type = categories[['recipe_id','recipe_category_name']]
    ingredients = ingredients[['recipe_id','ingredients_list']]

    import pandas as pd

    # Schritt 1: Merge von recipe_profile und data_feature_table
    merged_df = pd.merge(recipe_profile, data_feature_table, on='recipe_id', how='inner')

    # Schritt 2: Merge mit recipe_profiles (enthält bereits recipe_id)
    merged_df = pd.merge(merged_df, recipe_profiles, on='recipe_id', how='inner')

    # Schritt 3: Merge mit recipe_type (Kategorien)
    merged_df = pd.merge(merged_df, recipe_type, on='recipe_id', how='inner')

    merged_df = pd.merge(merged_df, ingredients, on='recipe_id', how='inner')

    merged_df = merged_df[merged_df['recipe_category_name']!= "Home"]

    merged_df = merged_df.drop_duplicates(subset='recipe_id')

    merged_df.to_csv(DATASET_PATHS / "all_recipe.csv")


