# -*- coding: utf-8 -*-
"""
策略相关数据模型

定义策略系统中的所有核心数据结构，包括：
- 策略元数据：策略的基本信息和配置
- 参数定义：策略参数的类型、验证规则等
- 交易信号：策略生成的买卖信号
- 执行上下文：策略运行时的环境信息
"""

from datetime import datetime, date
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import pandas as pd

from .common import ParameterType


class ParameterDefinition(BaseModel):
    """
    策略参数定义模型
    
    定义单个策略参数的所有属性，支持：
    - 类型验证：基于type字段进行数据类型检查
    - 值域限制：通过min_value、max_value限制数字范围
    - 选项约束：通过options限制可选值
    - UI生成：前端根据此定义自动生成参数输入界面
    """
    name: str = Field(..., description="参数名称，用作参数的唯一标识符")
    type: ParameterType = Field(..., description="参数数据类型")
    default: Any = Field(..., description="参数默认值，新建策略时的初始值")
    description: str = Field(..., description="参数说明，向用户解释此参数的作用")
    required: bool = Field(default=True, description="是否为必填参数")
    
    # 选项约束（用于SELECT和MULTI_SELECT类型）
    options: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="可选项列表，格式：[{'value': 'key', 'label': 'display_name'}]"
    )
    
    # 数值约束（用于NUMBER类型）
    min_value: Optional[float] = Field(
        default=None,
        description="数值参数的最小值限制"
    )
    max_value: Optional[float] = Field(
        default=None,
        description="数值参数的最大值限制"
    )
    
    # 自定义验证（高级功能，暂未实现）
    validation_rule: Optional[str] = Field(
        default=None,
        description="自定义验证规则表达式（预留功能）"
    )
    
    # 扩展字段
    validation_rules: Optional[Dict[str, Any]] = Field(
        default=None,
        description="验证规则字典，支持复杂验证逻辑"
    )
    
    depends_on: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="参数依赖关系，格式：[{'parameter': 'param_name', 'values': [...]}]"
    )

    class Config:
        """Pydantic模型配置"""
        schema_extra = {
            "example": {
                "name": "investment_amount",
                "type": "number",
                "default": 1000.0,
                "description": "每期投资金额（元）",
                "required": True,
                "min_value": 100.0,
                "max_value": 1000000.0
            }
        }


class StrategyMetadata(BaseModel):
    """
    策略元数据模型
    
    包含策略的基本信息和分类属性，用于：
    - 策略展示：在UI中显示策略列表和详情
    - 策略管理：根据分类和风险等级进行筛选
    - 版本控制：跟踪策略的版本变化
    """
    id: str = Field(..., description="策略唯一标识符，用于API调用和内部引用")
    name: str = Field(..., description="策略显示名称")
    description: str = Field(..., description="策略详细说明，解释策略的投资逻辑和适用场景")
    category: str = Field(..., description="策略分类，如：定投类、轮动类、量化类等")
    risk_level: str = Field(..., description="风险等级：低、中、高")
    supported_markets: List[str] = Field(
        ..., 
        description="支持的市场列表，如：['A股', '美股', '港股']"
    )
    author: str = Field(default="系统内置", description="策略作者")
    version: str = Field(default="1.0.0", description="策略版本号")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="策略创建时间"
    )

    class Config:
        """Pydantic模型配置"""
        schema_extra = {
            "example": {
                "id": "dca_strategy",
                "name": "定投策略",
                "description": "定期定额投资策略，通过分散投资时间降低市场波动风险",
                "category": "定投类",
                "risk_level": "低",
                "supported_markets": ["A股", "美股"],
                "author": "系统内置",
                "version": "1.0.0"
            }
        }


class TradeSignal(BaseModel):
    """
    交易信号模型
    
    策略生成的具体交易指令，包含：
    - 交易标的：要买卖的资产代码
    - 交易动作：买入、卖出或持有
    - 交易数量：具体的买卖数量或权重比例
    - 执行价格：市价或限价
    """
    symbol: str = Field(..., description="交易标的代码，如：510300（沪深300ETF）")
    action: str = Field(..., description="交易动作：buy（买入）、sell（卖出）、hold（持有）")
    quantity: float = Field(
        default=0, 
        description="交易数量，0表示按权重比例计算"
    )
    weight: float = Field(
        default=0, 
        description="权重比例，0-1之间的小数，表示占组合的百分比"
    )
    price: Optional[float] = Field(
        default=None, 
        description="指定成交价格，None表示市价成交"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="信号生成时间"
    )
    reason: str = Field(default="", description="生成此交易信号的原因说明")

    class Config:
        """Pydantic模型配置"""
        schema_extra = {
            "example": {
                "symbol": "510300",
                "action": "buy", 
                "quantity": 0,
                "weight": 0.1,
                "price": None,
                "reason": "定投策略：月度定投1000元"
            }
        }


class StrategyContext(BaseModel):
    """
    策略执行上下文模型
    
    提供策略运行时所需的所有环境信息：
    - 时间信息：当前回测日期
    - 资金信息：当前组合价值和现金余额
    - 持仓信息：各资产的持仓数量
    - 市场数据：用于策略计算的历史价格数据
    """
    current_date: date = Field(..., description="当前回测日期")
    portfolio_value: float = Field(..., description="当前组合总价值（元）")
    cash: float = Field(..., description="当前可用现金（元）")
    positions: Dict[str, float] = Field(
        ..., 
        description="当前持仓字典，key为资产代码，value为持仓数量"
    )
    market_data: Optional[pd.DataFrame] = Field(
        default=None,
        description="市场数据DataFrame，包含历史价格信息"
    )
    
    class Config:
        """Pydantic模型配置"""
        # 允许任意类型（DataFrame不是标准JSON类型）
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "current_date": "2024-01-15",
                "portfolio_value": 10000.0,
                "cash": 5000.0,
                "positions": {
                    "510300": 100,
                    "510500": 50
                }
            }
        }