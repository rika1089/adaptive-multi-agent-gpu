# from collections import deque
# import time

# queues = {
#     "coord":deque(),
#     "nlp":deque(),
#     "vision":deque(),
#     "reasoning":deque()
# }

# arrival_times = {
#     "coord":[],
#     "nlp":[],
#     "vision":[],
#     "reasoning":[]
# }

def add_query(agent,query):

    queues[agent].append(query)

    arrival_times[agent].append(time.time())


from collections import deque
import time

# ---------------------------------
# DATA STRUCTURES
# ---------------------------------

queues = {
    "coord": deque(),
    "nlp": deque(),
    "vision": deque(),
    "reasoning": deque()
}

arrival_times = {
    "coord": [],
    "nlp": [],
    "vision": [],
    "reasoning": []
}

latencies = {
    "coord": [],
    "nlp": [],
    "vision": [],
    "reasoning": []
}

completed_requests = {
    "coord": 0,
    "nlp": 0,
    "vision": 0,
    "reasoning": 0
}

sla_violations = {
    "coord": 0,
    "nlp": 0,
    "vision": 0,
    "reasoning": 0
}

# SLA threshold (ms)
SLA_THRESHOLD = 200


# ---------------------------------
# REQUEST TRACKING
# ---------------------------------

def add_query(agent, query):
    queues[agent].append(query)
    arrival_times[agent].append(time.time())


def complete_query(agent):
    if not arrival_times[agent]:
        return

    start_time = arrival_times[agent].pop(0)
    latency = (time.time() - start_time) * 1000  # ms

    latencies[agent].append(latency)
    completed_requests[agent] += 1

    # SLA check
    if latency > SLA_THRESHOLD:
        sla_violations[agent] += 1

    # remove from queue
    if queues[agent]:
        queues[agent].popleft()


# ---------------------------------
# METRICS FUNCTIONS
# ---------------------------------

def compute_queue_length(agent):
    return len(queues[agent])


def compute_arrival_rate(agent, window=10):
    now = time.time()
    recent = [t for t in arrival_times[agent] if now - t < window]
    return len(recent) / window


def compute_avg_latency(agent):
    if not latencies[agent]:
        return 0
    return sum(latencies[agent]) / len(latencies[agent])


def compute_throughput(agent, duration=60):
    # requests per second
    return completed_requests[agent] / duration


def compute_sla_violation_rate(agent):
    total = completed_requests[agent]
    if total == 0:
        return 0
    return sla_violations[agent] / total


# ---------------------------------
# FAIRNESS (Jain’s Index)
# ---------------------------------

def compute_fairness(allocation):
    values = list(allocation.values())

    if not values:
        return 0

    numerator = (sum(values)) ** 2
    denominator = len(values) * sum([v**2 for v in values])

    if denominator == 0:
        return 0

    return numerator / denominator


# ---------------------------------
# DEBUG PRINT (OPTIONAL)
# ---------------------------------

def print_metrics():
    print("\n📊 METRICS")
    for agent in queues.keys():
        print(f"\nAgent: {agent}")
        print(f"Queue Length: {compute_queue_length(agent)}")
        print(f"Arrival Rate: {round(compute_arrival_rate(agent),2)}")
        print(f"Avg Latency: {round(compute_avg_latency(agent),2)} ms")
        print(f"Throughput: {round(compute_throughput(agent),2)} req/s")
        print(f"SLA Violations: {compute_sla_violation_rate(agent)}")