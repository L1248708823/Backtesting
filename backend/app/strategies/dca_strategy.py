# -*- coding: utf-8 -*-
"""
定投策略（Dollar Cost Averaging Strategy）

核心逻辑：
- 定期定额投资指定标的
- 支持不同投资频率（日/周/月/季）
- 支持节假日跳过和智能调整
- 适合长期投资，风险较低，是最经典的投资策略之一

策略优势：
1. 分散时间风险：通过时间分散化降低择时风险
2. 操作简单：无需复杂的技术分析和择时
3. 强制储蓄：培养良好的投资习惯
4. 复利效应：长期投资享受复利收益

适用场景：
- 投资新手或风险偏好较低的投资者
- 希望进行长期投资的投资者（建议≥3年）
- 没有时间频繁关注市场的投资者
- 追求稳定收益，不追求超额收益的投资者
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP

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


# 配置日志
logger = logging.getLogger(__name__)


@register_strategy
class DCAStrategy(BaseStrategy):
    """
    定投策略实现
    
    定投（Dollar Cost Averaging）是一种投资技巧，指在固定时间间隔
    投入固定金额购买某种投资产品，不管该产品价格如何变化。
    
    这种策略的核心思想是通过分批购买来平摊成本，降低市场波动的影响。
    """
    
    # 策略版本号，用于兼容性管理
    STRATEGY_VERSION = "1.1.0"
    
    # 支持的投资频率常量
    FREQUENCY_DAILY = "daily"
    FREQUENCY_WEEKLY = "weekly" 
    FREQUENCY_MONTHLY = "monthly"
    FREQUENCY_QUARTERLY = "quarterly"
    
    @classmethod
    def get_metadata(cls) -> StrategyMetadata:
        """获取策略元数据"""
        return StrategyMetadata(
            id="dca_strategy",
            name="定投策略",
            description=(
                "定期定额投资策略，通过分散投资时间降低市场波动风险。"
                "适合长期投资，特别适合投资新手和追求稳定收益的投资者。"
                "建议投资期限≥3年以获得更好的效果。"
            ),
            category="定投类",
            risk_level="低",
            supported_markets=["A股", "美股"],
            author="系统内置",
            version=cls.STRATEGY_VERSION,
            tags=["长期投资", "风险分散", "适合新手", "稳健收益"]
        )
    
    @classmethod
    def get_parameter_definitions(cls) -> List[ParameterDefinition]:
        """
        获取策略参数定义
        
        定投策略的参数设计原则：
        1. 参数简单易懂，避免过度复杂化
        2. 提供合理的默认值和范围限制
        3. 每个参数都有详细的说明和使用建议
        """
        return [
            ParameterDefinition(
                name="symbol",
                type=ParameterType.TEXT,
                default="510300",
                description=(
                    "投资标的代码。例如：\n"
                    "• A股ETF：510300（沪深300）、512100（中证1000）\n"
                    "• 美股ETF：SPY（标普500）、QQQ（纳斯达克100）\n"
                    "建议选择流动性好的宽基指数ETF"
                ),
                required=True,
                validation_rules={
                    "min_length": 3,
                    "max_length": 20,
                    "pattern": r"^[A-Za-z0-9]+$"
                }
            ),
            
            ParameterDefinition(
                name="investment_amount",
                type=ParameterType.NUMBER,
                default=1000.0,
                description=(
                    "每期投资金额（元）。建议设置方案：\n"
                    "• 保守型：月收入的10-15%\n"
                    "• 积极型：月收入的20-30%\n"
                    "• 最小建议：500元/月（降低交易成本影响）"
                ),
                required=True,
                min_value=100.0,
                max_value=1000000.0,
                validation_rules={
                    "step": 100.0  # 建议以100元为步进
                }
            ),
            
            ParameterDefinition(
                name="frequency",
                type=ParameterType.SELECT,
                default=cls.FREQUENCY_MONTHLY,
                description=(
                    "投资频率选择建议：\n"
                    "• 每日：适合金额较小，手续费极低的情况\n"
                    "• 每周：平衡了成本和风险分散效果\n"
                    "• 每月：最常见选择，平衡收益和成本（推荐）\n"
                    "• 每季度：适合大额投资，降低交易频率"
                ),
                required=True,
                options=[
                    {"value": cls.FREQUENCY_DAILY, "label": "每日投资"},
                    {"value": cls.FREQUENCY_WEEKLY, "label": "每周投资"},
                    {"value": cls.FREQUENCY_MONTHLY, "label": "每月投资（推荐）"},
                    {"value": cls.FREQUENCY_QUARTERLY, "label": "每季度投资"}
                ]
            ),
            
            ParameterDefinition(
                name="investment_day",
                type=ParameterType.NUMBER,
                default=1,
                description=(
                    "每月投资日期（1-28号）。建议：\n"
                    "• 发薪日后：如5号、10号、15号\n"
                    "• 月初：1-5号，便于记忆和规划\n"
                    "• 避免月末：防止遇到月份天数差异"
                ),
                required=False,
                min_value=1,
                max_value=28,
                depends_on=[
                    {"parameter": "frequency", "values": [cls.FREQUENCY_MONTHLY, cls.FREQUENCY_QUARTERLY]}
                ]
            ),
            
            ParameterDefinition(
                name="skip_holidays",
                type=ParameterType.BOOLEAN,
                default=True,
                description=(
                    "节假日处理方式：\n"
                    "• 开启：如遇节假日自动顺延到下一交易日\n"
                    "• 关闭：严格按日期执行，可能错过某些投资机会\n"
                    "建议开启，确保投资的连续性"
                ),
                required=False
            ),
            
            ParameterDefinition(
                name="max_single_weight",
                type=ParameterType.NUMBER,
                default=0.1,
                description=(
                    "单次投资最大占组合比例限制。例如：\n"
                    "• 0.05（5%）：非常保守，适合大额账户\n"
                    "• 0.1（10%）：平衡选择（推荐）\n"
                    "• 0.2（20%）：相对激进，适合小额账户\n"
                    "此参数防止单次投资过于集中"
                ),
                required=False,
                min_value=0.01,
                max_value=0.5,  # 最多不超过50%
                validation_rules={
                    "step": 0.01
                }
            ),
            
            ParameterDefinition(
                name="enable_cost_control",
                type=ParameterType.BOOLEAN,
                default=True,
                description=(
                    "成本控制优化：\n"
                    "• 开启：当交易成本占比过高时暂停投资\n"
                    "• 关闭：严格执行投资计划，不考虑成本\n"
                    "建议开启，提高投资效率"
                ),
                required=False
            ),
            
            ParameterDefinition(
                name="min_cost_ratio",
                type=ParameterType.NUMBER,
                default=0.01,
                description=(
                    "最小成本效益比（仅成本控制开启时有效）：\n"
                    "当交易成本占投资金额比例超过此值时跳过本次投资\n"
                    "• 0.005（0.5%）：严格控制成本\n"
                    "• 0.01（1%）：平衡选择\n"
                    "• 0.02（2%）：相对宽松"
                ),
                required=False,
                min_value=0.001,
                max_value=0.05,
                depends_on=[
                    {"parameter": "enable_cost_control", "values": [True]}
                ]
            )
        ]
    
    def _initialize(self):
        """
        策略初始化
        
        在策略开始执行前进行必要的初始化工作：
        1. 读取和验证参数
        2. 初始化内部状态
        3. 设置日志记录
        """
        try:
            # 读取核心参数
            self.symbol = self.get_parameter_value("symbol")
            self.investment_amount = Decimal(str(self.get_parameter_value("investment_amount")))
            self.frequency = self.get_parameter_value("frequency")
            
            # 读取可选参数
            self.investment_day = self.get_parameter_value("investment_day", 1)
            self.skip_holidays = self.get_parameter_value("skip_holidays", True)
            self.max_single_weight = self.get_parameter_value("max_single_weight", 0.1)
            self.enable_cost_control = self.get_parameter_value("enable_cost_control", True)
            self.min_cost_ratio = self.get_parameter_value("min_cost_ratio", 0.01)
            
            # 初始化内部状态
            self.last_investment_date: Optional[date] = None
            self.total_invested = Decimal('0')  # 累计投资金额
            self.investment_count = 0  # 投资次数
            self.skipped_count = 0  # 跳过次数（成本控制或其他原因）
            
            # 参数验证
            self._validate_parameters()
            
            # 记录策略初始化信息
            logger.info(f"定投策略初始化成功: {self.symbol}, "
                       f"投资金额: {self.investment_amount}, "
                       f"频率: {self.frequency}")
                       
        except Exception as e:
            logger.error(f"定投策略初始化失败: {str(e)}")
            raise ValueError(f"策略初始化失败: {str(e)}")
    
    def _validate_parameters(self):
        """参数验证"""
        # 验证投资标的
        if not self.symbol or len(self.symbol.strip()) == 0:
            raise ValueError("投资标的代码不能为空")
        
        # 验证投资金额
        if self.investment_amount <= 0:
            raise ValueError("投资金额必须大于0")
        
        # 验证频率
        valid_frequencies = [self.FREQUENCY_DAILY, self.FREQUENCY_WEEKLY, 
                           self.FREQUENCY_MONTHLY, self.FREQUENCY_QUARTERLY]
        if self.frequency not in valid_frequencies:
            raise ValueError(f"不支持的投资频率: {self.frequency}")
        
        # 验证投资日期
        if self.frequency in [self.FREQUENCY_MONTHLY, self.FREQUENCY_QUARTERLY]:
            if not (1 <= self.investment_day <= 28):
                raise ValueError("投资日期必须在1-28之间")
    
    def generate_signals(self, context: StrategyContext) -> List[TradeSignal]:
        """
        生成交易信号
        
        定投策略的核心逻辑：
        1. 判断是否到达投资时间点
        2. 进行成本效益分析（如果启用）
        3. 计算实际投资金额
        4. 生成买入信号
        
        Args:
            context: 策略执行上下文，包含当前日期、组合状态等信息
            
        Returns:
            List[TradeSignal]: 交易信号列表
        """
        signals = []
        
        try:
            # 检查是否应该进行投资
            if not self._should_invest(context.current_date):
                return signals
            
            # 计算实际投资金额（考虑各种限制）
            actual_amount = self._calculate_investment_amount(context)
            
            if actual_amount <= 0:
                logger.debug(f"投资金额为0，跳过本次投资: {context.current_date}")
                self.skipped_count += 1
                return signals
            
            # 成本控制检查
            if self.enable_cost_control and not self._check_cost_effectiveness(actual_amount, context):
                logger.info(f"成本效益不佳，跳过本次投资: {context.current_date}")
                self.skipped_count += 1
                return signals
            
            # 生成买入信号
            weight = self._calculate_position_weight(actual_amount, context)
            
            signal = TradeSignal(
                symbol=self.symbol,
                action="buy",
                quantity=0,  # 按金额购买，数量由执行引擎计算
                amount=float(actual_amount),
                weight=weight,
                reason=self._generate_signal_reason(actual_amount),
                signal_time=datetime.combine(context.current_date, datetime.min.time()),
                confidence=0.8,  # 定投策略置信度固定为0.8
                metadata={
                    "investment_count": self.investment_count + 1,
                    "total_invested_after": float(self.total_invested + actual_amount),
                    "frequency": self.frequency,
                    "is_dca_signal": True
                }
            )
            signals.append(signal)
            
            # 更新内部状态
            self._update_investment_state(context.current_date, actual_amount)
            
            logger.info(f"生成定投买入信号: {self.symbol}, "
                       f"金额: {actual_amount}, 日期: {context.current_date}")
                       
        except Exception as e:
            logger.error(f"生成交易信号时发生错误: {str(e)}")
            # 在生产环境中，可以选择返回空信号而不是抛出异常
            # 这里为了调试方便，选择抛出异常
            raise
        
        return signals
    
    def _should_invest(self, current_date: date) -> bool:
        """
        判断是否应该投资
        
        根据设定的投资频率和上次投资时间，判断当前日期是否应该进行投资。
        
        Args:
            current_date: 当前日期
            
        Returns:
            bool: 是否应该投资
        """
        # 如果从未投资，则开始投资
        if self.last_investment_date is None:
            return True
        
        # 根据频率判断
        if self.frequency == self.FREQUENCY_DAILY:
            # 每日投资：每天都投资（实际中不太现实，但支持）
            return True
        
        elif self.frequency == self.FREQUENCY_WEEKLY:
            # 每周投资：每周一投资，且距离上次投资至少7天
            return (current_date.weekday() == 0 and 
                    (current_date - self.last_investment_date).days >= 7)
        
        elif self.frequency == self.FREQUENCY_MONTHLY:
            # 每月投资：指定日期投资，且不在同一个月
            return (current_date.day == self.investment_day and
                    not self._is_same_month(current_date, self.last_investment_date))
        
        elif self.frequency == self.FREQUENCY_QUARTERLY:
            # 每季度投资：指定日期投资，且不在同一个季度
            return (current_date.day == self.investment_day and
                    not self._is_same_quarter(current_date, self.last_investment_date))
        
        return False
    
    def _is_same_month(self, date1: date, date2: date) -> bool:
        """判断两个日期是否在同一个月"""
        return date1.year == date2.year and date1.month == date2.month
    
    def _is_same_quarter(self, date1: date, date2: date) -> bool:
        """判断两个日期是否在同一个季度"""
        if date1.year != date2.year:
            return False
        
        quarter1 = (date1.month - 1) // 3
        quarter2 = (date2.month - 1) // 3
        return quarter1 == quarter2
    
    def _calculate_investment_amount(self, context: StrategyContext) -> Decimal:
        """
        计算实际投资金额
        
        考虑多种限制因素：
        1. 设定的投资金额
        2. 可用现金限制
        3. 单次投资比例限制
        4. 最小投资金额限制（避免小额交易）
        
        Args:
            context: 策略执行上下文
            
        Returns:
            Decimal: 实际可投资金额
        """
        # 基础投资金额
        target_amount = self.investment_amount
        
        # 限制1：可用现金
        available_cash = Decimal(str(context.cash))
        target_amount = min(target_amount, available_cash)
        
        # 限制2：单次投资不能超过组合总值的一定比例
        if context.portfolio_value > 0:
            portfolio_value = Decimal(str(context.portfolio_value))
            max_amount = portfolio_value * Decimal(str(self.max_single_weight))
            target_amount = min(target_amount, max_amount)
        
        # 限制3：最小投资金额（避免过小的交易）
        min_investment = Decimal('50')  # 最小投资50元
        if target_amount < min_investment:
            logger.debug(f"投资金额{target_amount}小于最小限制{min_investment}，跳过投资")
            return Decimal('0')
        
        # 确保金额为正数，并四舍五入到2位小数
        return max(Decimal('0'), target_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    def _check_cost_effectiveness(self, amount: Decimal, context: StrategyContext) -> bool:
        """
        检查成本效益
        
        当启用成本控制时，如果交易成本占投资金额比例过高，则跳过本次投资。
        这样可以避免高频小额交易带来的成本拖累。
        
        Args:
            amount: 预计投资金额
            context: 策略执行上下文
            
        Returns:
            bool: 是否通过成本效益检查
        """
        if not self.enable_cost_control:
            return True
        
        # 估算交易成本（这里使用简化的估算）
        # 实际系统中应该从context获取真实的交易成本
        estimated_cost = self._estimate_transaction_cost(amount, context)
        
        # 计算成本比例
        cost_ratio = estimated_cost / amount if amount > 0 else 1
        
        # 检查是否超过阈值
        is_cost_effective = cost_ratio <= Decimal(str(self.min_cost_ratio))
        
        if not is_cost_effective:
            logger.info(f"交易成本比例{cost_ratio:.4f}超过阈值{self.min_cost_ratio:.4f}，跳过投资")
        
        return is_cost_effective
    
    def _estimate_transaction_cost(self, amount: Decimal, context: StrategyContext) -> Decimal:
        """
        估算交易成本
        
        这是一个简化的成本估算方法，实际系统应该根据具体的券商费率计算。
        
        Args:
            amount: 交易金额
            context: 策略执行上下文
            
        Returns:
            Decimal: 预估交易成本
        """
        # 简化的成本模型：
        # 1. 佣金：万分之3，最小5元
        # 2. 印花税：千分之1（卖出时，这里暂不考虑）
        # 3. 过户费：万分之0.2（A股，这里简化处理）
        
        commission_rate = Decimal('0.0003')  # 万分之3
        min_commission = Decimal('5')        # 最小佣金5元
        transfer_fee_rate = Decimal('0.00002')  # 万分之0.2
        
        # 计算佣金
        commission = max(amount * commission_rate, min_commission)
        
        # 计算过户费
        transfer_fee = amount * transfer_fee_rate
        
        # 总成本
        total_cost = commission + transfer_fee
        
        return total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _calculate_position_weight(self, amount: Decimal, context: StrategyContext) -> float:
        """
        计算持仓权重
        
        Args:
            amount: 投资金额
            context: 策略执行上下文
            
        Returns:
            float: 持仓权重（0-1之间）
        """
        if context.portfolio_value <= 0:
            return 0.0
        
        return float(amount / Decimal(str(context.portfolio_value)))
    
    def _generate_signal_reason(self, amount: Decimal) -> str:
        """
        生成交易信号原因描述
        
        Args:
            amount: 投资金额
            
        Returns:
            str: 信号原因描述
        """
        frequency_desc = {
            self.FREQUENCY_DAILY: "每日",
            self.FREQUENCY_WEEKLY: "每周", 
            self.FREQUENCY_MONTHLY: "每月",
            self.FREQUENCY_QUARTERLY: "每季度"
        }.get(self.frequency, self.frequency)
        
        return (f"定投策略执行：{frequency_desc}定投，"
                f"投资{amount}元购买{self.symbol}，"
                f"第{self.investment_count + 1}次投资")
    
    def _update_investment_state(self, investment_date: date, amount: Decimal):
        """
        更新投资状态
        
        Args:
            investment_date: 投资日期
            amount: 投资金额
        """
        self.last_investment_date = investment_date
        self.total_invested += amount
        self.investment_count += 1
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        获取策略详细信息（用于展示和调试）
        
        Returns:
            Dict[str, Any]: 策略信息字典
        """
        frequency_desc = {
            self.FREQUENCY_DAILY: "每日",
            self.FREQUENCY_WEEKLY: "每周", 
            self.FREQUENCY_MONTHLY: "每月",
            self.FREQUENCY_QUARTERLY: "每季度"
        }.get(self.frequency, self.frequency)
        
        return {
            "策略名称": self.get_metadata().name,
            "策略版本": self.STRATEGY_VERSION,
            "投资标的": self.symbol,
            "投资金额": f"{self.investment_amount}元",
            "投资频率": frequency_desc,
            "投资日期": (self.investment_day 
                      if self.frequency in [self.FREQUENCY_MONTHLY, self.FREQUENCY_QUARTERLY] 
                      else "不适用"),
            "跳过节假日": "是" if self.skip_holidays else "否",
            "最大单次投资比例": f"{self.max_single_weight*100:.1f}%",
            "成本控制": "开启" if self.enable_cost_control else "关闭",
            "最小成本效益比": f"{self.min_cost_ratio*100:.2f}%" if self.enable_cost_control else "不适用",
            "上次投资日期": (self.last_investment_date.strftime("%Y-%m-%d") 
                          if self.last_investment_date else "未开始"),
            "累计投资金额": f"{self.total_invested}元",
            "投资次数": self.investment_count,
            "跳过次数": self.skipped_count,
            "投资成功率": (f"{self.investment_count/(self.investment_count + self.skipped_count)*100:.1f}%" 
                        if (self.investment_count + self.skipped_count) > 0 else "0%")
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取策略执行的关键指标
        
        Returns:
            Dict[str, Any]: 性能指标字典
        """
        total_attempts = self.investment_count + self.skipped_count
        
        return {
            "total_invested": float(self.total_invested),
            "investment_count": self.investment_count,
            "skipped_count": self.skipped_count,
            "total_attempts": total_attempts,
            "success_rate": (self.investment_count / total_attempts 
                           if total_attempts > 0 else 0),
            "average_investment": (float(self.total_invested) / self.investment_count 
                                 if self.investment_count > 0 else 0),
            "last_investment_date": (self.last_investment_date.isoformat() 
                                   if self.last_investment_date else None),
            "strategy_version": self.STRATEGY_VERSION,
            "frequency": self.frequency
        }
    
    def validate_context(self, context: StrategyContext) -> bool:
        """
        验证策略执行上下文是否有效
        
        Args:
            context: 策略执行上下文
            
        Returns:
            bool: 上下文是否有效
        """
        try:
            # 检查必要的上下文信息
            if context is None:
                logger.error("策略执行上下文为空")
                return False
            
            if context.current_date is None:
                logger.error("当前日期信息缺失")
                return False
            
            if context.cash < 0:
                logger.error(f"现金余额不能为负数: {context.cash}")
                return False
            
            if context.portfolio_value < 0:
                logger.error(f"组合价值不能为负数: {context.portfolio_value}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"上下文验证失败: {str(e)}")
            return False
    
    def reset_state(self):
        """
        重置策略状态
        
        用于重新开始回测或清理策略状态
        """
        self.last_investment_date = None
        self.total_invested = Decimal('0')
        self.investment_count = 0
        self.skipped_count = 0
        
        logger.info("定投策略状态已重置")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"定投策略(标的={self.symbol}, 金额={self.investment_amount}, 频率={self.frequency})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"DCAStrategy(symbol='{self.symbol}', "
                f"investment_amount={self.investment_amount}, "
                f"frequency='{self.frequency}', "
                f"investment_count={self.investment_count})")