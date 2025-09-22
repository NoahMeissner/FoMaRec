# Noah Meissner 04.08.2025

from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.agents.agent_names import AgentEnum

@dataclass
class AgentState(Dict):
    """State shared between all agents in the graph"""
    user_id: str
    task_id: int
    task_description: str = None
    analysis_data: str= None
    item_analysis: Optional[Dict[str, Any]] = None
    search_results: Optional[str] = None
    messages: Optional[str] = None # raus
    candidate_answer: Optional[str] = None 
    run_count: int = 0
    revision_round: int = 0 # eher raus
    is_final: bool = False # drin
    feedback: Optional[str] = None  # brauchen wir
    next_agent: Optional[str] = None # brauchen wir
    completed_agents: Set[str] = None # brauchen wir
    model: ModelEnum = ModelEnum.LLAMA
    post_rejection_cycle_state: AgentEnum = None
    required_data: Dict[str, bool] = None # raus
    reflection_feedback: Dict = None # drin
    post_rejection_search_completed: bool = False
    biase: bool = False # drin
    last_completed_agent: str = "" # raus
    reflector_query: str = "" # raus
    query: str = "" # drin
    search_query: str = ""
    reflector_accepted: Optional[bool] = False # raus

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "user_id": self.user_id,
            "run_count": self.run_count,
            "post_rejection_cycle_state": self.post_rejection_cycle_state,
            "post_rejection_search_completed": self.post_rejection_search_completed,
            "reflector_accepted":self.reflector_accepted,
            "messages": self.messages,
            "last_completed_agent": self.last_completed_agent,
            "model": self.model.name,  # Store as string
            "biase": self.biase,
            "query": self.query,
            "reflector_query": self.reflector_query,
            "reflection_feedback": self.reflection_feedback,
            "is_final": self.is_final,
            "completed_agents": list({agent.lower() for agent in (self.completed_agents or [])}),
            "required_data": self.required_data,
            "task_description": self.task_description,
            "analysis_data": self.analysis_data,
            "item_analysis": self.item_analysis,
            "search_results": self.search_results,
            "search_query": self.search_query,
            "candidate_answer": self.candidate_answer,
            "feedback": self.feedback,
            "revision_round": self.revision_round,
            "next_agent": self.next_agent,
        }

    @staticmethod
    def from_dict(data: dict) -> 'AgentState':
        return AgentState(
            reflector_accepted=data.get("reflector_accepted",False),
            messages=data.get("messages",""),
            task_id=data.get("task_id", ""),
            post_rejection_cycle_state = data.get("post_rejection_cycle_state",None),
            user_id=data.get("user_id", ""),
            post_rejection_search_completed=data.get("post_rejection_search_completed",False),
            search_query=data.get("search_query",""),
            last_completed_agent = data.get("last_completed_agent",""),
            reflection_feedback=("reflection_feedback",{}),
            reflector_query=("reflector_query",""),
            run_count=data.get("run_count", 0),
            model=ModelEnum[data.get("model", "Gemini")],  # Convert from string
            biase=data.get("biase", False),
            query=data.get("query", ""),
            revision_round = data.get("revision_round", 0),
            is_final=data.get("is_final", False),
            completed_agents={agent.lower() for agent in data.get("completed_agents", [])},
            required_data=data.get("required_data", {}),
            task_description=data.get("task_description"),
            analysis_data=data.get("analysis_data"),
            item_analysis=data.get("item_analysis"),
            search_results=data.get("search_results"),
            candidate_answer=data.get("candidate_answer"),
            feedback=data.get("feedback"),
            next_agent=data.get("next_agent"))