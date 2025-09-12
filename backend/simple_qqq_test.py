# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import requests
import time

print("开始测试QQQ数据获取 - 使用增强配置...")

# 设置代理和用户代理
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# 设置代理
session.proxies.update({
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897'
})

def test_symbol_with_retry(symbol, max_retries=1):
    """带重试的股票数据获取测试"""
    for attempt in range(max_retries):
        try:
            print(f"\n尝试获取 {symbol} 数据 (第 {attempt + 1}/{max_retries} 次)")
            
            # ticker = yf.Ticker(symbol, session=session)
            ticker = yf.Ticker('AAPL')
            df = ticker.history(
                start="2024-11-01",
                end="2024-12-01",
                interval="1d",
                prepost=False,
                auto_adjust=True,
                back_adjust=False,
                repair=True,
                keepna=False,
                timeout=30
            )
            print(f"成功获取 {symbol} 数据: {df} ")
            
            if df.empty:
                print(f"WARNING: {symbol} 数据为空 (尝试 {attempt + 1})")
                if attempt < max_retries - 1:
                    print(f"等待2秒后重试...")
                    time.sleep(2)
                    continue
                else:
                    print(f"ERROR: {symbol} 所有尝试均失败")
                    return False
            else:
                print(f"SUCCESS: {symbol} 获取到 {len(df)} 条数据")
                print(f"日期范围: {df.index[0].date()} 到 {df.index[-1].date()}")
                print(f"最新收盘价: ${df['Close'][-1]:.2f}")
                return True
                
        except Exception as e:
            print(f"ERROR: {symbol} 尝试 {attempt + 1} 失败: {e}")
            if attempt < max_retries - 1:
                print(f"等待2秒后重试...")
                time.sleep(2)
            else:
                print(f"ERROR: {symbol} 所有尝试均失败")
                return False

# 测试多个美股ETF
symbols = ["QQQ", "SPY", "IWM", "VTI"]
for symbol in symbols:
    success = test_symbol_with_retry(symbol)
    print(f"{symbol} 测试结果: {'成功' if success else '失败'}")

print("\n测试完成")