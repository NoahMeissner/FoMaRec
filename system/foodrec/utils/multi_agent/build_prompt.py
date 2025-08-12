# Noah Meissner 11.08.2025

"""
    This class is responsible for the generation of the Thought Manager prompt
"""


from foodrec.agents.agent_state import AgentState
from typing import List
from foodrec.utils.multi_agent.create_multi_agent_prompt import _build_available_data_summary, _build_completion_status, _build_reflections, _build_task_prompt
from foodrec.config.prompts.load_prompt import PromptEnum, get_prompt
from foodrec.agents.manager_steps import ManagerStep
from foodrec.agents.agent_names import AgentEnum
from foodrec.config.prompts.agent_prompt.agent_descriptions import get_agent_description

def _build_scratchpad(state, steps: List[ManagerStep]) -> str:
    """Build scratchpad from previous steps with completion status"""
    scratchpad = ""
    for step in steps:
        scratchpad += f"Thought: {step.thought}\n"
        scratchpad += f"Action: {step.action}\n"
        if step.observation:
            scratchpad += f"Observation: {step.observation}\n"
    
        scratchpad += "\n**CURRENT STATUS:**\n"
        if state.completed_agents:
            scratchpad += f"Completed agents: {', '.join(state.completed_agents)}\n"
        if state.analysis_data:
            scratchpad += f"User analysis: Available\n"
        if state.task_description:
            scratchpad += f"Task interpreted: {state.task_description}\n"
        if state.search_results:
            scratchpad += f"Search results: Available\n"
    return None if scratchpad == "" else scratchpad

def _allowed_actions(state: AgentState) -> List[str]:
    """
    Determine which actions are allowed based on what has been completed.
    Always allow INTERPRETER and USER_ANALYST; progressively unlock the rest.
    """
    completed = {agent.lower() for agent in (state.completed_agents or [])}
    # Start with the two that are always allowed
    allowed = []
    if AgentEnum.INTERPRETER.value.lower() not in completed or state.run_count > 0:
        allowed.append(AgentEnum.INTERPRETER.value)
    if AgentEnum.USER_ANALYST.value.lower() not in completed or state.run_count > 0:
        allowed.append(AgentEnum.USER_ANALYST.value)
    # If user analysis is done, allow SEARCH
    if AgentEnum.USER_ANALYST.value.lower() in completed:
        allowed.append(AgentEnum.SEARCH.value)

    # If search is done, allow ITEM_ANALYST
    if AgentEnum.SEARCH.value.lower() in completed:
        allowed.append(AgentEnum.ITEM_ANALYST.value)

    # If item analysis is done, allow REFLECTOR
    if AgentEnum.ITEM_ANALYST.value.lower() in completed:
        allowed.append(AgentEnum.REFLECTOR.value)

    # If reflector is done, allow FINISH
    if AgentEnum.REFLECTOR.value.lower() in completed and state.is_final:
        allowed.append(AgentEnum.FINISH.value)

    return allowed

def _load_agent(ls_agent_names):
    descriptions = get_agent_description()
    return [[name, descriptions[name]] for name in ls_agent_names]

def build_prompt_thought(state: AgentState) -> str:
    sections = {
            "reflections": _build_reflections(state),
            "query": state.query,
            "task_interpretation": _build_task_prompt(state),
            "scratchpad": _build_scratchpad(state, state.manager_steps),
            "allowed" : _allowed_actions(state)
        }
    available_data = _build_available_data_summary(state)
    completed_agents = state.completed_agents
    prompt = get_prompt(PromptEnum.THOUGHT, biased=state.biase)
    for key, value in sections.items():
        replacement_txt = f"{key} : {value}" if value != None else ""
        prompt = prompt.replace(f"${key}$", str(replacement_txt))

    if completed_agents:
        prompt += f"Already called Agents: {completed_agents}"
    if available_data:
        prompt += f"\n\n**AVAILABLE DATA:**\n{available_data}\n"
    if hasattr(state, 'reflector_accepted'):
        prompt += f"\n\n**Reflector Acceptance Status:**\n{state.is_final}\n"

    return prompt

def build_prompt_action(state:AgentState, thought: str) -> str:
    prompt = get_prompt(PromptEnum.ACTION, biased=state.biase)
    action_names = _allowed_actions(state)
    actions = _load_agent(action_names)
    prompt = prompt.replace("$THOUGHT$",thought)
    prompt = prompt.replace("$ALLOWED$", str(actions))
    return prompt


