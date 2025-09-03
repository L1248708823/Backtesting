# -*- coding: utf-8 -*-
"""
回测相关数据模型

定义回测配置、任务状态、结果等相关的数据模型。

📚 学习点：
- 异步任务模式：回测任务的生命周期管理
- 状态机设计：任务状态的转换和追踪  
- 结果数据结构：复杂回测结果的结构化存储
"""

from typing import List, Dict, Optional, Any, Union
from datetime import date, datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel, Field
from .common import (
    TaskStatus, PerformanceMetrics, TimeSeriesPoint, 
    DateRange, PriceData, BaseResponse
)
from .strategy import StrategyParameters


# =============================================================================
# 回测配置相关模型  
# =============================================================================

class TradingCosts(BaseModel):
    """
    交易成本配置模型
    
    📚 学习点：
    - Decimal用于精确的金融计算，避免浮点数精度问题
    - 交易成本是回测准确性的关键因素
    """
    commission_rate: Decimal = Field(Decimal("0.0003"), description="佣金费率（万分之3）")
    min_commission: Decimal = Field(Decimal("5.0"), description="最低佣金（元）")
    stamp_duty_rate: Decimal = Field(Decimal("0.001"), description="印花税费率（千分之1，卖出时）")  
    transfer_fee_rate: Decimal = Field(Decimal("0.00002"), description="过户费费率（万分之0.2）")
    slippage_rate: Decimal = Field(Decimal("0.001"), description="滑点费率（千分之1）")


class BacktestConfig(BaseModel):
    """
    回测配置模型
    
    📚 学习点：
    - 这是启动回测任务的完整配置
    - 包含策略配置、时间范围、资金设置、交易成本等
    """
    # 策略配置
    strategy_parameters: StrategyParameters = Field(..., description="策略参数配置")
    
    # 时间配置
    date_range: DateRange = Field(..., description="回测时间范围")
    
    # 资金配置
    initial_capital: Decimal = Field(..., description="初始资金（元）")
    
    # 交易成本配置
    trading_costs: TradingCosts = Field(default_factory=TradingCosts, description="交易成本配置")
    
    # 基准比较（可选）
    benchmark_symbol: Optional[str] = Field(None, description="基准标的代码")
    
    # 回测选项
    enable_slippage: bool = Field(True, description="是否启用滑点")
    enable_commission: bool = Field(True, description="是否启用手续费")
    
    # 风控配置
    max_position_size: Optional[Decimal] = Field(None, description="最大单一持仓比例")
    stop_loss_pct: Optional[Decimal] = Field(None, description="止损百分比")


# =============================================================================
# 回测任务相关模型
# =============================================================================

