# Noah Meissner 11.08.2025

"""
    This class is responsible for the generation of the Thought Manager prompt
"""


from foodrec.agents.agent_state import AgentState
from typing import List
from foodrec.utils.multi_agent.create_multi_agent_prompt import _build_available_data_summary, _build_reflections, _build_task_prompt
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

def _get_post_rejection_allowed_actions(state: AgentState, completed: set) -> List[str]:
    """
    Determine allowed actions during post-rejection cycle.
    Enforces the mandatory sequence: SEARCH -> ITEM_ANALYST -> REFLECTOR
    """
    if state.last_completed_agent == AgentEnum.REFLECTOR.value and state.is_final == False:
        # After rejection, must search again
        return [AgentEnum.SEARCH.value]
    elif state.last_completed_agent == AgentEnum.SEARCH.value:
        # After search, must analyze
        return [AgentEnum.ITEM_ANALYST.value]
    elif state.last_completed_agent == AgentEnum.ITEM_ANALYST.value:
        # After analysis, must reflect
        return [AgentEnum.REFLECTOR.value]
    elif state.last_completed_agent == AgentEnum.REFLECTOR.value:
        # Finally accepted, can finish
        return [AgentEnum.FINISH.value]
    else:
        # Fallback to search if state is unclear
        return [AgentEnum.SEARCH.value]


def _allowed_actions(state: AgentState) -> List[str]:
    """
    Determine which actions are allowed based on what has been completed.
    Always allow INTERPRETER and USER_ANALYST; progressively unlock the rest.
    """
    completed = {agent.lower() for agent in (state.completed_agents or [])}
    # Start with the two that are always allowed
    if state.feedback != None and not state.is_final:
        return _get_post_rejection_allowed_actions(state, completed)

    allowed = []
    if AgentEnum.INTERPRETER.value.lower() not in completed or state.run_count > 0:
        allowed.append(AgentEnum.INTERPRETER.value)
    if AgentEnum.USER_ANALYST.value.lower() not in completed and AgentEnum.INTERPRETER.value.lower() in completed or state.run_count > 0:
        allowed.append(AgentEnum.USER_ANALYST.value)
    # If user analysis is done, allow SEARCH
    if AgentEnum.USER_ANALYST.value.lower() in completed and state.last_completed_agent != AgentEnum.SEARCH.value:
        allowed.append(AgentEnum.SEARCH.value)

    # If search is done, allow ITEM_ANALYST
    if AgentEnum.SEARCH.value.lower() in completed:
        allowed.append(AgentEnum.ITEM_ANALYST.value)

    # If item analysis is done, allow REFLECTOR
    if AgentEnum.ITEM_ANALYST.value.lower() in completed:
        allowed.append(AgentEnum.REFLECTOR.value)

    # If reflector is done, allow FINISH
    if AgentEnum.REFLECTOR.value.lower() in completed and state.is_final:
        allowed = [AgentEnum.FINISH.value]

    return allowed

def _load_agent(ls_agent_names):
    descriptions = get_agent_description()
    return [[name, descriptions[name]] for name in ls_agent_names]

def next_agent(last, allowed, state):
    print(type(last), last, type(allowed[0]), allowed)
    sequence = [AgentEnum.INTERPRETER.value,
                 AgentEnum.USER_ANALYST.value,
                   AgentEnum.SEARCH.value,
                     AgentEnum.ITEM_ANALYST.value,
                       AgentEnum.REFLECTOR.value]
    if AgentEnum.REFLECTOR.value == last and state.is_final:
        return AgentEnum.FINISH.value
    elif AgentEnum.REFLECTOR.value == last and not state.is_final:
        return AgentEnum.SEARCH.value
    elif len(allowed) ==1 and last != AgentEnum.INTERPRETER.value:
        print(f"chosen{allowed[0]}")
        return str(allowed[0])
    try:
        current = sequence.index(last)
    except:
        for a in sequence:
            last = a if a.lower() == last.lower() else last
        current = sequence.index(last)
    next_agent = sequence[current+1]
    if next_agent in allowed:
        print(type(next_agent))
        return str(next_agent)


    
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

    rf = getattr(state, "reflection_feedback", {}) or {}
    last_query = getattr(state, "search_query", "") or getattr(state, "query", "") or ""
    last_completed = getattr(state, "last_completed_agent", None) or ""

    prompt = prompt.replace("$last_query$", last_query)
    prompt = prompt.replace("$last_completed$", last_completed)
    prompt = prompt.replace("$recommended$", next_agent(last_completed, sections["allowed"], state))
    """
    if completed_agents:
        prompt += f"Already called Agents: {completed_agents}"
    if available_data:
        prompt += f"\n\n**AVAILABLE DATA:**\n{available_data}\n"
    if hasattr(state, 'reflector_accepted'):
        prompt += f"\n\n**Reflector Acceptance Status:**\n{state.is_final}\n"
    """
    
    # Add explicit instruction about the cycle
    prompt = prompt.replace("$cycle$", """
REMEMBER THE CYCLE:
1. SEARCH (based on reflector feedback if rejected)
2. ITEM_ANALYST (analyze new results)  
3. REFLECTOR (evaluate if results are now acceptable)
4. If accepted → FINISH, if rejected → back to step 1 with new feedback
""")

    return prompt


def build_prompt_action(state:AgentState, thought: str) -> str:
    prompt = get_prompt(PromptEnum.ACTION, biased=state.biase)
    action_names = _allowed_actions(state)
    actions = _load_agent(action_names)
    prompt = prompt.replace("$THOUGHT$",thought)
    prompt = prompt.replace("$ALLOWED$", str(actions))
    return prompt


