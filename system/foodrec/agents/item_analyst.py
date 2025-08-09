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
from foodrec.llms.gemini import AnyGeminiLLM
from foodrec.utils.multi_agent.get_model import get_model
from foodrec.config.prompts.load_prompt import get_prompt, PromptEnum
from foodrec.utils.multi_agent.output import output_item_analyst



class ItemAnalystAgent(Agent):
    """Agent zur Analyse von Item Informationen"""
    
    def __init__(self):
        super().__init__("Item Analyst")
    
    def _define_requirements(self) -> Set[str]:
        return {"task_description", "analysis_data", "search_results"}
    
    def _define_provides(self) -> Set[str]:
        return {"item_analysis"}
    
    def _create_prompt(self, state:AgentState) -> str:
        prompt = get_prompt(PromptEnum.ITEM_ANALYST, state.biase)
        analysis_data = state.analysis_data
        search_results = state.search_results
        task_description = state.task_description
        prompt = prompt.replace("$analysis_data$",str(analysis_data))
        prompt = prompt.replace("$search_results$",str(search_results))
        prompt = prompt.replace("$task_description$",str(task_description))
        return prompt
    
    def _parse_llm_response(self, response: str) -> dict:

        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start == -1 or json_end <= json_start:
            raise ValueError("No valid JSON object found in response.")
        
        json_str = response[json_start:json_end]
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError("LLM response could not be parsed as JSON.") from e

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
        prompt = self._create_prompt(state)
        model = get_model(state.model)
        try:
            llm_response = model(prompt)
            result = self._parse_llm_response(llm_response)
        except Exception as e:
            print(f"❗️ ITEM ANALYST ERROR: {e}")
        state.item_analysis = result
        state.messages = state.get("messages", []) + [
            f"{self.name}: Analysis complete - {llm_response}"
        ]
        output_item_analyst(result)
        return state
    
    def output(self, results):
        print(20*'='+"Item Analyst"+'='*20)
        explanations = results['explanations']
        for index, expl in enumerate(explanations):
            print(f"Recipe {index}")
            print(f"Explanation: {expl}")
            print(10*"=")
        
