# Noah Meissner 11.08.2025

"""
    This class is responsible for the name handling of the agents
"""
from enum import Enum

class AgentEnum(Enum):
    REFLECTOR = "REFLECTOR"
    SEARCH = "SEARCH"
    MANAGER = "MANAGER"
    USER_ANALYST = "USER_ANALYST"
    ITEM_ANALYST = "ITEM_ANALYST"
    INTERPRETER = "INTERPRETER"
    FINISH = "FINISH"