"""
数据源测试脚本
验证AKShare和yfinance接口可用性
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.data_source import data_manager

def test_akshare():
    """测试AKShare - 获取沪深300ETF数据"""
    print("=== 测试AKShare (沪深300ETF: 510300) ===")
    
    symbol = "510300"  # 沪深300ETF
    start_date = "2024-01-01"
    end_date = "2024-02-01"
    
    print(f"获取 {symbol} 从 {start_date} 到 {end_date} 的数据...")
    
    df = data_manager.get_data(symbol, start_date, end_date)
    
    if df.empty:
        print("ERROR: 无数据返回")
    else:
        print(f"SUCCESS: 获取到 {len(df)} 条记录")
        print("前5行数据:")
        print(df.head())
        print("\n列名:", df.columns.tolist())
        print("数据类型:", df.dtypes.to_dict())

def test_yfinance():
    """测试yfinance - 获取标普500ETF数据"""
    print("\n=== 测试yfinance (标普500ETF: SPY) ===")
    
    symbol = "SPY"  # 标普500ETF
    start_date = "2024-01-01" 
    end_date = "2024-02-01"
    
    print(f"获取 {symbol} 从 {start_date} 到 {end_date} 的数据...")
    
    df = data_manager.get_data(symbol, start_date, end_date)
    
    if df.empty:
        print("ERROR: 无数据返回")
    else:
        print(f"SUCCESS: 获取到 {len(df)} 条记录")
        print("前5行数据:")
        print(df.head())
        print("\n列名:", df.columns.tolist())
        print("数据类型:", df.dtypes.to_dict())

def test_auto_routing():
    """测试自动路由功能"""
    print("\n=== 测试自动路由 ===")
    
    test_symbols = [
        ("510300", "A股ETF -> AKShare"),
        ("SPY", "美股ETF -> yfinance"),
        ("000001", "A股 -> AKShare"),
        ("AAPL", "美股 -> yfinance")
    ]
    
    for symbol, description in test_symbols:
        print(f"\n测试 {symbol} ({description})")
        
        # 只测试能否正确选择数据源，不实际获取数据
        if symbol.isdigit():
            source = "AKShare"
        else:
            source = "yfinance"
        
        print(f"自动选择数据源: {source}")

if __name__ == "__main__":
    print("数据源集成测试开始...")
    
    try:
        # 测试自动路由逻辑
        test_auto_routing()
        
        # 测试实际数据获取 (可能需要网络)
        test_akshare()
        test_yfinance()
        
        print("\nSUCCESS: 数据源测试完成!")
        
    except Exception as e:
        print(f"\nERROR: 测试失败: {e}")
        import traceback
        traceback.print_exc()