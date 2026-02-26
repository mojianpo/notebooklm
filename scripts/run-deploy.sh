#!/bin/bash
set -e

echo "=== Run Deployment Script ==="

# 安装后端依赖
echo "Step 1: Installing backend dependencies..."
cd backend
pip install -r ../requirements.txt > /dev/null 2>&1

# 安装 coze-coding-dev-sdk
echo "Step 2: Installing coze-coding-dev-sdk..."
pip install coze-coding-dev-sdk > /dev/null 2>&1

# 启动后端服务
echo "Step 3: Starting backend service..."
python -m uvicorn main:app --host 0.0.0.0 --port 5000
