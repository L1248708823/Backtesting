# 🥷 Ninja韭菜道场 (Ninja Backtesting Dojo)

> **别人恐惧我贪婪，别人小亏我破产** 

一个采用忍者黑客终端风格的量化交易策略回测平台，专为程序员投资者设计。从韭菜到忍者的修炼之路，从这里开始！

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
- **框架**: React 18 + TypeScript - 现代化前端开发
- **UI组件**: Ant Design - 企业级组件库  
- **样式方案**: Tailwind CSS - 快速构建忍者终端风格
- **图表库**: ECharts - 专业数据可视化
- **构建工具**: Vite - 极速开发体验
- **状态管理**: React Context - 轻量级状态管理

## 📋 功能特性

### 🥷 当前已修炼完成
- ✅ **忍者黑客终端界面** - 终端风格黑绿配色，让你感受真正的Hacker体验
- ✅ **DCA定投策略** - 完整的后端实现，专为懒人韭菜设计
- ✅ **策略选择页** - 忍者情报网风格，展示可用策略和实时市场动向  
- ✅ **Backtrader专业引擎** - 基于专业回测框架，告别自制玩具引擎
- ✅ **FastAPI高性能后端** - 现代异步API，响应速度飞快

### 🔥 正在修炼中 (DCA策略专项联调)
- 🔄 **AKShare真实数据源** - 正在集成，告别假数据自嗨
- 🔄 **DCA前端页面重构** - 适配忍者风格，提供最优用户体验
- 🔄 **完整用户流程** - 从策略选择到结果查看的端到端验证

### 🎯 下个阶段规划 (ETF轮动策略)
- ⏳ **ETF轮动策略** - 月度/季度/年度轮动，专业投资者必备
- ⏳ **策略对比功能** - 让不同策略PK，找出最强王者
- ⏳ **更多忍者功能** - 基于真实使用需求逐步添加

### ⚠️ 修炼须知
> **重要提醒**: 本道场专注实用主义，功能状态如实标注。✅=能用，🔄=开发中，⏳=计划中。
> 投资有风险，韭菜需谨慎！本系统仅供学习研究，不构成投资建议。

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
py -3.12 -m venv venv312
venv312\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
  cd backend
  py -3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port     
   8008
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

## 📖 忍者修炼指南

### 🥷 新手入门 (当前可用)
1. **启动终端**: `docker-compose up -d` 一键启动忍者道场
2. **进入道场**: 浏览器访问 http://localhost:3000 
3. **选择修炼**: 在忍者情报网中选择DCA定投策略
4. **开始历练**: 配置参数，观察市场，等待时机

### 🔥 高级修炼 (开发中)
1. **真实对战**: 集成AKShare真实数据，告别模拟训练
2. **ETF轮动术**: 掌握更高级的轮动策略技能
3. **策略对决**: 让不同策略在同一战场上较量

## ⚠️ 道场守则

> **忍者信条**: 
> - 🥷 本道场专为程序员韭菜设计，承认失败是修炼必经路
> - 💀 历史数据只能说明过去，未来永远充满不确定性
> - 🎯 实际交易比回测复杂100倍，心理素质比技术更重要
> - 🚫 **不构成投资建议** - 我们只是提供修炼工具，亏钱请自负

### 💡 修炼心得
- 别人恐惧我贪婪，别人小亏我破产 
- 韭菜到忍者的路很长，但至少我们有了工具
- 程序员的浪漫：用代码验证投资直觉的对错

## 🤝 道场共建

### 🥷 参与修炼
- 发现Bug? 提Issue让我们一起踩坑！
- 有好想法? 提PR分享你的忍者技巧！
- 想要新策略? 按照DCA策略的开发模式来贡献！

### 🔥 开发者社区
- 每个策略都独立开发，避免过早抽象
- 遵循"先具体后抽象"的修炼之道
- 真诚交流，承认错误，共同成长

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**最后更新**: 2024-09-03  
**当前版本**: v2.0 "忍者韭菜道场"  
**开发状态**: DCA策略专项联调中 🔥

## 🔗 相关链接

- [产品需求文档](PRD.md)
- [API文档](docs/api.md)
- [开发指南](docs/development.md)