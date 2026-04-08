#!/bin/bash

pkill -f "vllm.entrypoints" 2>/dev/null
sleep 2
mkdir -p logs

MODELS=/nfsshare/users/sreekar/models

echo "Starting coord → port 8001 on GPU 5"
CUDA_VISIBLE_DEVICES=5 \
python -m vllm.entrypoints.openai.api_server \
  --model $MODELS/phi3 --port 8001 \
  --max-model-len 2048 --gpu-memory-utilization 0.4 \
  > logs/coord.log 2>&1 &

sleep 5

echo "Starting nlp → port 8002 on GPU 6"
CUDA_VISIBLE_DEVICES=6 \
python -m vllm.entrypoints.openai.api_server \
  --model $MODELS/qwen --port 8002 \
  --max-model-len 2048 --gpu-memory-utilization 0.4 \
  > logs/nlp.log 2>&1 &

sleep 5

echo "Starting vision → port 8003 on GPU 7"
CUDA_VISIBLE_DEVICES=7 \
python -m vllm.entrypoints.openai.api_server \
  --model $MODELS/tinyllama --port 8003 \
  --max-model-len 2048 --gpu-memory-utilization 0.4 \
  > logs/vision.log 2>&1 &

sleep 5

echo "Starting reasoning → port 8004 on GPU 5 (second slot)"
CUDA_VISIBLE_DEVICES=5 \
python -m vllm.entrypoints.openai.api_server \
  --model $MODELS/phi3 --port 8004 \
  --max-model-len 2048 --gpu-memory-utilization 0.4 \
  > logs/reasoning.log 2>&1 &

echo ""
echo "All launched. Tailing coord log — wait for 'Application startup complete'"
tail -f logs/coord.log
