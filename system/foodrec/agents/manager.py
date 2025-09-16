# Noah Meissner 09.08.2025

'''
Manager Agent using LLM-based reasoning with Thought-Action-Observation pattern
We have three phases:
- First Thought process
- Second Action Process
- Third Observation process
'''

from foodrec.agents.agent import Agent
from foodrec.agents.agent_state import AgentState
from foodrec.agents.interpreter import TaskInterpreterAgent
from foodrec.agents.user_analyst import UserItemAnalystAgent
from foodrec.agents.item_analyst import ItemAnalystAgent
from foodrec.agents.search import SearcherAgent
from foodrec.agents.reflect import ReflectorAgent
from foodrec.config.prompts.load_prompt import PromptEnum, get_prompt
from foodrec.utils.multi_agent.get_model import get_model
from foodrec.utils.multi_agent.output import output_manager
from typing import List, Optional, Set
from dataclasses import dataclass
from foodrec.utils.multi_agent.create_multi_agent_prompt import _build_available_data_summary, _build_completion_status, _build_reflections, _build_task_prompt
import re
import time 
from foodrec.tools.conversation_manager import record
import json
from foodrec.config.structure.paths import CONVERSATION
from foodrec.utils.multi_agent.build_prompt import build_prompt_thought, build_prompt_action
from foodrec.agents.agent_names import AgentEnum, AgentReporter

@dataclass
class ManagerStep:
    """Represents a single step in the Manager's reasoning process"""
    step_number: int
    thought: str
    action: str
    observation: Optional[str] = None
    is_final: bool = False

