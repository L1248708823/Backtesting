# -*- coding: utf-8 -*-
"""
Backtrader策略基类

提供所有策略的通用基础功能和接口。
"""

import backtrader as bt
from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Optional
from ..models.strategy import StrategyMetadata, StrategyParameters


class BaseStrategyMeta(ABCMeta, type(bt.Strategy)):
    """解决bt.Strategy和ABC的元类冲突"""
    pass


class BaseStrategy(bt.Strategy, metaclass=BaseStrategyMeta):
    """
    所有策略的基类
    
    📚 学习点：
    - 继承bt.Strategy获得Backtrader的完整功能
    - 使用ABC确保子类实现必要方法
    - 统一参数管理和日志记录
    """
    
    # 策略元数据（子类必须设置）
    METADATA: Optional[StrategyMetadata] = None
    
    def __init__(self):
        super().__init__()
        
        # 策略执行日志
        self.trades_log = []
        self.positions_log = []
        
        # 策略状态
        self.start_value = None
        self.end_value = None
        
    def start(self):
        """策略开始时调用"""
        self.start_value = self.broker.getvalue()
        self.log(f'策略开始，初始资金: {self.start_value:.2f}')
        
    def stop(self):
        """策略结束时调用"""
        self.end_value = self.broker.getvalue()
        total_return = (self.end_value - self.start_value) / self.start_value * 100
        self.log(f'策略结束，最终资金: {self.end_value:.2f}, 总收益率: {total_return:.2f}%')
        
    def log(self, message: str, dt=None):
        """记录日志"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}: {message}')
        
    def notify_order(self, order):
        """订单状态变化通知"""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入成交: 价格={order.executed.price:.2f}, 数量={order.executed.size}')
            elif order.issell():
                self.log(f'卖出成交: 价格={order.executed.price:.2f}, 数量={order.executed.size}')
                
    def notify_trade(self, trade):
        """交易完成通知"""
        if trade.isclosed:
            self.log(f'交易完成: 盈亏={trade.pnl:.2f}, 净盈亏={trade.pnlcomm:.2f}')
            self.trades_log.append({
                'date': self.datas[0].datetime.date(0).isoformat(),
                'pnl': trade.pnl,
                'pnlcomm': trade.pnlcomm
            })
    
    @abstractmethod 
    def next(self):
        """策略主逻辑（子类必须实现）"""
        pass
    
    @classmethod
    @abstractmethod
    def get_metadata(cls) -> StrategyMetadata:
        """获取策略元数据（子类必须实现）"""
        pass
    
    @classmethod
    @abstractmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        """获取默认参数（子类必须实现）"""
        pass
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """获取基础性能指标"""
        if self.start_value is None or self.end_value is None:
            return {}
            
        total_return = (self.end_value - self.start_value) / self.start_value * 100
        
        return {
            'start_value': self.start_value,
            'end_value': self.end_value, 
            'total_return': total_return,
            'total_trades': len(self.trades_log)
        }