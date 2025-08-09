# Noah Meissner 07.08.2025

from foodrec.agents.interpreter import TaskInterpreterAgent
from foodrec.agents.agent_state import AgentState

from foodrec.config.structure.dataset_enum import ModelEnum


def test_task_interpreter_agent():

    # Example input state
    example_state = AgentState({
        "task_id": "task_002",
        "user_id": 456,
        "query": "Ich möchte ein schnelles, vegetarisches Abendessen finden.",
        "model": ModelEnum.Gemini,  # Adjust to the model you're using
        "biase": False,
        "required_data": {},
        "completed_agents": set()
    })

    # Instantiate agent
    agent = TaskInterpreterAgent()

    # Execute logic
    updated_state = agent._execute_logic(example_state)

    # Output result
    print("Interpretierte Taskbeschreibung:")
    print(updated_state.get("task_description"))
