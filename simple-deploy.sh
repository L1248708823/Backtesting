#!/bin/bash
# 量化回测系统部署脚本

set -e  # 遇到错误立即退出

echo "🚀 开始部署..."

# 检查Docker权限
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker权限不足，请执行："
    echo "sudo usermod -aG docker $USER"
    echo "newgrp docker"
    exit 1
fi

# echo "📥 拉取最新代码..."
# git pull origin main

echo "🛑 停止现有容器..."
docker-compose down || true

echo "🏗️ 启动容器 (利用缓存)..."
docker-compose up -d

echo "💡 如需强制重建，请使用: docker-compose up -d --build"

echo "⏳ 等待服务启动..."
sleep 15

echo "✅ 部署完成！"
echo "前端: http://localhost:3000"
echo "后端: http://localhost:8000"
echo ""
echo "🔍 健康检查:"
curl -f http://localhost:8000/health && echo "✅ 后端健康" || echo "❌ 后端异常"
curl -f http://localhost:3000 > /dev/null 2>&1 && echo "✅ 前端健康" || echo "❌ 前端异常"