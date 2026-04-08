agents = ["coord", "nlp", "vision", "reasoning"]

min_share = {
    "coord": 0.1,
    "nlp": 0.2,
    "vision": 0.2,
    "reasoning": 0.3
}

ports = {
    "coord": 8001,
    "nlp": 8002,
    "vision": 8003,
    "reasoning": 8004
}


model_paths = {
    "coord":"/models/phi3",
    "nlp":"/models/qwen",
    # "vision":"/models/blip",
    "vision": "/models/tinyllama",
    # "reasoning":"/models/llama3b"
    "reasoning": "/models/tinyllama"
}


# # =Your allocator started the container with:

# # gpu_memory_utilization = 0.09

# # That is too small for vLLM to allocate KV cache.

# min_share = {
#     "coord":0.3,
#     "nlp":0.3,
#     "vision":0.3,
#     "reasoning":0.3
# }