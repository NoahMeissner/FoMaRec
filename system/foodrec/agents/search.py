# 13.06.2025 @Noah Meissner

"""
Agent responsible for request to the DataBase
"""

from foodrec.agents.agent import Agent
from typing import Set
from foodrec.agents.agent_state import AgentState
from foodrec.search.search_ingredients import Search
from foodrec.config.structure.dataset_enum import DatasetEnum
from elasticsearch import Elasticsearch
from foodrec.utils.multi_agent.get_model import get_model
from foodrec.config.prompts.load_prompt import get_prompt, PromptEnum
import json
from foodrec.utils.multi_agent.output import output_search
from foodrec.utils.elastic_search.elastic_manager import IndexElastic
from foodrec.config.structure.dataset_enum import DatasetEnum

def check_Elastic(es):
        if not es.indices.exists(index='database'):
            IE = IndexElastic(dataset_name=DatasetEnum.ALL_RECIPE)
            IE.index_data(new=True)

class SearcherAgent(Agent):
    """Agent für externe Suchen"""
    
    def __init__(self):
        super().__init__("Searcher")
        es = Elasticsearch("http://localhost:9200")
        check_Elastic(es)
        self.search = Search(es_client=es,dataset_name=DatasetEnum.ALL_RECIPE)
    
    def _define_requirements(self) -> Set[str]:
        return {"analysis_data"}
    
    def _define_provides(self) -> Set[str]:
        return {"search_results"}
    
    def create_prompt(self, state: AgentState) -> str:
        task_description = state.task_description
        analysis_data = state.analysis_data
        prompt = get_prompt(PromptEnum.SEARCH, state.biase)
        prompt = prompt.replace("$task_description$", str(task_description))
        prompt = prompt.replace("$analysis_data$", str(analysis_data))
        return prompt
    
    
    def parse_output(self, response: dict) -> str:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
        request = result['REQUEST']
        return request
    
    def parse_search_output(self, response: enumerate) -> list:
        ls = []
        for i, hit in enumerate(response, 1):
            recipe = {}
            source = hit["_source"]
            title = source.get("title", "Kein Titel vorhanden")
            calories = source.get("kcal")
            cuisine = source.get("cuisine")
            rating = source.get("rate_average")
            cooking_time = source.get("cooking_time")
            ingredients = source.get("ingredients")
            recipe['id'] = i
            recipe['title'] = title
            recipe['calories'] = calories
            recipe['cuisine'] = cuisine
            recipe['rating'] = rating
            recipe['cooking_time'] = cooking_time
            recipe['ingredients'] = ingredients
            ls.append(recipe)
        return ls
    
    def _execute_logic(self, state: AgentState) -> AgentState:
        prompt = self.create_prompt(state)
        model = get_model(state.model)
        result = None
        try:
            model_output = model.__call__(prompt)
            response = self.parse_output(model_output)
            search_output = self.search.search(response)
            result = self.parse_search_output(search_output)
            output_search(result)
        except Exception as e:
            print(f"❗️ Search Agent Error: {e}")
        
        state.search_results = result
        state.messages = state.get("messages", []) + [
            f"{self.name}: Search completed - {result}"
        ]
        return state

