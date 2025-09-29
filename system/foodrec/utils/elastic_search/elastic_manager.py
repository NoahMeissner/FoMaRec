# Noah Meissner 16.07.2025

'''
This class is responsible for indexing the data into the database
'''


from foodrec.data.kochbar import KochbarLoader
from foodrec.data.all_recipe import AllRecipeLoader

from foodrec.utils.data_preperation.cuisine_classifier import CuisineClassifier
from foodrec.utils.data_preperation.recipe_embedding import RecipeEmbedder
import joblib
from foodrec.evaluation.is_ketogen import is_ketogenic
from tqdm import tqdm
tqdm.pandas()
import logging
from enum import Enum
import ast

from foodrec.utils.elastic_search.elastic_index import Indexer
from elasticsearch import Elasticsearch
from foodrec.config.structure.paths import DATASET_PATHS
from foodrec.utils.elastic_search.elastic_configurator import SetUpElastic
from foodrec.config.structure.dataset_enum import DatasetEnum
import pandas as pd
class set_up(Enum):
        DEPLOYED = 1
        EMPTY = 2
        ERROR = 3
        NEW = 4
        FINISH = 5



class IndexElastic:

    def __init__(self, dataset_name =DatasetEnum.KOCHBAR):
        '''
            TODO
            - Cusine Classification
            - Embeddings Generation
            - In Elastic reinklatschen
        '''
        self.dataset = self.load_dataset(dataset_name)
        print(self.dataset.columns)
        self.dataset_name = dataset_name
        print("Dataset Loaded")

    def load_dataset(self, dataset_name):
        if dataset_name == DatasetEnum.KOCHBAR:
            KB = KochbarLoader()
            return KB.load_dataset()
        else:
            AL = AllRecipeLoader()
            return AL.load_dataset()
        
    def prepare_and_classify(self, ingredients):
        if isinstance(ingredients, str):
            try:
                ingredients = ast.literal_eval(ingredients)
            except (ValueError, SyntaxError):
                ingredients = []
        return self.cuisine_classifier.classify(ingredients)

    '''Classify the cuisine for each Recipe'''
    def get_cuisine(self, df):
        PATH = DATASET_PATHS / f"cuisine_{self.dataset_name.name}.csv"
        if PATH.exists():
            df = pd.read_csv(PATH)
            df['cuisine'] = df['cuisine'].apply(lambda x: ast.literal_eval(x)[0] if isinstance(x, str) and x.startswith('[') else x)
            return df
        print("start cuisisne")
        self.cuisine_classifier = CuisineClassifier(self.dataset_name)
        df['cuisine'] = df['ingredients_normalized'].progress_apply(self.prepare_and_classify)
        df.to_csv(DATASET_PATHS / f"cuisine_{self.dataset_name.name}.csv")
        print("cuisine finished")
        return df
    
    '''Generate Embeddings and Save Them'''
    def get_title_embedding(self, df):
        PATH = DATASET_PATHS / f"recipe_embeddings_{self.dataset_name.name}.pkl"
        if PATH.exists():
            return joblib.load(PATH)
        print("start embedding")
        recipe_embedder = RecipeEmbedder()
        embeddings = recipe_embedder.generate_embeddings(df)
        print("embedding Finish")
        joblib.dump(embeddings, DATASET_PATHS / f"recipe_embeddings_{self.dataset_name.name}.pkl")
        return embeddings
    

    def connect_data(self, embeddings, df, biase=False):
        recipes = []
        errors = 0

        for idx, emb_id in enumerate(embeddings["id"]):
            df_id = df.iloc[idx].get("recipe_href")

            if emb_id != df_id:
                logging.warning(f"ID mismatch at index {idx}: embedding_id='{emb_id}' vs df_id='{df_id}'")
                errors += 1
                continue  # oder: raise ValueError(...) wenn du stoppen willst
            calories = df.iloc[idx].get("kcal")
            protein = df.iloc[idx].get("protein")
            fat = df.iloc[idx].get("fat")
            carbohydrates = df.iloc[idx].get("carbohydrates")
            ketogen = is_ketogenic(protein_g=protein, carbs_g=carbohydrates, fat_g=fat, calories=calories)
            doc = {
                "id": emb_id,
                "title": df.iloc[idx].get("recipe_name"),
                "rate_average": df.iloc[idx].get("rate_average", 3.0),
                "ingredients": df.iloc[idx].get("ingredients_normalized", []),
                "tutorial": df.iloc[idx].get("tutorial"),
                "cooking_time": df.iloc[idx].get("cooking_time"),
                "kcal": df.iloc[idx].get("kcal"),
                "protein": df.iloc[idx].get("protein"),
                "carbohydrates": df.iloc[idx].get("carbohydrates"),
                "fat": df.iloc[idx].get("fat"),
                "recipe_href": emb_id,
                "cuisine": df.iloc[idx].get("cuisine"),
                "embeddings": embeddings["text_embeddings"][idx].tolist(),
            }
            if not biase or ketogen:
                recipes.append(doc)
            

        logging.info(f"Successfully matched {len(recipes)} recipes. Skipped {errors} due to ID mismatch.")
        return recipes

    

    def index_data(self, new=False, biase=False):     
        try:        
            es_client = Elasticsearch("http://localhost:9200")
            setup = SetUpElastic(new=new, es_client=es_client, index_name="database")
            bool_exist = setup.setUp()
            print(bool_exist)
            if not bool_exist:
                return set_up.DEPLOYED

            # First Step: Add Cuisine to Data
            print("heir")
            cuisine_df = self.get_cuisine(self.dataset)

            # Second: Generate Embeddings
            recipe_embeddings = self.get_title_embedding(cuisine_df)

            # Third: Combine Data
            ls_recipes = self.connect_data(recipe_embeddings, cuisine_df, biase)
            print(ls_recipes[0])

            # Fourth: Index Data
            indexer = Indexer(ls_data=ls_recipes, es_client=es_client, index_name="database")
            success = indexer.index_data(batch_size=100)

            if success:
                print("Alle indexiert.")
                return set_up.FINISH
            else:
                print("❌ Indexierung fehlgeschlagen.")
                return set_up.ERROR

        except Exception as e:
            print(f"❌ Fehler beim Indexieren: {e}")
            return set_up.ERROR
            