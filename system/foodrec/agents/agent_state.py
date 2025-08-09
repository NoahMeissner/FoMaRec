# Noah Meissner 04.08.2025

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod
from langgraph.graph import StateGraph, END
from foodrec.config.structure.dataset_enum import ModelEnum
import json
from dataclasses import dataclass, field

@dataclass
class AgentState(Dict):
    """State shared between all agents in the graph"""
    task_id: str
    user_id: int
    task_description: str = None
    analysis_data: str= None
    item_analysis: Optional[Dict[str, Any]] = None
    search_results: Optional[str] = None
    messages: Optional[str] = None
    candidate_answer: Optional[str] = None
    run_count: int = 0
    is_final: bool = False
    feedback: Optional[str] = None
    next_agent: Optional[str] = None
    completed_agents: Set[str] = None
    model: ModelEnum = ModelEnum.LLAMA
    required_data: Dict[str, bool] = None
    reflection_feedback: Dict = None
    biase: bool = False
    reflector_query: str = ""
    query: str = ""
    reflector_accepted: Optional[bool] = False

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "user_id": self.user_id,
            "run_count": self.run_count,
            "reflector_accepted":self.reflector_accepted,
            "messages": self.messages,
            "model": self.model.name,  # Store as string
            "biase": self.biase,
            "query": self.query,
            "reflector_query": self.reflector_query,
            "reflection_feedback": self.reflection_feedback,
            "is_final": self.is_final,
            "completed_agents": list(self.completed_agents),
            "required_data": self.required_data,
            "task_description": self.task_description,
            "analysis_data": self.analysis_data,
            "item_analysis": self.item_analysis,
            "search_results": self.search_results,
            "candidate_answer": self.candidate_answer,
            "feedback": self.feedback,
            "next_agent": self.next_agent,
        }

    @staticmethod
    def from_dict(data: dict) -> 'AgentState':
        return AgentState(
            reflector_accepted=data.get("reflector_accepted",False),
            messages=data.get("messages",""),
            task_id=data.get("task_id", ""),
            user_id=data.get("user_id", ""),
            reflection_feedback=("reflection_feedback",{}),
            reflector_query=("reflector_query",""),
            run_count=data.get("run_count", 0),
            model=ModelEnum[data.get("model", "Gemini")],  # Convert from string
            biase=data.get("biase", False),
            query=data.get("query", ""),
            is_final=data.get("is_final", False),
            completed_agents=set(data.get("completed_agents", [])),
            required_data=data.get("required_data", {}),
            task_description=data.get("task_description"),
            analysis_data=data.get("analysis_data"),
            item_analysis=data.get("item_analysis"),
            search_results=data.get("search_results"),
            candidate_answer=data.get("candidate_answer"),
            feedback=data.get("feedback"),
            next_agent=data.get("next_agent"))