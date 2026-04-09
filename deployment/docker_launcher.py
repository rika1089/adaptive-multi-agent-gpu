# The fix — switch from os.system() to subprocess.run() which avoids shell quoting entirely:

import subprocess
from deployment.gpu_selector import select_best_gpu

def launch_model(model):
    gpu = select_best_gpu()

    print(f"Launching {model['name']} on GPU {gpu}")

    subprocess.run([
    "docker", "run", "-d",
    "--gpus", f"device={gpu}",   # 🔥 IMPORTANT
    "--ipc=host",                # recommended for vLLM
    "-p", f"{model['port']}:8000",
    "-v", "/nfsshare/users/sreekar/models:/models",
    "--name", f"{model['name']}_server",
    "vllm/vllm-openai",
    model['path'],
    "--max-model-len", "2048",
    "--gpu-memory-utilization", "0.4"
])


## Before the model loading error this was running like this

# import os
# from gpu_selector import select_best_gpu

# def launch_model(model):
#     gpu = select_best_gpu()

#     cmd = f"""
#     docker run -d --gpus '"device={gpu}"' \
#     -p {model['port']}:8000 \
#     -v /nfsshare/users/sreekar/models:/models \
#     --name {model['name']}_server \
#     vllm/vllm-openai {model['path']} \
#     --max-model-len 2048 \
#     --gpu-memory-utilization 0.3
#     """
#     #--gpu-memory-utilization 0.25
#     print(f"Launching {model['name']} on GPU {gpu}")
#     os.system(cmd)

#     # Give each model time to load before launching the next
#     print(f"Waiting 20s for {model['name']} to initialize...")
#     time.sleep(20)
