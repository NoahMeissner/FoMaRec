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
from foodrec.config.structure.paths import CONVERSATION
from typing import Iterable, Mapping, Any, List, Dict, Optional
from uuid import uuid4

def _to_number(val: Any, typ=float) -> Optional[float]:
    if val is None:
        return None
    try:
        # handle strings like "123", "123.4", "  99 "
        return typ(str(val).strip())
    except (ValueError, TypeError):
        return None

def _to_list(val: Any) -> List[str]:
    if val is None:
        return []
    if isinstance(val, list):
        # ensure all items are strings
        return [str(x).strip() for x in val if x is not None]
    # sometimes a comma/semicolon-separated string
    s = str(val).strip()
    if not s:
        return []
    # split on commas or semicolons
    parts = [p.strip() for p in s.replace(";", ",").split(",")]
    return [p for p in parts if p]


class SearcherAgent(Agent):
    """Agent für externe Suchen"""
    
    def __init__(self):
        super().__init__(AgentEnum.SEARCH.value)
        es = Elasticsearch("http://localhost:9200")
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
            record(AgentReporter.SEARCH_Prompt.name, prompt, path=CONVERSATION / state.model.name)
            return prompt

        else:
            task_description = state.task_description
            analysis_data = state.analysis_data
            prompt = get_prompt(PromptEnum.SEARCH, state.biase)
            prompt = prompt.replace("$task_description$", str(task_description))
            prompt = prompt.replace("$analysis_data$", str(analysis_data))
            record(AgentReporter.SEARCH_Prompt.name, prompt, path=CONVERSATION / state.model.name)
            return prompt
    
    
    def parse_output(self, response: dict) -> str:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
        request = result['REQUEST']
        return request
    
    def parse_search_output(self,query, response: Iterable[Mapping[str, Any]], biase:bool) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for hit in response:
            # hit is expected to look like an ES hit: {"_id": "...", "_source": {...}}
            source: Mapping[str, Any] = hit.get("_source", {}) if isinstance(hit, Mapping) else {}

            title = str(source.get("title") or "Kein Titel vorhanden")

            recipe: Dict[str, Any] = {
                "id": hit.get("_id") or str(uuid4()),  # stable if _id exists, otherwise UUID
                "title": title,
                "calories": _to_number(source.get("kcal"), float),
                "cuisine": source.get("cuisine"),
                "rating": _to_number(source.get("rate_average"), float),
                "cooking_time": _to_number(source.get("cooking_time"), int),  # assume minutes
                "ingredients": _to_list(source.get("ingredients")),
                "proteins": _to_number(source.get("protein"), float),
                "fat": _to_number(source.get("fat"), float),
                "carbohydrates": _to_number(source.get("carbohydrates"), float),
            }

            results.append(recipe)

        return results
    
    def search_recipe(self, response:str, biase: bool):
        return self.search.search(response, biase)
    
    def _execute_logic(self, state: AgentState) -> AgentState:
        prompt = self.create_prompt(state)
        model = get_model(state.model)
        result = None
        response = state.query
        error = False
        try:
            model_output = model.__call__(prompt)
            response = self.parse_output(model_output)
            record(AgentReporter.SEARCH_Output.name, response)
            
            search_output = self.search_recipe(response, state.biase)
            result = self.parse_search_output(response, search_output, state.biase)
            output_search(result)
        except Exception as e:
            error = True
            print(f"❗️ Search Agent Error: {e}")
        state.search_feedback = ""
        if state.feedback != None and state.feedback != "":
            if not error:
                before = state.search_results
                if before is not None:
                    result.extend(before)
        state.search_results = result
        record(AgentReporter.Search_Results.name, "SEARCH_RESULTS", result)
        state.search_query = response
        state.messages = state.get("messages", []) + [
            (self.name, f"Search completed - {result}")
        ]
        return state

