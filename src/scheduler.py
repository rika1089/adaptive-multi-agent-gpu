# scheduler.py

import random
from metrics import queues

weights = {
    "coord": 0.25,
    "nlp": 0.25,
    "vision": 0.25,
    "reasoning": 0.25
}

def update_weights(new_weights):
    global weights
    weights = new_weights


def pick_agent():
    available = []

    for agent in queues:
        if len(queues[agent]) > 0:
            available.append(agent)

    if not available:
        return None

    probs = [weights[a] for a in available]
    s = sum(probs)
    probs = [p/s for p in probs]

    return random.choices(available, probs)[0]

# import random
# from metrics import queues

# weights = {
#     "coord":0.25,
#     "nlp":0.25,
#     "vision":0.25,
#     "reasoning":0.25
# }

# def update_weights(new_weights):
#     global weights
#     weights = new_weights


# def pick_agent():

#     available = []

#     for agent in queues:
#         if len(queues[agent]) > 0:
#             available.append(agent)

#     if not available:
#         return None

#     probs = [weights[a] for a in available]

#     s = sum(probs)

#     probs = [p/s for p in probs]

#     return random.choices(available, probs)[0]