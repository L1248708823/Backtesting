# 开发指南

## 项目结构说明

```
quantitative-backtesting/
├── backend/                 # Python后端
│   ├── app/
│   │   ├── main.py         # FastAPI应用入口
│   │   ├── api/            # API路由
│   │   ├── core/           # 回测核心引擎
│   │   ├── strategies/     # 策略实现
│   │   └── utils/          # 工具函数
│   ├── tests/              # 测试文件
│   ├── requirements.txt    # Python依赖
│   ├── Dockerfile         # Docker配置
│   └── pyproject.toml     # 项目配置
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   └── utils/         # 工具函数
│   ├── package.json       # Node.js依赖
│   ├── vite.config.ts     # Vite配置
│   └── Dockerfile         # Docker配置
├── shared/                 # 共享代码
├── docs/                   # 文档
├── docker-compose.yml      # Docker编排
├── README.md               # 项目说明
└── PRD.md                  # 产品需求文档
```

## 环境设置

### 本地开发环境

**1. 环境要求**
- Python 3.9+
- Node.js 16+
- Git

**2. 后端开发**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**3. 前端开发**
```bash
cd frontend
npm install
npm run dev
```

### Docker开发环境（推荐）

**一键启动**
```bash
docker-compose up -d
```

访问地址：
- 前端：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 开发规范

### 后端代码规范

**代码格式化**
```bash
cd backend
black .
isort .
```

**代码检查**
```bash
flake8 .
mypy .
```

**运行测试**
```bash
pytest
```

### 前端代码规范

**代码检查和修复**
```bash
cd frontend
npm run lint
npm run lint:fix
```

**类型检查**
```bash
npm run build
```

## API开发指南

### 添加新的API端点

1. 在 `backend/app/api/` 目录下创建或修改相应的路由文件
2. 定义Pydantic模型用于请求和响应
3. 实现业务逻辑
4. 添加单元测试

### 示例：添加新的策略API

```python
# backend/app/api/strategies.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class NewStrategyRequest(BaseModel):
    name: str
    parameters: dict

@router.post("/new-strategy")
async def create_strategy(request: NewStrategyRequest):
    # 实现逻辑
    return {"message": "Strategy created"}
```

## 前端开发指南

### 组件开发规范

1. 使用TypeScript编写所有组件
2. 遵循React Hooks最佳实践
3. 使用Ant Design组件库
4. 保持组件单一职责

### 添加新页面

1. 在 `frontend/src/pages/` 目录创建页面组件
2. 在 `App.tsx` 中添加路由
3. 在侧边栏菜单中添加导航

### 状态管理

目前使用React Context进行状态管理，复杂状态可以考虑使用Redux Toolkit。

## 测试指南

### 后端测试

```bash
cd backend
pytest tests/
```

### 前端测试

```bash
cd frontend
npm test
```

## 部署指南

### 开发环境部署

使用Docker Compose：
```bash
docker-compose up -d
```

### 生产环境部署

1. 构建镜像
```bash
docker-compose -f docker-compose.prod.yml build
```

2. 启动服务
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 常见问题

### Q: 端口冲突怎么解决？
A: 修改 `docker-compose.yml` 中的端口映射，或使用 `docker-compose down` 停止服务。

### Q: 前端无法访问后端API？
A: 检查CORS配置和环境变量设置。

### Q: 如何添加新的数据源？
A: 在 `backend/app/core/` 目录下实现数据源适配器，并在配置中注册。

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交变更
4. 创建Pull Request

请确保代码通过所有测试和代码检查。