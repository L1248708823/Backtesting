# -*- coding: utf-8 -*-
"""
回测相关API接口
"""

import backtrader as bt
import pandas as pd
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core.strategy_registry import registry
from ..core.data_source import data_manager
from datetime import datetime as dt

router = APIRouter(prefix="/api/v1/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    """回测请求模型"""
    strategy_id: str
    parameters: Dict[str, Any]
    start_date: str  # YYYY-MM-DD格式
    end_date: str    # YYYY-MM-DD格式
    initial_cash: float = 10000.0


class BacktestResult(BaseModel):
    """回测结果模型"""
    strategy_id: str
    parameters: Dict[str, Any]
    start_date: str
    end_date: str
    initial_cash: float
    final_value: float
    total_return: float
    total_trades: int
    performance_metrics: Dict[str, Any]


@router.post("/run", response_model=BacktestResult)
async def run_backtest(request: BacktestRequest):
    """
    运行策略回测 - 新版本支持双重回测对比
    
    对于DCA策略：
    - 如果exit_strategy != 'hold'，会额外运行一次hold策略作为基准
    - 基准对比数据来自实际回测结果，不是理论计算
    
    Args:
        request: 回测请求
        
    Returns:
        回测结果（包含准确的基准对比数据）
    """
    try:
        # 获取策略类
        strategy_class = registry.get_strategy(request.strategy_id)
        if not strategy_class:
            raise HTTPException(
                status_code=404,
                detail=f"策略不存在: {request.strategy_id}"
            )
        
        # 执行主策略回测
        main_result = await _run_single_backtest(
            strategy_class, 
            request.parameters, 
            request.initial_cash,
            request.start_date,
            request.end_date
        )
        
        # 检查是否需要双重回测（仅DCA策略 + 非hold策略）
        is_dca = request.strategy_id == "dca_strategy"
        exit_strategy = request.parameters.get('exit_strategy', 'hold')
        need_dual_backtest = is_dca and exit_strategy != 'hold'
        
        if need_dual_backtest:
            # 执行基准策略回测（强制exit_strategy='hold'）
            benchmark_params = request.parameters.copy()
            benchmark_params['exit_strategy'] = 'hold'
            
            benchmark_result = await _run_single_backtest(
                strategy_class,
                benchmark_params,
                request.initial_cash, 
                request.start_date,
                request.end_date
            )
            
            # 将基准回测结果注入到主结果的benchmark_comparison中
            main_result.performance_metrics['benchmark_comparison'] = _create_dual_backtest_comparison(
                main_result, benchmark_result, exit_strategy
            )
        
        # 构建最终结果
        result = BacktestResult(
            strategy_id=request.strategy_id,
            parameters=request.parameters,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_cash=main_result.initial_cash,
            final_value=main_result.final_value,
            total_return=main_result.total_return,
            total_trades=main_result.performance_metrics.get('buy_orders', 0),
            performance_metrics=main_result.performance_metrics
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"回测执行失败: {str(e)}"
        )


async def _run_single_backtest(strategy_class, parameters: Dict[str, Any], 
                              initial_cash: float, start_date: str, end_date: str):
    """
    执行单次回测
    
    Args:
        strategy_class: 策略类
        parameters: 策略参数
        initial_cash: 初始资金
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        回测结果对象
    """
    # 创建Backtrader引擎
    cerebro = bt.Cerebro()
    
    # 设置初始资金
    cerebro.broker.setcash(initial_cash)
    
    # 添加策略（使用请求参数）
    cerebro.addstrategy(strategy_class, **parameters)
    
    # 添加Backtrader内置分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 获取真实数据
    symbol = parameters.get('symbol', '510300')
    try:
        data = get_real_data(symbol, start_date, end_date)
    except Exception as data_error:
        raise HTTPException(
            status_code=400,
            detail=f"数据获取失败 [{symbol}]: {str(data_error)}"
        )
    
    # 添加数据源
    cerebro.adddata(data)
    
    # 记录初始资金
    initial_value = cerebro.broker.getvalue()
    
    # 运行回测
    results = cerebro.run()
    
    # 获取最终资金
    final_value = cerebro.broker.getvalue()
    
    # 获取策略实例（用于获取性能指标）
    strategy_instance = results[0]
    
    # 计算收益率
    total_return = (final_value - initial_value) / initial_value * 100
    
    # 获取Backtrader内置分析器结果
    bt_analyzers = {
        'sharpe': strategy_instance.analyzers.sharpe.get_analysis(),
        'drawdown': strategy_instance.analyzers.drawdown.get_analysis(),
        'returns': strategy_instance.analyzers.returns.get_analysis(),
        'trades': strategy_instance.analyzers.trades.get_analysis()
    }
    
    # 获取策略自定义指标（DCA特殊数据等）
    strategy_metrics = strategy_instance.get_performance_metrics()
    
    # 合并内置分析器结果与自定义指标
    performance_metrics = merge_backtrader_and_custom_metrics(bt_analyzers, strategy_metrics, 
                                                             initial_value, final_value,
                                                             start_date, end_date)
    
    # 创建结果对象 
    class BacktestResultInternal:
        def __init__(self, initial_cash, final_value, total_return, performance_metrics):
            self.initial_cash = initial_cash
            self.final_value = final_value
            self.total_return = total_return
            self.performance_metrics = performance_metrics
    
    return BacktestResultInternal(initial_value, final_value, total_return, performance_metrics)


def _create_dual_backtest_comparison(main_result, benchmark_result, exit_strategy: str) -> Dict[str, Any]:
    """
    基于双重回测结果创建准确的基准对比数据
    
    Args:
        main_result: 主策略回测结果（带止盈）
        benchmark_result: 基准策略回测结果（纯hold）
        exit_strategy: 止盈策略类型
        
    Returns:
        基准对比分析数据
    """
    # 提取主策略数据
    main_metrics = main_result.performance_metrics
    main_investment = main_metrics.get('total_invested', 0)
    main_shares = main_metrics.get('total_shares', 0)
    main_avg_cost = main_metrics.get('average_cost', 0)
    
    # 提取基准策略数据
    bench_metrics = benchmark_result.performance_metrics
    bench_investment = bench_metrics.get('total_invested', 0)
    bench_shares = bench_metrics.get('total_shares', 0)
    bench_avg_cost = bench_metrics.get('average_cost', 0)
    
    # 计算差异
    return_difference = main_result.total_return - benchmark_result.total_return
    shares_difference = bench_shares - main_shares  # 基准持有的更多（因为没卖出）
    value_difference = main_result.final_value - benchmark_result.final_value
    
    # 检查是否实际执行了止盈（通过卖出记录判断）
    exit_actually_executed = len(main_metrics.get('sell_records', [])) > 0
    
    # 策略描述
    strategy_descriptions = {
        'profit_target': f"目标收益止盈 - 达到收益率后全部卖出",
        'time_limit': f"时间止盈 - 到期后自动卖出",
        'batch_exit': "分批止盈 - 达到不同收益点位时分批卖出"
    }
    
    return {
        # 策略描述
        'current_exit_strategy': exit_strategy,
        'strategy_description': strategy_descriptions.get(exit_strategy, f"未知策略: {exit_strategy}"),
        
        # 基准策略数据（DCA纯持有，来自真实回测）
        'benchmark_investment': bench_investment,
        'benchmark_shares': bench_shares,
        'benchmark_average_cost': bench_avg_cost,
        'benchmark_current_value': benchmark_result.final_value,
        'benchmark_return': benchmark_result.total_return,
        
        # 主策略数据（DCA带止盈，来自真实回测）
        'dca_investment': main_investment,
        'dca_shares': main_shares,
        'dca_average_cost': main_avg_cost,
        'dca_current_value': main_result.final_value,
        'dca_return': main_result.total_return,
        
        # 对比分析
        'return_difference': return_difference,
        'shares_difference': shares_difference,
        'value_difference': value_difference,
        'exit_strategy_better': return_difference > 0,
        'is_same_strategy': False,  # 双重回测必然不同策略
        'exit_actually_executed': exit_actually_executed,
        
        # 定投统计（从主策略获取）
        'total_investment_count': len(main_metrics.get('investment_records', [])),
        'investment_duration_months': _calculate_duration_months(main_metrics.get('investment_records', [])),
        'investment_frequency_actual': main_metrics.get('investment_frequency_actual', 30),
        
        # 风险分析
        'price_volatility_during_period': main_metrics.get('price_range', {}).get('price_volatility', 0)
    }


def _calculate_duration_months(investment_records) -> float:
    """计算投资持续月数"""
    if not investment_records or len(investment_records) < 2:
        return 0
    
    from datetime import datetime
    start_date = datetime.strptime(investment_records[0]['date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(investment_records[-1]['date'], '%Y-%m-%d').date()
    
    return round((end_date - start_date).days / 30.0, 1)


def get_real_data(symbol: str, start_date: str, end_date: str):
    """
    获取真实市场数据
    
    使用data_manager自动选择数据源获取真实数据
    
    Args:
        symbol: 证券代码 (如510300, SPY)
        start_date: 开始日期 YYYY-MM-DD
        end_date: 结束日期 YYYY-MM-DD
        
    Returns:
        Backtrader数据源
        
    Raises:
        ValueError: 数据获取失败或数据为空
    """
    try:
        # 使用数据管理器获取真实数据
        df = data_manager.get_data(symbol, start_date, end_date)
        
        if df.empty:
            raise ValueError(f"未找到标的 {symbol} 在 {start_date} 至 {end_date} 期间的数据，请检查代码和日期范围")
        
        # 数据质量检查
        if len(df) < 10:
            raise ValueError(f"数据量过少 ({len(df)} 条)，无法进行有效回测，建议扩大时间范围")
        
        # 确保数据格式符合Backtrader要求
        df_bt = df.copy().reset_index()
        
        # 重命名列以符合Backtrader约定
        df_bt = df_bt.rename(columns={
            'Date': 'datetime',
            'Open': 'open', 
            'High': 'high',
            'Low': 'low', 
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # 验证必要的列存在
        required_columns = ['datetime', 'open', 'high', 'low', 'close']
        missing_columns = [col for col in required_columns if col not in df_bt.columns]
        if missing_columns:
            raise ValueError(f"数据缺少必要列: {missing_columns}")
        
        # 创建Backtrader数据源
        data = bt.feeds.PandasData(
            dataname=df_bt,
            datetime='datetime',
            open='open',
            high='high',
            low='low', 
            close='close',
            volume='volume',
            openinterest=-1  # 不使用持仓量
        )
        
        return data
        
    except ValueError:
        # 重新抛出ValueError，保持错误信息
        raise
    except Exception as e:
        # 其他异常统一包装
        raise ValueError(f"数据源连接失败: {str(e)}，请检查网络连接或稍后重试")


def merge_backtrader_and_custom_metrics(bt_analyzers: Dict, strategy_metrics: Dict, 
                                        initial_value: float, final_value: float,
                                        start_date: str, end_date: str) -> Dict[str, Any]:
    """
    合并Backtrader内置分析器结果与策略自定义指标
    
    Args:
        bt_analyzers: Backtrader分析器结果
        strategy_metrics: 策略自定义指标
        initial_value: 初始资金
        final_value: 最终资金
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        合并后的完整性能指标
    """
    # 提取Backtrader分析器数据
    sharpe_data = bt_analyzers.get('sharpe', {})
    drawdown_data = bt_analyzers.get('drawdown', {})
    returns_data = bt_analyzers.get('returns', {})
    trades_data = bt_analyzers.get('trades', {})
    
    # 计算基础指标
    total_return = (final_value - initial_value) / initial_value * 100
    
    # 计算时间相关数据
    start_dt = dt.strptime(start_date, '%Y-%m-%d')
    end_dt = dt.strptime(end_date, '%Y-%m-%d')
    total_days = (end_dt - start_dt).days
    total_years = total_days / 365.0
    
    # 尝试从Returns分析器获取年化收益率，否则用自己计算的兜底
    annual_return = 0.0
    returns_data = bt_analyzers.get('returns', {})
    if returns_data:
        # Backtrader Returns分析器可能提供年化数据，这里简化处理
        # 如果框架没有直接的年化收益率，仍用复合增长率公式
        annual_return = (final_value / initial_value) ** (1/total_years) - 1 if total_years > 0 else 0
    else:
        # 兜底计算
        annual_return = (final_value / initial_value) ** (1/total_years) - 1 if total_years > 0 else 0
    
    # 构建合并结果
    merged_metrics = {
        # 基础指标
        'start_value': initial_value,
        'end_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return * 100,
        'total_days': total_days,
        
        # Backtrader内置分析器结果  
        'sharpe_ratio': sharpe_data.get('sharperatio', 0.0),
        'max_drawdown': abs(drawdown_data.get('max', {}).get('drawdown', 0.0)),  # Backtrader已经是百分比形式
        'max_drawdown_duration': drawdown_data.get('max', {}).get('len', 0),
        
        # 交易统计 (优先使用内置分析器)
        'total_trades': trades_data.get('total', {}).get('closed', 0),
        'winning_trades': trades_data.get('won', {}).get('total', 0),
        'losing_trades': trades_data.get('lost', {}).get('total', 0),
        'win_rate': (trades_data.get('won', {}).get('total', 0) / 
                    max(trades_data.get('total', {}).get('closed', 1), 1)) * 100,
        
        # 策略特殊数据（从自定义指标获取）
        **{k: v for k, v in strategy_metrics.items() if k in [
            'buy_orders', 'sell_orders', 'buy_records', 'sell_records',
            'investment_records', 'total_invested', 'total_shares', 'average_cost',
            'cost_reduction_effect', 'investment_efficiency', 'current_position_value',
            'unrealized_pnl', 'unrealized_return', 'price_range', 'daily_values',
            'daily_returns', 'daily_dates', 'benchmark_comparison'
        ]},
        
        # 波动率计算（如果自定义指标中有）
        'volatility': strategy_metrics.get('volatility', 0.0),
    }
    
    return merged_metrics


# 假数据生成函数已删除 - 没有真实数据就直接报错，不自欺欺人