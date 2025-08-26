# -*- coding: utf-8 -*-
"""
简化版回测引擎 (Simplified Backtest Engine)

专为定投策略优化设计的回测引擎，具有以下特点：
1. 轻量级：去除复杂的功能，专注核心回测逻辑
2. 高性能：针对定投场景优化，支持长期回测
3. 易理解：清晰的代码结构，便于学习和维护
4. 可扩展：为后续复杂策略预留接口

核心功能：
- 时间序列回测循环
- 资金管理和持仓跟踪
- 交易执行和成本计算
- 基础性能指标统计
- 详细的执行日志

设计原则：
- 策略与引擎分离：引擎只负责执行，策略负责信号
- 数据驱动：基于历史数据进行模拟
- 状态管理：准确跟踪资金、持仓等状态
- 错误处理：优雅处理异常情况
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, asdict
from enum import Enum

# 导入策略相关模型
from app.models import StrategyContext, TradeSignal
from app.strategies.base import BaseStrategy


# 配置日志
logger = logging.getLogger(__name__)


class BacktestStatus(Enum):
    """回测状态枚举"""
    PENDING = "pending"      # 等待开始
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 执行失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class BacktestConfig:
    """
    回测配置
    
    包含回测执行所需的所有配置参数
    """
    # 基础配置
    strategy_id: str                    # 策略ID
    strategy_params: Dict[str, Any]     # 策略参数
    
    # 时间范围
    start_date: date                    # 开始日期
    end_date: date                      # 结束日期
    
    # 资金配置
    initial_capital: Decimal            # 初始资金
    
    # 交易成本配置
    commission_rate: Decimal = Decimal('0.0003')    # 佣金费率（万分之3）
    min_commission: Decimal = Decimal('5')          # 最小佣金（5元）
    stamp_duty_rate: Decimal = Decimal('0.001')     # 印花税（千分之1，卖出时）
    transfer_fee_rate: Decimal = Decimal('0.00002') # 过户费（万分之0.2）
    
    # 执行配置
    benchmark_symbol: Optional[str] = None          # 基准标的（用于比较）
    enable_slippage: bool = True                   # 是否启用滑点
    slippage_rate: Decimal = Decimal('0.001')     # 滑点率（千分之1）
    
    # 风控配置
    max_position_ratio: Decimal = Decimal('0.95')  # 最大仓位比例
    min_cash_ratio: Decimal = Decimal('0.05')      # 最小现金比例
    
    def __post_init__(self):
        """初始化后验证"""
        if self.start_date >= self.end_date:
            raise ValueError("开始日期必须早于结束日期")
        
        if self.initial_capital <= 0:
            raise ValueError("初始资金必须大于0")
        
        # 确保所有金额字段都是Decimal类型
        if not isinstance(self.initial_capital, Decimal):
            self.initial_capital = Decimal(str(self.initial_capital))


@dataclass 
class Position:
    """持仓信息"""
    symbol: str             # 标的代码
    quantity: Decimal       # 持仓数量
    avg_cost: Decimal       # 平均成本
    market_value: Decimal   # 市值
    unrealized_pnl: Decimal # 未实现盈亏
    
    def __post_init__(self):
        """确保类型正确"""
        for field in ['quantity', 'avg_cost', 'market_value', 'unrealized_pnl']:
            value = getattr(self, field)
            if not isinstance(value, Decimal):
                setattr(self, field, Decimal(str(value)))


@dataclass
class Transaction:
    """交易记录"""
    date: date              # 交易日期
    symbol: str            # 标的代码
    action: str            # 买入/卖出
    quantity: Decimal      # 交易数量
    price: Decimal         # 交易价格
    amount: Decimal        # 交易金额
    commission: Decimal    # 佣金
    stamp_duty: Decimal    # 印花税
    transfer_fee: Decimal  # 过户费
    total_cost: Decimal    # 总成本
    reason: str            # 交易原因
    signal_metadata: Dict[str, Any] = None  # 信号元数据
    
    def __post_init__(self):
        """确保类型正确"""
        decimal_fields = ['quantity', 'price', 'amount', 'commission', 
                         'stamp_duty', 'transfer_fee', 'total_cost']
        for field in decimal_fields:
            value = getattr(self, field)
            if not isinstance(value, Decimal):
                setattr(self, field, Decimal(str(value)))
        
        if self.signal_metadata is None:
            self.signal_metadata = {}


@dataclass
class BacktestResult:
    """回测结果"""
    # 基础信息
    config: BacktestConfig
    status: BacktestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # 资金状况
    initial_capital: Decimal = Decimal('0')
    final_capital: Decimal = Decimal('0')
    final_cash: Decimal = Decimal('0')
    final_market_value: Decimal = Decimal('0')
    
    # 收益指标
    total_return: Decimal = Decimal('0')        # 总收益率
    annualized_return: Decimal = Decimal('0')   # 年化收益率
    max_drawdown: Decimal = Decimal('0')        # 最大回撤
    sharpe_ratio: Decimal = Decimal('0')        # 夏普比率
    
    # 交易统计
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: Decimal = Decimal('0')
    
    # 详细数据
    transactions: List[Transaction] = None
    daily_values: List[Tuple[date, Decimal]] = None  # 每日组合价值
    positions: Dict[str, Position] = None
    
    def __post_init__(self):
        """初始化默认值"""
        if self.transactions is None:
            self.transactions = []
        if self.daily_values is None:
            self.daily_values = []
        if self.positions is None:
            self.positions = {}


class SimpleBacktestEngine:
    """
    简化版回测引擎
    
    专为定投策略设计的轻量级回测引擎，具有清晰的执行流程和状态管理。
    """
    
    def __init__(self):
        """初始化回测引擎"""
        self.result: Optional[BacktestResult] = None
        self.current_cash: Decimal = Decimal('0')
        self.positions: Dict[str, Position] = {}
        self.transactions: List[Transaction] = []
        self.daily_values: List[Tuple[date, Decimal]] = []
        
        logger.info("回测引擎初始化完成")
    
    def run_backtest(self, 
                    config: BacktestConfig, 
                    strategy: BaseStrategy,
                    price_data: Dict[str, Dict[date, Decimal]],
                    progress_callback: Optional[callable] = None) -> BacktestResult:
        """
        执行回测
        
        Args:
            config: 回测配置
            strategy: 策略实例
            price_data: 价格数据 {symbol: {date: price}}
            progress_callback: 进度回调函数
            
        Returns:
            BacktestResult: 回测结果
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"开始执行回测: {config.strategy_id}")
            logger.info(f"时间范围: {config.start_date} 到 {config.end_date}")
            logger.info(f"初始资金: {config.initial_capital}")
            
            # 初始化回测结果
            self.result = BacktestResult(
                config=config,
                status=BacktestStatus.RUNNING,
                start_time=start_time,
                initial_capital=config.initial_capital
            )
            
            # 初始化状态
            self._initialize_backtest_state(config)
            
            # 初始化策略
            strategy.initialize(config.strategy_params)
            
            # 验证数据完整性
            self._validate_price_data(price_data, config)
            
            # 执行回测主循环
            self._execute_backtest_loop(config, strategy, price_data, progress_callback)
            
            # 计算最终结果
            self._finalize_results()
            
            self.result.status = BacktestStatus.COMPLETED
            self.result.end_time = datetime.now()
            
            duration = self.result.end_time - start_time
            logger.info(f"回测完成，耗时: {duration.total_seconds():.2f}秒")
            logger.info(f"总收益率: {self.result.total_return:.4f}")
            logger.info(f"年化收益率: {self.result.annualized_return:.4f}")
            logger.info(f"最大回撤: {self.result.max_drawdown:.4f}")
            
        except Exception as e:
            error_msg = f"回测执行失败: {str(e)}"
            logger.error(error_msg)
            
            if self.result:
                self.result.status = BacktestStatus.FAILED
                self.result.error_message = error_msg
                self.result.end_time = datetime.now()
            else:
                # 如果result还没创建，创建一个失败的结果
                self.result = BacktestResult(
                    config=config,
                    status=BacktestStatus.FAILED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    error_message=error_msg
                )
            
            raise
        
        return self.result
    
    def _initialize_backtest_state(self, config: BacktestConfig):
        """初始化回测状态"""
        self.current_cash = config.initial_capital
        self.positions = {}
        self.transactions = []
        self.daily_values = []
        
        logger.debug(f"回测状态初始化完成，初始现金: {self.current_cash}")
    
    def _validate_price_data(self, price_data: Dict[str, Dict[date, Decimal]], config: BacktestConfig):
        """验证价格数据完整性"""
        if not price_data:
            raise ValueError("价格数据为空")
        
        # 检查每个标的的数据完整性
        for symbol, prices in price_data.items():
            if not prices:
                raise ValueError(f"标的 {symbol} 无价格数据")
            
            # 检查日期范围覆盖
            min_date = min(prices.keys())
            max_date = max(prices.keys())
            
            if min_date > config.start_date:
                logger.warning(f"标的 {symbol} 数据开始日期({min_date})晚于回测开始日期({config.start_date})")
            
            if max_date < config.end_date:
                logger.warning(f"标的 {symbol} 数据结束日期({max_date})早于回测结束日期({config.end_date})")
            
            logger.debug(f"标的 {symbol} 数据验证通过，共 {len(prices)} 个交易日")
    
    def _execute_backtest_loop(self, 
                              config: BacktestConfig, 
                              strategy: BaseStrategy,
                              price_data: Dict[str, Dict[date, Decimal]],
                              progress_callback: Optional[callable] = None):
        """执行回测主循环"""
        current_date = config.start_date
        total_days = (config.end_date - config.start_date).days
        processed_days = 0
        
        while current_date <= config.end_date:
            try:
                # 创建策略上下文
                context = self._create_strategy_context(current_date, price_data)
                
                # 生成交易信号
                signals = strategy.generate_signals(context)
                
                # 执行交易
                if signals:
                    self._execute_trades(signals, current_date, price_data, config)
                
                # 更新组合价值
                portfolio_value = self._calculate_portfolio_value(current_date, price_data)
                self.daily_values.append((current_date, portfolio_value))
                
                # 更新进度
                if progress_callback and processed_days % 10 == 0:  # 每10天回调一次
                    progress = processed_days / total_days
                    progress_callback(progress)
                
                processed_days += 1
                current_date += timedelta(days=1)
                
            except Exception as e:
                logger.error(f"处理日期 {current_date} 时发生错误: {str(e)}")
                # 在回测循环中遇到错误时，可以选择跳过该日期继续执行
                # 或者抛出异常终止回测，这里选择抛出异常
                raise
    
    def _create_strategy_context(self, current_date: date, price_data: Dict[str, Dict[date, Decimal]]) -> StrategyContext:
        """创建策略执行上下文"""
        portfolio_value = self._calculate_portfolio_value(current_date, price_data)
        
        return StrategyContext(
            current_date=current_date,
            cash=float(self.current_cash),
            portfolio_value=float(portfolio_value),
            positions={symbol: {
                'quantity': float(pos.quantity),
                'avg_cost': float(pos.avg_cost),
                'market_value': float(pos.market_value)
            } for symbol, pos in self.positions.items()},
            price_data={symbol: {
                d.isoformat(): float(price) 
                for d, price in prices.items()
                if d == current_date  # 只提供当前日期的价格
            } for symbol, prices in price_data.items()}
        )
    
    def _execute_trades(self, 
                       signals: List[TradeSignal], 
                       trade_date: date,
                       price_data: Dict[str, Dict[date, Decimal]],
                       config: BacktestConfig):
        """执行交易"""
        for signal in signals:
            try:
                self._execute_single_trade(signal, trade_date, price_data, config)
            except Exception as e:
                logger.error(f"执行交易信号失败 {signal.symbol} {signal.action}: {str(e)}")
    def _execute_trades(self, 
                       signals: List[TradeSignal], 
                       trade_date: date,
                       price_data: Dict[str, Dict[date, Decimal]],
                       config: BacktestConfig):
        """执行交易"""
        for signal in signals:
            try:
                self._execute_single_trade(signal, trade_date, price_data, config)
            except Exception as e:
                logger.error(f"执行交易信号失败 {signal.symbol} {signal.action}: {str(e)}")
                # 单个交易失败不应该终止整个回测
                continue
    
    def _execute_single_trade(self,
                             signal: TradeSignal,
                             trade_date: date, 
                             price_data: Dict[str, Dict[date, Decimal]],
                             config: BacktestConfig):
        """执行单个交易"""
        symbol = signal.symbol
        action = signal.action.lower()
        
        # 获取当日价格
        if symbol not in price_data or trade_date not in price_data[symbol]:
            logger.warning(f"无法获取 {symbol} 在 {trade_date} 的价格数据，跳过交易")
            return
        
        base_price = price_data[symbol][trade_date]
        
        # 应用滑点
        if config.enable_slippage:
            if action == "buy":
                execution_price = base_price * (Decimal('1') + config.slippage_rate)
            else:  # sell
                execution_price = base_price * (Decimal('1') - config.slippage_rate)
        else:
            execution_price = base_price
        
        if action == "buy":
            self._execute_buy_order(signal, trade_date, execution_price, config)
        elif action == "sell":
            self._execute_sell_order(signal, trade_date, execution_price, config)
        else:
            logger.warning(f"未知的交易动作: {action}")
    
    def _execute_buy_order(self,
                          signal: TradeSignal,
                          trade_date: date,
                          price: Decimal,
                          config: BacktestConfig):
        """执行买入订单"""
        symbol = signal.symbol
        
        # 确定购买金额（定投策略通常按金额购买）
        if hasattr(signal, 'amount') and signal.amount > 0:
            target_amount = Decimal(str(signal.amount))
        elif signal.weight > 0:
            # 如果没有指定金额，根据权重计算
            portfolio_value = self.current_cash + sum(pos.market_value for pos in self.positions.values())
            target_amount = portfolio_value * Decimal(str(signal.weight))
        else:
            logger.warning(f"买入信号缺少金额或权重信息: {symbol}")
            return
        
        # 检查现金是否足够
        if target_amount > self.current_cash:
            logger.warning(f"现金不足，无法买入 {symbol}，需要{target_amount}，可用{self.current_cash}")
            return
        
        # 计算可购买数量（股票以手为单位，ETF可以是1份）
        quantity = (target_amount / price).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        actual_amount = quantity * price
        
        if quantity <= 0:
            logger.warning(f"计算得到的购买数量为0: {symbol}, 价格: {price}, 金额: {target_amount}")
            return
        
        # 计算交易成本
        costs = self._calculate_transaction_costs(actual_amount, "buy", config)
        total_cost = actual_amount + costs['total']
        
        # 再次检查现金
        if total_cost > self.current_cash:
            logger.warning(f"加上交易成本后现金不足: 需要{total_cost}，可用{self.current_cash}")
            return
        
        # 执行买入
        self.current_cash -= total_cost
        
        # 更新持仓
        if symbol in self.positions:
            # 已有持仓，计算新的平均成本
            old_pos = self.positions[symbol]
            total_quantity = old_pos.quantity + quantity
            total_cost_basis = old_pos.quantity * old_pos.avg_cost + actual_amount
            new_avg_cost = total_cost_basis / total_quantity
            
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=total_quantity,
                avg_cost=new_avg_cost,
                market_value=total_quantity * price,
                unrealized_pnl=(price - new_avg_cost) * total_quantity
            )
        else:
            # 新持仓
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_cost=price,
                market_value=actual_amount,
                unrealized_pnl=Decimal('0')
            )
        
        # 记录交易
        transaction = Transaction(
            date=trade_date,
            symbol=symbol,
            action="buy",
            quantity=quantity,
            price=price,
            amount=actual_amount,
            commission=costs['commission'],
            stamp_duty=costs['stamp_duty'],
            transfer_fee=costs['transfer_fee'],
            total_cost=costs['total'],
            reason=signal.reason,
            signal_metadata=getattr(signal, 'metadata', {})
        )
        self.transactions.append(transaction)
        
        logger.debug(f"买入成功: {symbol} {quantity}份 @{price} 总成本{total_cost}")
    
    def _execute_sell_order(self,
                           signal: TradeSignal,
                           trade_date: date,
                           price: Decimal,
                           config: BacktestConfig):
        """执行卖出订单"""
        symbol = signal.symbol
        
        # 检查是否有持仓
        if symbol not in self.positions or self.positions[symbol].quantity <= 0:
            logger.warning(f"无持仓无法卖出: {symbol}")
            return
        
        current_pos = self.positions[symbol]
        
        # 确定卖出数量
        if signal.quantity > 0:
            sell_quantity = min(Decimal(str(signal.quantity)), current_pos.quantity)
        else:
            # 如果没有指定数量，默认全部卖出
            sell_quantity = current_pos.quantity
        
        sell_amount = sell_quantity * price
        
        # 计算交易成本
        costs = self._calculate_transaction_costs(sell_amount, "sell", config)
        net_proceeds = sell_amount - costs['total']  # 净收入
        
        # 执行卖出
        self.current_cash += net_proceeds
        
        # 更新持仓
        remaining_quantity = current_pos.quantity - sell_quantity
        if remaining_quantity > 0:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=remaining_quantity,
                avg_cost=current_pos.avg_cost,
                market_value=remaining_quantity * price,
                unrealized_pnl=(price - current_pos.avg_cost) * remaining_quantity
            )
        else:
            # 清空持仓
            del self.positions[symbol]
        
        # 记录交易
        transaction = Transaction(
            date=trade_date,
            symbol=symbol,
            action="sell",
            quantity=sell_quantity,
            price=price,
            amount=sell_amount,
            commission=costs['commission'],
            stamp_duty=costs['stamp_duty'],
            transfer_fee=costs['transfer_fee'],
            total_cost=costs['total'],
            reason=signal.reason,
            signal_metadata=getattr(signal, 'metadata', {})
        )
        self.transactions.append(transaction)
        
        logger.debug(f"卖出成功: {symbol} {sell_quantity}份 @{price} 净收入{net_proceeds}")
    
    def _calculate_transaction_costs(self, amount: Decimal, action: str, config: BacktestConfig) -> Dict[str, Decimal]:
        """计算交易成本"""
        costs = {
            'commission': Decimal('0'),
            'stamp_duty': Decimal('0'), 
            'transfer_fee': Decimal('0'),
            'total': Decimal('0')
        }
        
        # 佣金（买卖都有）
        commission = amount * config.commission_rate
        costs['commission'] = max(commission, config.min_commission)
        
        # 印花税（只有卖出时收取）
        if action.lower() == "sell":
            costs['stamp_duty'] = amount * config.stamp_duty_rate
        
        # 过户费（买卖都有，简化处理）
        costs['transfer_fee'] = amount * config.transfer_fee_rate
        
        # 总成本
        costs['total'] = costs['commission'] + costs['stamp_duty'] + costs['transfer_fee']
        
        # 四舍五入到分
        for key in costs:
            costs[key] = costs[key].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return costs
    
    def _calculate_portfolio_value(self, current_date: date, price_data: Dict[str, Dict[date, Decimal]]) -> Decimal:
        """计算组合总价值"""
        total_value = self.current_cash
        
        # 计算持仓市值
        for symbol, position in self.positions.items():
            if symbol in price_data and current_date in price_data[symbol]:
                current_price = price_data[symbol][current_date]
                market_value = position.quantity * current_price
                total_value += market_value
                
                # 更新持仓信息
                position.market_value = market_value
                position.unrealized_pnl = (current_price - position.avg_cost) * position.quantity
            else:
                # 如果没有当日价格，使用上一个价格（或平均成本）
                total_value += position.market_value
        
        return total_value
    
    def _finalize_results(self):
        """计算最终结果和性能指标"""
        if not self.result:
            return
        
        # 基础数据
        self.result.final_cash = self.current_cash
        self.result.final_market_value = sum(pos.market_value for pos in self.positions.values())
        self.result.final_capital = self.result.final_cash + self.result.final_market_value
        self.result.transactions = self.transactions.copy()
        self.result.daily_values = self.daily_values.copy()
        self.result.positions = {k: Position(**asdict(v)) for k, v in self.positions.items()}
        
        # 计算收益指标
        if self.result.initial_capital > 0:
            self.result.total_return = (self.result.final_capital - self.result.initial_capital) / self.result.initial_capital
        
        # 计算年化收益率
        if len(self.daily_values) > 1:
            days = len(self.daily_values)
            years = days / 365.0
            if years > 0:
                self.result.annualized_return = ((self.result.final_capital / self.result.initial_capital) ** (1/years)) - 1
        
        # 计算最大回撤
        self.result.max_drawdown = self._calculate_max_drawdown()
        
        # 计算夏普比率（简化版）
        self.result.sharpe_ratio = self._calculate_sharpe_ratio()
        
        # 交易统计
        self.result.total_trades = len(self.transactions)
        
        # 胜率统计（基于每次买入后的最终盈亏）
        buy_trades = [t for t in self.transactions if t.action == "buy"]
        sell_trades = [t for t in self.transactions if t.action == "sell"] 
        
        # 简化的胜率计算（实际应该更复杂）
        if buy_trades and sell_trades:
            winning_count = 0
            for sell_trade in sell_trades:
                # 找到对应的买入交易（简化处理）
                buy_trade = next((b for b in buy_trades if b.symbol == sell_trade.symbol), None)
                if buy_trade and sell_trade.price > buy_trade.price:
                    winning_count += 1
            
            self.result.winning_trades = winning_count
            self.result.losing_trades = len(sell_trades) - winning_count
            self.result.win_rate = Decimal(str(winning_count)) / Decimal(str(len(sell_trades)))
    
    def _calculate_max_drawdown(self) -> Decimal:
        """计算最大回撤"""
        if len(self.daily_values) < 2:
            return Decimal('0')
        
        max_drawdown = Decimal('0')
        peak = self.daily_values[0][1]  # 历史最高点
        
        for date, value in self.daily_values[1:]:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self) -> Decimal:
        """计算夏普比率（简化版）"""
        if len(self.daily_values) < 2:
            return Decimal('0')
        
        # 计算日收益率
        daily_returns = []
        for i in range(1, len(self.daily_values)):
            prev_value = self.daily_values[i-1][1]
            curr_value = self.daily_values[i][1]
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                daily_returns.append(daily_return)
        
        if not daily_returns:
            return Decimal('0')
        
        # 计算平均收益和标准差
        avg_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
        std_dev = variance ** Decimal('0.5')
        
        # 夏普比率（假设无风险利率为0）
        if std_dev > 0:
            sharpe = avg_return / std_dev * (Decimal('252') ** Decimal('0.5'))  # 年化
            return sharpe
        
        return Decimal('0')
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """获取回测摘要统计"""
        if not self.result:
            return {}
        
        return {
            "基础信息": {
                "策略ID": self.result.config.strategy_id,
                "回测期间": f"{self.result.config.start_date} 至 {self.result.config.end_date}",
                "初始资金": f"{self.result.initial_capital:,.2f} 元",
                "最终资金": f"{self.result.final_capital:,.2f} 元",
                "状态": self.result.status.value
            },
            "收益指标": {
                "总收益率": f"{self.result.total_return:.4%}",
                "年化收益率": f"{self.result.annualized_return:.4%}",
                "最大回撤": f"{self.result.max_drawdown:.4%}",
                "夏普比率": f"{self.result.sharpe_ratio:.4f}"
            },
            "交易统计": {
                "总交易次数": self.result.total_trades,
                "盈利交易": self.result.winning_trades,
                "亏损交易": self.result.losing_trades,
                "胜率": f"{self.result.win_rate:.2%}" if self.result.win_rate else "N/A"
            },
            "资产配置": {
                "现金": f"{self.result.final_cash:,.2f} 元",
                "市值": f"{self.result.final_market_value:,.2f} 元",
                "持仓数量": len(self.result.positions)
            }
        }


def create_simple_backtest_engine() -> SimpleBacktestEngine:
    """工厂函数：创建简化回测引擎实例"""
    return SimpleBacktestEngine()