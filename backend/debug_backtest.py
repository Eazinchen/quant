import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategies import moving_average_crossover_strategy, rsi_strategy, bollinger_band_strategy
from backtest import BacktestEngine
from data import get_stock_data, generate_simulated_data

# 直接测试回测引擎
def debug_backtest():
    print("\n=== 调试回测引擎 ===")
    
    # 测试不同的策略
    strategies = [
        {"name": "双均线金叉死叉策略", "func": moving_average_crossover_strategy},
        {"name": "RSI超卖反转策略", "func": rsi_strategy},
        {"name": "布林带突破策略", "func": bollinger_band_strategy}
    ]
    
    # 测试不同的股票代码和时间范围
    test_cases = [
        {"stock_code": "000001", "start_date": "20240101", "end_date": "20241231", "name": "平安银行 - 2024年全年"},
        {"stock_code": "600519", "start_date": "20240101", "end_date": "20241231", "name": "贵州茅台 - 2024年全年"}
    ]
    
    for test_case in test_cases:
        print(f"\n=== 测试: {test_case['name']} ===")
        print(f"股票代码: {test_case['stock_code']}")
        print(f"时间范围: {test_case['start_date']} 到 {test_case['end_date']}")
        
        try:
            # 获取股票数据
            data = get_stock_data(
                symbol=test_case['stock_code'], 
                start_date=test_case['start_date'], 
                end_date=test_case['end_date']
            )
            print(f"股票数据形状: {data.shape}")
            print(f"股票数据日期范围: {data.index.min()} 到 {data.index.max()}")
            print(f"股票数据前5行:\n{data.head()}")
            
            # 测试每个策略
            for strategy in strategies:
                print(f"\n--- 测试 {strategy['name']} ---")
                
                try:
                    # 生成交易信号
                    data_with_signals = strategy['func'](data)
                    
                    # 检查信号数量
                    buy_signals = (data_with_signals['信号'] == 1).sum()
                    sell_signals = (data_with_signals['信号'] == -1).sum()
                    print(f"买入信号数量: {buy_signals}")
                    print(f"卖出信号数量: {sell_signals}")
                    print(f"信号列统计:\n{data_with_signals['信号'].describe()}")
                    
                    # 检查是否有信号
                    if buy_signals == 0 and sell_signals == 0:
                        print("警告: 没有生成任何交易信号!")
                    else:
                        print("成功生成交易信号!")
                    
                    # 创建回测引擎实例
                    backtest_engine = BacktestEngine(
                        data_with_signals,
                        initial_capital=100000,
                        transaction_cost=0.001,
                        slippage=0.0005
                    )
                    print("回测引擎实例创建成功")
                    
                    # 执行回测
                    results = backtest_engine.run(trade_logic='full')
                    print("回测执行成功")
                    
                    # 打印回测结果
                    print("\n回测结果:")
                    for key, value in results.items():
                        print(f"{key}: {value}")
                    
                    # 检查回测数据
                    backtest_data = backtest_engine.backtest_data
                    print(f"\n回测数据形状: {backtest_data.shape}")
                    print(f"回测数据前5行:\n{backtest_data.head()}")
                    print(f"策略收益率统计:\n{backtest_data['策略收益率'].describe()}")
                    print(f"策略累计收益率统计:\n{backtest_data['策略累计收益率'].describe()}")
                    print(f"总资金统计:\n{backtest_data['总资金'].describe()}")
                    
                except Exception as e:
                    print(f"测试 {strategy['name']} 失败: {e}")
                    import traceback
                    traceback.print_exc()
                    
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_backtest()
