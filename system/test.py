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
#from foodrec.evaluation.ingredient_normalisation import run_comprehensive_evaluation

# run_comprehensive_evaluation(sample_percentage=0.2, use_stratified=False)
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

#from foodrec.system_request import run_query
#from foodrec.config.structure.dataset_enum import ModelEnum
#out = run_query("I want to eat sth quick veggi and italian",chat_id="ALINA", model=ModelEnum.Gemini, biase=True)

from foodrec.evaluation.create_dataset import create_dataset
from foodrec.config.structure.dataset_enum import ModelEnum 
from foodrec.utils.multi_agent.get_model import get_model
import time
df = create_dataset(model=ModelEnum.Gemini, biase_agent=False, biase_search=False, print_output=False)
#df.to_csv("dataset.csv", index=False)

prompt= """
You are an Interpreter Agent in a multi-agent recipe recommendation system.\n\nYour role is to interpret the user\'s natural language query and produce a clear, concise **task description** that another agent (the Manager) can use to decide what to do next.\n\n---\n\n**This is the user query:**  \n"Recommend recipes which do not have ingredient evaporated milk?"\n\nYour goal is to:\n- Understand the user\'s intent from the query.\n- Clarify vague or underspecified requests by inferring possible meanings.\n- Rephrase the query into a clear **task objective**, such as:\n  - "Search for tomato-based recipes."\n  - "Find healthy vegan recipes."\n  - "Recommend products that include tomatoes."\n  - "Determine whether the user wants a recipe or product related to tomatoes."\n\n---\n\nPlease respond **only in valid JSON**, in the following format:\n\n```json\n{\n  "RESPONSE": "<your clear task description>"\n}\n
"""
"""
for i in range(0,10):
    model = get_model(ModelEnum.GPT_OPEN_SOURCE)
    try:
        print(model.__call__(prompt))
    except Exception as e:
        print(e)
    """