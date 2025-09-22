# Noah Meißner 16.09.2025
"""
This class is responsible for the calculation of the reward
"""

import json
from foodrec.config.structure.dataset_enum import ModelEnum
from foodrec.agents.agent_names import AgentEnum
from foodrec.evaluation.reward_evaluation import final_episode_reward

def check_reward(persona_id: int, query: str, model: ModelEnum, path = None):
    query_stempt = query.replace(" ", "_").lower()
    query_id = f"{persona_id}_{query_stempt}_{model.name}"
    filepath = path / f"{query_id}.jsonl"
    if not filepath.exists():
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
                except Exception as e:
                    print(f"Error processing line: {line}, Error: {e}")
                    continue
            return ls_route
    except Exception as exception:
        print(f"Error reading file {filepath}, {exception}")
        return None
    
    return None

def reward_average_calculation(reward_system):
    gamma = 1
    normalize = True

    scores = []
    for episode in reward_system[1:]:
        score = final_episode_reward(episode, gamma=gamma, normalize=normalize)
        scores.append(score)

    avg_score = sum(scores) / len(scores) if scores else 0.0
    return f"Score: {avg_score:.4f} bei gamma={gamma}, normalize={normalize}"

def get_reward_set(df, model:ModelEnum, Path):
    ls_res = []
    for index, row in df.iterrows():
        try:
            persona_id = row["id"]
            query = row["query"]
            ls_res.append(check_reward(persona_id=persona_id, query=query, model=model, Path=Path))
        except Exception as e:
            print(query)
            print(e)
    return ls_res
