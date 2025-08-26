# -*- coding: utf-8 -*-
"""
API模式定义

定义所有API接口的请求和响应模式，包括：
- 请求模型：客户端发送给API的数据结构
- 响应模型：API返回给客户端的数据结构
- 验证规则：数据合法性检查规则
"""

from .strategy import StrategyRequestSchemas, StrategyResponseSchemas

__all__ = [
    'StrategyRequestSchemas',
    'StrategyResponseSchemas'
]