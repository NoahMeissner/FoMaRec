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
from foodrec.agents.agent_names import AgentEnum
from foodrec.agents.agent_names import AgentEnum, AgentReporter
from foodrec.tools.conversation_manager import record
import random

def check_Elastic(es):
        if not es.indices.exists(index='database'):
            IE = IndexElastic(dataset_name=DatasetEnum.ALL_RECIPE)
            IE.index_data(new=True)

class SearcherAgent(Agent):
    """Agent für externe Suchen"""
    
    def __init__(self):
        super().__init__(AgentEnum.SEARCH.value)
        es = Elasticsearch("http://localhost:9200")
        check_Elastic(es)
        self.again = False
        self.search = Search(es_client=es,dataset_name=DatasetEnum.ALL_RECIPE)
    
    def _define_requirements(self) -> Set[str]:
        return {"analysis_data"}
    
    def _define_provides(self) -> Set[str]:
        return {"search_results"}
    
    def create_prompt(self, state: AgentState) -> str:
        if state.feedback != None and state.feedback != "":
            print(f"Und dann hebt er ab und völlig losgelöst {state.feedback}")
            prompt = get_prompt(PromptEnum.SEARCH_AGAIN, state.biase)
            analysis_data = state.analysis_data
            self.again = True
            previous_query = state.search_query
            feedback = state.feedback
            task_description = state.task_description
            prompt = prompt.replace("$PreviousQUERY$", str(previous_query))
            prompt = prompt.replace("$task_description$", str(task_description))
            prompt = prompt.replace("$analysis_data$", str(analysis_data))
            prompt = prompt.replace("$FEEDBACK$", str(feedback))
            record(AgentReporter.SEARCH_Prompt.name, prompt)
            return prompt

        else:
            task_description = state.task_description
            analysis_data = state.analysis_data
            prompt = get_prompt(PromptEnum.SEARCH, state.biase)
            prompt = prompt.replace("$task_description$", str(task_description))
            prompt = prompt.replace("$analysis_data$", str(analysis_data))
            record(AgentReporter.SEARCH_Prompt.name, prompt)
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
            proteins = source.get("protein")
            fat = source.get("fat")
            carbohydrates = source.get("carbohydrates")
            recipe['id'] = random.randint(1, 100000)
            recipe['title'] = title
            recipe['calories'] = calories
            recipe['cuisine'] = cuisine
            recipe['rating'] = rating
            recipe['cooking_time'] = cooking_time
            recipe['ingredients'] = ingredients
            recipe['proteins'] = proteins
            recipe['fat'] = fat
            recipe['carbohydrates'] = carbohydrates
            ls.append(recipe)
        return ls
    
    def _execute_logic(self, state: AgentState) -> AgentState:
        prompt = self.create_prompt(state)
        model = get_model(state.model)
        result = None
        try:
            model_output = model.__call__(prompt)
            response = self.parse_output(model_output)
            record(AgentReporter.SEARCH_Output.name, response)
            
            search_output = self.search.search(response)
            result = self.parse_search_output(search_output)
            output_search(result)
        except Exception as e:
            print(f"❗️ Search Agent Error: {e}")
        state.search_feedback = ""
        if state.feedback != None and state.feedback != "":
            before = state.search_results
            result.extend(before)
        state.search_results = result
        record(AgentReporter.Search_Results.name, "SEARCH_RESULTS", result)
        state.search_query = response
        state.messages = state.get("messages", []) + [
            (self.name, f"Search completed - {result}")
        ]
        return state

