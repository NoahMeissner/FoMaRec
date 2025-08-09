# 13.06.2025 @Noah Meissner

"""
Agent responsible for the analysis of the users
"""

from foodrec.tools.info_database import InformationDataBase
from foodrec.agents.agent import Agent
from typing import  Set
import json
from foodrec.agents.agent_state import AgentState
from foodrec.tools.info_database import InformationDataBase
from foodrec.utils.multi_agent.output import output_user_analyst



class UserItemAnalystAgent(Agent):
    """Agent zur Analyse von User Informationen"""
    
    def __init__(self):
        super().__init__("User Item Analyst")
        self.info_database = InformationDataBase()
    
    def _define_requirements(self) -> Set[str]:
        return {}
    
    def _define_provides(self) -> Set[str]:
        return {"analysis_data"}
    
    def _execute_logic(self, state: AgentState) -> AgentState:
        id = state.user_id
        insights = self.info_database.query(id)
        state.analysis_data = str(json.loads(insights.to_json(orient="records"))[0])

        state.messages = state.get("messages", []) + [
            f"{self.name}: Analysis complete - {insights}"
        ]
        output_user_analyst(state.analysis_data)
        return state

