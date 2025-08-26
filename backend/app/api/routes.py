from fastapi import APIRouter
from .strategies import router as strategies_router
from .backtest import router as backtest_router
from .data import router as data_router

# 创建主路由
router = APIRouter()

# 注册子路由
router.include_router(strategies_router, prefix="/strategies", tags=["strategies"])
router.include_router(backtest_router, prefix="/backtest", tags=["backtest"])
router.include_router(data_router, prefix="/data", tags=["data"])

@router.get("/")
async def api_info():
    return {
        "message": "量化回测系统 API v1",
        "endpoints": {
            "strategies": "策略管理API",
            "backtest": "回测执行API", 
            "data": "数据管理API"
        }
    }