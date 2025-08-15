# Noah Meißner 17.07.2025

'''
This class is responsible for searching the ingredients 
'''

'''
In dieser Klasse soll die Pipeline abgerufen werden. 
Am Anfang wird der Information extraction prompt aufgerufen,
danach wird ingredients und co normalisiert und dann wird elastic requested und die ergebnisse abgerufen
danach wird noch so ein Beautiful ding frübergehauen, damit man das auch lesen kann
'''

from foodrec.utils.search.request_information_extraction import extract_information
from foodrec.tools.ingredient_normalizer import IngredientNormalisation
from foodrec.utils.data_preperation.process_information_extraction import process_data
from foodrec.utils.data_preperation.recipe_embedding import RecipeEmbedder
from foodrec.tools.request_elastic import request_elastic




def process_information(information, normalizer):
    ingredients_avoid = [normalizer.advanced_hybrid_search(obj, top_k=5)[0] for obj in information['ingredients_avoid']]
    ingredients_inclued = [normalizer.advanced_hybrid_search(obj, top_k=5)[0] for obj in information['ingredients_included']]
    time = information['time']
    cuisine = information['cuisine']
    calories = information['calories']
    return process_data(time, cuisine, calories, ingredients_avoid, ingredients_inclued)

class Search:

    def __init__(self, es_client, dataset_name):
        self.normalizer = IngredientNormalisation(dataset_name)
        self.embedder = RecipeEmbedder()
        self.es_client = es_client

    def search(self, request, biase = False):
        raw_information = extract_information(request)
        information = process_information(raw_information, self.normalizer)
        print(raw_information)
        #{'time': [0, 30], 'difficulty': 'easy', 'cuisine': None, 'calories': None, 'include': ['garlic'], 'avoid': None}
        request_embedding = self.embedder.generate_request_embedding(request)
        res = request_elastic(request_embedding=request_embedding, data=information, es_client=self.es_client)
        hits = res.get("hits", {}).get("hits", [])
        return hits

            




