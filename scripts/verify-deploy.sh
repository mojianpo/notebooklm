#!/bin/bash

echo "=== Deployment Verification Script ==="
echo ""

# 检查端口
echo "1. Checking port 5000..."
if ss -lptn 'sport = :5000' | grep -q LISTEN; then
    echo "   ✅ Port 5000 is listening"
else
    echo "   ❌ Port 5000 is not listening"
fi
echo ""

# 检查前端构建
echo "2. Checking frontend build..."
if [ -f "backend/static/index.html" ]; then
    echo "   ✅ Frontend build exists"
    echo "   📁 Static files:"
    ls -lh backend/static/ | tail -n +2 | awk '{print "      " $9 " (" $5 ")"}'
else
    echo "   ❌ Frontend build not found"
fi
echo ""

# 测试健康检查
echo "3. Testing health check..."
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    response=$(curl -s http://localhost:5000/health)
    echo "   ✅ Health check passed: $response"
else
    echo "   ❌ Health check failed"
fi
echo ""

# 测试前端页面
echo "4. Testing frontend page..."
if curl -s http://localhost:5000/ | grep -q "NotebookLM"; then
    echo "   ✅ Frontend page accessible"
else
    echo "   ❌ Frontend page not accessible"
fi
echo ""

# 测试 API 端点
echo "5. Testing API endpoint..."
if curl -s http://localhost:5000/api/v1/notebooks/ > /dev/null 2>&1; then
    count=$(curl -s http://localhost:5000/api/v1/notebooks/ | grep -o '\[.*\]' | wc -c)
    echo "   ✅ API endpoint accessible"
    echo "   📊 Response size: $count bytes"
else
    echo "   ❌ API endpoint not accessible"
fi
echo ""

# 检查错误日志
echo "6. Checking error logs..."
error_count=$(tail -n 50 /app/work/logs/bypass/backend.log 2>/dev/null | grep -iE "error|exception|warn" | wc -l)
if [ $error_count -eq 0 ]; then
    echo "   ✅ No errors in recent logs"
else
    echo "   ⚠️  Found $error_count errors in recent logs"
    tail -n 50 /app/work/logs/bypass/backend.log 2>/dev/null | grep -iE "error|exception|warn" | head -n 3 | sed 's/^/      /'
fi
echo ""

echo "=== Verification Complete ==="
