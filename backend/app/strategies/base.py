# -*- coding: utf-8 -*-
"""
策略抽象基类和接口定义

核心设计原则：
1. 策略与回测引擎解耦 - 策略只关注信号生成，不关注执行细节
2. 参数类型化 - 强类型参数定义，支持自动验证和UI生成
3. 统一接口 - 所有策略都实现相同的核心接口
4. 可扩展性 - 支持任意复杂的策略逻辑和参数
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

# 从models模块导入数据模型
from app.models import (
    ParameterDefinition,
    StrategyMetadata, 
    TradeSignal,
    StrategyContext
)


class BaseStrategy(ABC):
    """
    策略抽象基类
    
    所有策略都必须继承此类并实现核心方法。
    设计思路：策略只负责生成交易信号，具体执行由回测引擎处理。
    """
    
    def __init__(self, parameters: Dict[str, Any]):
        """
        初始化策略
        
        Args:
            parameters: 策略参数字典
        """
        self.parameters = parameters
        self._validate_parameters()
        self._initialize()
    
    @classmethod
    @abstractmethod
    def get_metadata(cls) -> StrategyMetadata:
        """
        获取策略元数据
        
        Returns:
            StrategyMetadata: 策略元数据对象
        """
        pass
    
    @classmethod
    @abstractmethod  
    def get_parameter_definitions(cls) -> List[ParameterDefinition]:
        """
        获取策略参数定义
        
        Returns:
            List[ParameterDefinition]: 参数定义列表
        """
        pass
    
    @abstractmethod
    def generate_signals(self, context: StrategyContext) -> List[TradeSignal]:
        """
        生成交易信号
        
        Args:
            context: 策略执行上下文
            
        Returns:
            List[TradeSignal]: 交易信号列表
        """
        pass
    
    def _validate_parameters(self):
        """验证参数有效性"""
        param_defs = {p.name: p for p in self.get_parameter_definitions()}
        
        for param_def in param_defs.values():
            if param_def.required and param_def.name not in self.parameters:
                raise ValueError(f"缺少必需参数: {param_def.name}")
            
            if param_def.name in self.parameters:
                value = self.parameters[param_def.name]
                self._validate_parameter_value(param_def, value)
    
    def _validate_parameter_value(self, param_def: ParameterDefinition, value: Any):
        """
        验证单个参数值
        
        根据参数定义的类型和约束条件，验证参数值的有效性。
        这里使用从models模块导入的ParameterType枚举。
        """
        from app.models.common import ParameterType
        
        if param_def.type == ParameterType.NUMBER:
            if not isinstance(value, (int, float)):
                raise ValueError(f"参数 {param_def.name} 必须是数字")
            if param_def.min_value is not None and value < param_def.min_value:
                raise ValueError(f"参数 {param_def.name} 不能小于 {param_def.min_value}")
            if param_def.max_value is not None and value > param_def.max_value:
                raise ValueError(f"参数 {param_def.name} 不能大于 {param_def.max_value}")
        
        elif param_def.type == ParameterType.SELECT:
            if param_def.options and str(value) not in param_def.options:
                raise ValueError(f"参数 {param_def.name} 必须是以下选项之一: {param_def.options}")
    
    def _initialize(self):
        """策略初始化（子类可重写）"""
        pass
    
    def get_parameter_value(self, name: str, default: Any = None) -> Any:
        """获取参数值"""
        return self.parameters.get(name, default)


class StrategyFactory:
    """策略工厂类 - 负责策略的创建和管理"""
    
    _strategies: Dict[str, type] = {}
    
    @classmethod
    def register(cls, strategy_class: type):
        """注册策略类"""
        metadata = strategy_class.get_metadata()
        cls._strategies[metadata.id] = strategy_class
        return strategy_class
    
    @classmethod
    def create_strategy(cls, strategy_id: str, parameters: Dict[str, Any]) -> BaseStrategy:
        """创建策略实例"""
        if strategy_id not in cls._strategies:
            raise ValueError(f"未知策略ID: {strategy_id}")
        
        strategy_class = cls._strategies[strategy_id]
        return strategy_class(parameters)
    
    @classmethod
    def get_all_strategies(cls) -> List[StrategyMetadata]:
        """获取所有已注册策略的元数据"""
        return [strategy_class.get_metadata() for strategy_class in cls._strategies.values()]
    
    @classmethod
    def get_strategy_parameters(cls, strategy_id: str) -> List[ParameterDefinition]:
        """获取指定策略的参数定义"""
        if strategy_id not in cls._strategies:
            raise ValueError(f"未知策略ID: {strategy_id}")
        
        return cls._strategies[strategy_id].get_parameter_definitions()


# 策略注册装饰器
def register_strategy(strategy_class: type):
    """策略注册装饰器"""
    return StrategyFactory.register(strategy_class)