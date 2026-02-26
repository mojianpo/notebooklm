#!/bin/bash
set -e

echo "=== Start Development Script ==="

# 安装前端依赖
echo "Step 1: Installing frontend dependencies..."
pnpm --prefix frontend install

# 安装后端依赖
echo "Step 2: Installing backend dependencies..."
cd backend && pip install -r ../requirements.txt

# 启动后端服务（后台）
echo "Step 3: Starting backend service..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /app/work/logs/bypass/backend.log 2>&1 &

# 等待后端启动
sleep 3

# 启动前端服务
echo "Step 4: Starting frontend service..."
cd ../frontend && pnpm dev
