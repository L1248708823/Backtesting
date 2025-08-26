from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

router = APIRouter()

class BacktestConfig(BaseModel):
    """回测配置模型"""
    strategy_id: str
    parameters: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000.0
    commission: float = 0.0003  # 手续费率
    slippage: float = 0.001     # 滑点

class BacktestStatus(BaseModel):
    """回测状态模型"""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None

class BacktestResult(BaseModel):
    """回测结果模型"""
    task_id: str
    strategy_id: str
    config: BacktestConfig
    results: Dict[str, Any]
    performance_metrics: Dict[str, float]
    created_at: datetime

# 内存中存储回测任务（生产环境应使用数据库）
backtest_tasks: Dict[str, BacktestStatus] = {}
backtest_results: Dict[str, BacktestResult] = {}

@router.post("/start")
async def start_backtest(config: BacktestConfig, background_tasks: BackgroundTasks):
    """启动回测任务"""
    task_id = str(uuid.uuid4())
    
    # 创建任务状态
    task_status = BacktestStatus(
        task_id=task_id,
        status="pending",
        progress=0,
        message="回测任务已创建，等待执行",
        created_at=datetime.now()
    )
    backtest_tasks[task_id] = task_status
    
    # 添加后台任务
    background_tasks.add_task(run_backtest, task_id, config)
    
    return {"task_id": task_id, "message": "回测任务已启动"}

@router.get("/status/{task_id}")
async def get_backtest_status(task_id: str):
    """获取回测任务状态"""
    if task_id not in backtest_tasks:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="任务未找到")
    
    return backtest_tasks[task_id]

@router.get("/result/{task_id}")
async def get_backtest_result(task_id: str):
    """获取回测结果"""
    if task_id not in backtest_results:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="回测结果未找到")
    
    return backtest_results[task_id]

async def run_backtest(task_id: str, config: BacktestConfig):
    """执行回测（后台任务）"""
    import time
    import random
    
    try:
        # 更新状态为运行中
        backtest_tasks[task_id].status = "running"
        backtest_tasks[task_id].message = "正在执行回测..."
        
        # 模拟回测过程
        for i in range(5):
            time.sleep(1)  # 模拟处理时间
            progress = (i + 1) * 20
            backtest_tasks[task_id].progress = progress
            backtest_tasks[task_id].message = f"回测进行中... {progress}%"
        
        # 模拟回测结果
        mock_result = {
            "total_return": round(random.uniform(0.05, 0.25), 4),
            "annual_return": round(random.uniform(0.08, 0.15), 4),
            "max_drawdown": round(random.uniform(0.05, 0.20), 4),
            "sharpe_ratio": round(random.uniform(1.0, 2.5), 2),
            "win_rate": round(random.uniform(0.45, 0.65), 2),
            "trades_count": random.randint(50, 200)
        }
        
        # 保存结果
        result = BacktestResult(
            task_id=task_id,
            strategy_id=config.strategy_id,
            config=config,
            results={"equity_curve": [], "trades": []},  # 实际应包含详细数据
            performance_metrics=mock_result,
            created_at=datetime.now()
        )
        backtest_results[task_id] = result
        
        # 更新状态为完成
        backtest_tasks[task_id].status = "completed"
        backtest_tasks[task_id].progress = 100
        backtest_tasks[task_id].message = "回测完成"
        backtest_tasks[task_id].completed_at = datetime.now()
        
    except Exception as e:
        # 更新状态为失败
        backtest_tasks[task_id].status = "failed"
        backtest_tasks[task_id].message = f"回测失败: {str(e)}"