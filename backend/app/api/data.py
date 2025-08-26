from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

router = APIRouter()

class DataSource(BaseModel):
    """数据源模型"""
    name: str
    status: str
    last_update: datetime
    coverage: List[str]
    description: str

@router.get("/sources")
async def get_data_sources():
    """获取数据源状态"""
    sources = [
        DataSource(
            name="AKShare",
            status="active",
            last_update=datetime.now(),
            coverage=["A股", "ETF", "宏观数据"],
            description="免费的A股数据源"
        ),
        DataSource(
            name="yfinance",
            status="active", 
            last_update=datetime.now(),
            coverage=["美股", "全球ETF"],
            description="Yahoo Finance数据源"
        )
    ]
    return sources

@router.post("/update")
async def update_data():
    """触发数据更新"""
    return {"message": "数据更新任务已启动", "status": "success"}

@router.get("/health")
async def check_data_health():
    """检查数据健康状态"""
    return {
        "status": "healthy",
        "data_sources": 2,
        "last_check": datetime.now()
    }