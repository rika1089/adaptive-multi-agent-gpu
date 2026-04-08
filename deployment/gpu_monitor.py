import pynvml

pynvml.nvmlInit()

def get_gpu_info():
    gpus = []

    for i in range(pynvml.nvmlDeviceGetCount()):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)

        # Memory info (always works)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
        free_mem = mem.free
        total_mem = mem.total

        # Try utilization (may fail on DGX / MIG)
        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_util = util.gpu
        except pynvml.NVMLError_NotSupported:
            # Fallback → estimate using memory
            gpu_util = int((mem.used / total_mem) * 100)

        gpus.append({
            "id": i,
            "free_mem": free_mem,
            "used_mem": mem.used,
            "total_mem": total_mem,
            "util": gpu_util
        })

    return gpus