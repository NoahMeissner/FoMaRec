# Noah Meißner 16.09.2025
"""
This class is responsible for the calculation of the reward
"""

import json
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.agents.agent_names import AgentEnum
from foodrec.evaluation.reward_evaluation import final_episode_reward
from analysis_helper.load_dataset import get_file_path

def check_reward(persona_id: int, query: str, model: ModelEnum, path = None):
    """Check the reward of the conversation"""
    filepath = get_file_path(Path=path, query=query, persona_id=persona_id, model=model)
    if filepath is None:
        return None, None
    roles = [AgentEnum.USER_ANALYST.value,
             AgentEnum.SEARCH.value,
             AgentEnum.REFLECTOR.value,
             AgentEnum.FINISH.value,
             AgentEnum.ITEM_ANALYST.value,
             AgentEnum.INTERPRETER.value
            ]
    try:
        with open(filepath, "r", encoding="utf-8") as json_list:
            ls_route = [AgentEnum.START.value]
            for line in json_list:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                try:
                    if obj.get("role") in roles:
                        ls_route.append(obj.get("role"))
                    if obj.get("role") == "INTERPRETER_Output":
                        ls_route.append(AgentEnum.INTERPRETER.value)
                    if obj.get("role") == "Search_Results":
                        ls_route.append(AgentEnum.SEARCH.value)
                    if obj.get("role") == "assistant":
                        ls_route.append(AgentEnum.FINISH.value)
                except Exception as exception: #pylint: disable=broad-except
                    print(f"Error processing line: {line}, Error: {exception}")
                    continue
            return ls_route
    except Exception as exception: #pylint: disable=broad-except
        print(f"Error reading file {filepath}, {exception}")
        return None

    return None

def reward_average_calculation(reward_system):
    """Calculate the average reward of the conversation"""
    gamma = 1
    normalize = True

    scores = []
    for episode in reward_system[1:]:
        score = final_episode_reward(episode, gamma=gamma, normalize=normalize)
        scores.append(score)

    avg_score = sum(scores) / len(scores) if scores else 0.0
    return f"Score: {avg_score:.4f} bei gamma={gamma}, normalize={normalize}"

def get_reward_set(dataframe, model:ModelEnum, path):
    """Get the reward set for the dataframe"""
    ls_res = []
    for index, row in dataframe.iterrows():
        try:
            persona_id = row["id"]
            query = row["query"]
            ls_res.append(check_reward(persona_id=persona_id, query=query, model=model, path=path))
        except Exception as exception:#pylint: disable=broad-except
            print(query)
            print(exception)
    return ls_res
