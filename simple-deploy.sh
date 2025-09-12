#!/bin/bash
# 超简单部署脚本

echo "🚀 开始部署..."

# 拉取最新代码
git pull origin main

# 重启服务
docker-compose down
docker-compose up -d --build

echo "✅ 部署完成！"
echo "前端: http://localhost:3001"
echo "后端: http://localhost:8008"