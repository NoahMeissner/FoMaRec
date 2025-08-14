# Noah Meissner 14.08.2025

'''
    This method is responsible for ordering the recipe list and to give it back to the user
'''

from foodrec.agents.agent_state import AgentState

def get_list(state: AgentState):
    search_results = state['search_results']
    analysis = state['item_analysis']
    ordered_recipes = analysis['ordered_recipes']
    explanations = analysis['explanations']
    ls_res = []
    for index, id in enumerate(ordered_recipes):
        res_json_obj = {}
        explanation = explanations[index]
        for json_obj in search_results:
            if json_obj['id'] == id:
                res_json_obj = json_obj
                break
        res_json_obj['explanation'] = explanation
        ls_res.append(res_json_obj)
    return ls_res[:3]
