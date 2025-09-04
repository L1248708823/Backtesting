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
        symbol = request.parameters.get('symbol', '510300')
        try:
            data = get_real_data(
                symbol,
                request.start_date, 
                request.end_date
            )
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


# 假数据生成函数已删除 - 没有真实数据就直接报错，不自欺欺人