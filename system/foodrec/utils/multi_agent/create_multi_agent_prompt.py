# Noah Meissner 09.08.2025

"""
This class is responsible for creating the Multi Agent Prompt
"""

from foodrec.agents.agent_state import AgentState
import ast
from typing import List, Optional, Set

def _build_completion_status(state: AgentState) -> str:
    """Build a clear status of what's already been completed."""
    status_map = {
        "task_interpreter": lambda: f"✓ Task interpreted: {state.task_description}",
        "user_item_analyst": lambda: "✓ User analysis completed - all user preferences are known",
        "searcher": lambda: f"✓ Search completed - {len(state.search_results)} results available" if isinstance(state.search_results, list) else "✓ Search completed",
        "item_analyst": lambda: "✓ Item analysis completed"
    }
    return "\n".join(func() for agent, func in status_map.items() if agent in state.completed_agents and getattr(state, agent.replace("_", ""), None))

def _build_available_data_summary(state: AgentState) -> str:
    """Build a summary of currently available data"""
    data_summary = []
    
    if state.task_description:
        data_summary.append(f"• Task: {state.task_description}")
    
    if state.analysis_data:
        user_info = state.analysis_data
        if isinstance(user_info, str) and user_info.startswith("{'"):
            try:
                user_dict = ast.literal_eval(user_info)
                diet = user_dict.get('diet', 'unknown')
                allergies = user_dict.get('allergies', [])
                time_limit = user_dict.get('max_time_per_recipe', 'unknown')
                favorites = user_dict.get('favorite_ingredients', [])
                cultural = user_dict.get('cultural_preferences', [])
                
                data_summary.append(f"• User Profile: {diet} diet, allergies to {allergies}, max {time_limit}min recipes")
                data_summary.append(f"• User Preferences: likes {favorites}, prefers {cultural} cuisines")
            except:
                data_summary.append(f"• User Analysis: Available (raw data)")
        else:
            data_summary.append(f"• User Analysis: {user_info}")
    
    if state.search_results:
        if isinstance(state.search_results, list):
            data_summary.append(f"• Search Results: {len(state.search_results)} items found")
        else:
            data_summary.append(f"• Search Results: Available")
    
    if state.item_analysis:
        data_summary.append(f"• Item Analysis: Available")
    
    return "\n".join(data_summary) if data_summary else ""

def _build_reflections(state: AgentState) -> str:
    """Build reflections section if feedback is available"""
    if state.feedback:
        return f"""Previous attempt feedback: {state.feedback}
Please improve your approach based on this feedback."""
    return None

def _build_task_prompt(state: AgentState) -> str:
    """Build the task prompt section"""
    if state.task_description:
        if state.task_description != "":
            return f"Task: {state.task_description}"
    return None
