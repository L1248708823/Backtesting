# -*- coding: utf-8 -*-
"""
简单测试脚本 - 测试DCA策略功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# 直接测试策略功能，避开复杂的导入
import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime, date

# 简化版本的DCA策略（直接定义，避免导入问题）
class SimpleDCAStrategy(bt.Strategy):
    """简化版DCA定投策略"""
    
    params = (
        ('investment_amount', 1000),
        ('frequency_days', 30),
    )
    
    def __init__(self):
        self.last_investment_date = None
        self.investment_count = 0
        
    def next(self):
        current_date = self.datas[0].datetime.date(0)
        
        if self.should_invest(current_date):
            self.execute_investment()
    
    def should_invest(self, current_date):
        if self.last_investment_date is None:
            return True
            
        days_since_last = (current_date - self.last_investment_date).days
        return days_since_last >= self.params.frequency_days
    
    def execute_investment(self):
        current_price = self.datas[0].close[0]
        shares_to_buy = int(self.params.investment_amount / current_price)
        
        if shares_to_buy > 0:
            self.buy(size=shares_to_buy)
            self.last_investment_date = self.datas[0].datetime.date(0)
            self.investment_count += 1
            
            actual_amount = shares_to_buy * current_price
            print(f'第{self.investment_count}次定投: 价格={current_price:.2f}, 股数={shares_to_buy}, 实际金额={actual_amount:.2f}')


def generate_test_data():
    """生成测试数据"""
    # 生成2023年1月到12月的交易日数据
    date_range = pd.bdate_range(start='2023-01-01', end='2023-12-31')
    
    # 生成模拟价格数据
    np.random.seed(42)
    base_price = 3.5
    
    returns = np.random.normal(0.0005, 0.02, len(date_range))
    prices = [base_price]
    
    for return_rate in returns[1:]:
        next_price = prices[-1] * (1 + return_rate)
        prices.append(max(next_price, 0.1))
    
    # 构建OHLC数据
    df = pd.DataFrame({
        'datetime': date_range,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': [1000000] * len(date_range)
    })
    
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


def test_dca_strategy():
    """测试DCA策略"""
    print("=" * 50)
    print("开始测试DCA定投策略")
    print("=" * 50)
    
    # 创建Backtrader引擎
    cerebro = bt.Cerebro()
    
    # 设置初始资金
    initial_cash = 10000.0
    cerebro.broker.setcash(initial_cash)
    
    # 添加策略
    cerebro.addstrategy(SimpleDCAStrategy, investment_amount=500, frequency_days=30)
    
    # 添加数据
    data = generate_test_data()
    cerebro.adddata(data)
    
    # 记录初始资金
    initial_value = cerebro.broker.getvalue()
    print(f'初始资金: {initial_value:.2f}')
    
    # 运行回测
    print("\n开始执行回测...")
    results = cerebro.run()
    
    # 获取最终结果
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - initial_value) / initial_value * 100
    
    print(f'\n最终资金: {final_value:.2f}')
    print(f'总收益率: {total_return:.2f}%')
    print(f'绝对收益: {final_value - initial_value:.2f}')
    
    print("\n=" * 50)
    print("DCA策略测试完成")
    print("=" * 50)
    
    return {
        'initial_value': initial_value,
        'final_value': final_value,
        'total_return': total_return
    }


if __name__ == "__main__":
    result = test_dca_strategy()
    print(f"\n测试结果: {result}")