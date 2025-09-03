"""
测试DCA策略完整回测流程
使用真实数据验证策略功能
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import requests
import json

def test_dca_backtest():
    """测试DCA策略回测API"""
    print("=== 测试DCA策略完整回测 ===")
    
    # 回测请求参数
    request_data = {
        "strategy_id": "dca_strategy",
        "parameters": {
            "investment_amount": 1000,
            "frequency_days": 30,
            "symbol": "510300"  # 沪深300ETF
        },
        "start_date": "2024-01-01",
        "end_date": "2024-03-01", 
        "initial_cash": 10000.0
    }
    
    # 发送回测请求
    try:
        response = requests.post(
            "http://localhost:8008/api/v1/backtest/run",
            json=request_data,
            timeout=60
        )
        
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 回测成功完成!")
            print(f"策略: {result['strategy_id']}")
            print(f"初始资金: {result['initial_cash']:.2f}")
            print(f"最终资金: {result['final_value']:.2f}")
            print(f"总收益率: {result['total_return']:.2f}%")
            print(f"交易次数: {result['total_trades']}")
            print(f"性能指标: {json.dumps(result['performance_metrics'], indent=2, ensure_ascii=False)}")
            
            return True
        else:
            print(f"❌ 回测请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_strategy_list():
    """测试策略列表API"""
    print("\n=== 验证策略注册状态 ===")
    
    try:
        response = requests.get("http://localhost:8008/api/v1/strategies/")
        
        if response.status_code == 200:
            strategies = response.json()
            print(f"✅ 发现 {len(strategies)} 个策略:")
            
            for strategy in strategies:
                print(f"  - {strategy['metadata']['name']} ({strategy['metadata']['id']})")
            
            return len(strategies) > 0
        else:
            print(f"❌ 获取策略列表失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    print("开始测试DCA策略完整回测流程...")
    
    # 先检查服务状态
    try:
        health = requests.get("http://localhost:8008/health", timeout=5)
        if health.status_code != 200:
            print("❌ 后端服务未正常运行，请先启动服务")
            exit(1)
    except:
        print("❌ 无法连接到后端服务，请检查端口8008")
        exit(1)
    
    print("✅ 后端服务连接正常")
    
    # 测试策略列表
    if not test_strategy_list():
        print("❌ 策略列表测试失败")
        exit(1)
    
    # 测试完整回测流程
    if test_dca_backtest():
        print("\n🎉 DCA策略回测测试成功!")
    else:
        print("\n❌ DCA策略回测测试失败")
        exit(1)