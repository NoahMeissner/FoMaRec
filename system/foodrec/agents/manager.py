# Noah Meissner 09.08.2025

'''
Manager Agent using LLM-based reasoning with Thought-Action-Observation pattern
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
        super().__init__("Manager")
        self.available_agents = {
            "task_interpreter": TaskInterpreterAgent(),
            "user_item_analyst": UserItemAnalystAgent(),
            "item_analyst": ItemAnalystAgent(),
            "searcher": SearcherAgent(),
            "reflector": ReflectorAgent()
        }
        self.max_steps = 10
    
    def _define_requirements(self) -> Set[str]:
        return set()
    
    def _define_provides(self) -> Set[str]:
        return {"next_agent", "candidate_answer", "manager_steps", "scratchpad"}
    
    def _match_action(self, action: str, keyword: str) -> Optional[str]:
        match = re.match(fr"{keyword}\[(.*)\]", action)
        return match

    
    def call_model(self, state):
        model = get_model(state.model)
        prompt = self._build_prompt(state)
        return model.__call__(prompt)
    
    def _execute_logic(self, state: AgentState) -> AgentState:
        """Main execution using LLM-based reasoning"""
        self._current_state = state
        
        self._initialize_state(state)
        
        current_step = len(getattr(state, 'manager_steps', []))
        
        if current_step >= self.max_steps:
            state.is_final = True
            state.candidate_answer = self._generate_fallback_answer(state)
            return state
                
        model_output = self.call_model(state=state)
        step = self._parse_llm_output(model_output, current_step + 1)
        
        if not hasattr(state, 'manager_steps'):
            state.manager_steps = []
        state.manager_steps.append(step)
        
        self._execute_action(state, step)

        if getattr(state, "last_completed_agent", None) == "reflector" and not state.reflector_accepted:
            if state.revision_round < 1:  # Only retry once
                state.revision_round += 1
                new_query = self._revise_search_requirements(state)  # ⬅️ This is the call
                state.search_results = None
                state.completed_agents.discard("searcher")  # Allow Search to run again
                state.search_query = new_query
                state.next_agent = "searcher"
                self._add_observation_to_last_step(
                    state,
                    f"Revision round {state.revision_round}: Broadening search with -> {new_query}"
                )

        state.scratchpad = self._build_scratchpad(state.manager_steps)
        output_manager(thought=step.thought,obersvation=step.observation, action=step.action,routing=state.next_agent, isfinal=state.is_final)
        if step.observation:
            if step.observation and state.next_agent:
                state.next_agent = None

        if getattr(state, "last_completed_agent", None) == "reflector" and not state.reflector_accepted:
            if state.revision_round < 1:  
                state.revision_round += 1
                new_query = self._revise_search_requirements(state)
                state.search_results = None
                state.completed_agents.discard("searcher")
                state.search_query = new_query
                state.next_agent = "searcher"
                self._add_observation_to_last_step(
                    state,
                    f"Revision round {state.revision_round}: Broadening search with -> {new_query}"
                )
            else:
                pass

        
        return state

    def _initialize_state(self, state: AgentState):
        """Initialize missing state fields with defaults."""
        defaults = {
            'completed_agents': set(),
            'manager_steps': [],
            'scratchpad': "",
            'last_completed_agent': None,
            'max_step': self.max_steps
        }
        for key, value in defaults.items():
            setattr(state, key, getattr(state, key, value))
    
    def _build_prompt(self, state: AgentState) -> str:
        sections = {
            "reflections": _build_reflections(state),
            "query": state.query,
            "task_prompt": _build_task_prompt(state),
            "scratchpad": state.scratchpad,
            "user_id": state.user_id
        }
        available_data = _build_available_data_summary(state)
        completion_status = _build_completion_status(state)

        prompt = get_prompt(PromptEnum.MANAGER, biased=state.biase)
        for key, value in sections.items():
            prompt = prompt.replace(f"${key}$", str(value))

        if available_data:
            prompt += f"\n\n**AVAILABLE DATA:**\n{available_data}\n"
        if completion_status:
            prompt += f"\n\n**IMPORTANT - ALREADY COMPLETED:**\n{completion_status}\n\nDo NOT repeat these actions. Build upon existing results.\n"
        if hasattr(state, 'reflector_accepted'):
            prompt += f"\n\n**Reflector Acceptance Status:**\n{state.reflector_accepted}\n"

        return prompt


    def _build_scratchpad(self, steps: List[ManagerStep]) -> str:
        """Build scratchpad from previous steps with completion status"""
        scratchpad = ""
        for step in steps:
            scratchpad += f"Thought: {step.thought}\n"
            scratchpad += f"Action: {step.action}\n"
            if step.observation:
                scratchpad += f"Observation: {step.observation}\n"
        
        if hasattr(self, '_current_state'):
            state = self._current_state
            scratchpad += "\n**CURRENT STATUS:**\n"
            if state.completed_agents:
                scratchpad += f"Completed agents: {', '.join(state.completed_agents)}\n"
            if state.analysis_data:
                scratchpad += f"User analysis: Available\n"
            if state.task_description:
                scratchpad += f"Task interpreted: {state.task_description}\n"
            if state.search_results:
                scratchpad += f"Search results: Available\n"
        
        return scratchpad

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

    def _execute_action(self, state: AgentState, step: ManagerStep):
        """Execute the action specified in the step"""
        action = step.action
        
        if action.startswith("Finish["):
            finish_match = self._match_action(action=action, keyword="Finish")
            final_answer = finish_match.group(1) if finish_match else "Task completed"
            state.candidate_answer = final_answer
            state.is_final = True
            state.next_agent = None
            step.observation = f"Task finished with answer: {final_answer}"
            
        elif action.startswith("Analyse[user"):
            if state.analysis_data and "user_item_analyst" in state.completed_agents:
                step.observation = f"User analysis already available: {state.analysis_data}"
                state.next_agent = None
            else:
                state.next_agent = "user_item_analyst"
                step.observation = None
                
        elif action.startswith("ItemAnalyst["):
            item_match = self._match_action(action=action, keyword="ItemAnalyst")
            if item_match:
                item_id = item_match.group(1).strip()
                if hasattr(state, 'analyzed_items') and item_id in state.analyzed_items:
                    step.observation = f"Item {item_id} already analyzed"
                    state.next_agent = None
                else:
                    state.target_item_id = item_id
                    state.next_agent = "item_analyst"
                    step.observation = None

        elif action.startswith("Reflector["):
            reflector_match = self._match_action(action=action, keyword="Reflector")
            if reflector_match:
                reflector_query = reflector_match.group(1)
                if state.reflection_feedback and "reflector" in state.completed_agents:
                    step.observation = f"Reflector already completed. Results available: {state.reflection_feedback}"
                    state.next_agent = None
                else:
                    state.reflector_query = reflector_query
                    state.next_agent = "reflector"
                    step.observation = None
            
        elif action.startswith("Search["):
            search_match = self._match_action(action=action, keyword="Search")
            if search_match:
                if "user_item_analyst" not in state.completed_agents:
                    step.observation = "Error: You must call Analyse[user, $user_id$] before Search. User preferences are required to perform meaningful search."
                    state.next_agent = None
                search_query = search_match.group(1)
                if state.search_results and "searcher" in state.completed_agents and state.revision_round == 0:
                    step.observation = f"Search already completed. Results available: {len(state.search_results) if isinstance(state.search_results, list) else 'Available'} items found"
                    state.next_agent = None
                else:
                    state.search_query = search_query
                    state.next_agent = "searcher"
                    step.observation = None
                    
        elif action.startswith("Interpret["):
            if state.task_description and "task_interpreter" in state.completed_agents:
                step.observation = f"Task already interpreted: {state.task_description}"
                state.next_agent = None
            else:
                interpret_match = self._match_action(action=action, keyword="Interpret")
                if interpret_match:
                    content_to_interpret = interpret_match.group(1)
                    state.interpret_content = content_to_interpret
                state.next_agent = "task_interpreter"
                step.observation = None
        elif action.startswith("Finish["):
            if not state.reflector_accepted:
                step.observation = "Cannot finalize. Reflector did not accept the recommendation yet."
                state.next_agent = None
                return
            finish_match = self._match_action(action=action, keyword="Finish")
            final_answer = finish_match.group(1) if finish_match else "Task completed"
            state.candidate_answer = final_answer
            state.is_final = True
            state.next_agent = None
            step.observation = f"Task finished with answer: {final_answer}"
   
        else:
            step.observation = f"Unknown action: {action}"
            state.next_agent = None


    def _add_observation_to_last_step(self, state: AgentState, observation: str):
        """Add observation to the last step after agent execution"""
        if hasattr(state, 'manager_steps') and state.manager_steps:
            state.manager_steps[-1].observation = observation
            state.scratchpad = self._build_scratchpad(state.manager_steps)

    def _generate_fallback_answer(self, state: AgentState) -> str:
        """Generate a fallback answer when max steps are reached"""
        available_info = []
        
        if state.task_description:
            available_info.append(f"task: {state.task_description}")
        if state.analysis_data:
            available_info.append(f"user analysis: {state.analysis_data}")
        if state.item_analysis:
            available_info.append(f"item analysis: {state.item_analysis.get('insights', 'basic item analysis')}")
        if state.search_results:
            available_info.append(f"search: {state.search_results}")
        if available_info:
            return f"Based on the information gathered: {', '.join(available_info)}, I recommend proceeding with the available options."
        else:
            return "I need more information to provide a comprehensive recommendation. Please provide more details about your preferences."

    def _revise_search_requirements(self, state) -> str:
        """Turn reflector feedback into an updated search query string."""
        prev = getattr(state, "search_query", "") or ""
        cues = {
            "cuisine": set(),
            "constraints": set(),
            "adaptables": 0
        }

        fb = state.feedback
        if isinstance(fb, dict):
            # Structured feedback
            for s in fb.get("suggestions", []):
                t = (s.get("type") or "").lower()
                if t == "add_cuisine" and s.get("value"):
                    cues["cuisine"].add(s["value"])
                elif t == "broaden_search":
                    for h in s.get("hints", []):
                        cues["constraints"].add(h)
                elif t in ("add_adaptables", "allow_adaptables"):
                    cues["adaptables"] = max(cues["adaptables"], int(s.get("value", 2)))
        else:
            # Heuristic fallback on free text
            text = str(fb).lower()
            if "italian" in text:
                cues["cuisine"].add("Italian")
            if "broader" in text or "broaden" in text:
                cues["constraints"].update({"≤30 minutes", "≤10 ingredients"})
            if "adaptable" in text or "twist" in text:
                cues["adaptables"] = 2

        cuisine_clause = ""
        if cues["cuisine"]:
            cuisine_clause = f" prioritize {'/'.join(sorted(cues['cuisine']))}"

        constraints_clause = ""
        if cues["constraints"]:
            constraints_clause = "; " + "; ".join(sorted(cues["constraints"]))

        adaptables_clause = ""
        if cues["adaptables"] > 0:
            adaptables_clause = f"; include ~{cues['adaptables']} non-cuisine items with explicit '{next(iter(cues['cuisine']), 'Italian')}' twists"

        # Build a revised query that keeps the original but widens scope
        revised = (
            f"{prev} {cuisine_clause}{constraints_clause}{adaptables_clause}; "
            "return 10–15 candidates with URLs and ratings"
        ).strip()

        # Clean double spaces
        revised = " ".join(revised.split())
        return revised


    


