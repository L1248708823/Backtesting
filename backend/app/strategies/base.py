# -*- coding: utf-8 -*-
"""
Backtrader策略基类

提供所有策略的通用基础功能和接口。
"""

import backtrader as bt
import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
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
        self.orders_log = []  # 新增：订单执行日志
        
        # 策略状态
        self.start_value = None
        self.end_value = None
        
        # 每日价格记录 (标的价格，不是总资产)
        self.daily_prices = []  # 标的每日收盘价
        self.daily_returns = []  # 基于价格的日收益率
        self.daily_dates = []   # 对应日期
        
        # 总资产价值记录 (用于计算投资组合指标)
        self.daily_portfolio_values = []
        
    def start(self):
        """策略开始时调用"""
        self.start_value = self.broker.getvalue()
        self.log(f'策略开始，初始资金: {self.start_value:.2f}')
        
    def prenext(self):
        """在next之前调用，用于数据收集"""
        self._collect_daily_data()
    
    def next(self):
        """策略主逻辑入口（基类实现数据收集）"""
        # 确保每日数据收集只进行一次
        if not self._data_collected_today():
            self._collect_daily_data()
        
        # 调用子类的策略逻辑
        self._next_impl()
    
    @abstractmethod 
    def _next_impl(self):
        """策略主逻辑（子类必须实现）"""
        pass
    
    def _data_collected_today(self) -> bool:
        """检查今天是否已经收集了数据"""
        if not self.daily_dates:
            return False
        
        current_date = self.datas[0].datetime.date(0)
        return self.daily_dates[-1] == current_date
    
    def _collect_daily_data(self):
        """收集每日标的价格和资产价值数据"""
        # 获取标的收盘价（用于净值图表）
        current_price = self.datas[0].close[0] if self.datas and len(self.datas[0]) > 0 else 0
        # 获取总资产价值（现金 + 持仓价值，用于投资组合分析）
        current_portfolio_value = self.broker.getvalue()
        current_date = self.datas[0].datetime.date(0)
        
        # 避免重复添加同一天的数据
        if self.daily_dates and self.daily_dates[-1] == current_date:
            # 更新当天的数据（最后一个记录）
            self.daily_prices[-1] = current_price
            self.daily_portfolio_values[-1] = current_portfolio_value
        else:
            # 添加新一天的数据
            self.daily_prices.append(current_price)
            self.daily_portfolio_values.append(current_portfolio_value)
            self.daily_dates.append(current_date)
            
            # 计算基于标的价格的日收益率
            if len(self.daily_prices) > 1:
                daily_return = (current_price - self.daily_prices[-2]) / self.daily_prices[-2]
                self.daily_returns.append(daily_return)
            else:
                self.daily_returns.append(0.0)  # 第一天收益率为0
            
    
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
                # 记录每次买入执行
                self.orders_log.append({
                    'date': self.datas[0].datetime.date(0).isoformat(),
                    'type': 'buy',
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'value': order.executed.value,
                    'commission': order.executed.comm
                })
            elif order.issell():
                self.log(f'卖出成交: 价格={order.executed.price:.2f}, 数量={order.executed.size}')
                # 记录每次卖出执行
                self.orders_log.append({
                    'date': self.datas[0].datetime.date(0).isoformat(),
                    'type': 'sell',
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'value': order.executed.value,
                    'commission': order.executed.comm
                })
                
    def notify_trade(self, trade):
        """交易完成通知"""
        if trade.isclosed:
            self.log(f'交易完成: 盈亏={trade.pnl:.2f}, 净盈亏={trade.pnlcomm:.2f}')
            self.trades_log.append({
                'date': self.datas[0].datetime.date(0).isoformat(),
                'pnl': trade.pnl,
                'pnlcomm': trade.pnlcomm
            })
    
    
    
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
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取完整的性能指标"""
        if self.start_value is None or self.end_value is None:
            return {}
        
        # 统计买入卖出次数
        buy_orders = [order for order in self.orders_log if order['type'] == 'buy']
        sell_orders = [order for order in self.orders_log if order['type'] == 'sell']
        
        # 只返回基础数据，让Backtrader内置分析器处理复杂指标
        metrics = {
            # 基础交易数据
            'buy_orders': len(buy_orders),
            'sell_orders': len(sell_orders),
            'buy_records': buy_orders,
            'sell_records': sell_orders,
            
            # 每日数据（供图表展示和波动率计算）
            'daily_prices': self.daily_prices,              # 标的价格走势
            'daily_portfolio_values': self.daily_portfolio_values,  # 投资组合价值
            'daily_returns': self.daily_returns,            # 基于标的价格的收益率
            'daily_dates': [d.isoformat() for d in self.daily_dates],
            
            # 波动率计算（保留自己实现）
            'volatility': self._calculate_volatility() if len(self.daily_returns) > 1 else 0.0,
        }
        
        return metrics
    
    def _calculate_volatility(self) -> float:
        """计算年化波动率"""
        if len(self.daily_returns) < 2:
            return 0.0
        
        returns = np.array(self.daily_returns)
        volatility = np.std(returns) * np.sqrt(252) * 100  # 年化波动率(%)
        return volatility