class ManagerAgent(Agent):

    def __init__(self):
        super().__init__(AgentEnum.MANAGER.value)
        self.available_agents = {
            AgentEnum.INTERPRETER.value: TaskInterpreterAgent(),
            AgentEnum.USER_ANALYST.value: UserItemAnalystAgent(),
            AgentEnum.ITEM_ANALYST.value: ItemAnalystAgent(),
            AgentEnum.SEARCH.value: SearcherAgent(),
            AgentEnum.REFLECTOR.value: ReflectorAgent()
        }
        self.max_steps = 4

    def _define_requirements(self) -> Set[str]:
        return set()
    
    def _define_provides(self) -> Set[str]:
        return {"next_agent", "candidate_answer", "manager_steps", "scratchpad"}
        
    def call_thought(self, state):
        try:
            model = get_model(state.model)
            prompt = build_prompt_thought(state)
            record(AgentReporter.MANAGER_Thought_Prompt.name, prompt)
            return model.__call__(prompt)
        except Exception as e:
            print(e)

    def call_action(self, state, thought):
        model = get_model(state.model)
        prompt = build_prompt_action(state, thought)
        record(AgentReporter.MANAGER_Action_Prompt.name, prompt)
        return model.__call__(prompt)

    def _initialize_state(self, state: AgentState):
        """Initialize missing state fields with defaults."""
        defaults = {
            'manager_steps': [],
            'scratchpad': "",
            'last_completed_agent': None,
            'max_step': self.max_steps
        }
        for key, value in defaults.items():
            setattr(state, key, getattr(state, key, value))

    
    def _parse_llm_output(self, model_output: str, step_number: int) -> ManagerStep:
        """Parse the LLM output to extract Thought, Action, and potentially Observation"""
        model_output = model_output.replace("*","")
        thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|$)", model_output, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else "No thought provided"
        action_match = re.search(r"Action:\s*(.*?)(?=Observation:|Thought:|$)", model_output, re.DOTALL)
        action = action_match.group(1).strip() if action_match else "No action provided"
        is_final = action.startswith("Finish[")
        
        return ManagerStep(
            step_number=step_number,
            thought=thought,
            action=action,
            is_final=is_final
        )
    
    def convert_str_json(self, response: str) -> json:
        try:
            response = response.replace("*", "")
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return result
        except:
            print("#"*20 + "Error" + 20*"#")
            print(response)

            # find() gibt int zurück → prüfe auf -1 statt direkt auf truthy
            if response.find('{') != -1:
                if response.find('}') == -1:
                    return self.convert_str_json(response=response + '}')
            return response
    
    def _parse_thought_output(self, model_output: str) -> str:
        try:
            structured_ouput = self.convert_str_json(model_output)
            result = structured_ouput.get("ANSWER", None)
            if result is None:
                return model_output
            return result
        except:
            print(model_output)
            return model_output
    
    def _parse_action_output(self, model_output: str) -> str:
        structured_ouput = self.convert_str_json(model_output)
        agent_name = structured_ouput.get("Agent", None)
        reqeust = structured_ouput.get("Request", None)
        if agent_name == None:
            print(model_output)
            print("error")
        return [agent_name, reqeust]
    
    
    def _execute_action(self, state: AgentState, step: ManagerStep):
        try:
            action = step.action
            action_name = (AgentEnum(a.upper()).name if (a := action[0]) and isinstance(a, str) else None)
            request = action[1]
            if action_name != None:
                if action_name == AgentEnum.INTERPRETER.name:
                    if state.task_description and AgentEnum.INTERPRETER.value in state.completed_agents:
                        step.observation = f"Task already interpreted: {state.task_description}"
                        state.next_agent = None
                    else:
                        state.interpret_content = request
                        step.observation = None
                        state.next_agent = AgentEnum.INTERPRETER.value
                elif action_name == AgentEnum.USER_ANALYST.name:
                    if state.analysis_data and AgentEnum.USER_ANALYST.value in state.completed_agents:
                        step.observation = f"User analysis already available: {state.analysis_data}"
                        state.next_agent = None
                    else:
                        state.next_agent = AgentEnum.USER_ANALYST.value
                        step.observation = None
                elif action_name == AgentEnum.SEARCH.name:
                    if hasattr(state, 'reflection_feedback') and not state.is_final:
                        state.post_rejection_search_completed = False
                    if state.search_results and AgentEnum.SEARCH.value in state.completed_agents and state.run_count == 0:
                        step.observation = f"Search already completed. Results available: {len(state.search_results) if isinstance(state.search_results, list) else 'Available'} items found"
                        state.next_agent = None
                    else:
                        state.search_query = request
                        state.next_agent = AgentEnum.SEARCH.value
                        step.observation = None
                elif action_name == AgentEnum.ITEM_ANALYST.name:
                    if state.item_analysis and AgentEnum.ITEM_ANALYST.value in state.completed_agents and state.run_count == 0:
                        step.observation = f"Search Results already analyzed"
                        state.next_agent = None
                    else:
                        state.next_agent = AgentEnum.ITEM_ANALYST.value
                        step.observation = None
                elif action_name == AgentEnum.REFLECTOR.name:
                    if state.reflection_feedback and AgentEnum.REFLECTOR.value in state.completed_agents and state.run_count == 0:
                        step.observation = f"Reflector already completed. Results available: {state.reflection_feedback}"
                        state.next_agent = None
                    else:
                        state.reflector_query = request
                        state.next_agent = AgentEnum.REFLECTOR.value
                        step.observation = None
                elif action_name == AgentEnum.FINISH.name:
                    if not state.is_final:
                        step.observation = "Cannot finalize. Reflector did not accept the recommendation yet."
                        state.next_agent = None
                    else:
                        state.candidate_answer = request
                        state.next_agent = None
                        step.observation = f"Task finished with answer: {request}"
                else:
                    step.observation = f"Unknown action: {action}"
                    state.next_agent = None
        except Exception as e:
            print(e)

    

    def _execute_logic(self, state: AgentState) -> AgentState:
        self._current_state = state        
        self._initialize_state(state)

        # If we have more than 4 revisions call fallback answer
        current_step = state.run_count
        if current_step > self.max_steps:
            state.is_final = True
            state.candidate_answer = "Maximum Iterations reached. No further revisions possible."
            return state
        if not hasattr(state, 'manager_steps'):
            state.manager_steps = []

        output_thought = self.call_thought(state=state)
        thought = self._parse_thought_output(output_thought)
        record(AgentReporter.MANAGER_Thought.name, output_thought)
        output_action = self.call_action(state=state, thought=thought)
        record(AgentReporter.MANAGER_Action.name, output_action)

        action = self._parse_action_output(output_action)
        step = ManagerStep(
            step_number=current_step,
            thought=thought,
            action=action,
            is_final=state.is_final
        )
        state.manager_steps.append(step)
        self._execute_action(state, step)
        output_manager(thought=step.thought,obersvation=step.observation, action=step.action,routing=state.next_agent, isfinal=state.is_final)
        return state
