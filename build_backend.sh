#!/bin/bash
set -e

echo "🐍 Setting up backend..."

pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html

# Remove GPU-related packages if they sneak in
pip uninstall -y \
  nvidia-cublas-cu12 \
  nvidia-cuda-runtime-cu12 \
  nvidia-cudnn-cu12 \
  nvidia-pyindex \
  triton || true

echo "✅ Backend setup complete."