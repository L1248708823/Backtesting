# -*- coding: utf-8 -*-
"""
策略模块初始化文件

负责导入所有策略实现，确保策略自动注册到工厂类。
重构后的导入结构：
- 数据模型从 app.models 导入
- 业务逻辑从 .base 导入
- 具体策略实现自动导入和注册
"""

# 导入基础设施
from .base import BaseStrategy, StrategyFactory, register_strategy

# 从models模块导入数据模型（保持向后兼容）
from app.models import (
    ParameterDefinition,
    StrategyMetadata,
    TradeSignal,
    StrategyContext
)
from app.models.common import ParameterType

# 导入所有策略实现（这样会触发自动注册）
from .dca_strategy import DCAStrategy

# 导出主要接口
__all__ = [
    # 基础设施
    'BaseStrategy',
    'StrategyFactory', 
    'register_strategy',
    
    # 数据模型
    'StrategyMetadata',
    'ParameterDefinition',
    'ParameterType',
    'TradeSignal',
    'StrategyContext',
    
    # 具体策略
    'DCAStrategy'
]