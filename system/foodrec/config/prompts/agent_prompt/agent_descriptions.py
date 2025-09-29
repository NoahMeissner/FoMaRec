# Noah Meissner 11.08.2025

from foodrec.agents.agent_names import AgentEnum

_interpreter = """
Purpose: Understand or clarify the user's original query.
"""

_analyse = """
Purpose: Retrieve or analyze the preferences of the user with ID $user_id$.
"""

_item_analyst = """
Purpose: Order Search results based on user preferences and query.
"""

_search = """
Purpose: Find items (e.g., recipes, products) that meet specific requirements.
"""

_reflector = """
Purpose: Check if your recommendations align with the user’s preferences and query.
"""

_finish = """
Purpose: Return the final answer to the user.
"""

def get_agent_description():
    return {
        AgentEnum.INTERPRETER.value : _interpreter,
        AgentEnum.ITEM_ANALYST.value : _item_analyst,
        AgentEnum.SEARCH.value : _search,
        AgentEnum.REFLECTOR.value : _reflector,
        AgentEnum.USER_ANALYST.value : _analyse,
        AgentEnum.FINISH.value : _finish
    }


