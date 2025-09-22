# Noah Meißner 17.07.2025

'''
This class is responsible for searching the ingredients 
'''

'''
In this class, the pipeline is to be called up. 
At the beginning, the information extraction prompt is called up,
then ingredients and co are normalised, and then elastic is requested and the results are retrieved.
After that, a beautiful thing is thrown in so that you can read it.
'''

from foodrec.utils.search.request_information_extraction import extract_information
from foodrec.tools.ingredient_normalizer import IngredientNormalisation
from foodrec.utils.data_preperation.process_information_extraction import process_data
from foodrec.utils.data_preperation.recipe_embedding import RecipeEmbedder
from foodrec.tools.request_elastic import request_elastic




def process_information(information, normalizer: IngredientNormalisation):
    ingredients_avoid = [normalizer.normalize(obj, top_k=5)[0] for obj in information['ingredients_avoid']]
    ingredients_inclued = [normalizer.normalize(obj, top_k=5)[0] for obj in information['ingredients_included']]
    time = information['time']
    cuisine = information['cuisine']
    calories = information['calories']
    protein = information['protein']
    fat = information['fat']
    carbohydrates = information['carbohydrates']
    return process_data(time, cuisine, calories, ingredients_avoid, ingredients_inclued, protein, fat, carbohydrates)

class Search:

    def __init__(self, es_client, dataset_name):
        self.normalizer = IngredientNormalisation(dataset_name)
        self.embedder = RecipeEmbedder()
        self.es_client = es_client

    def search(self, request):
        raw_information = extract_information(request)
        information = process_information(raw_information, self.normalizer)
        print(raw_information)
        request_embedding = self.embedder.generate_request_embedding(request)
        res = request_elastic(request_embedding=request_embedding, data=information, es_client=self.es_client)
        hits = res.get("hits", {}).get("hits", [])
        if len(hits) == 0 or hits is None:
            print("No hits found, trying to search with ingredients excluded")
            print("Information: ", information)
            information['include'] = []
            res = request_elastic(request_embedding=request_embedding, data=information, es_client=self.es_client)
            hits = res.get("hits", {}).get("hits", [])
        return hits

            




