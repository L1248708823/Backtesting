# -*- coding: utf-8 -*-
"""
定投策略（Dollar Cost Averaging Strategy）

核心逻辑：
- 定期定额投资指定标的
- 支持不同投资频率（日/周/月）
- 支持节假日跳过
- 适合长期投资，风险较低
"""

from typing import List, Dict, Any
from datetime import datetime, date, timedelta

# 从models导入数据模型
from app.models import (
    ParameterDefinition,
    StrategyMetadata,
    TradeSignal,
    StrategyContext
)
from app.models.common import ParameterType

# 从base导入基类和装饰器
from .base import BaseStrategy, register_strategy


@register_strategy
class DCAStrategy(BaseStrategy):
    """定投策略实现"""
    
    @classmethod
    def get_metadata(cls) -> StrategyMetadata:
        """获取策略元数据"""
        return StrategyMetadata(
            id="dca_strategy",
            name="定投策略",
            description="定期定额投资策略，通过分散投资时间降低市场波动风险，适合长期投资",
            category="定投类",
            risk_level="低",
            supported_markets=["A股", "美股"],
            author="系统内置",
            version="1.0.0"
        )
    
    @classmethod
    def get_parameter_definitions(cls) -> List[ParameterDefinition]:
        """获取策略参数定义"""
        return [
            ParameterDefinition(
                name="symbol",
                type=ParameterType.TEXT,
                default="510300",
                description="投资标的代码（如：510300表示沪深300ETF）",
                required=True
            ),
            ParameterDefinition(
                name="investment_amount",
                type=ParameterType.NUMBER,
                default=1000.0,
                description="每期投资金额（元）",
                required=True,
                min_value=100.0,
                max_value=1000000.0
            ),
            ParameterDefinition(
                name="frequency",
                type=ParameterType.SELECT,
                default="monthly",
                description="投资频率",
                required=True,
                options=["daily", "weekly", "monthly", "quarterly"]
            ),
            ParameterDefinition(
                name="investment_day",
                type=ParameterType.NUMBER,
                default=1,
                description="每月投资日期（1-28，仅月度/季度频率有效）",
                required=False,
                min_value=1,
                max_value=28
            ),
            ParameterDefinition(
                name="skip_holidays",
                type=ParameterType.BOOLEAN,
                default=True,
                description="是否跳过节假日（如果投资日是节假日则顺延）",
                required=False
            ),
            ParameterDefinition(
                name="max_single_weight",
                type=ParameterType.NUMBER,
                default=0.1,
                description="单次投资最大占组合比例（0.1表示10%）",
                required=False,
                min_value=0.01,
                max_value=1.0
            )
        ]
    
    def _initialize(self):
        """策略初始化"""
        self.symbol = self.get_parameter_value("symbol")
        self.investment_amount = self.get_parameter_value("investment_amount")
        self.frequency = self.get_parameter_value("frequency") 
        self.investment_day = self.get_parameter_value("investment_day", 1)
        self.skip_holidays = self.get_parameter_value("skip_holidays", True)
        self.max_single_weight = self.get_parameter_value("max_single_weight", 0.1)
        
        # 记录上次投资时间
        self.last_investment_date = None
        
        # 频率映射到天数
        self.frequency_days = {
            "daily": 1,
            "weekly": 7, 
            "monthly": 30,  # 近似值，实际以月份计算
            "quarterly": 90  # 近似值，实际以季度计算
        }
    
    def generate_signals(self, context: StrategyContext) -> List[TradeSignal]:
        """
        生成交易信号
        
        定投策略的核心逻辑：
        1. 判断是否到达投资时间点
        2. 计算投资金额和权重
        3. 生成买入信号
        """
        signals = []
        
        # 检查是否应该进行投资
        if self._should_invest(context.current_date):
            # 计算实际投资金额（考虑组合限制）
            actual_amount = self._calculate_investment_amount(context)
            
            if actual_amount > 0:
                # 生成买入信号
                signal = TradeSignal(
                    symbol=self.symbol,
                    action="buy",
                    quantity=0,  # 按金额购买，数量由执行引擎计算
                    weight=actual_amount / context.portfolio_value if context.portfolio_value > 0 else 0,
                    reason=f"定投策略：{self.frequency}频率，投资{actual_amount:.2f}元"
                )
                signals.append(signal)
                
                # 更新上次投资时间
                self.last_investment_date = context.current_date
        
        return signals
    
    def _should_invest(self, current_date: date) -> bool:
        """判断是否应该投资"""
        # 如果从未投资，则开始投资
        if self.last_investment_date is None:
            return True
        
        # 根据频率判断
        if self.frequency == "daily":
            return True  # 每天都投资
        
        elif self.frequency == "weekly":
            # 每周投资一次（假设每周一）
            return current_date.weekday() == 0 and \
                   (current_date - self.last_investment_date).days >= 7
        
        elif self.frequency == "monthly":
            # 每月指定日期投资
            return current_date.day == self.investment_day and \
                   (current_date.year != self.last_investment_date.year or 
                    current_date.month != self.last_investment_date.month)
        
        elif self.frequency == "quarterly":
            # 每季度指定日期投资
            current_quarter = (current_date.month - 1) // 3
            last_quarter = (self.last_investment_date.month - 1) // 3
            
            return current_date.day == self.investment_day and \
                   (current_date.year != self.last_investment_date.year or 
                    current_quarter != last_quarter)
        
        return False
    
    def _calculate_investment_amount(self, context: StrategyContext) -> float:
        """计算实际投资金额"""
        # 基础投资金额
        target_amount = self.investment_amount
        
        # 限制1：可用现金
        target_amount = min(target_amount, context.cash)
        
        # 限制2：单次投资不能超过组合总值的一定比例
        if context.portfolio_value > 0:
            max_amount = context.portfolio_value * self.max_single_weight
            target_amount = min(target_amount, max_amount)
        
        # 确保金额为正数
        return max(0, target_amount)
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """获取策略详细信息（用于展示和调试）"""
        return {
            "策略名称": self.get_metadata().name,
            "投资标的": self.symbol,
            "投资金额": f"{self.investment_amount:.2f}元",
            "投资频率": {
                "daily": "每日",
                "weekly": "每周", 
                "monthly": "每月",
                "quarterly": "每季度"
            }.get(self.frequency, self.frequency),
            "投资日期": self.investment_day if self.frequency in ["monthly", "quarterly"] else "不适用",
            "跳过节假日": "是" if self.skip_holidays else "否",
            "最大单次投资比例": f"{self.max_single_weight*100:.1f}%",
            "上次投资日期": self.last_investment_date.strftime("%Y-%m-%d") if self.last_investment_date else "未开始"
        }