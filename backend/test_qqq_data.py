# -*- coding: utf-8 -*-
"""
QQQ数据获取诊断脚本
用于测试和修复美股ETF数据获取问题
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

def test_qqq_basic():
    """基础QQQ数据获取测试"""
    print("=== 基础QQQ数据获取测试 ===")
    my_proxy = {
              'http': 'http://127.0.0.1:7897',
              'https': 'http://127.0.0.1:7897'
          }
    try:
        data1 = yf.download("QQQ", start="2024-12-01", end="2024-12-10", proxy=my_proxy)
        print(f"download成功: {data1.shape}")
        # ticker = yf.Ticker("QQQ")
        # print(f"QQQ Ticker对象创建成功")
        
        # 获取基本信息
        # info = ticker.info
        # print(f"QQQ基本信息: {info.get('shortName', 'N/A')}")
        
    except Exception as e:
        print(f"QQQ基础测试失败: {e}")

def test_qqq_history_different_periods():
    """测试不同时间段的QQQ历史数据"""
    print("\n=== QQQ历史数据测试 - 不同时间段 ===")
    
    test_periods = [
        ("1个月", "2024-11-01", "2024-12-01"),
        ("3个月", "2024-09-01", "2024-12-01"), 
        ("1年", "2023-12-01", "2024-12-01"),
        ("最近30天", None, None)  # 使用period参数
    ]
    
    ticker = yf.Ticker("QQQ")
    
    for period_name, start, end in test_periods:
        try:
            print(f"\n测试 {period_name}:")
            
            if start is None:
                # 使用period参数
                df = ticker.history(period="1mo")
            else:
                df = ticker.history(start=start, end=end)
            
            if df.empty:
                print(f"  ❌ {period_name}: 无数据")
            else:
                print(f"  ✅ {period_name}: {len(df)}条记录")
                print(f"  📊 日期范围: {df.index[0].date()} 到 {df.index[-1].date()}")
                print(f"  💰 最新收盘价: ${df['Close'][-1]:.2f}")
                
        except Exception as e:
            print(f"  ❌ {period_name}: 错误 - {e}")

def test_qqq_with_enhanced_params():
    """使用增强参数测试QQQ数据获取"""
    print("\n=== QQQ增强参数测试 ===")
    
    try:

        data1 = yf.download("QQQ", start="2024-12-01", end="2024-12-10", proxy=my_proxy)
        print(f"download成功: {data1.shape}")
        ticker = yf.Ticker("QQQ")
        
        # 使用更多参数
        df = ticker.history(
            start="2024-01-01",
            end="2024-12-01", 
            interval="1d",           # 明确指定日线
            prepost=False,           # 排除盘前盘后
            auto_adjust=True,        # 自动复权
            back_adjust=False,       # 不反向复权
            repair=True,             # 修复数据
            keepna=False,            # 删除NA值
            proxy=None,              # 不使用代理
            rounding=True,           # 四舍五入
            timeout=10               # 设置超时
        )
        
        if df.empty:
            print("  ❌ 增强参数测试: 无数据")
        else:
            print(f"  ✅ 增强参数测试: {len(df)}条记录")
            print(f"  📊 日期范围: {df.index[0].date()} 到 {df.index[-1].date()}")
            print(f"  📈 数据完整性检查:")
            print(f"    - Open列: {df['Open'].notna().sum()}/{len(df)}")
            print(f"    - Close列: {df['Close'].notna().sum()}/{len(df)}")
            print(f"    - Volume列: {df['Volume'].notna().sum()}/{len(df)}")
            
    except Exception as e:
        print(f"  ❌ 增强参数测试失败: {e}")

def test_multiple_us_etfs():
    """测试多个美股ETF"""
    print("\n=== 多个美股ETF测试 ===")
    
    symbols = ["QQQ", "SPY", "IWM", "VTI", "TQQQ"]
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d")  # 最近5天
            
            if df.empty:
                print(f"  ❌ {symbol}: 无数据")
            else:
                print(f"  ✅ {symbol}: {len(df)}条记录, 最新价格: ${df['Close'][-1]:.2f}")
                
        except Exception as e:
            print(f"  ❌ {symbol}: 错误 - {e}")

def test_network_and_retry():
    """网络重试机制测试"""
    print("\n=== 网络重试机制测试 ===")
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"  尝试 {attempt + 1}/{max_retries}")
            ticker = yf.Ticker("QQQ")
            df = ticker.history(start="2024-11-01", end="2024-12-01")
            
            if not df.empty:
                print(f"  ✅ 重试成功: {len(df)}条记录")
                break
            else:
                print(f"  ⚠️ 尝试 {attempt + 1}: 返回空数据")
                
        except Exception as e:
            print(f"  ❌ 尝试 {attempt + 1}: {e}")
            
        if attempt < max_retries - 1:
            print(f"  ⏳ 等待{retry_delay}秒后重试...")
            time.sleep(retry_delay)

if __name__ == "__main__":
    print("QQQ数据获取诊断开始")
    print("=" * 50)
    
    # 运行所有测试
    test_qqq_basic()
    # test_qqq_history_different_periods()
    # test_qqq_with_enhanced_params()
    # test_multiple_us_etfs()
    # test_network_and_retry()
    
    print("\n" + "=" * 50)
    print("QQQ数据获取诊断完成")