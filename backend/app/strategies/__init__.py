# -*- coding: utf-8 -*-
"""
策略实现模块

基于Backtrader框架的量化交易策略实现。
"""

from .base import BaseStrategy
from .dca_strategy import DCAStrategy

# 导入策略会自动注册到registry
__all__ = ["BaseStrategy", "DCAStrategy"]