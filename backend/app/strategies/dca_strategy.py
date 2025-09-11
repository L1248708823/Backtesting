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
        
        # 止盈策略参数
        ('exit_strategy', 'hold'),        # 止盈策略类型: hold/profit_target/time_limit/batch_exit
        ('profit_target', 30.0),          # 目标收益率(%)
        ('time_limit_months', 36),        # 时间止盈期限(月)
        ('batch_exit_levels', [20.0, 40.0, 60.0]),  # 分批止盈点位(%)
        ('batch_exit_ratios', [0.3, 0.5, 1.0]),     # 分批止盈比例
    )
    
    def __init__(self):
        super().__init__()
        
        # 记录上次投资日期
        self.last_investment_date = None
        self.investment_count = 0
        
        # DCA特殊数据记录
        self.investment_records = []  # 每次定投详细记录
        self.total_invested = 0       # 累计投入金额
        self.total_shares = 0         # 累计买入份额
        
        # 止盈策略状态
        self.strategy_start_date = None     # 策略开始时间
        self.exit_executed = False          # 是否已执行止盈
        self.batch_exit_tracker = {}        # 分批止盈跟踪 {level: executed}
        
        self.log(f'DCA策略初始化: 每{self.params.frequency_days}天投资{self.params.investment_amount}元于{self.params.symbol}')
    
    def start(self):
        """策略开始时调用"""
        super().start()
        self.strategy_start_date = self.datas[0].datetime.date(0)
        
        # 初始化分批止盈跟踪器
        if self.params.exit_strategy == 'batch_exit':
            for level in self.params.batch_exit_levels:
                self.batch_exit_tracker[level] = False
    
    def next(self):
        """策略主逻辑"""
        current_date = self.datas[0].datetime.date(0)
        
        # 确保每日数据收集（防止prenext/postnext不工作）
        self._collect_daily_data()
        
        # 1. 检查止盈条件（每个交易日都检查）
        if not self.exit_executed and self.total_shares > 0:
            self.check_exit_conditions(current_date)
        
        # 2. 检查是否到了投资日期 (如果还没止盈)
        if not self.exit_executed and self.should_invest(current_date):
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
        current_date = self.datas[0].datetime.date(0)
        
        # 计算可购买股数（向下取整）
        shares_to_buy = int(self.params.investment_amount / current_price)
        
        if shares_to_buy > 0:
            # 下单购买
            self.buy(size=shares_to_buy)
            
            # 更新投资记录
            self.last_investment_date = current_date
            self.investment_count += 1
            
            actual_amount = shares_to_buy * current_price
            
            # 记录详细定投信息
            investment_record = {
                'date': current_date.isoformat(),
                'round': self.investment_count,
                'price': current_price,
                'shares': shares_to_buy,
                'amount': actual_amount,
                'target_amount': self.params.investment_amount,
                'market_value': self.broker.getvalue()  # 当前总市值
            }
            self.investment_records.append(investment_record)
            
            # 更新累计统计
            self.total_invested += actual_amount
            self.total_shares += shares_to_buy
            
            self.log(f'第{self.investment_count}次定投: 价格={current_price:.2f}, 股数={shares_to_buy}, 实际金额={actual_amount:.2f}')
        else:
            self.log(f'资金不足定投: 价格={current_price:.2f}, 目标金额={self.params.investment_amount}')
    
    def check_exit_conditions(self, current_date):
        """检查止盈条件"""
        if self.params.exit_strategy == 'hold':
            return  # 纯持有策略，不执行止盈
        
        # 计算当前收益率
        current_price = self.datas[0].close[0]
        current_position_value = self.total_shares * current_price
        if self.total_invested == 0:
            return
        
        current_return = (current_position_value - self.total_invested) / self.total_invested * 100
        
        # 目标收益止盈
        if self.params.exit_strategy == 'profit_target':
            if current_return >= self.params.profit_target:
                self.execute_exit('profit_target', current_return, shares_ratio=1.0)
        
        # 时间止盈
        elif self.params.exit_strategy == 'time_limit':
            if self.strategy_start_date:
                months_passed = self._calculate_months_passed(current_date)
                if months_passed >= self.params.time_limit_months:
                    self.execute_exit('time_limit', current_return, shares_ratio=1.0)
        
        # 分批止盈
        elif self.params.exit_strategy == 'batch_exit':
            self.check_batch_exit(current_return)
    
    def check_batch_exit(self, current_return):
        """检查分批止盈条件"""
        levels = self.params.batch_exit_levels
        ratios = self.params.batch_exit_ratios
        
        for i, level in enumerate(levels):
            if not self.batch_exit_tracker.get(level, False) and current_return >= level:
                # 计算本次卖出比例
                if i == 0:
                    sell_ratio = ratios[0]
                else:
                    sell_ratio = ratios[i] - ratios[i-1]
                
                self.execute_exit('batch_exit', current_return, shares_ratio=sell_ratio)
                self.batch_exit_tracker[level] = True
                
                # 如果是最后一个点位，标记完全止盈
                if i == len(levels) - 1:
                    self.exit_executed = True
    
    def execute_exit(self, exit_type: str, return_rate: float, shares_ratio: float):
        """执行止盈卖出"""
        if self.total_shares == 0:
            return
        
        shares_to_sell = int(self.total_shares * shares_ratio)
        if shares_to_sell > 0:
            self.sell(size=shares_to_sell)
            
            self.log(f'执行{exit_type}止盈: 收益率={return_rate:.2f}%, 卖出股数={shares_to_sell}, 卖出比例={shares_ratio:.1%}')
            
            # 如果是完全卖出，标记已执行止盈
            if shares_ratio >= 1.0:
                self.exit_executed = True
    
    def _calculate_months_passed(self, current_date):
        """计算已过月数"""
        if not self.strategy_start_date:
            return 0
        
        delta = current_date - self.strategy_start_date
        return delta.days / 30.0  # 简单按30天一个月计算
    
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
                ),
                ParameterDefinition(
                    name="exit_strategy",
                    display_name="止盈策略",
                    description="选择止盈方式：纯持有/目标收益止盈/时间止盈/分批止盈",
                    parameter_type=ParameterType.SELECT,
                    default_value="hold",
                    options=[
                        ParameterOption(value="hold", label="纯持有", description="长期持有不卖出"),
                        ParameterOption(value="profit_target", label="目标收益止盈", description="达到目标收益率后全部卖出"),
                        ParameterOption(value="time_limit", label="时间止盈", description="到期后自动卖出"),
                        ParameterOption(value="batch_exit", label="分批止盈", description="分批逐步减仓")
                    ],
                    validation_rules=ValidationRule(required=True),
                    group="止盈配置",
                    order=4
                ),
                ParameterDefinition(
                    name="profit_target",
                    display_name="目标收益率",
                    description="目标收益止盈的收益率阈值(%)",
                    parameter_type=ParameterType.NUMBER,
                    default_value=30.0,
                    validation_rules=ValidationRule(
                        min_value=5.0,
                        max_value=200.0,
                        required=False
                    ),
                    group="止盈配置",
                    order=5
                ),
                ParameterDefinition(
                    name="time_limit_months",
                    display_name="投资期限",
                    description="时间止盈的投资期限(月)",
                    parameter_type=ParameterType.NUMBER,
                    default_value=36,
                    validation_rules=ValidationRule(
                        min_value=6,
                        max_value=120,
                        required=False
                    ),
                    group="止盈配置",
                    order=6
                )
            ]
        )
    
    @classmethod
    def get_default_parameters(cls) -> Dict[str, Any]:
        """获取默认参数"""
        return {
            'investment_amount': 1000,
            'frequency_days': 30,
            'symbol': '510300',
            'exit_strategy': 'hold',
            'profit_target': 30.0,
            'time_limit_months': 36
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取DCA策略的完整性能指标"""
        # 首先获取基础指标
        base_metrics = super().get_performance_metrics()
        
        # 计算DCA特殊指标
        dca_metrics = self._calculate_dca_metrics()
        
        # 合并指标
        return {
            **base_metrics,
            **dca_metrics
        }
    
    def _calculate_dca_metrics(self) -> Dict[str, Any]:
        """计算DCA策略特殊指标"""
        if not self.investment_records:
            return {
                'average_cost': 0.0,
                'cost_reduction_effect': 0.0,
                'investment_efficiency': 0.0
            }
        
        # 计算平均成本
        if self.total_shares > 0:
            average_cost = self.total_invested / self.total_shares
        else:
            average_cost = 0.0
        
        # 计算成本摊薄效果 (对比平均价格买入的效果)
        prices = [record['price'] for record in self.investment_records]
        if prices:
            simple_average_price = sum(prices) / len(prices)  # 简单平均价格
            cost_reduction_effect = (simple_average_price - average_cost) / simple_average_price * 100
        else:
            cost_reduction_effect = 0.0
        
        # 投资执行效率 (实际投资与目标投资的比率)
        target_total = len(self.investment_records) * self.params.investment_amount
        if target_total > 0:
            investment_efficiency = (self.total_invested / target_total) * 100
        else:
            investment_efficiency = 0.0
        
        # 当前持仓价值
        current_price = self.datas[0].close[0] if self.datas and len(self.datas[0]) > 0 else 0
        current_position_value = self.total_shares * current_price
        
        # 未实现收益
        unrealized_pnl = current_position_value - self.total_invested
        unrealized_return = (unrealized_pnl / self.total_invested * 100) if self.total_invested > 0 else 0
        
        return {
            # DCA核心指标
            'investment_records': self.investment_records,
            'total_invested': self.total_invested,
            'total_shares': self.total_shares,
            'average_cost': average_cost,
            
            # DCA效果分析
            'cost_reduction_effect': cost_reduction_effect,  # 成本摊薄效果(%)
            'investment_efficiency': investment_efficiency,   # 投资执行效率(%)
            
            # 持仓分析
            'current_position_value': current_position_value,
            'unrealized_pnl': unrealized_pnl,
            'unrealized_return': unrealized_return,
            
            # 投资时机分析
            'price_range': {
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
                'price_volatility': (max(prices) - min(prices)) / min(prices) * 100 if prices and min(prices) > 0 else 0
            }
        }
    
