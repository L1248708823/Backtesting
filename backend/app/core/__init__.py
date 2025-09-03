# -*- coding: utf-8 -*-
"""
核心业务逻辑模块

包含策略注册管理器等核心组件。
"""

from .strategy_registry import registry, StrategyRegistry

__all__ = ["registry", "StrategyRegistry"]