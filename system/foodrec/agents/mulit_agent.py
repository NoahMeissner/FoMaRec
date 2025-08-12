# Noah Meissner 07.08.2025

"""
    This script implements the system
"""

from foodrec.agents.agent import Agent
from foodrec.agents.agent_state import AgentState
from langgraph.graph import StateGraph, END
from foodrec.agents.interpreter import TaskInterpreterAgent
from foodrec.agents.user_analyst import UserItemAnalystAgent
from foodrec.agents.search import SearcherAgent
from foodrec.agents.reflect import ReflectorAgent
from foodrec.agents.item_analyst import ItemAnalystAgent
from foodrec.agents.manager import ManagerAgent
from foodrec.config.structure.dataset_enum import ModelEnum
from dataclasses import asdict
from foodrec.agents.agent_names import AgentEnum

def create_agent_node(agent: Agent):
    """Standard agent node without completion tracking"""
    def agent_node(state: dict) -> dict:
        agent_state = AgentState.from_dict(state)
        updated_state = agent.execute(agent_state)
        return updated_state.to_dict()
    return agent_node

def create_agent_node_with_completion_tracking(agent: Agent, agent_name: str):
    """Create agent node that tracks completion"""
    def agent_node(state: dict) -> dict:
        agent_state = AgentState.from_dict(state)
        
        print(f"\n=== {agent_name.upper()} EXECUTING ===")
        print(f"Before execution - completed_agents: {agent_state.completed_agents}")
        
        # Execute the agent
        updated_state = agent.execute(agent_state)
        agent_name_lower = agent_name.lower()

        print(f"After execution - task_description: {updated_state.task_description}")
        print(f"After execution - analysis_data: {bool(updated_state.analysis_data)}")
        print(f"After execution - search_results: {bool(updated_state.search_results)}")
        print(f"After execution - item_analysis: {bool(updated_state.item_analysis)}")
        completed_agents = {agent.lower() for agent in (updated_state.completed_agents or [])}
        # Mark this agent as completed if it produced results
        if agent_name == AgentEnum.INTERPRETER.value and updated_state.task_description:
            completed_agents.add(agent_name_lower)
            print(f"✓ Marked {agent_name} as completed")
            updated_state.last_completed_agent = AgentEnum.INTERPRETER.value
        elif agent_name == AgentEnum.USER_ANALYST.value and updated_state.analysis_data:
            completed_agents.add(agent_name_lower)
            updated_state.last_completed_agent = AgentEnum.USER_ANALYST.value
            print(f"✓ Marked {agent_name} as completed")
        elif agent_name == AgentEnum.SEARCH.value and updated_state.search_results:
            completed_agents.add(agent_name_lower)
            updated_state.last_completed_agent = AgentEnum.SEARCH.value
            print(f"✓ Marked {agent_name} as completed")
        elif agent_name == AgentEnum.ITEM_ANALYST.value and updated_state.item_analysis:
            completed_agents.add(agent_name_lower)
            updated_state.last_completed_agent = AgentEnum.ITEM_ANALYST.value
            print(f"✓ Marked {agent_name} as completed")
        elif agent_name == AgentEnum.REFLECTOR.value and updated_state.feedback:
            completed_agents.add(agent_name_lower)
            updated_state.last_completed_agent = AgentEnum.REFLECTOR.value
            print(f"✓ Marked {agent_name} as completed")
        else:
            print(f"⚠️  {agent_name} did not produce expected results - not marked as completed")
        
        print(f"Final completed_agents: {updated_state.completed_agents}")
        print(f"=== {agent_name.upper()} COMPLETED ===\n")
        updated_state.completed_agents = completed_agents
        return updated_state.to_dict()
    return agent_node

def route_next_agent(state: dict) -> str:
    """Routing function based on Manager decision"""
    next_agent = state.get("next_agent")
    is_final = state.get("is_final", False)
    
    print(f"\n=== ROUTING ===")
    print(f"next_agent: {next_agent}")
    print(f"is_final: {is_final}")
    print(f"===============\n")
    
    if is_final or next_agent is None:
        return "end"
    
    return next_agent

