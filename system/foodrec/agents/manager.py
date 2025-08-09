from typing import List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re

# Your existing imports
from foodrec.agents.agent import Agent
from foodrec.agents.agent_state import AgentState  # Using your AgentState
from foodrec.agents.interpreter import TaskInterpreterAgent
from foodrec.agents.user_analyst import UserItemAnalystAgent
from foodrec.agents.item_analyst import ItemAnalystAgent
from foodrec.agents.search import SearcherAgent
from foodrec.agents.reflect import ReflectorAgent
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.config.prompts.load_prompt import PromptEnum, get_prompt
from foodrec.utils.multi_agent.get_model import get_model
from foodrec.utils.multi_agent.output import output_manager


class ActionType(Enum):
    ANALYSE_USER = "Analyse[user"
    ANALYSE_ITEM = "Analyse[item"
    SEARCH = "Search"
    INTERPRET = "Interpret"
    FINISH = "Finish"


@dataclass
class ManagerStep:
    """Represents a single step in the Manager's reasoning process"""
    step_number: int
    thought: str
    action: str
    observation: Optional[str] = None
    is_final: bool = False


class ManagerAgent(Agent):
    """Manager Agent using LLM-based reasoning with Thought-Action-Observation pattern"""
    
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
    
    def _execute_logic(self, state: AgentState) -> AgentState:
        """Main execution using LLM-based reasoning"""
        # Store state reference for scratchpad building
        self._current_state = state
        
        # Initialize state fields if needed
        self._initialize_state(state)
        
        current_step = len(getattr(state, 'manager_steps', []))
        
        if current_step >= self.max_steps:
            # Force finish if max steps reached
            state.is_final = True
            state.candidate_answer = self._generate_fallback_answer(state)
            return state
                
        # Get LLM model
        model = get_model(state.model)
        
        # Prepare prompt and get LLM response
        prompt = self._build_prompt(state, current_step)
        model_output = model.__call__(prompt)
        
        # Parse LLM output
        step = self._parse_llm_output(model_output, current_step + 1)
        
        # Store step in state
        if not hasattr(state, 'manager_steps'):
            state.manager_steps = []
        state.manager_steps.append(step)
        
        # Execute the action
        self._execute_action(state, step)
        
        # Update scratchpad
        state.scratchpad = self._build_scratchpad(state.manager_steps)
        output_manager(thought=step.thought,obersvation=step.observation, action=step.action,routing=state.next_agent, isfinal=state.is_final)
        if step.observation:
            # If observation is set immediately (action already completed), don't delegate
            if step.observation and state.next_agent:
                state.next_agent = None
        
        return state

    def _initialize_state(self, state: AgentState):
        """Initialize state fields if they don't exist"""
        if state.completed_agents is None:
            state.completed_agents = set()
        if not hasattr(state, 'manager_steps'):
            state.manager_steps = []
        if not hasattr(state, 'scratchpad'):
            state.scratchpad = ""
        if not hasattr(state, 'last_completed_agent'):
            state.last_completed_agent = None
        if not hasattr(state, 'max_step'):
            state.max_step = self.max_steps

    def _build_completion_status(self, state: AgentState) -> str:
        """Build a clear status of what's already been completed"""
        status = []
        
        if "task_interpreter" in state.completed_agents and state.task_description:
            status.append(f"✓ Task interpreted: {state.task_description}")
        
        if "user_item_analyst" in state.completed_agents and state.analysis_data:
            status.append("✓ User analysis completed - preferences known")
        
        if "searcher" in state.completed_agents and state.search_results:
            status.append("✓ Search completed - results available")
        
        if state.item_analysis:
            status.append("✓ Item analysis completed")
        
        return "\n".join(status) if status else ""

    def _build_prompt(self, state: AgentState, current_step: int) -> str:
        """Build the prompt for the LLM with better state awareness"""
        
        # Build reflections if available
        reflections = self._build_reflections(state)
        
        # Build task prompt
        task_prompt = self._build_task_prompt(state)
        
        # Build scratchpad from previous steps
        scratchpad = state.scratchpad
        
        # Build available data summary
        available_data = self._build_available_data_summary(state)
        
        # Add completion status to help LLM avoid repetition
        completion_status = self._build_completion_status(state)
        
        prompt = get_prompt(PromptEnum.MANAGER, biased=state.biase)
        prompt = prompt.replace("$max_steps$", str(self.max_steps))
        prompt = prompt.replace("$reflections$", str(reflections))
        prompt = prompt.replace("$query$", str(state.query))
        prompt = prompt.replace("$task_prompt$", str(task_prompt))
        prompt = prompt.replace("$scratchpad$", str(scratchpad))
        prompt = prompt.replace("$user_id$", str(state.user_id))
        
        # Add available data information
        if available_data:
            prompt += f"\n\n**AVAILABLE DATA:**\n{available_data}\n"
        
        # Add completion status before the final instruction
        if completion_status:
            prompt += f"\n\n**IMPORTANT - ALREADY COMPLETED:**\n{completion_status}\n\nDo NOT repeat these actions. Build upon existing results.\n"
        if hasattr(state, 'reflector_accepted'):
            prompt += f"\n\n**Reflector Acceptance Status:**\n{state.reflector_accepted}\n"
        return prompt

    def _build_available_data_summary(self, state: AgentState) -> str:
        """Build a summary of currently available data"""
        data_summary = []
        
        if state.task_description:
            data_summary.append(f"• Task: {state.task_description}")
        
        if state.analysis_data:
            # Parse the user data if it's a string representation of a dict
            user_info = state.analysis_data
            if isinstance(user_info, str) and user_info.startswith("{'"):
                try:
                    import ast
                    user_dict = ast.literal_eval(user_info)
                    diet = user_dict.get('diet', 'unknown')
                    allergies = user_dict.get('allergies', [])
                    time_limit = user_dict.get('max_time_per_recipe', 'unknown')
                    favorites = user_dict.get('favorite_ingredients', [])
                    cultural = user_dict.get('cultural_preferences', [])
                    
                    data_summary.append(f"• User Profile: {diet} diet, allergies to {allergies}, max {time_limit}min recipes")
                    data_summary.append(f"• User Preferences: likes {favorites}, prefers {cultural} cuisines")
                except:
                    data_summary.append(f"• User Analysis: Available (raw data)")
            else:
                data_summary.append(f"• User Analysis: {user_info}")
        
        if state.search_results:
            if isinstance(state.search_results, list):
                data_summary.append(f"• Search Results: {len(state.search_results)} items found")
            else:
                data_summary.append(f"• Search Results: Available")
        
        if state.item_analysis:
            data_summary.append(f"• Item Analysis: Available")
        
        return "\n".join(data_summary) if data_summary else ""

    def _build_completion_status(self, state: AgentState) -> str:
        """Build a clear status of what's already been completed"""
        status = []
        
        if "task_interpreter" in state.completed_agents and state.task_description:
            status.append(f"✓ Task interpreted: {state.task_description}")
        
        if "user_item_analyst" in state.completed_agents and state.analysis_data:
            status.append("✓ User analysis completed - all user preferences are known and available")
        
        if "searcher" in state.completed_agents and state.search_results:
            status.append("✓ Search completed - results available")
        
        if "item_analyst" in state.completed_agents and state.item_analysis:
            status.append("✓ Item analysis completed")
        
        return "\n".join(status) if status else ""




    def _build_reflections(self, state: AgentState) -> str:
        """Build reflections section if feedback is available"""
        if state.feedback:
            return f"""Previous attempt feedback: {state.feedback}
Please improve your approach based on this feedback."""
        return ""

    def _build_task_prompt(self, state: AgentState) -> str:
        """Build the task prompt section"""
        if state.task_description:
            return f"Task: {state.task_description}"
        return ""

    def _build_scratchpad(self, steps: List[ManagerStep]) -> str:
        """Build scratchpad from previous steps with completion status"""
        scratchpad = ""
        for step in steps:
            scratchpad += f"Thought: {step.thought}\n"
            scratchpad += f"Action: {step.action}\n"
            if step.observation:
                scratchpad += f"Observation: {step.observation}\n"
        
    
        # Add current state summary
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
        
        # Extract thought
        model_output = model_output.replace("*","")
        thought_match = re.search(r"Thought:\s*(.*?)(?=Action:|$)", model_output, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else "No thought provided"
        
        # Extract action
        action_match = re.search(r"Action:\s*(.*?)(?=Observation:|Thought:|$)", model_output, re.DOTALL)
        action = action_match.group(1).strip() if action_match else "No action provided"
        
        # Check if it's a finish action
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
            # Extract the final answer
            finish_match = re.search(r"Finish\[(.*)\]", action)
            final_answer = finish_match.group(1) if finish_match else "Task completed"
            state.candidate_answer = final_answer
            state.is_final = True
            state.next_agent = None
            step.observation = f"Task finished with answer: {final_answer}"
            
        elif action.startswith("Analyse[user"):
            # Check if user analysis already exists
            if state.analysis_data and "user_item_analyst" in state.completed_agents:
                step.observation = f"User analysis already available: {state.analysis_data}"
                state.next_agent = None  # Don't delegate again
            else:
                state.next_agent = "user_item_analyst"
                step.observation = None
                
        elif action.startswith("ItemAnalyst["):
            # Item analysis request
            item_match = re.search(r"ItemAnalyst\[(.*)\]", action)
            if item_match:
                item_id = item_match.group(1).strip()
                # Check if this specific item was already analyzed
                if hasattr(state, 'analyzed_items') and item_id in state.analyzed_items:
                    step.observation = f"Item {item_id} already analyzed"
                    state.next_agent = None
                else:
                    state.target_item_id = item_id
                    state.next_agent = "item_analyst"
                    step.observation = None

        elif action.startswith("Reflector["):
            reflector_match = re.search(r"Reflector\[(.*)\]", action)
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
            # Check if search already completed with similar query
            search_match = re.search(r"Search\[(.*)\]", action)
            if search_match:
                if "user_item_analyst" not in state.completed_agents:
                    step.observation = "Error: You must call Analyse[user, $user_id$] before Search. User preferences are required to perform meaningful search."
                    state.next_agent = None
                search_query = search_match.group(1)
                if state.search_results and "searcher" in state.completed_agents:
                    step.observation = f"Search already completed. Results available: {len(state.search_results) if isinstance(state.search_results, list) else 'Available'} items found"
                    state.next_agent = None
                else:
                    state.search_query = search_query
                    state.next_agent = "searcher"
                    step.observation = None
                    
        elif action.startswith("Interpret["):
            # Check if interpretation already done
            if state.task_description and "task_interpreter" in state.completed_agents:
                step.observation = f"Task already interpreted: {state.task_description}"
                state.next_agent = None
            else:
                interpret_match = re.search(r"Interpret\[(.*)\]", action)
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
            finish_match = re.search(r"Finish\[(.*)\]", action)
            final_answer = finish_match.group(1) if finish_match else "Task completed"
            state.candidate_answer = final_answer
            state.is_final = True
            state.next_agent = None
            step.observation = f"Task finished with answer: {final_answer}"
   
        else:
            # Unknown action
            step.observation = f"Unknown action: {action}"
            state.next_agent = None


    def _add_observation_to_last_step(self, state: AgentState, observation: str):
        """Add observation to the last step after agent execution"""
        if hasattr(state, 'manager_steps') and state.manager_steps:
            state.manager_steps[-1].observation = observation
            # Update scratchpad
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


    


