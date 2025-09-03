# -*- coding: utf-8 -*-
"""
策略注册管理器

负责策略的注册、发现和管理。
"""

from typing import Dict, List, Type, Optional
from ..strategies.base import BaseStrategy
from ..models.strategy import StrategyMetadata, StrategyInfo


class StrategyRegistry:
    """
    策略注册管理器
    
    📚 学习点：
    - 单例模式管理全局策略注册表
    - 自动策略发现和元数据管理
    - 提供策略列表和详情查询接口
    """
    
    _instance = None
    _strategies: Dict[str, Type[BaseStrategy]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_strategy(self, strategy_class: Type[BaseStrategy]) -> None:
        """
        注册策略
        
        Args:
            strategy_class: 策略类
        """
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError(f"{strategy_class.__name__} 必须继承自 BaseStrategy")
            
        metadata = strategy_class.get_metadata()
        strategy_id = metadata.id
        
        if strategy_id in self._strategies:
            print(f"警告: 策略 {strategy_id} 已存在，将被覆盖")
            
        self._strategies[strategy_id] = strategy_class
        print(f"策略已注册: {metadata.name} ({strategy_id})")
    
    def get_strategy(self, strategy_id: str) -> Optional[Type[BaseStrategy]]:
        """
        获取策略类
        
        Args:
            strategy_id: 策略ID
            
        Returns:
            策略类或None
        """
        return self._strategies.get(strategy_id)
    
    def get_all_strategies(self) -> Dict[str, Type[BaseStrategy]]:
        """获取所有注册的策略"""
        return self._strategies.copy()
    
    def list_strategies(self) -> List[StrategyInfo]:
        """
        获取策略信息列表
        
        Returns:
            策略信息列表
        """
        strategies = []
        
        for strategy_id, strategy_class in self._strategies.items():
            metadata = strategy_class.get_metadata()
            
            strategy_info = StrategyInfo(
                metadata=metadata,
                status="available",
                usage_count=0,  # TODO: 从数据库获取
                last_updated=None
            )
            
            strategies.append(strategy_info)
            
        return strategies
    
    def get_strategy_info(self, strategy_id: str) -> Optional[StrategyInfo]:
        """
        获取特定策略的详细信息
        
        Args:
            strategy_id: 策略ID
            
        Returns:
            策略信息或None
        """
        strategy_class = self.get_strategy(strategy_id)
        if not strategy_class:
            return None
            
        metadata = strategy_class.get_metadata()
        
        return StrategyInfo(
            metadata=metadata,
            status="available",
            usage_count=0,  # TODO: 从数据库获取
            last_updated=None
        )
    
    def get_strategy_parameters(self, strategy_id: str) -> Optional[Dict[str, any]]:
        """
        获取策略的默认参数
        
        Args:
            strategy_id: 策略ID
            
        Returns:
            默认参数字典或None
        """
        strategy_class = self.get_strategy(strategy_id)
        if not strategy_class:
            return None
            
        return strategy_class.get_default_parameters()


# 全局策略注册表实例
registry = StrategyRegistry()


def register_strategy(strategy_class: Type[BaseStrategy]):
    """
    策略注册装饰器
    
    用法:
    @register_strategy
    class MyStrategy(BaseStrategy):
        pass
    """
    registry.register_strategy(strategy_class)
    return strategy_class