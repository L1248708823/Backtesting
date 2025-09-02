# -*- coding: utf-8 -*-
"""
量化回测系统 - 极简版本
基于 Backtrader 专业回测框架重新设计

架构原则：
- 极简至上：删除所有过度抽象
- Backtrader优先：使用专业框架的最佳实践
- 直接有效：最少的代码实现最核心的功能
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="量化回测系统",
    description="基于Backtrader的个人量化回测平台",
    version="2.0.0"  # 重构版本
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """系统状态检查"""
    return {
        "message": "量化回测系统 v2.0 - 基于Backtrader重构版本",
        "status": "running",
        "version": "2.0.0",
        "framework": "FastAPI + Backtrader"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)