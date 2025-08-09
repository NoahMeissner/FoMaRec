# Noah Meissner 04.08.2025


from foodrec.agents.agent import Agent
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod
from foodrec.agents.agent_state import AgentState
from langgraph.graph import StateGraph, END
import json
from foodrec.agents.interpreter import TaskInterpreterAgent
from foodrec.agents.user_analyst import UserItemAnalystAgent
from foodrec.agents.search import SearcherAgent
from foodrec.agents.reflect import ReflectorAgent
from foodrec.agents.manager import ManagerAgent


def create_agent_node(agent: Agent):
    """Factory function um Agent-Node für LangGraph zu erstellen"""
    def agent_node(state: AgentState) -> AgentState:
        return agent.execute(state)
    return agent_node

def route_next_agent(state: AgentState) -> str:
    """Routing-Funktion basierend auf Manager-Entscheidung"""
    next_agent = state.get("next_agent")
    
    if state.get("is_final", False) or next_agent is None:
        return "end"
    
    return next_agent

# Graph Creation
def create_multi_agent_graph():
    """Erstellt und konfiguriert den manager-gesteuerten Multi-Agent Workflow Graph"""
    
    # Initialisiere Agents
    manager = ManagerAgent()
    task_interpreter = TaskInterpreterAgent()
    user_item_analyst = UserItemAnalystAgent()
    searcher = SearcherAgent()
    reflector = ReflectorAgent()
    
    workflow = StateGraph(AgentState)
    
    # Füge Nodes hinzu
    workflow.add_node("manager", create_agent_node(manager))
    workflow.add_node("task_interpreter", create_agent_node(task_interpreter))
    workflow.add_node("user_item_analyst", create_agent_node(user_item_analyst))
    workflow.add_node("searcher", create_agent_node(searcher))
    workflow.add_node("reflector", create_agent_node(reflector))
    
    # Setze Entry Point auf Manager
    workflow.set_entry_point("manager")
    
    # Alle Agents kehren zum Manager zurück
    workflow.add_edge("task_interpreter", "manager")
    workflow.add_edge("user_item_analyst", "manager")
    workflow.add_edge("searcher", "manager")
    workflow.add_edge("reflector", "manager")
    
    # Manager entscheidet welcher Agent als nächstes aufgerufen wird
    workflow.add_conditional_edges(
        "manager",
        route_next_agent,
        {
            "task_interpreter": "task_interpreter",
            "user_item_analyst": "user_item_analyst",
            "searcher": "searcher",
            "reflector": "reflector",
            "end": END
        }
    )
    
    return workflow.compile()

# Beispiel-Nutzung
def run_example():
    """Demonstriert die Nutzung des objekt-orientierten Multi-Agent Systems"""
    
    # Erstelle Graph
    app = create_multi_agent_graph()
    
    # Initial State
    initial_state = {
        "task_id": "task_001",
        "conversation_history": [
            {"role": "user", "content": "I need latest movie recommendations"},
            {"role": "assistant", "content": "What genres do you prefer?"},
            {"role": "user", "content": "I like comedy and drama, something recent"}
        ],
        "messages": ["User: I need latest movie recommendations"],
        "run_count": 0,
        "is_final": False,
        "completed_agents": set(),
        "required_data": None
    }
    
    print("Starting object-oriented multi-agent workflow...")
    print("=" * 60)
    
    # Führe Workflow aus
    final_state = app.invoke(initial_state)
    
    print("=" * 60)
    print("Final Results:")
    print(f"Task ID: {final_state['task_id']}")
    print(f"Task Description: {final_state.get('task_description')}")
    print(f"Final Answer: {final_state.get('candidate_answer')}")
    print(f"Total Runs: {final_state.get('run_count')}")
    print(f"Completed Agents: {final_state.get('completed_agents')}")
    print(f"Final Feedback: {final_state.get('feedback')}")
    
    print("\nWorkflow Messages:")
    for msg in final_state.get("messages", []):
        print(f"  {msg}")
    
    return final_state

def demonstrate_agent_requirements():
    """Demonstriert die Requirements und Capabilities der Agents"""
    
    agents = [
        TaskInterpreterAgent(),
        UserItemAnalystAgent(),
        SearcherAgent(),
        ReflectorAgent(),
        ManagerAgent()
    ]
    
    print("Agent Requirements and Capabilities:")
    print("=" * 50)
    
    for agent in agents:
        print(f"\n🤖 {agent.name}")
        print(f"   Requirements: {agent.requirements}")
        print(f"   Provides: {agent.provides}")
    
    print("\n" + "=" * 50)

def start():
    print("=== AGENT REQUIREMENTS OVERVIEW ===")
    demonstrate_agent_requirements()
    
    print("\n\n=== WORKFLOW EXECUTION ===")
    run_example()