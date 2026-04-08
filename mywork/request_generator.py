# import requests
# import time
# import random

# ports = [8001, 8002] #, 8003, 8004]

# while True:
#     p = random.choice(ports)
#     try:
#         requests.post(
#             f"http://localhost:{p}/v1/chat/completions",
#             json={
#                 "model": "dummy",
#                 "messages": [{"role": "user", "content": "Hello"}],
#                 "max_tokens": 50
#             },
#             timeout=2
#         )
#     except:
#         pass
#     time.sleep(0.05)

import random
import time
import requests

from coordinator import route_query
from config import ports
from scheduler import pick_agent
from metrics import add_query, complete_query


# MODEL_MAPPING 
MODEL_MAP = {
    "coord": "/models/phi3",
    "nlp": "/models/qwen",
    "vision": "/models/tinyllama",
    "reasoning": "/models/phi3"
}

# queries = [

# {"type":"text","query":"Explain climate change"},
# {"type":"text","query":"Summarize machine learning"},
# {"type":"vision","query":"Describe a sunset image"},
# {"type":"logic","query":"Solve a puzzle"}

# ]

queries = [

{"type":"text","query":"Explain climate change"},
{"type":"text","query":"Summarize machine learning"},

# {"type":"vision","query":"Describe a sunset over mountains"},
# { "type":"vision","query":"https://upload.wikimedia.org/wikipedia/commons/4/47/Sunset_2007-1.jpg"},
{"type":"vision","query":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQp5YY8SQAOA4ZJdv2EpB3tmcrvz2E5hxaBpQ&s"},


{"type":"logic","query":"If 3 cats catch 3 mice in 3 minutes how long for 100 cats"},
{"type":"logic","query":"What has keys but no locks"}

]

# def is_alive(port):
#     try:
#         requests.get(f"http://localhost:{port}/v1/models", timeout=1)
#         complete_query(agent)
#         return True
#     except:
#         return False

# Added Fallback because if one model fails then also its respective requests will still be processed by some other model
def fallback_agent(agent):
    fallback_map = {
        "reasoning": "coord",
        "vision": "nlp",
        "nlp": "coord",
        "coord": "nlp"
    }
    return fallback_map.get(agent, "coord")


    
while True:

    q = random.choice(queries)

    # ✅ Step 1: route + add to queue
    route_query(q)

    # ✅ Step 2: scheduler picks agent
    agent = pick_agent()

    if agent is None:
        time.sleep(1)
        continue

    # fallback
    if agent not in ["coord", "nlp"]:
        print(f"{agent} not available → fallback")
        agent = fallback_agent(agent)

    port = ports[agent]

    try:
        requests.get(f"http://localhost:{port}/v1/models", timeout=1)
    except:
        print(f"{agent} is DOWN → skipping")
        time.sleep(3)
        continue

    try:
        response = requests.post(
            f"http://localhost:{port}/v1/chat/completions",
            json={
                "model": MODEL_MAP[agent],
                "messages": [{"role": "user", "content": q["query"]}],
                "max_tokens": 50
            },
            timeout=5
        )

        print("\n====================================")
        print("\nAgent:", agent)
        print("Query:", q["query"])
        print("Status:", response.status_code)
        print("======================================")

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print("Response:", answer)

        # ✅ COMPLETE QUERY HERE ONLY
        complete_query(agent)

    except Exception as e:
        print("Request failed:", e)

    time.sleep(1.0)
