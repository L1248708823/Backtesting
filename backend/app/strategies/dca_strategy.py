# -*- coding: utf-8 -*-
"""
DCA定投策略

基于Backtrader实现的定期定额投资策略。
"""

import backtrader as bt
from typing import Dict, Any
from datetime import datetime

from .base import BaseStrategy
from ..models.strategy import StrategyMetadata, ParameterDefinition, ParameterType, ValidationRule, ParameterOption
from ..models.common import StrategyType, MarketType


class DCAStrategy(BaseStrategy):
    """
    DCA定投策略
    
    📚 学习点：
    - 定期定额投资的经典实现
    - 时间触发的投资逻辑
    - 资金管理和仓位控制
    """
    
    # 策略参数定义
    params = (
        ('investment_amount', 1000),      # 每期投资金额
        ('frequency_days', 30),           # 投资频率（天数）
        ('symbol', '510300'),             # 投资标的
    )
    
    def __init__(self):
        super().__init__()
        
        # 记录上次投资日期
        self.last_investment_date = None
        self.investment_count = 0
        
        self.log(f'DCA策略初始化: 每{self.params.frequency_days}天投资{self.params.investment_amount}元于{self.params.symbol}')
    
    def next(self):
        """策略主逻辑"""
        current_date = self.datas[0].datetime.date(0)
        
        # 检查是否到了投资日期
        if self.should_invest(current_date):
            self.execute_investment()
    
    def should_invest(self, current_date) -> bool:
        """判断是否应该投资"""
        if self.last_investment_date is None:
            # 第一次投资
            return True
            
        # 计算距离上次投资的天数
        days_since_last = (current_date - self.last_investment_date).days
        return days_since_last >= self.params.frequency_days
    
    def execute_investment(self):
        """执行定投"""
        current_price = self.datas[0].close[0]
        
        # 计算可购买股数（向下取整）
        shares_to_buy = int(self.params.investment_amount / current_price)
        
        if shares_to_buy > 0:
            # 下单购买
            self.buy(size=shares_to_buy)
            
            # 更新投资记录
            self.last_investment_date = self.datas[0].datetime.date(0)
            self.investment_count += 1
            
            actual_amount = shares_to_buy * current_price
            self.log(f'第{self.investment_count}次定投: 价格={current_price:.2f}, 股数={shares_to_buy}, 实际金额={actual_amount:.2f}')
        else:
            self.log(f'资金不足定投: 价格={current_price:.2f}, 目标金额={self.params.investment_amount}')
    
    @classmethod
    def get_metadata(cls) -> StrategyMetadata:
        """获取策略元数据"""
        return StrategyMetadata(
            id="dca_strategy",
            name="DCA定投策略",
            description="定期定额投资策略，通过分散投资时间降低市场波动风险。适合长期投资ETF、指数基金等标的。",
            category="投资策略",
            strategy_type=StrategyType.DCA,
            risk_level="低",
            supported_markets=[MarketType.A_STOCK, MarketType.US_STOCK],
            author="量化回测系统",
            version="1.0.0",
            tags=["定投", "DCA", "长期投资", "风险分散"],
            features=["定期投资", "固定金额", "自动执行", "适合新手"],
            parameters=[
                ParameterDefinition(
                    name="investment_amount",
                    display_name="投资金额",
                    description="每期定投金额（元），建议不少于500元以降低手续费影响",
                    parameter_type=ParameterType.NUMBER,
                    default_value=1000.0,
                    validation_rules=ValidationRule(
                        min_value=100.0,
                        max_value=100000.0,
                        required=True
                    ),
                    group="基础配置",
                    order=1
                ),
                ParameterDefinition(
                    name="frequency_days", 
                    display_name="投资频率",
                    description="定投间隔天数，常用选项：7天(周)、30天(月)、90天(季)",
                    parameter_type=ParameterType.SELECT,
                    default_value=30,
                    options=[
                        ParameterOption(value="7", label="每周定投", description="风险分散度最高"),
                        ParameterOption(value="30", label="每月定投", description="经典定投频率"), 
                        ParameterOption(value="90", label="每季定投", description="降低交易成本")
                    ],
                    validation_rules=ValidationRule(
                        min_value=1,
                        max_value=365,
                        required=True
                    ),
                    group="时间配置",
                    order=2
                ),
                ParameterDefinition(
                    name="symbol",
                    display_name="投资标的",
                    description="投资标的代码，如：510300(沪深300ETF)、SPY(标普500ETF)",
                    parameter_type=ParameterType.STRING,
                    default_value="510300", 
                    validation_rules=ValidationRule(
                        min_length=3,
                        max_length=20,
                        pattern=r"^[A-Za-z0-9]+$",
                        required=True
                    ),
                    group="基础配置",
                    order=3
                )
            ]
        )
    
    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        """获取默认参数"""
        return {
            'investment_amount': 1000,
            'frequency_days': 30,
            'symbol': '510300'
        }