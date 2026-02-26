#!/bin/bash
set -e

echo "=== Build Deployment Script ==="

# 安装前端依赖
echo "Step 1: Installing frontend dependencies..."
cd frontend
pnpm install

# 构建前端
echo "Step 2: Building frontend..."
pnpm build

echo "=== Build Complete ==="
