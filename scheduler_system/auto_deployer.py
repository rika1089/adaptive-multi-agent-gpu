# from model_config import MODELS
# from docker_launcher import launch_model

# def deploy_all():
#     for model in MODELS:
#         launch_model(model)

# if __name__ == "__main__":
#     deploy_all()

import requests
import time
from model_config import MODELS
from docker_launcher import launch_model


def wait_until_ready(port, timeout=120):
    print(f"  Checking port {port}...", end="", flush=True)
    

    for i in range(timeout):
        try:
            r = requests.get(f"http://localhost:{port}/v1/models", timeout=2)
            if r.status_code == 200:
                print(f"✅ READY in {i}s")
                return True
        except:
            pass

        print(f"⏳ Loading... {i+1}s  ", end="\r")
        time.sleep(1)

    print("❌ TIMEOUT")
def deploy_all():
    for model in MODELS:
        launch_model(model)
        ready = wait_until_ready(model['port'])
        if not ready:
            print(f"WARNING: {model['name']} failed to start — check: docker logs {model['name']}_server")

# Instead of manually deleting every time, modify your auto_deployer.py:

# Add this before launching containers:

import os
def remove_if_exists(name):
    os.system(f"docker rm -f {name} 2>/dev/null")

# before launching each agent
remove_if_exists("coord_server")
remove_if_exists("nlp_server")
remove_if_exists("vision_server")
remove_if_exists("reasoning_server")
        

if __name__ == "__main__":
    deploy_all()