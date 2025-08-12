# Noah Meissner 31.07.2025

"""
This Agent is for the Interpretation Task responsible
"""

from foodrec.agents.agent import Agent
from foodrec.utils.multi_agent.get_model import get_model
from foodrec.config.prompts.load_prompt import get_prompt, PromptEnum
from foodrec.utils.multi_agent.output import output_interpreter
from foodrec.agents.agent_state import AgentState
import json
from typing import Set
from foodrec.agents.agent_names import AgentEnum


class TaskInterpreterAgent(Agent):    
    def __init__(self):
        super().__init__(AgentEnum.INTERPRETER.value)
    
    def _define_requirements(self) -> Set[str]:
        return {}
    
    def _define_provides(self) -> Set[str]:
        return {"task_description"}
    
    def _create_prompt(self, state:AgentState) -> str:
        query = state.query
        prompt = get_prompt(PromptEnum.INTERPRETER, state.biase)
        prompt = prompt.replace("$query$",query)
        return prompt
    
    def _parse_llm_response(self, response: str) -> list[str]:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
        request = result['RESPONSE']
        return request 

    def _execute_logic(self, state: AgentState) -> AgentState:
        prompt = self._create_prompt(state)
        model = get_model(state.model)
        try:
             llm_response = model(prompt)
             result = self._parse_llm_response(llm_response)
        except Exception as e:
            print(f"❗️ Interpreter ERROR: {e}")
        
        state.task_description = result
        print(state)
        state.messages = state.get("messages", []) + [
            (self.name, f"Task interpreted - {result}")
        ]
        output_interpreter(result)
        return state