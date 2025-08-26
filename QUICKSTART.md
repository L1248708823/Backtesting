# 快速启动指南

## 🚀 一分钟快速启动

### 前置要求
- Docker 和 Docker Compose
- 或者 Python 3.9+ 和 Node.js 16+

### 方式一：Docker 启动（推荐）

```bash
# 1. 克隆并进入项目目录
cd "/mnt/e/py/cc 回测"

# 2. 启动所有服务
docker-compose up -d

# 3. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8008
# API文档: http://localhost:8008/docs
```

### 方式二：本地开发启动

**后端启动**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**前端启动（新终端）**
```bash
cd frontend
npm install
npm run dev
```

## 📋 项目状态检查

### 验证后端服务
```bash
curl http://localhost:8008/health
# 预期输出: {"status": "healthy"}
```

### 验证前端服务
浏览器访问 http://localhost:3000

### 验证API功能
```bash
curl http://localhost:8008/api/v1/strategies/
# 预期输出: 策略列表JSON
```

## 🛠️ 开发工具

### 代码格式化
```bash
# 后端
cd backend && black . && isort .

# 前端
cd frontend && npm run lint:fix
```

### 运行测试
```bash
# 后端测试
cd backend && pytest

# 前端测试
cd frontend && npm test
```

## 📁 关键文件说明

| 文件 | 用途 |
|------|------|
| `PRD.md` | 产品需求文档 |
| `docker-compose.yml` | Docker编排配置 |
| `backend/app/main.py` | 后端API入口 |
| `frontend/src/App.tsx` | 前端应用入口 |
| `docs/development.md` | 详细开发指南 |

## ⚡ 下一步

项目初始化已完成！你可以：

1. **开始设计阶段**: 输入 `/设计` 启动UI/UX设计师
2. **查看API文档**: 访问 http://localhost:8000/docs
3. **修改配置**: 编辑 `docker-compose.yml` 或环境变量文件
4. **添加新功能**: 参考 `docs/development.md`

## 🔧 常见问题

**端口被占用？**
```bash
# 停止服务
docker-compose down

# 修改端口（编辑 docker-compose.yml）
# 然后重新启动
docker-compose up -d
```

**权限问题？**
```bash
# Linux/Mac 用户可能需要
sudo docker-compose up -d
```

**清理和重建？**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```