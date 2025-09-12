#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DCA策略图表数据生成
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.strategies.dca_strategy import DCAStrategy
from app.core.data_source import data_manager
import backtrader as bt
from datetime import datetime

def test_dca_daily_data():
    """测试DCA策略的daily_values数据生成"""
    print("=== 测试DCA策略图表数据生成 ===")
    
    # 创建Backtrader引擎
    cerebro = bt.Cerebro()
    
    # 设置初始资金
    cerebro.broker.setcash(100000)
    
    # 添加DCA策略
    cerebro.addstrategy(DCAStrategy,
        investment_amount=2000,
        frequency_days=7,  # 周投
        symbol='510300',
        exit_strategy='hold'
    )
    
    # 获取测试数据
    try:
        print("获取测试数据...")
        df = data_manager.get_data('510300', '2024-01-01', '2024-03-31')
        print(f"数据获取成功，共{len(df)}条记录")
        
        # 创建数据源
        data = bt.feeds.PandasData(
            dataname=df.reset_index(),
            datetime='Date',
            open='Open',
            high='High',
            low='Low',
            close='Close',
            volume='Volume',
            openinterest=-1
        )
        
        cerebro.adddata(data)
        
        # 运行回测
        print("开始运行回测...")
        results = cerebro.run()
        strategy = results[0]
        
        # 获取每日数据
        daily_prices = strategy.daily_prices
        daily_portfolio_values = strategy.daily_portfolio_values
        daily_dates = strategy.daily_dates
        daily_returns = strategy.daily_returns
        
        print(f"每日价格数据: {len(daily_prices)} 条")
        print(f"每日组合价值数据: {len(daily_portfolio_values)} 条") 
        print(f"每日日期数据: {len(daily_dates)} 条")
        print(f"每日收益率数据: {len(daily_returns)} 条")
        
        if daily_prices:
            print(f"标的价格范围: {min(daily_prices):.2f} - {max(daily_prices):.2f}")
            print(f"前5个价格: {daily_prices[:5]}")
            print(f"后5个价格: {daily_prices[-5:]}")
            
        if daily_portfolio_values:
            print(f"投资组合价值范围: {min(daily_portfolio_values):.2f} - {max(daily_portfolio_values):.2f}")
        
        if daily_dates:
            print(f"日期范围: {daily_dates[0]} - {daily_dates[-1]}")
            
        # 获取性能指标
        metrics = strategy.get_performance_metrics()
        print(f"定投记录: {len(metrics.get('investment_records', []))} 次")
        
        # 验证双Y轴数据一致性
        if len(daily_prices) == len(daily_portfolio_values) == len(daily_dates):
            print(f"✅ 双Y轴数据长度一致: {len(daily_prices)} 条")
        else:
            print(f"❌ 数据长度不一致: 价格{len(daily_prices)}, 组合{len(daily_portfolio_values)}, 日期{len(daily_dates)}")
        
        # 显示关键数据点对比
        if daily_prices and daily_portfolio_values:
            mid_index = len(daily_prices) // 2
            print(f"中间数据点对比:")
            print(f"  日期: {daily_dates[mid_index]}")
            print(f"  价格: ¥{daily_prices[mid_index]:.2f}")
            print(f"  组合价值: ¥{daily_portfolio_values[mid_index]:.2f}")
            
            # 验证是否真的有每日数据
            print(f"\n📊 数据密度验证:")
            print(f"  总时间跨度: {daily_dates[0]} 到 {daily_dates[-1]}")
            print(f"  数据点数量: {len(daily_prices)} 个")
            print(f"  定投次数: {len(metrics.get('investment_records', []))} 次")
            print(f"  数据/定投比例: {len(daily_prices) / len(metrics.get('investment_records', [1])):.1f}:1")
            
            # 显示前5个交易日的波动
            print(f"\n📈 前5个交易日价格波动:")
            for i in range(min(5, len(daily_prices))):
                print(f"  {daily_dates[i]}: ¥{daily_prices[i]:.3f}")
                
            print(f"\n💰 对应投资组合价值:")
            for i in range(min(5, len(daily_portfolio_values))):
                print(f"  {daily_dates[i]}: ¥{daily_portfolio_values[i]:.2f}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dca_daily_data()
    if success:
        print("\n✅ 测试成功！图表数据生成正常")
    else:
        print("\n❌ 测试失败！")