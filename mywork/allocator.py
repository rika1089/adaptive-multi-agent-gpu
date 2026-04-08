
# allocator.py

from metrics import queues, arrival_times
from metrics import compute_avg_latency, compute_queue_length
from config import agents, min_share

import time

# -------------------------------
# PRIORITY CONFIG (ADD THIS)
# -------------------------------
priority = {
    "coord": 1,        # HIGH
    "nlp": 2,          # MEDIUM
    "vision": 2,       # MEDIUM
    "reasoning": 1     # HIGH
}
# -------------------------------
# METRICS FUNCTIONS
# -------------------------------

def compute_queue_length(agent):
    return len(queues[agent])


def compute_arrival_rate(agent, window=10):
    now = time.time()
    recent = [t for t in arrival_times[agent] if now - t < window]
    return len(recent) / window


# -------------------------------
# 🚀 DEMAND-BASED ALLOCATION
# -------------------------------

def compute_allocation():

    demand = {}

    for a in agents:
        lam = compute_arrival_rate(a)     # arrival rate
        q = compute_queue_length(a)       # queue backlog
        R = min_share[a]                  # minimum GPU share
        P = priority[a]                  # priority

        # 🔥 FINAL DEMAND FORMULA (BEST VERSION)
        demand[a] = (lam + q) * min_share[a] / priority[a]

    total_demand = sum(demand.values())

    if total_demand == 0:
        return {a: 1/len(agents) for a in agents}

    allocation = {}

    # proportional allocation
    for a in agents:
        allocation[a] = demand[a] / total_demand

    # enforce minimum share
    for a in agents:
        allocation[a] = max(allocation[a], min_share[a])

    # normalize again
    s = sum(allocation.values())
    for a in agents:
        allocation[a] /= s

    return allocation
    
if __name__ == "__main__":
    while True:
        alloc = compute_allocation()
        print("📊 Allocation:", alloc)
        time.sleep(5)

# import time
# import subprocess
# from collections import deque

# from metrics import queues, arrival_times
# from config import agents, ports, model_paths, min_share
# from scheduler import update_weights

# # ---------------------------------
# # Agent Configuration
# # ---------------------------------

# agents = ["coord", "nlp", "vision", "reasoning"]

# ports = {
#     "coord": 8001,
#     "nlp": 8002,
#     "vision": 8003,
#     "reasoning": 8004
# }

# # Model paths on DGX server
# model_paths = {
#     "coord": "/models/phi3",
#     "nlp": "/models/qwen",
#     "vision": "/models/blip",
#     "reasoning": "/models/llama3b"
# }

# # ---------------------------------
# # Minimum GPU Share
# # ---------------------------------

# min_share = {
#     "coord": 0.1,
#     "nlp": 0.1,
#     "vision": 0.1,
#     "reasoning": 0.1
# }

# # ---------------------------------
# # Request Queues
# # ---------------------------------

# queues = {
#     "coord": deque(),
#     "nlp": deque(),
#     "vision": deque(),
#     "reasoning": deque()
# }

# # ---------------------------------
# # Arrival Time Tracking
# # ---------------------------------

# arrival_times = {
#     "coord": [],
#     "nlp": [],
#     "vision": [],
#     "reasoning": []
# }

# # ---------------------------------
# # Query Arrival Simulation
# # ---------------------------------

# def add_query(agent, query):

#     queues[agent].append(query)

#     arrival_times[agent].append(time.time())


# # ---------------------------------
# # Queue Length
# # ---------------------------------

# def compute_queue_length(agent):

#     return len(queues[agent])


# # ---------------------------------
# # Arrival Rate Calculation
# # ---------------------------------

# def compute_arrival_rate(agent, window=10):

#     now = time.time()

#     arrivals = arrival_times[agent]

#     recent = [t for t in arrivals if now - t < window]

#     return len(recent) / window


# # ---------------------------------
# # Adaptive GPU Allocation Algorithm
# # ---------------------------------

# def compute_allocation():

#     demand = {}

#     for a in agents:

#         lam = compute_arrival_rate(a)

#         q = compute_queue_length(a)

#         demand[a] = lam + q

#     total = sum(demand.values())

#     allocation = {}

#     if total == 0:

#         return {a: 0.25 for a in agents}

#     for a in agents:

#         allocation[a] = demand[a] / total

#     # enforce minimum share
#     for a in agents:

#         allocation[a] = max(allocation[a], min_share[a])

#     # normalize
#     s = sum(allocation.values())

#     for a in agents:

#         allocation[a] /= s

#     return allocation


# # ---------------------------------
# # Docker Server Restart
# # ---------------------------------

# def restart_server(agent, share):

#     container_name = f"{agent}_server"

#     print(f"\nRestarting {agent} with GPU share {round(share,2)}")

#     subprocess.run(
#         ["docker", "rm", "-f", container_name],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL
#     )

#     subprocess.run([
#         "docker", "run", "-d",
#         "--gpus", "all",
#         "-p", f"{ports[agent]}:8000",
#         "-v", "/nfsshare/users/sreekar/models:/models",
#         "--name", container_name,
#         "vllm/vllm-openai",
#         model_paths[agent],
#         "--max-model-len", "4096" #"2048",
#         "--gpu-memory-utilization", str(round(share,2))
#     ])


# # ---------------------------------
# # Simulated Query Generator
# # ---------------------------------

# def simulate_queries():

#     add_query("nlp", "Explain climate change")
#     add_query("nlp", "Summarize machine learning")
#     add_query("vision", "Describe an image")
#     add_query("reasoning", "Solve a puzzle")


# # ---------------------------------
# # Main Loop
# # ---------------------------------

# if __name__ == "__main__":

#     prev_alloc = None

#     while True:

#         # simulate workload
#         simulate_queries()

#         gs = compute_allocation()

#         print("\nCurrent GPU allocation:", gs)

#         # restart servers only if allocation changed significantly
#         if prev_alloc is None or any(abs(gs[a] - prev_alloc[a]) > 0.05 for a in agents):
            
            
#             #print("Allocation changed. Restarting servers...")

#             # for agent, share in gs.items():

#             #     restart_server(agent, share)
#             #3️⃣ Replace Restart With Weight Update

#             # Replace the restart block with:

#             print("Allocation changed. Updating scheduler weights...")

#             update_weights(gs)

#             prev_alloc = gs

#         else:

#             print("No major change in allocation.")

#         time.sleep(30)