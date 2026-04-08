# from gpu_monitor import get_gpu_info

# def select_best_gpu():
#     gpus = get_gpu_info()
#     # best = max(gpus, key=lambda x: x["free_mem"])
#     best = max(available, key=lambda x: (x["free_mem"], -x["util"]))
#     return best["id"]
import pynvml
from gpu_monitor import get_gpu_info

used_gpus = set()

def select_best_gpu():
    global used_gpus

    gpus = get_gpu_info()

    # ✅ define available GPUs
    # available = [g for g in gpus if g["id"] not in used_gpus]
    if len(used_gpus) < pynvml.nvmlDeviceGetCount():
        available = [g for g in gpus if g["id"] not in used_gpus]
    else:
        used_gpus.clear()
        available = gpus

    # if all GPUs used → reset
    if not available:
        used_gpus.clear()
        available = gpus

    # ✅ select best GPU
    best = max(available, key=lambda x: (x["free_mem"], -x["util"]))

    used_gpus.add(best["id"])

    return best["id"]