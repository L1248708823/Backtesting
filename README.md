# 量化回测系统 (Quantitative Backtesting System)

一个专为个人投资者设计的量化交易策略回测验证平台，专注ETF轮动等策略的可行性验证。

## 🏗️ 项目架构

```
quantitative-backtesting/
├── backend/          # Python后端 (FastAPI + Backtrader)
├── frontend/         # React前端 (TypeScript + Ant Design)
├── shared/          # 共享类型和常量
├── docs/            # 项目文档
├── PRD.md           # 产品需求文档
└── README.md        # 项目说明
```

## 🚀 技术栈

### 后端技术栈
- **框架**: FastAPI
- **回测引擎**: Backtrader
- **数据源**: AKShare (A股) + yfinance (美股)
- **数据库**: SQLite (MVP) / PostgreSQL (扩展)
- **容器**: Docker

### 前端技术栈
- **框架**: React 18 + TypeScript
- **UI组件**: Ant Design
- **图表库**: ECharts
- **构建工具**: Vite
- **状态管理**: React Context

## 📋 功能特性

### 核心功能
- ✅ 多策略回测支持 (定投、ETF轮动、均值回归等)
- ✅ 灵活参数配置
- ✅ 详细回测报告和可视化
- ✅ A股和美股ETF支持
- ✅ 交易成本精确计算

### 高级功能
- 📊 收益曲线和回撤分析
- 📈 关键指标计算 (夏普比率、最大回撤等)
- 📝 策略代码查看
- 📁 历史回测记录管理

## 🛠️ 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- Docker (可选)

### 安装和运行

1. **克隆项目**
```bash
git clone <repository-url>
cd quantitative-backtesting
```

2. **后端启动**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. **前端启动**
```bash
cd frontend
npm install
npm run dev
```

4. **Docker启动 (推荐)**
```bash
docker-compose up -d
```

## 📖 使用指南

1. **选择策略**: 在首页选择要测试的回测策略
2. **配置参数**: 设置策略参数、时间范围、交易成本等
3. **执行回测**: 提交回测任务，实时查看进度
4. **查看结果**: 分析回测报告、图表和关键指标

## ⚠️ 重要提示

- 本系统仅用于学习和研究目的
- 历史业绩不代表未来收益
- 实际交易存在额外成本和风险
- 不构成任何投资建议

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [产品需求文档](PRD.md)
- [API文档](docs/api.md)
- [开发指南](docs/development.md)