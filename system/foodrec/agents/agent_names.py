# Noah Meissner 11.08.2025

"""
    This class is responsible for the name handling of the agents
"""
from enum import Enum, unique

class AgentEnum(Enum):
    REFLECTOR = "REFLECTOR"
    SEARCH = "SEARCH"
    MANAGER = "MANAGER"
    USER_ANALYST = "USER_ANALYST"
    ITEM_ANALYST = "ITEM_ANALYST"
    INTERPRETER = "INTERPRETER"
    FINISH = "FINISH"

@unique
class AgentReporter(Enum):
    REFLECTOR_Prompt = "REFLECTOR_Prompt"
    REFLECTOR = "REFLECTOR"
    SEARCH_Prompt = "SEARCH_Prompt"
    SEARCH_Output = "SEARCH_Output"
    Search_Results = "Search_Results"
    MANAGER_Action = "MANAGER_Action"
    MANAGER_Action_Prompt = "MANAGER_Action_Prompt"
    MANAGER_Thought = "MANAGER_Thought"
    MANAGER_Thought_Prompt = "MANAGER_Thought_Prompt"
    MANAGER_Observation = "MANAGER_Observation"
    USER_ANALYST = "USER_ANALYST"
    ITEM_ANALYST_Prompt = "ITEM_ANALYST_Prompt"
    ITEM_ANALYST = "ITEM_ANALYST"
    INTERPRETER_Prompt = "INTERPRETER_Prompt"
    INTERPRETER_Output = "INTERPRETER_Output"
    FINISH = "FINISH"
