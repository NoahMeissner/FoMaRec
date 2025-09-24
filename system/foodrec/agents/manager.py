# Noah Meissner 09.08.2025

'''
Manager Agent using LLM-based reasoning with Thought-Action-Observation pattern
We have three phases:
- First Thought process
- Second Action Process
- Third Observation process
'''
import re
import json
from typing import Optional, Set
from dataclasses import dataclass
from foodrec.agents.agent import Agent
from foodrec.agents.agent_state import AgentState
from foodrec.agents.interpreter_agent import TaskInterpreterAgent
from foodrec.agents.user_analyst import UserItemAnalystAgent
from foodrec.agents.item_analyst import ItemAnalystAgent
from foodrec.agents.search_agent import SearcherAgent
from foodrec.agents.reflector_agent import ReflectorAgent
from foodrec.utils.multi_agent.get_model import get_model
from foodrec.utils.multi_agent.output import output_manager
from foodrec.tools.conversation_manager import record
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
    """Agent that manages the workflow of other agents using LLM-based reasoning."""
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
        """Calls the LLM to generate a thought based on the current state."""
        try:
            model = get_model(state.model)
            prompt = build_prompt_thought(state)
            record(AgentReporter.MANAGER_Thought_Prompt.name, prompt)
            return model.__call__(prompt)
        except Exception as exception: #pylint: disable=broad-except
            print(exception)
            return "Thought: Error generating thought. Action: Finish[Error]"

    def call_action(self, state, thought):
        """Calls the LLM to decide on an action based on the current thought."""
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
        action_match = re.search(r"Action:\s*(.*?)(?=Observation:|Thought:|$)",
                                model_output,
                                re.DOTALL)
        action = action_match.group(1).strip() if action_match else "No action provided"
        is_final = action.startswith("Finish[")

        return ManagerStep(
            step_number=step_number,
            thought=thought,
            action=action,
            is_final=is_final
        )

    def convert_str_json(self, response: str) -> json:
        """Convert a string that contains JSON into a JSON object."""
        try:
            response = response.replace("*", "")
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                return result
        except Exception as exception: # pylint: disable=broad-exception-caught
            print(f"❗️ JSON parsing failed: {exception}")
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
        except Exception as exception: # pylint: disable=broad-exception-caught
            print(f"❗️ Thought parsing failed: {exception}")
            print(model_output)
            return model_output

    def _parse_action_output(self, model_output: str) -> str:
        structured_ouput = self.convert_str_json(model_output)
        agent_name = structured_ouput.get("Agent", None)
        reqeust = structured_ouput.get("Request", None)
        if agent_name is None:
            print(model_output)
            print("error")
        return [agent_name, reqeust]

    def _execute_action(self, state: AgentState, step: ManagerStep):
        def set_step(observation=None, next_agent=None):
            step.observation = observation
            state.next_agent = next_agent

        def get_action_name(action):
            if not action or not isinstance(action, (list, tuple)) or not action[0]:
                return None, None
            act = action[0]
            request_ = action[1] if len(action) > 1 else None
            try:
                return AgentEnum(str(act).upper()).name, request_
            except Exception:
                return None, request_

        def already_done(attr_name: str, agent_enum: AgentEnum) -> bool:
            return (getattr(state, attr_name, None)
                    and agent_enum.value in state.completed_agents
                    and getattr(state, "run_count", 0) == 0)

        action = step.action
        action_name, request = get_action_name(action)

        try:
            if action_name is None:
                set_step(f"Unknown action: {action}", None)
                return

            # --- Handlers ---
            def handle_interpreter():
                if state.task_description and AgentEnum.INTERPRETER.value in state.completed_agents:
                    set_step(f"Task already interpreted: {state.task_description}", None)
                else:
                    state.interpret_content = request
                    set_step(None, AgentEnum.INTERPRETER.value)

            def handle_user_analyst():
                if state.analysis_data and AgentEnum.USER_ANALYST.value in state.completed_agents:
                    set_step(f"User analysis already available: {state.analysis_data}", None)
                else:
                    set_step(None, AgentEnum.USER_ANALYST.value)

            def handle_search():
                if hasattr(state, "reflection_feedback") and not getattr(state, "is_final", False):
                    state.post_rejection_search_completed = False
                if already_done("search_results", AgentEnum.SEARCH):
                    count = (len(state.search_results)
                            if isinstance(state.search_results, list)
                            else "Available")
                    set_step(f"""Search already completed.
                             Results available: {count} items found""", None)
                else:
                    state.search_query = request
                    set_step(None, AgentEnum.SEARCH.value)

            def handle_item_analyst():
                if already_done("item_analysis", AgentEnum.ITEM_ANALYST):
                    set_step("Search Results already analyzed", None)
                else:
                    set_step(None, AgentEnum.ITEM_ANALYST.value)

            def handle_reflector():
                if already_done("reflection_feedback", AgentEnum.REFLECTOR):
                    set_step(f"""Reflector already completed.
                             \nResults available: {state.reflection_feedback}\n""", None)
                else:
                    state.reflector_query = request
                    set_step(None, AgentEnum.REFLECTOR.value)

            def handle_finish():
                if not getattr(state, "is_final", False):
                    set_step("Cannot finalize. \nReflector did not accept the recommendation yet.", None)
                else:
                    state.candidate_answer = request
                    set_step(f"Task finished with answer: {request}", None)

            # --- Dispatch table ---
            handlers = {
                AgentEnum.INTERPRETER.name: handle_interpreter,
                AgentEnum.USER_ANALYST.name: handle_user_analyst,
                AgentEnum.SEARCH.name: handle_search,
                AgentEnum.ITEM_ANALYST.name: handle_item_analyst,
                AgentEnum.REFLECTOR.name: handle_reflector,
                AgentEnum.FINISH.name: handle_finish,
            }

            handler = handlers.get(action_name)
            if handler is None:
                set_step(f"Unknown action: {action}", None)
                return

            handler()

        except Exception as exception:  # pylint: disable=broad-except
            print(exception)


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
        output_manager(thought=step.thought,
                    obersvation=step.observation,
                    action=step.action,
                    routing=state.next_agent,
                    isfinal=state.is_final)
        return state