class BacktestTask(BaseModel):
    """
    回测任务模型
    
    📚 学习点：
    - UUID作为任务唯一标识
    - 状态机管理任务生命周期
    - 异步执行模式的核心数据结构
    """
    task_id: str = Field(..., description="任务唯一标识符")
    status: TaskStatus = Field(TaskStatus.PENDING, description="任务状态")
    
    # 配置信息
    config: BacktestConfig = Field(..., description="回测配置")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="任务创建时间")
    started_at: Optional[datetime] = Field(None, description="任务开始时间")
    completed_at: Optional[datetime] = Field(None, description="任务完成时间")
    
    # 执行信息
    progress: float = Field(0.0, description="执行进度（0.0-1.0）")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    # 结果存储
    result: Optional['BacktestResult'] = Field(None, description="回测结果")
    
    @property
    def duration(self) -> Optional[timedelta]:
        """计算任务执行时长"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property  
    def is_running(self) -> bool:
        """任务是否正在运行"""
        return self.status == TaskStatus.RUNNING
    
    @property
    def is_completed(self) -> bool:
        """任务是否已完成（成功或失败）"""
        return self.status in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED]


# =============================================================================
# 交易记录相关模型
# =============================================================================

class Transaction(BaseModel):
    """
    交易记录模型
    
    📚 学习点：
    - 完整记录每笔交易的所有信息
    - 用于后续的交易分析和验证
    """
    # 基本信息
    trading_date: date = Field(..., description="交易日期")
    symbol: str = Field(..., description="交易标的")
    action: str = Field(..., description="交易动作：buy/sell")
    
    # 数量和价格
    quantity: Decimal = Field(..., description="交易数量")
    price: Decimal = Field(..., description="交易价格")
    
    # 金额和费用
    gross_amount: Decimal = Field(..., description="交易总额（未扣费用）")
    commission: Decimal = Field(..., description="佣金费用")
    stamp_duty: Decimal = Field(..., description="印花税") 
    transfer_fee: Decimal = Field(..., description="过户费")
    total_cost: Decimal = Field(..., description="总费用")
    net_amount: Decimal = Field(..., description="净交易额（扣除费用）")
    
    # 策略信息
    strategy_signal: Optional[str] = Field(None, description="策略信号描述")
    extra_data: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")


class Position(BaseModel):
    """
    持仓记录模型
    
    📚 学习点：
    - 跟踪每个时间点的持仓状态
    - 用于计算持仓收益和风险指标
    """
    symbol: str = Field(..., description="标的代码")
    quantity: Decimal = Field(..., description="持仓数量") 
    avg_cost: Decimal = Field(..., description="持仓平均成本")
    market_value: Decimal = Field(..., description="持仓市值")
    unrealized_pnl: Decimal = Field(..., description="未实现盈亏")
    weight: float = Field(..., description="持仓权重")


class PortfolioSnapshot(BaseModel):
    """
    组合快照模型（某个时间点的组合状态）
    """
    snapshot_date: date = Field(..., description="快照日期")
    cash: Decimal = Field(..., description="现金余额")
    total_value: Decimal = Field(..., description="组合总价值")
    positions: List[Position] = Field(default_factory=list, description="持仓列表")


# =============================================================================
# 回测结果相关模型
# =============================================================================

class BacktestResult(BaseModel):
    """
    回测结果模型
    
    📚 学习点：
    - 完整的回测结果数据结构
    - 包含性能指标、交易记录、时间序列等所有信息
    - 前端可以根据这个结果生成各种图表和报告
    """
    # 基本信息
    task_id: str = Field(..., description="关联的任务ID")
    strategy_name: str = Field(..., description="策略名称")
    
    # 配置信息（用于结果展示）
    config_summary: Dict[str, Any] = Field(..., description="配置摘要")
    
    # 时间信息
    start_date: date = Field(..., description="回测开始日期")
    end_date: date = Field(..., description="回测结束日期")
    total_days: int = Field(..., description="回测总天数")
    trading_days: int = Field(..., description="实际交易天数")
    
    # 资金信息
    initial_capital: Decimal = Field(..., description="初始资金")
    final_capital: Decimal = Field(..., description="最终资金")
    final_cash: Decimal = Field(..., description="最终现金")
    final_positions: List[Position] = Field(default_factory=list, description="最终持仓")
    
    # 性能指标
    performance_metrics: PerformanceMetrics = Field(..., description="性能指标")
    
    # 时间序列数据（用于绘制图表）
    equity_curve: List[TimeSeriesPoint] = Field(default_factory=list, description="权益曲线")
    drawdown_curve: List[TimeSeriesPoint] = Field(default_factory=list, description="回撤曲线")
    
    # 基准对比（如果有）
    benchmark_curve: Optional[List[TimeSeriesPoint]] = Field(None, description="基准曲线")
    
    # 交易记录
    transactions: List[Transaction] = Field(default_factory=list, description="所有交易记录")
    
    # 组合快照（可选，用于详细分析）
    portfolio_snapshots: Optional[List[PortfolioSnapshot]] = Field(None, description="组合快照序列")
    
    # 其他分析数据
    monthly_returns: Optional[List[TimeSeriesPoint]] = Field(None, description="月度收益")
    yearly_returns: Optional[List[TimeSeriesPoint]] = Field(None, description="年度收益")
    
    @property
    def total_return_pct(self) -> float:
        """总收益率百分比"""
        if self.initial_capital > 0:
            return float((self.final_capital - self.initial_capital) / self.initial_capital * 100)
        return 0.0


# =============================================================================
# API响应模型
# =============================================================================

class BacktestTaskResponse(BaseResponse):
    """启动回测任务的响应"""
    data: Dict[str, Any] = Field(..., description="响应数据")
    
    @classmethod
    def create_success(cls, task_id: str, message: str = "回测任务已启动"):
        return cls(
            success=True,
            message=message,
            data={"task_id": task_id, "status": TaskStatus.PENDING}
        )


class BacktestStatusResponse(BaseResponse):
    """查询回测状态的响应"""
    data: Dict[str, Any] = Field(..., description="任务状态数据")
    
    @classmethod
    def create_from_task(cls, task: BacktestTask):
        return cls(
            success=True,
            message="状态查询成功",
            data={
                "task_id": task.task_id,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error_message": task.error_message
            }
        )


class BacktestResultResponse(BaseResponse):
    """获取回测结果的响应"""
    data: Optional[BacktestResult] = Field(None, description="回测结果")
    
    @classmethod
    def create_success(cls, result: BacktestResult):
        return cls(
            success=True,
            message="回测结果获取成功",
            data=result
        )
        
    @classmethod
    def create_not_ready(cls, status: TaskStatus):
        return cls(
            success=False,
            message=f"回测尚未完成，当前状态：{status.value}",
            data=None
        )


# 导出所有回测相关类型
__all__ = [
    # 配置相关
    "TradingCosts", "BacktestConfig",
    
    # 任务相关  
    "BacktestTask",
    
    # 交易和持仓
    "Transaction", "Position", "PortfolioSnapshot",
    
    # 结果相关
    "BacktestResult", 
    
    # API响应
    "BacktestTaskResponse", "BacktestStatusResponse", "BacktestResultResponse"
]