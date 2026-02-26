#!/bin/bash

# Start NotebookLM

echo "Starting NotebookLM..."

# Install frontend dependencies
cd frontend
pnpm install

cd ..

# Install backend dependencies
cd backend
pip install -r ../requirements.txt

# Start backend server in background
echo "Starting backend server on port 8000..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /app/work/logs/bypass/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend server
echo "Starting frontend server on port 5000..."
cd ../frontend
pnpm dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
