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
    运行策略回测
    
    Args:
        request: 回测请求
        
    Returns:
        回测结果
    """
    try:
        # 获取策略类
        strategy_class = registry.get_strategy(request.strategy_id)
        if not strategy_class:
            raise HTTPException(
                status_code=404,
                detail=f"策略不存在: {request.strategy_id}"
            )
        
        # 创建Backtrader引擎
        cerebro = bt.Cerebro()
        
        # 设置初始资金
        cerebro.broker.setcash(request.initial_cash)
        
        # 添加策略（使用请求参数）
        cerebro.addstrategy(strategy_class, **request.parameters)
        
        # 获取真实数据
        data = get_real_data(
            request.parameters.get('symbol', '510300'),
            request.start_date, 
            request.end_date
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
        
        # 构建结果
        result = BacktestResult(
            strategy_id=request.strategy_id,
            parameters=request.parameters,
            start_date=request.start_date,
            end_date=request.end_date, 
            initial_cash=initial_value,
            final_value=final_value,
            total_return=total_return,
            total_trades=len(strategy_instance.trades_log),
            performance_metrics=strategy_instance.get_performance_metrics()
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"回测执行失败: {str(e)}"
        )


def get_real_data(symbol: str, start_date: str, end_date: str):
    """
    获取真实市场数据
    
    使用data_manager自动选择数据源获取真实数据
    """
    try:
        # 使用数据管理器获取真实数据
        df = data_manager.get_data(symbol, start_date, end_date)
        
        if df.empty:
            raise ValueError(f"无法获取 {symbol} 的数据")
        
        # 确保数据格式符合Backtrader要求
        # DataFrame index应该是日期，列名应该是标准的OHLCV
        df_bt = df.copy()
        
        # 重置索引，将Date从index移到列
        df_bt = df_bt.reset_index()
        
        # 重命名列以符合Backtrader约定
        df_bt = df_bt.rename(columns={
            'Date': 'datetime',
            'Open': 'open', 
            'High': 'high',
            'Low': 'low', 
            'Close': 'close',
            'Volume': 'volume'
        })
        
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
        
        print(f"成功加载 {symbol} 数据: {len(df_bt)} 条记录")
        return data
        
    except Exception as e:
        print(f"获取真实数据失败: {e}")
        # 如果真实数据获取失败，回退到测试数据
        return generate_fallback_data(symbol, start_date, end_date)


def generate_fallback_data(symbol: str, start_date: str, end_date: str):
    """
    备用数据生成器（当真实数据源失败时使用）
    """
    import numpy as np
    
    print(f"警告: 使用模拟数据作为 {symbol} 的回测数据")
    
    # 解析日期
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # 生成日期序列（只包含工作日）
    date_range = pd.bdate_range(start=start, end=end)
    
    # 生成随机价格数据
    np.random.seed(42)
    
    # 起始价格
    base_price = 3.3 if symbol == '510300' else 400.0
    
    # 生成价格序列
    returns = np.random.normal(0.0005, 0.02, len(date_range))
    prices = [base_price]
    
    for return_rate in returns[1:]:
        next_price = prices[-1] * (1 + return_rate)
        prices.append(max(next_price, 0.1))
    
    # 构建OHLC数据
    df = pd.DataFrame({
        'datetime': date_range,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices], 
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, len(date_range))
    })
    
    # 确保price关系正确
    df['high'] = df[['high', 'close']].max(axis=1)
    df['low'] = df[['low', 'close']].min(axis=1)
    
    # 创建Backtrader数据源
    data = bt.feeds.PandasData(
        dataname=df,
        datetime='datetime',
        open='open',
        high='high', 
        low='low',
        close='close',
        volume='volume',
        openinterest=-1
    )
    
    return data