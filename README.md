# Adaptive Multi-Agent GPU

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://docker.com)
[![vLLM](https://img.shields.io/badge/vLLM-Supported-blue.svg)](https://vllm.readthedocs.io)

An intelligent multi-agent LLM inference system with **adaptive GPU resource allocation** across multiple model serving containers on NVIDIA DGX/cluster environments.

## Overview

This project implements an adaptive GPU allocation system that dynamically distributes GPU resources among multiple LLM serving agents based on real-time demand metrics. It uses vLLM for high-performance model serving with Docker containers, and intelligently routes queries to available agents while monitoring GPU utilization, queue lengths, arrival rates, latency, and SLA compliance.

## Architecture

```
adaptive-multi-agent-gpu/
├── src/                    # Core logic modules
│   ├── adaptive_controller.py  # Main control loop - monitors & reallocates
│   ├── allocator.py            # Demand-based GPU allocation algorithm
│   ├── scheduler.py            # Weighted agent selection for queries
│   ├── coordinator.py          # Query routing (text/vision/logic → agents)
│   ├── metrics.py              # Metrics tracking (queues, latency, SLA)
│   ├── request_generator.py    # Simulated query generator
│   └── Previous model loading code.txt
├── deployment/             # Docker deployment & GPU management
│   ├── auto_deployer.py        # Auto-deploy all model containers
│   ├── docker_launcher.py      # Launch individual model containers
│   ├── gpu_monitor.py          # GPU monitoring via PyNVML
│   ├── gpu_selector.py         # Smart GPU selection algorithm
│   └── launch_all.sh           # Shell script to launch all
├── configs/                # Configuration files
│   ├── config.py               # Agents, ports, model paths, min_share
│   └── model_config.py         # Model definitions list
├── dashboard/              # Real-time monitoring
│   └── dashboard_gpu.py        # Live GPU + metrics dashboard (Rich TUI)
└── scripts/                # Utility scripts
    └── run_scheduler.py        # Run the auto-deployer via runpy
```

## Features

- **Adaptive GPU Allocation**: Dynamically adjusts GPU memory share for each agent based on demand (arrival rate + queue backlog)
- **Priority-Based Scheduling**: High-priority agents (coord, reasoning) get preferential GPU share
- **Multi-Model Support**: Runs different LLMs (Phi-3, Qwen, TinyLLaMA) on separate containers
- **Real-Time Dashboard**: Live TUI showing GPU utilization, memory, queue length, latency, throughput, and SLA violations
- **Smart GPU Selection**: Automatically selects the best available GPU using PyNVML
- **Fallback Mechanism**: If an agent is down, queries are routed to a fallback agent
- **SLA Monitoring**: Tracks response latency and flags SLA violations (>200ms threshold)
- **Docker Container Management**: Auto-cleanup of existing containers before deploying new ones

## Agents

| Agent     | Model      | Port | Min GPU Share | Priority |
|-----------|-----------|------|---------------|----------|
| coord     | Phi-3     | 8001 | 10%           | HIGH (1) |
| nlp       | Qwen 2.5  | 8002 | 20%           | MEDIUM (2) |
| vision    | TinyLLaMA | 8003 | 20%           | MEDIUM (2) |
| reasoning | Phi-3     | 8004 | 30%           | HIGH (1) |

## Prerequisites

- NVIDIA DGX or GPU cluster with Docker support
- Docker with NVIDIA Container Toolkit (`--gpus` flag)
- Python 3.8+
- Required Python packages: `pynvml`, `requests`, `rich`

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rika1089/adaptive-multi-agent-gpu.git
cd adaptive-multi-agent-gpu
```

### 2. Download Models

Models should be placed in `/nfsshare/users/sreekar/models/` or update `configs/config.py` with your model paths.

Example:
```bash
# Download Qwen2.5-7B-Instruct-AWQ
cd /nfsshare/users/sreekar/my_models
git clone https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-AWQ qwen7b_awq
cd qwen7b_awq && git restore --source=HEAD ./

# Download other models similarly
```

### 3. Install Python Dependencies

```bash
pip install pynvml requests rich
```

## Usage

### Option 1: Run All at Once

```bash
cd scripts
python run_scheduler.py
```

This deploys all model containers and starts the adaptive allocation loop.

### Option 2: Manual Deployment

```bash
# Step 1: Deploy all containers
cd deployment
python auto_deployer.py

# Step 2: Start the adaptive controller (in another terminal)
cd ../src
python adaptive_controller.py

# Step 3: Start the request generator (in another terminal)
python request_generator.py

# Step 4: View the dashboard (in another terminal)
cd ../dashboard
python dashboard_gpu.py
```

### Option 3: Use the Launch Script

```bash
cd deployment
./launch_all.sh
```

## How It Works

### Adaptive Allocation Algorithm

The `allocator.py` computes GPU share for each agent using:

```
demand[agent] = (arrival_rate + queue_length) * min_share / priority
gpu_share[agent] = demand[agent] / total_demand
```

- **arrival_rate**: Requests per second in the last 10 seconds
- **queue_length**: Number of pending requests
- **min_share**: Minimum guaranteed GPU share
- **priority**: Higher priority = lower divisor = more GPU share

### Query Flow

1. **Request Generator** creates queries and sends them to the **Coordinator**
2. **Coordinator** routes queries based on type (text → nlp, vision → vision, logic → reasoning)
3. **Scheduler** picks an available agent based on current weights
4. **Fallback** mechanism routes to alternative agent if primary is unavailable
5. **Metrics** are tracked: latency, throughput, SLA violations
6. **Adaptive Controller** periodically recomputes allocations and updates scheduler weights

## Dashboard

The dashboard (`dashboard_gpu.py`) displays:

- **GPU**: Which GPU each agent is running on
- **Util %**: Current GPU utilization
- **Mem (GB)**: GPU memory used
- **Queue**: Number of pending requests
- **ArrRate**: Arrival rate (requests/sec)
- **Latency**: Average response latency (ms)
- **Throughput**: Requests completed per second
- **SLA**: SLA violation rate
- **Status**: 🟢 UP / 🔴 DOWN

## Configuration

Edit `configs/config.py` to customize:

- **agents**: List of agent names
- **min_share**: Minimum GPU share per agent
- **ports**: Port mappings for each agent
- **model_paths**: Paths to model directories

## Installation

### Prerequisites

- **Python 3.8+**
- **Docker** with NVIDIA Container Toolkit
- **NVIDIA GPU** (DGX or compatible with multiple GPUs)
- **vLLM** compatible models (Phi-3, Qwen 2.5, TinyLLaMA)
- **PyNVML** for GPU monitoring

### Setup Steps

1. **Clone the repository:**
```bash
git clone https://github.com/rika1089/adaptive-multi-agent-gpu.git
cd adaptive-multi-agent-gpu
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
# Or install individually:
pip install requests rich pynvml
```

3. **Download LLM models:**
Models should be placed in the shared NFS path. Default model paths in `configs/config.py`:
```python
model_paths = {
    "coord": "/models/phi3",
    "nlp": "/models/qwen",
    "vision": "/models/tinyllama",
    "reasoning": "/models/tinyllama"
}
```

4. **Verify GPU access:**
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

## Quick Start

### 1. Deploy All Agents

Run the auto-deployer to launch all model containers:
```bash
python -m scripts.run_scheduler
```

Or directly:
```bash
cd deployment
python auto_deployer.py
```

The deployer will:
- Clean up any existing containers
- Launch each agent on the best available GPU
- Wait for each model to be ready before proceeding

### 2. Run the Request Generator

In a separate terminal, start the query generator:
```bash
cd src
python request_generator.py
```

This will continuously send queries to the agent cluster and track metrics.

### 3. Launch the Dashboard

In another terminal, start the real-time monitoring dashboard:
```bash
cd dashboard
python dashboard_gpu.py
```

The dashboard shows live GPU utilization, queue lengths, latency, throughput, and SLA metrics for all agents.

## System Workflow

```
[User Query] 
     |
     v
[Coordinator] -- routes by type (text->nlp, vision->vision, logic->reasoning)
     |
     v
[Scheduler] -- picks agent based on current weights
     |
     v
[vLLM Container] -- processes request on GPU
     |
     v
[Metrics] -- tracks latency, throughput, SLA
     |
     v
[Allocator] -- adjusts GPU shares based on demand
```

## Configuration

Edit `configs/config.py` to customize:

### Agent Configuration
| Parameter | Description |
|-----------|-------------|
| `agents` | List of agent names: `["coord", "nlp", "vision", "reasoning"]` |
| `min_share` | Minimum GPU memory share per agent (must sum to <= 1.0) |
| `ports` | Port mappings for each agent's vLLM API |
| `model_paths` | Paths to model directories on the host |

### Example min_share settings:
```python
min_share = {
    "coord": 0.1,      # 10% - lightweight coordinator
    "nlp": 0.2,        # 20% - NLP specialist
    "vision": 0.2,     # 20% - vision specialist
    "reasoning": 0.3   # 30% - reasoning specialist (heaviest)
}
```

### Priority Configuration (in allocator.py)
```python
priority = {
    "coord": 1,      # HIGH - latency sensitive
    "nlp": 2,        # MEDIUM
    "vision": 2,     # MEDIUM
    "reasoning": 1   # HIGH - complex reasoning
}
```

### Demand-Based Allocation Formula
The allocation algorithm computes demand as:
```
demand[agent] = (arrival_rate + queue_length) * min_share / priority
```
Resources are then allocated proportionally to demand scores while enforcing minimum share guarantees.

## API Endpoints

Each agent exposes a vLLM-compatible OpenAI API:

| Agent | Port | Endpoint |
|-------|------|----------|
| coord | 8001 | `http://localhost:8001/v1/chat/completions` |
| nlp | 8002 | `http://localhost:8002/v1/chat/completions` |
| vision | 8003 | `http://localhost:8003/v1/chat/completions` |
| reasoning | 8004 | `http://localhost:8004/v1/chat/completions` |

### Example Request
```bash
curl http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "/models/qwen",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

## Performance

Based on the underlying research [arXiv:2512.22149](https://arxiv.org/abs/2512.22149):
- **85% latency reduction** compared to round-robin scheduling
- **Comparable throughput** to static allocation (58.1 req/s vs 60.0 req/s)
- **O(N) complexity** for real-time GPU allocation adaptation
- **Balanced per-agent latency** with priority-aware scheduling

## Troubleshooting

## Troubleshooting

### Container fails to start
```bash
docker logs {agent}_server
```

### GPU not found
Ensure NVIDIA Container Toolkit is installed:
```bash
nvidia-docker run --rm nvidia/cuda:11.0-base nvidia-smi
```

### Import errors
Run scripts from the project root or use the path setup in `run_scheduler.py`.

### Model loading errors
Check that model paths in `configs/config.py` are correct and the models are downloaded.

## License

MIT License

## Acknowledgments

Built with:
- [vLLM](https://vllm.readthedocs.io) - High-throughput LLM serving
- [PyNVML](https://pypi.org/project/pynvml/) - NVIDIA GPU monitoring
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal UI
- Docker & NVIDIA Container Toolkit
