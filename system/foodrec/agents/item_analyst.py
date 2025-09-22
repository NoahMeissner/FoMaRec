# 13.06.2025 @Noah Meissner

"""
Agent responsible for analysis of recipes
"""

from foodrec.agents.agent import Agent
from typing import Set
from foodrec.agents.agent_state import AgentState
import json
from foodrec.agents.agent import Agent
from typing import Set
from foodrec.agents.agent_state import AgentState
from foodrec.utils.multi_agent.get_model import get_model
from foodrec.config.prompts.load_prompt import get_prompt, PromptEnum
from foodrec.utils.multi_agent.output import output_item_analyst
from foodrec.agents.agent_names import AgentEnum
from foodrec.agents.agent_names import AgentEnum, AgentReporter
from foodrec.tools.conversation_manager import record
from foodrec.evaluation.is_ketogen import is_ketogenic


class ItemAnalystAgent(Agent):
    """Agent zur Analyse von Item Informationen"""
    
    def __init__(self):
        self.no_response = False
        super().__init__(AgentEnum.ITEM_ANALYST.value)
    
    def _define_requirements(self) -> Set[str]:
        return {"search_results"}
    
    def _define_provides(self) -> Set[str]:
        return {"item_analysis"}
    
    def filter_search(self, search_results):
        seen, out = set(), []
        for o in search_results:
            t = (o.get('title') or "").strip().casefold()
            if t and t not in seen:
                seen.add(t)
                out.append(o)
        for o in out:
            protein = o.get('proteins', 0)
            carbs = o.get('carbohydrates', 0)
            fat = o.get('fat', 0)
            calories = o.get('calories', 0)
            ketogen = is_ketogenic(protein_g= protein, calories=calories, fat_g=fat, carbs_g=carbs)
            o['is_ketogenic'] = ketogen
        return out

    
    def _create_prompt(self, state:AgentState) -> str:
        prompt = get_prompt(PromptEnum.ITEM_ANALYST, state.biase)
        analysis_data = state.analysis_data
        search_results = state.search_results
        filtered_search_results = self.filter_search(search_results)
        task_description = state.task_description
        prompt = prompt.replace("$analysis_data$",str(analysis_data))
        prompt = prompt.replace("$search_results$",str(filtered_search_results))
        prompt = prompt.replace("$task_description$",str(task_description))
        record(AgentReporter.ITEM_ANALYST_Prompt.name, prompt)
        return prompt
    
    def _parse_llm_response(self, response: str) -> dict:

        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start == -1 or json_end <= json_start:
            print(f"❗️ ITEM ANALYST ERROR: Invalid response format: {response}")
            self.no_response = True
            return response
        
        json_str = response[json_start:json_end]
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"❗️ ITEM ANALYST ERROR: Invalid response format: {response}")
            self.no_response = True
            return json_str

        # Extract ordered recipes and explanations
        recipe_list = []
        explanation_list = []

        # Keys like RECIPE1, RECIPE2, etc.
        i = 1
        while True:
            recipe_key = f"RECIPE{i}"
            explanation_key = f"RECIPE{i}_EXPLANATION"

            if recipe_key not in parsed:
                break

            recipe_id = parsed[recipe_key]
            explanation = parsed.get(explanation_key, "")

            recipe_list.append(recipe_id)
            explanation_list.append(explanation)
            i += 1

        return {
            "ordered_recipes": recipe_list,
            "explanations": explanation_list
        }

    
    def _execute_logic(self, state: AgentState) -> AgentState:
        self.no_response = False
        prompt = self._create_prompt(state)
        model = get_model(state.model)
        result = None
        try:
            llm_response = model(prompt)
            try:
                result = self._parse_llm_response(llm_response)
                print(f"Item Analyst Result: {result}")
                record(AgentReporter.ITEM_ANALYST.name, result)
                if not self.no_response:
                    output_item_analyst(result)
                state.item_analysis = result
                state.messages = state.get("messages", []) + [
                    (self.name, f"Analysis complete - {llm_response}")
                ]
            except Exception as e:
                print(e)
                print(llm_response)
        except Exception as e:
            print(f"❗️ ITEM ANALYST ERROR: {e}")
        return state
    
        
