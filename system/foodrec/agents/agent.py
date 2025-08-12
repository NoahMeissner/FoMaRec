# Noah Meissner 04.08.2025

from typing import Set
from abc import ABC, abstractmethod
from foodrec.agents.agent_state import AgentState


class Agent(ABC):
    """Abstrakte Basis-Klasse für alle Agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.requirements = self._define_requirements()
        self.provides = self._define_provides()
    
    @abstractmethod
    def _define_requirements(self) -> Set[str]:
        """Definiert welche Daten dieser Agent benötigt"""
        pass
    
    @abstractmethod
    def _define_provides(self) -> Set[str]:
        """Definiert welche Daten dieser Agent bereitstellt"""
        pass
    
    @abstractmethod
    def _execute_logic(self, state: AgentState) -> AgentState:
        """Führt die spezifische Logik des Agents aus"""
        pass
    
    def can_execute(self, state: AgentState) -> bool:
        state_dict = state.to_dict()
        """Prüft ob alle Requirements erfüllt sind"""
        for requirement in self.requirements:
            if requirement == "task_description":
                if not state_dict.get("task_description"):
                    return False
            elif requirement == "analysis_data":
                if not state_dict.get("analysis_data"):
                    return False
            elif requirement == "search_results":
                if not state_dict.get("search_results"):
                    return False
            elif requirement == "candidate_answer":
                if not state_dict.get("candidate_answer"):
                    return False
        return True
    
    def execute(self, state: AgentState) -> AgentState:
        """Führt den Agent aus und markiert ihn als completed"""
        print(f"{self.name} processing task {state.task_id}")
        
        # Prüfe Requirements
        if not self.can_execute(state):
            print(60*'===')
            print(state)
            print(60*'===')
            missing = [req for req in self.requirements if not self._has_requirement(state, req)]
            print(f"⚠️  {self.name} cannot execute. Missing: {missing}")
            return state
        
        # Führe Agent-spezifische Logik aus
        state = self._execute_logic(state)        
        return state
    
    def _has_requirement(self, state: AgentState, requirement: str) -> bool:
        """Hilfsmethode um zu prüfen ob ein Requirement erfüllt ist"""
        if requirement == "conversation_history":
            return bool(state.get("conversation_history"))
        elif requirement == "task_description":
            return bool(state.get("task_description"))
        elif requirement == "analysis_data":
            return bool(state.get("analysis_data"))
        elif requirement == "search_results":
            return bool(state.get("search_results"))
        elif requirement == "candidate_answer":
            return bool(state.get("candidate_answer"))
        return False