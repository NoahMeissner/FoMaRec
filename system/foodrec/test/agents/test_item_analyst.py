from foodrec.agents.item_analyst import ItemAnalystAgent
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.test.agents.test_search_agent import test_searcher_agent
def test_item_analyst_agent():
    state = test_searcher_agent()    

    # Instantiate and execute the agent
    agent = ItemAnalystAgent()
    updated_state = agent._execute_logic(state)

    # Output the results
    print("\nOrdered Recipes:")
    for i, rid in enumerate(updated_state["item_analysis"]["ordered_recipes"], 1):
        print(f"{i}. {rid}")

    print("\nExplanations:")
    for i, expl in enumerate(updated_state["item_analysis"]["explanations"], 1):
        print(f"{i}. {expl}")
