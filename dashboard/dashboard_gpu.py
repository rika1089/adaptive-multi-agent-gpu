import time
import requests
from rich.live import Live
from rich.table import Table
import pynvml

from src.metrics import (

    compute_avg_latency,
    compute_queue_length,
    compute_arrival_rate,
    compute_throughput,
    compute_sla_violation_rate
)

pynvml.nvmlInit()

# ✅ FIX GPU MAPPING (IMPORTANT)
SERVERS = {
    "coord": {"port": 8001, "gpu": 0},
    "nlp": {"port": 8002, "gpu": 1},
    "vision": {"port": 8003, "gpu": 1},
    "reasoning": {"port": 8004, "gpu": 0},
}

def get_gpu_stats(gpu_id):
    handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)

    try:
        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
        gpu_util = util.gpu
    except:
        gpu_util = int((mem.used / mem.total) * 100)

    # ✅ convert to GB
    mem_gb = round(mem.used / (1024**3), 2)

    return gpu_util, mem_gb


def check_status(port):
    try:
        r = requests.get(f"http://localhost:{port}/v1/models", timeout=1)
        return "🟢 UP" if r.status_code == 200 else "🔴 DOWN"
    except:
        return "🔴 DOWN"


def generate_table():

    table = Table(title="🚀 AI Multi-Agent GPU Dashboard")

    # ✅ UPDATED COLUMNS
    table.add_column("Agent")
    table.add_column("GPU")
    table.add_column("Util %")
    table.add_column("Mem (GB)")
    table.add_column("Queue")
    table.add_column("ArrRate")
    table.add_column("Latency(ms)")
    table.add_column("Throughput")
    table.add_column("SLA")
    table.add_column("Status")

    for agent, data in SERVERS.items():

        gpu_id = data["gpu"]

        # GPU stats
        util, mem = get_gpu_stats(gpu_id)

        # 🔥 REAL METRICS (NOT FAKE)
        q_len = compute_queue_length(agent)
        arr = compute_arrival_rate(agent)
        lat = compute_avg_latency(agent)
        thr = compute_throughput(agent)
        sla = compute_sla_violation_rate(agent)

        status = check_status(data["port"])

        table.add_row(
            agent,
            f"GPU{gpu_id}",
            f"{util}%",
            str(mem),
            str(q_len),
            f"{round(arr,2)}",
            f"{round(lat,2)}",
            f"{round(thr,2)}",
            f"{round(sla,2)}",
            status
        )

    return table


with Live(generate_table(), refresh_per_second=1) as live:

    while True:
        time.sleep(2)   # faster update
        live.update(generate_table())
