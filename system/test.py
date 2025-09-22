# 13.06.2025 @Noah Meissner

"""
Goal of this script is the Test if System works probably
"""
"""
from elasticsearch import Elasticsearch
from 
es = Elasticsearch(
    "https://localhost:9200",
    api_key="1ZVDsJcBWVcH62eDr-gH:uL4ESFNQSo2cQs-NTTEfIw",
    verify_certs=False
)

print(es.info())
"""
"""
from foodrec.utils.embed_ingredient import Embedder

try:
    print("Creating embedder...")
    embedder = Embedder()
    print("Testing embedding...")
    result = embedder.get_embedding("tomato sauce")
    print(f"Embedding shape: {result.shape}")
    print("Test completed successfully!")
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
"""
"""
from foodrec.data.load_ingredient_embeddings import EmbeddingLoader
loader = EmbeddingLoader()
embeddings = loader.get_embeddings()
"""
"""
from foodrec.tools.search_ingredient import IngredientNormalisation

ING = IngredientNormalisation()
print(ING.advanced_hybrid_search("bread"))
"""
"""
import subprocess
from elasticsearch import Elasticsearch
from foodrec.config.structure.paths import CONFIG
# Start-Skript ausführen
try:
    subprocess.run([CONFIG / "shell" / "start_elastic.sh"], check=True)
except subprocess.CalledProcessError as e:
    print("Fehler beim Starten von Elasticsearch:", e)"""

#from foodrec.utils.data_preperation.cuisine_classifier import CuisineClassifier

#CC = CuisineClassifier()
#print(CC.classify(["salt","garlic","pepper","tomatoes","cheese"]))
"""
"""
"""
from foodrec.tools.request_elastic import RequestElastic

RE = RequestElastic()
request = {
"question": "simple meal",
"ingredients_included": "pepper",
"ingredients_avoid": "paprica",
}
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

print(RE.request_elastic(request=request, es_client=es))
"""
"""
from foodrec.search.search_ingredients import search

print(search("I want a simple meal with pepper and no bread"))
"""
"""
from foodrec.utils.elastic_search.elastic_manager import IndexElastic

IE = IndexElastic()
IE.index_data(new=True)
"""
#from foodrec.utils.elastic_search.elastic_manager import IndexElastic

#IE = IndexElastic()
#IE.index_data(new=False)



#from foodrec.search.search_ingredients import Search
#from elasticsearch import Elasticsearch

#es = Elasticsearch("http://localhost:9200")

#search = Search(es)

#search.search("I am really hungry and want sth with pork and should be really fast and no garlic")
"""
from foodrec.llms.open_source import OpenSource

model = OpenSource(model_name="llama-3.3-70b-instruct")

prompt = "Wie hoch ist der Eiffelturm?"
print("Sende Anfrage an Modell…")
response = model(prompt)
print("Antwort vom Modell:")
print(response)
"""
"""
from foodrec.data.load_ingredient_embeddings import EmbeddingLoader
from foodrec.config.structure.dataset_enum import DatasetEnum

E_All_recipe = EmbeddingLoader(DatasetEnum.ALL_RECIPE)
E_All_recipe.get_embeddings()
E_Kochbar= EmbeddingLoader(DatasetEnum.KOCHBAR)
E_Kochbar.get_embeddings()

"""

#from foodrec.evaluation.ingredient_normalisation import run_comprehensive_evaluation


#run_comprehensive_evaluation(sample_percentage=1)
"""

from foodrec.utils.elastic_search.elastic_manager import IndexElastic
from foodrec.config.structure.dataset_enum import DatasetEnum

IE = IndexElastic(dataset_name=DatasetEnum.ALL_RECIPE)
IE.index_data(new=True)
"""
"""
from foodrec.utils.elastic_search.elastic_manager import IndexElastic
from foodrec.config.structure.dataset_enum import DatasetEnum
from foodrec.search.search_ingredients import Search
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

search = Search(es, DatasetEnum.KOCHBAR)

search.search("i want sth american")
"""

#from foodrec.test.multi_agent_system import start

#start()
"""
from foodrec.agents.manager import FoodRecGraph
from foodrec.agents.agent_state import AgentState
from foodrec.config.structure.dataset_enum import ModelEnum

def example_usage():
    # Create initial state
    initial_state = AgentState(
        task_id="rec_001",
        user_id=12345,
        conversation_history=[],
        query="I want healthy Mediterranean dinner recommendations for tonight",
        completed_agents=set(),
        is_final=False,
        run_count=0,
        model=ModelEnum.LLAMA  # Use your preferred model
    )
    
    # Run the graph
    graph = FoodRecGraph()
    final_state = graph.run(initial_state)
    
    print(f"Final answer: {final_state.candidate_answer}")
    print(f"Steps taken: {len(final_state.manager_steps)}")
    for step in final_state.manager_steps:
        print(f"Step {step.step_number}: {step.action}")

example_usage()
"""

from foodrec.evaluation.create_dataset import create_dataset
from foodrec.config.structure.dataset_enum import ModelEnum 
from foodrec.utils.multi_agent.get_model import get_model
from playsound import playsound

import time
try:
    df = create_dataset(model=ModelEnum.Gemini, biase_agent=False, biase_search=True, print_output=False)
except Exception as e:
    for i in range(0,3):
        #playsound("alarm.mp3")
        print("Error during dataset creation, retrying...")
    raise e

