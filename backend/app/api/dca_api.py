# -*- coding: utf-8 -*-
"""
定投策略专用API端点

为定投策略提供专门优化的API接口，包括：
1. 定投回测执行和管理
2. 参数验证和配置
3. 实时进度跟踪
4. 结果展示和导出

设计特点：
- 专门针对定投策略优化
- 集成DCAStrategy和SimpleBacktestEngine
- 提供详细的进度反馈
- 支持结果缓存和管理
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid
import asyncio
import logging

# 导入自定义模块
from app.strategies.dca_strategy import DCAStrategy
from app.core.backtest_engine import SimpleBacktestEngine, BacktestConfig as EngineConfig
from app.services.data_provider import create_data_provider

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dca", tags=["定投策略"])


class DCABacktestConfig(BaseModel):
    """定投回测配置模型"""
    # 基础配置
    symbol: str = Field(..., description="投资标的代码", example="510300")
    investment_amount: float = Field(..., ge=100, le=1000000, description="每期投资金额（元）")
    frequency: str = Field(..., description="投资频率", example="monthly")
    
    # 时间配置
    start_date: date = Field(..., description="回测开始日期")
    end_date: date = Field(..., description="回测结束日期")
    initial_capital: float = Field(100000.0, ge=1000, description="初始资金（元）")
    
    # 可选配置
    investment_day: Optional[int] = Field(1, ge=1, le=28, description="每月投资日期")
    skip_holidays: bool = Field(True, description="是否跳过节假日")
    max_single_weight: float = Field(0.1, ge=0.01, le=0.5, description="单次投资最大占组合比例")
    enable_cost_control: bool = Field(True, description="是否启用成本控制")
    min_cost_ratio: float = Field(0.01, ge=0.001, le=0.05, description="最小成本效益比")
    
    # 交易成本配置
    commission_rate: float = Field(0.0003, ge=0, le=0.01, description="佣金费率")
    min_commission: float = Field(5.0, ge=0, description="最小佣金（元）")
    stamp_duty_rate: float = Field(0.001, ge=0, description="印花税费率")
    transfer_fee_rate: float = Field(0.00002, ge=0, description="过户费费率")


class DCABacktestStatus(BaseModel):
    """定投回测状态模型"""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float = Field(0.0, ge=0.0, le=1.0, description="进度(0-1)")
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class DCABacktestResult(BaseModel):
    """定投回测结果模型"""
    task_id: str
    config: DCABacktestConfig
    status: str
    
    # 基础结果
    initial_capital: float
    final_capital: float
    final_cash: float
    final_market_value: float
    
    # 收益指标
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    
    # 交易统计
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # 定投特定指标
    investment_count: int
    skipped_count: int
    average_cost: float
    total_invested: float
    
    # 时间信息
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # 详细数据（可选，用于图表展示）
    equity_curve: Optional[List[Dict[str, Any]]] = None
    transactions: Optional[List[Dict[str, Any]]] = None


# 内存中存储回测任务（生产环境应使用Redis等）
dca_tasks: Dict[str, DCABacktestStatus] = {}
dca_results: Dict[str, DCABacktestResult] = {}


@router.post("/backtest/start", response_model=Dict[str, str])
async def start_dca_backtest(config: DCABacktestConfig, background_tasks: BackgroundTasks):
    """启动定投策略回测"""
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 参数验证
        _validate_dca_config(config)
        
        # 创建任务状态
        task_status = DCABacktestStatus(
            task_id=task_id,
            status="pending",
            progress=0.0,
            message="定投回测任务已创建，正在准备执行...",
            created_at=datetime.now()
        )
        dca_tasks[task_id] = task_status
        
        # 添加后台任务
        background_tasks.add_task(execute_dca_backtest, task_id, config)
        
        logger.info(f"定投回测任务已启动: {task_id}, 标的: {config.symbol}")
        
        return {
            "task_id": task_id, 
            "message": "定投回测任务已启动",
            "status": "pending"
        }
        
    except Exception as e:
        logger.error(f"启动定投回测任务失败: {str(e)}")
        raise HTTPException(status_code=400, detail=f"启动回测失败: {str(e)}")


@router.get("/backtest/status/{task_id}", response_model=DCABacktestStatus)
async def get_dca_backtest_status(task_id: str):
    """获取定投回测任务状态"""
    if task_id not in dca_tasks:
        raise HTTPException(status_code=404, detail="定投回测任务未找到")
    
    return dca_tasks[task_id]


@router.get("/backtest/result/{task_id}", response_model=DCABacktestResult)
async def get_dca_backtest_result(task_id: str, include_details: bool = Query(False, description="是否包含详细数据")):
    """获取定投回测结果"""
    if task_id not in dca_results:
        raise HTTPException(status_code=404, detail="定投回测结果未找到")
    
    result = dca_results[task_id]
    
    # 如果不需要详细数据，清除大数据字段
    if not include_details:
        result_copy = result.model_copy()
        result_copy.equity_curve = None
        result_copy.transactions = None
        return result_copy
    
    return result


@router.get("/backtest/list", response_model=List[DCABacktestStatus])
async def list_dca_backtests(status: Optional[str] = Query(None, description="按状态过滤")):
    """获取定投回测任务列表"""
    tasks = list(dca_tasks.values())
    
    if status:
        tasks = [task for task in tasks if task.status == status]
    
    # 按创建时间倒序排序
    tasks.sort(key=lambda x: x.created_at, reverse=True)
    
    return tasks


@router.delete("/backtest/{task_id}")
async def delete_dca_backtest(task_id: str):
    """删除定投回测任务和结果"""
    deleted_items = []
    
    if task_id in dca_tasks:
        del dca_tasks[task_id]
        deleted_items.append("task")
    
    if task_id in dca_results:
        del dca_results[task_id]
        deleted_items.append("result")
    
    if not deleted_items:
        raise HTTPException(status_code=404, detail="任务未找到")
    
    return {"message": f"已删除: {', '.join(deleted_items)}", "task_id": task_id}


@router.get("/parameters", response_model=List[Dict[str, Any]])
async def get_dca_parameters():
    """获取定投策略参数定义"""
    try:
        # 获取策略参数定义
        param_definitions = DCAStrategy.get_parameter_definitions()
        
        # 转换为API友好的格式
        parameters = []
        for param in param_definitions:
            param_dict = {
                "name": param.name,
                "type": param.type.value,
                "default": param.default,
                "description": param.description,
                "required": param.required,
                "min_value": param.min_value,
                "max_value": param.max_value,
                "options": param.options,
                "validation_rules": param.validation_rules,
                "depends_on": param.depends_on
            }
            parameters.append(param_dict)
        
        return parameters
        
    except Exception as e:
        logger.error(f"获取参数定义失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取参数定义失败")


@router.get("/validate-symbol/{symbol}")
async def validate_dca_symbol(symbol: str):
    """验证投资标的是否有效"""
    try:
        # 创建数据提供者
        data_provider = create_data_provider()
        
        # 验证标的
        is_valid = data_provider.validate_symbol(symbol)
        
        result = {
            "symbol": symbol,
            "is_valid": is_valid,
            "message": "标的有效" if is_valid else "标的无效或暂无数据"
        }
        
        # 如果有效，尝试获取最新价格
        if is_valid:
            latest_price = data_provider.get_latest_price(symbol)
            if latest_price:
                result["latest_date"] = latest_price[0].isoformat()
                result["latest_price"] = float(latest_price[1])
        
        return result
        
    except Exception as e:
        logger.error(f"验证标的失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"验证标的失败: {str(e)}")


def _validate_dca_config(config: DCABacktestConfig):
    """验证定投回测配置"""
    # 时间范围验证
    if config.start_date >= config.end_date:
        raise ValueError("开始日期必须早于结束日期")
    
    # 投资期间长度检查
    days_diff = (config.end_date - config.start_date).days
    if days_diff < 30:
        raise ValueError("投资期间至少需要30天")
    
    # 频率和投资日期的匹配验证
    if config.frequency in ["monthly", "quarterly"] and config.investment_day is None:
        raise ValueError("月度或季度投资需要指定投资日期")
    
    # 资金配置验证
    if config.investment_amount > config.initial_capital * 0.5:
        raise ValueError("单次投资金额不能超过初始资金的50%")


async def execute_dca_backtest(task_id: str, config: DCABacktestConfig):
    """执行定投回测（后台任务）"""
    try:
        # 更新状态
        dca_tasks[task_id].status = "running"
        dca_tasks[task_id].message = "正在初始化定投策略..."
        dca_tasks[task_id].progress = 0.1
        
        # 1. 创建策略实例
        strategy_params = {
            "symbol": config.symbol,
            "investment_amount": config.investment_amount,
            "frequency": config.frequency,
            "investment_day": config.investment_day,
            "skip_holidays": config.skip_holidays,
            "max_single_weight": config.max_single_weight,
            "enable_cost_control": config.enable_cost_control,
            "min_cost_ratio": config.min_cost_ratio
        }
        
        strategy = DCAStrategy(strategy_params)
        
        # 更新进度
        dca_tasks[task_id].message = "正在获取价格数据..."
        dca_tasks[task_id].progress = 0.2
        
        # 2. 获取价格数据
        data_provider = create_data_provider()
        price_data = data_provider.get_price_data(
            config.symbol, 
            config.start_date, 
            config.end_date
        )
        
        if not price_data:
            raise ValueError(f"无法获取{config.symbol}的价格数据")
        
        # 更新进度
        dca_tasks[task_id].message = "正在配置回测引擎..."
        dca_tasks[task_id].progress = 0.3
        
        # 3. 配置回测引擎
        engine_config = EngineConfig(
            strategy_id="dca_strategy",
            strategy_params=strategy_params,
            start_date=config.start_date,
            end_date=config.end_date,
            initial_capital=Decimal(str(config.initial_capital)),
            commission_rate=Decimal(str(config.commission_rate)),
            min_commission=Decimal(str(config.min_commission)),
            stamp_duty_rate=Decimal(str(config.stamp_duty_rate)),
            transfer_fee_rate=Decimal(str(config.transfer_fee_rate))
        )
        
        # 4. 执行回测
        engine = SimpleBacktestEngine()
        
        def progress_callback(progress: float):
            """回测进度回调"""
            dca_tasks[task_id].progress = 0.3 + (progress * 0.6)  # 30%-90%
            dca_tasks[task_id].message = f"正在执行回测... {progress*100:.1f}%"
        
        dca_tasks[task_id].message = "开始执行回测..."
        dca_tasks[task_id].progress = 0.4
        
        # 转换价格数据格式
        formatted_price_data = {config.symbol: price_data}
        
        # 执行回测
        backtest_result = engine.run_backtest(
            config=engine_config,
            strategy=strategy,
            price_data=formatted_price_data,
            progress_callback=progress_callback
        )
        
        # 更新进度
        dca_tasks[task_id].message = "正在处理回测结果..."
        dca_tasks[task_id].progress = 0.95
        
        # 5. 处理结果
        strategy_metrics = strategy.get_performance_metrics()
        
        # 创建结果对象
        result = DCABacktestResult(
            task_id=task_id,
            config=config,
            status="completed",
            
            # 基础结果
            initial_capital=float(backtest_result.initial_capital),
            final_capital=float(backtest_result.final_capital),
            final_cash=float(backtest_result.final_cash),
            final_market_value=float(backtest_result.final_market_value),
            
            # 收益指标
            total_return=float(backtest_result.total_return),
            annualized_return=float(backtest_result.annualized_return),
            max_drawdown=float(backtest_result.max_drawdown),
            sharpe_ratio=float(backtest_result.sharpe_ratio),
            
            # 交易统计
            total_trades=backtest_result.total_trades,
            winning_trades=backtest_result.winning_trades,
            losing_trades=backtest_result.losing_trades,
            win_rate=float(backtest_result.win_rate),
            
            # 定投特定指标
            investment_count=strategy_metrics["investment_count"],
            skipped_count=strategy_metrics["skipped_count"],
            average_cost=strategy_metrics["average_investment"],
            total_invested=strategy_metrics["total_invested"],
            
            created_at=backtest_result.start_time,
            completed_at=datetime.now(),
            
            # 详细数据
            equity_curve=[
                {"date": d.isoformat(), "value": float(v)} 
                for d, v in backtest_result.daily_values
            ],
            transactions=[
                {
                    "date": t.date.isoformat(),
                    "symbol": t.symbol,
                    "action": t.action,
                    "quantity": float(t.quantity),
                    "price": float(t.price),
                    "amount": float(t.amount),
                    "commission": float(t.commission),
                    "total_cost": float(t.total_cost),
                    "reason": t.reason
                }
                for t in backtest_result.transactions
            ]
        )
        
        # 保存结果
        dca_results[task_id] = result
        
        # 更新任务状态为完成
        dca_tasks[task_id].status = "completed"
        dca_tasks[task_id].progress = 1.0
        dca_tasks[task_id].message = "定投回测完成"
        dca_tasks[task_id].completed_at = datetime.now()
        
        logger.info(f"定投回测任务完成: {task_id}, 总收益率: {result.total_return:.4f}")
        
    except Exception as e:
        error_msg = f"定投回测执行失败: {str(e)}"
        logger.error(f"任务 {task_id} 执行失败: {str(e)}")
        
        # 更新任务状态为失败
        dca_tasks[task_id].status = "failed"
        dca_tasks[task_id].message = error_msg
        dca_tasks[task_id].error_message = str(e)
        dca_tasks[task_id].completed_at = datetime.now()