def create_multi_agent_graph():
    """Creates and configures the manager-driven Multi-Agent Workflow Graph"""
    
    # Initialize Agents
    manager = ManagerAgent()
    task_interpreter = TaskInterpreterAgent()
    user_analyst = UserItemAnalystAgent()
    searcher = SearcherAgent()
    item_analyst = ItemAnalystAgent()
    reflector = ReflectorAgent()
    
    workflow = StateGraph(AgentState)
    
    # Add Nodes with Completion Tracking
    workflow.add_node(AgentEnum.MANAGER.value, create_agent_node(manager))  # Manager doesn't need completion tracking
    workflow.add_node(AgentEnum.INTERPRETER.value, create_agent_node_with_completion_tracking(task_interpreter, AgentEnum.INTERPRETER.value))
    workflow.add_node(AgentEnum.USER_ANALYST.value, create_agent_node_with_completion_tracking(user_analyst, AgentEnum.USER_ANALYST.value))
    workflow.add_node(AgentEnum.SEARCH.value, create_agent_node_with_completion_tracking(searcher, AgentEnum.SEARCH.value))
    workflow.add_node(AgentEnum.REFLECTOR.value, create_agent_node_with_completion_tracking(reflector, AgentEnum.REFLECTOR.value))
    workflow.add_node(AgentEnum.ITEM_ANALYST.value, create_agent_node_with_completion_tracking(item_analyst, AgentEnum.ITEM_ANALYST.value))

    # Set Entry Point to Manager
    workflow.set_entry_point(AgentEnum.MANAGER.value)
    
    # All Agents return to Manager
    workflow.add_edge(AgentEnum.INTERPRETER.value, AgentEnum.MANAGER.value)
    workflow.add_edge(AgentEnum.USER_ANALYST.value, AgentEnum.MANAGER.value)
    workflow.add_edge(AgentEnum.SEARCH.value, AgentEnum.MANAGER.value)
    workflow.add_edge(AgentEnum.REFLECTOR.value, AgentEnum.MANAGER.value)
    workflow.add_edge(AgentEnum.ITEM_ANALYST.value, AgentEnum.MANAGER.value)
    
    # Manager decides which Agent to call next
    workflow.add_conditional_edges(
        AgentEnum.MANAGER.value,
        route_next_agent,
        {
            AgentEnum.INTERPRETER.value: AgentEnum.INTERPRETER.value,
            AgentEnum.USER_ANALYST.value: AgentEnum.USER_ANALYST.value,
            AgentEnum.SEARCH.value: AgentEnum.SEARCH.value,
            AgentEnum.REFLECTOR.value: AgentEnum.REFLECTOR.value,
            AgentEnum.ITEM_ANALYST.value: AgentEnum.ITEM_ANALYST.value,
            "end": END
        }
    )
    
    return workflow.compile()

def create_initial_state(user_id, biase: bool = False, model: ModelEnum = ModelEnum.LLAMA, query: str = "") -> AgentState:
    return AgentState(
        task_id="task_001",
        user_id=user_id,
        run_count=0,
        model=model,
        biase=biase,
        query=query,
        is_final=False,
        completed_agents=set(),  
        required_data={}
    )

class MultiAgent:

    def __init__(self, user_id, biase: bool = False, model: ModelEnum = ModelEnum.Gemini):
        self.app = create_multi_agent_graph()
        self.user_id = user_id
        self.biase = biase
        self.model = model

    def run(self, query: str = ""):
        initial_state = create_initial_state(user_id=self.user_id, biase=self.biase, model=self.model, query=query)
        
        print(f"Starting with initial completed_agents: {initial_state.completed_agents}")
        
        final_state = self.app.invoke(initial_state.to_dict())

        print("=" * 60)
        print("Final Results:")
        print(f"Task ID: {final_state['task_id']}")
        print(f"Task Description: {final_state.get('task_description')}")
        print(f"Final Answer: {final_state.get('candidate_answer')}")
        print(f"Total Runs: {final_state.get('run_count')}")
        print(f"Completed Agents: {final_state.get('completed_agents')}")
        print(f"Final Feedback: {final_state.get('feedback')}")