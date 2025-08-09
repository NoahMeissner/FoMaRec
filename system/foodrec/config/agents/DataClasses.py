# Noah Meissner 4.08.2025

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class TaskInterpretRequest:
    task_id: str
    conversation_history: List[Dict[str, Any]]

@dataclass
class TaskInterpretResponse:
    task_description: str
    task_id: str

@dataclass
class AnalysisRequest:
    task_id: str
    entity_type: str
    entity_id: str
    tools_requested: List[str]

@dataclass
class AnalysisResponse:
    task_id: str
    entity_type: str
    analysis_data: Dict[str, Any]

@dataclass
class SearchRequest:
    task_id: str
    query: str
    search_tool: str

@dataclass
class SearchResponse:
    task_id: str
    summary: str

@dataclass
class ReflectionRequest:
    task_id: str
    candidate_answer: str
    run_count: int

@dataclass
class ReflectionResponse:
    task_id: str
    is_final: bool
    feedback: str

