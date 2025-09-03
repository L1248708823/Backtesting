# -*- coding: utf-8 -*-
"""
通用数据模型

定义项目中使用的通用数据类型、枚举和基础模型。

📚 学习点：
- Pydantic是FastAPI的数据验证库，类似Java的Bean Validation
- Enum用于定义固定选项，提供类型安全
- BaseModel是所有数据模型的基类，提供序列化和验证功能
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from pydantic import BaseModel, Field


# =============================================================================
# 基础枚举类型
# =============================================================================

class MarketType(str, Enum):
    """
    市场类型枚举
    
    📚 学习点：str, Enum多重继承让枚举值可以直接当字符串使用
    """
    A_STOCK = "a_stock"      # A股市场
    US_STOCK = "us_stock"    # 美股市场
    HK_STOCK = "hk_stock"    # 港股市场


class StrategyType(str, Enum):
    """策略类型枚举"""
    DCA = "dca"                    # 定投策略
    MOMENTUM = "momentum"          # 动量策略
    MEAN_REVERSION = "mean_reversion"  # 均值回归策略


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待中
    RUNNING = "running"      # 执行中
    SUCCESS = "success"      # 执行成功
    FAILED = "failed"        # 执行失败
    CANCELLED = "cancelled"  # 已取消


class ParameterType(str, Enum):
    """参数类型枚举"""
    STRING = "string"        # 字符串
    NUMBER = "number"        # 数字
    BOOLEAN = "boolean"      # 布尔值
    DATE = "date"           # 日期
    SELECT = "select"       # 选择项
    RANGE = "range"         # 数值范围


# =============================================================================
# 基础数据模型
# =============================================================================

class BaseResponse(BaseModel):
    """
    API响应基础模型
    
    📚 学习点：
    - Field()用于添加字段描述和验证规则
    - 所有API响应都应该继承这个基类，保证响应格式统一
    """
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    code: int = Field(200, description="响应状态码")


class DateRange(BaseModel):
    """日期范围模型"""
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    
    def model_post_init(self, __context) -> None:
        """
        📚 学习点：model_post_init是Pydantic v2的新特性
        在模型创建后自动调用，用于数据验证
        """
        if self.start_date >= self.end_date:
            raise ValueError("开始日期必须早于结束日期")


class ParameterOption(BaseModel):
    """参数选项模型（用于下拉选择等）"""
    value: str = Field(..., description="选项值")
    label: str = Field(..., description="选项显示文本")
    description: Optional[str] = Field(None, description="选项说明")


class ValidationRule(BaseModel):
    """参数验证规则模型"""
    min_value: Optional[float] = Field(None, description="最小值")
    max_value: Optional[float] = Field(None, description="最大值")
    min_length: Optional[int] = Field(None, description="最小长度")
    max_length: Optional[int] = Field(None, description="最大长度")
    pattern: Optional[str] = Field(None, description="正则表达式模式")
    required: bool = Field(True, description="是否必填")


# =============================================================================
# 量化指标相关模型
# =============================================================================

class PerformanceMetrics(BaseModel):
    """
    性能指标模型
    
    参考主流量化平台的标准指标体系
    """
    # 收益指标
    total_return: float = Field(..., description="总收益率")
    annual_return: float = Field(..., description="年化收益率")
    max_drawdown: float = Field(..., description="最大回撤")
    
    # 风险指标  
    sharpe_ratio: float = Field(..., description="夏普比率")
    sortino_ratio: Optional[float] = Field(None, description="索提诺比率")
    calmar_ratio: Optional[float] = Field(None, description="卡玛比率")
    volatility: float = Field(..., description="年化波动率")
    
    # 交易指标
    total_trades: int = Field(..., description="总交易次数")
    winning_trades: int = Field(..., description="盈利交易次数")
    losing_trades: int = Field(..., description="亏损交易次数")
    win_rate: float = Field(..., description="胜率")
    profit_factor: Optional[float] = Field(None, description="盈亏比")
    
    # 持仓指标
    max_positions: int = Field(..., description="最大持仓数量")
    avg_holding_period: Optional[float] = Field(None, description="平均持仓周期(天)")


class TimeSeriesPoint(BaseModel):
    """时间序列数据点模型"""
    trading_date: date = Field(..., description="日期")
    value: float = Field(..., description="数值")
    

class PriceData(BaseModel):
    """价格数据模型"""
    symbol: str = Field(..., description="标的代码")
    trading_date: date = Field(..., description="交易日期") 
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: int = Field(..., description="成交量")
    adj_close: Optional[float] = Field(None, description="复权收盘价")


# =============================================================================
# 工具函数
# =============================================================================

def create_error_response(message: str, code: int = 400) -> BaseResponse:
    """创建错误响应"""
    return BaseResponse(
        success=False,
        message=message,
        code=code
    )


def create_success_response(message: str = "操作成功", code: int = 200) -> BaseResponse:
    """创建成功响应"""
    return BaseResponse(
        success=True,
        message=message,
        code=code
    )


# 导出所有公共类型
__all__ = [
    # 枚举类型
    "MarketType", "StrategyType", "TaskStatus", "ParameterType",
    
    # 基础模型
    "BaseResponse", "DateRange", "ParameterOption", "ValidationRule",
    
    # 量化指标模型
    "PerformanceMetrics", "TimeSeriesPoint", "PriceData",
    
    # 工具函数
    "create_error_response", "create_success_response"
]