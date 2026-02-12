import requests
import json

# 测试运行回测的API端点
def test_backtest_api():
    print("\n=== 测试运行回测的API端点 ===")
    
    # API端点URL
    url = "http://localhost:8004/api/backtest"
    
    # 测试不同的策略和时间范围
    test_cases = [
        {
            "name": "双均线金叉死叉策略 - 2024年全年",
            "strategy_id": 1,
            "stock_code": "000001",
            "start_date": "20240101",
            "end_date": "20241231"
        },
        {
            "name": "RSI超卖反转策略 - 2024年全年",
            "strategy_id": 2,
            "stock_code": "000001",
            "start_date": "20240101",
            "end_date": "20241231"
        },
        {
            "name": "布林带突破策略 - 2024年全年",
            "strategy_id": 3,
            "stock_code": "000001",
            "start_date": "20240101",
            "end_date": "20241231"
        },
        {
            "name": "双均线金叉死叉策略 - 最近6个月",
            "strategy_id": 1,
            "stock_code": "000001",
            "start_date": "20240701",
            "end_date": "20241231"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"策略ID: {test_case['strategy_id']}")
        print(f"股票代码: {test_case['stock_code']}")
        print(f"时间范围: {test_case['start_date']} 到 {test_case['end_date']}")
        
        # 发送POST请求
        try:
            response = requests.post(
                url,
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            # 检查响应状态码
            if response.status_code == 200:
                # 解析响应数据
                data = response.json()
                
                # 打印回测结果
                print("\n回测结果:")
                for key, value in data['metrics'].items():
                    print(f"{key}: {value}")
                
                # 检查是否有图表数据
                if 'charts' in data:
                    print("\n图表数据:")
                    print(f"是否包含净值曲线图表: {'equity_curve' in data['charts']}")
                    print(f"是否包含热力图图表: {'heatmap' in data['charts']}")
            else:
                # 打印错误信息
                print(f"\n错误: 响应状态码 {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"\n请求失败: {e}")

if __name__ == "__main__":
    test_backtest_api()
