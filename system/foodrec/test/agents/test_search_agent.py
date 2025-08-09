# Noah Meissner 07.08.2025

from foodrec.agents.search import SearcherAgent  # Falls nicht schon im Kontext
from foodrec.agents.agent_state import AgentState  # Falls nicht schon im Kontext

from foodrec.config.structure.dataset_enum import ModelEnum




def test_searcher_agent():
    # Beispielzustand
    example_state = AgentState({
        "task_id": "task_001",
        "user_id": 123,
        "task_description": "Finde ein italienisches Rezept mit wenig Kalorien",
        "analysis_data": {
            "diet": "vegan",
            "max_calories": 400
        },
        "model": ModelEnum.Gemini,  
        "biase": False,
        "required_data": {},
        "completed_agents": set()
    })

    # Agent instanziieren
    agent = SearcherAgent()

    # Suche ausführen
    updated_state = agent._execute_logic(example_state)
    
    # Ergebnisse ausgeben
    print("Suchergebnisse:")
    for i, result in enumerate(updated_state.get("search_results", []), 1):
        print(f"\nErgebnis {i}:")
        for key, value in result.items():
            print(f"{key}: {value}")
    return updated_state
