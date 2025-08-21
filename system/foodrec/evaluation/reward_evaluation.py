# Noah Meissner 19.08.2025

from foodrec.agents.agent_names import AgentEnum

def create_next_dict():
    return {
        AgentEnum.START.value: [AgentEnum.INTERPRETER.value, AgentEnum.USER_ANALYST.value],
        AgentEnum.INTERPRETER.value: [AgentEnum.USER_ANALYST.value, AgentEnum.SEARCH.value],
        AgentEnum.USER_ANALYST.value: [AgentEnum.INTERPRETER.value, AgentEnum.SEARCH.value],
        AgentEnum.ITEM_ANALYST.value: [AgentEnum.REFLECTOR.value],
        AgentEnum.SEARCH.value: [AgentEnum.ITEM_ANALYST.value],
        AgentEnum.REFLECTOR.value: [AgentEnum.FINISH.value, AgentEnum.SEARCH.value],
        AgentEnum.FINISH.value: []
    }

def step_reward(action, next_actions):
    return 1 if action in next_actions else -1

def next_actions(previous):
    current = AgentEnum.START.value
    if len(previous) != 0:
        current = previous[-1]
    next_dict = create_next_dict()
    next_agents = next_dict.get(current, [])
    if current == AgentEnum.USER_ANALYST.value and AgentEnum.INTERPRETER.value in next_agents:
        next_agents.remove(AgentEnum.INTERPRETER.value)
    elif current == AgentEnum.INTERPRETER.value and AgentEnum.USER_ANALYST.value in next_agents:
        next_agents.remove(AgentEnum.USER_ANALYST.value)
    return next_agents


def final_episode_reward(actions, gamma=0.9, normalize=False):
    G = 0.0
    w = 1.0
    for index, a in enumerate(actions): 
        previous = actions[:index]
        before_actions_ground_truth = next_actions(previous) 
        r = step_reward(a, before_actions_ground_truth)     # r_{t+1}
        G += w * r             # add gamma^t * r_{t+1}
        w *= gamma
    if normalize:
        T = len(actions)
        weight_sum = (1 - gamma**T) / (1 - gamma) if gamma != 1 else T
        return G / weight_sum
    return G
