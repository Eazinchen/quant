import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategies import moving_average_crossover_strategy, rsi_strategy, bollinger_band_strategy
from backtest import BacktestEngine
from data import get_stock_data, generate_simulated_data

# 测试策略函数是否能够生成有效的交易信号
def test_strategy_signals():
    print("\n=== 测试策略函数是否能够生成有效的交易信号 ===")
    
    # 生成模拟数据
    data = generate_simulated_data(days=365)
    print(f"模拟数据形状: {data.shape}")
    print(f"模拟数据日期范围: {data.index.min()} 到 {data.index.max()}")
    
    # 测试双均线金叉死叉策略
    print("\n测试双均线金叉死叉策略:")
    ma_data = moving_average_crossover_strategy(data)
    print(f"信号列最大值: {ma_data['信号'].max()}")
    print(f"信号列最小值: {ma_data['信号'].min()}")
    print(f"买入信号数量: {(ma_data['信号'] == 1).sum()}")
    print(f"卖出信号数量: {(ma_data['信号'] == -1).sum()}")
    
    # 测试RSI超卖反转策略
    print("\n测试RSI超卖反转策略:")
    rsi_data = rsi_strategy(data)
    print(f"信号列最大值: {rsi_data['信号'].max()}")
    print(f"信号列最小值: {rsi_data['信号'].min()}")
    print(f"买入信号数量: {(rsi_data['信号'] == 1).sum()}")
    print(f"卖出信号数量: {(rsi_data['信号'] == -1).sum()}")
    
    # 测试布林带突破策略
    print("\n测试布林带突破策略:")
    bb_data = bollinger_band_strategy(data)
    print(f"信号列最大值: {bb_data['信号'].max()}")
    print(f"信号列最小值: {bb_data['信号'].min()}")
    print(f"买入信号数量: {(bb_data['信号'] == 1).sum()}")
    print(f"卖出信号数量: {(bb_data['信号'] == -1).sum()}")

# 测试回测引擎是否能够正确处理交易信号
def test_backtest_engine():
    print("\n=== 测试回测引擎是否能够正确处理交易信号 ===")
    
    # 测试不同时间范围的情况
    for days in [365, 180, 90, 30]:
        print(f"\n测试时间范围: {days} 天")
        
        # 生成模拟数据
        data = generate_simulated_data(days=days)
        
        # 使用双均线金叉死叉策略生成信号
        data_with_signals = moving_average_crossover_strategy(data)
        
        # 检查信号数量
        buy_signals = (data_with_signals['信号'] == 1).sum()
        sell_signals = (data_with_signals['信号'] == -1).sum()
        print(f"买入信号数量: {buy_signals}")
        print(f"卖出信号数量: {sell_signals}")
        
        # 创建回测引擎实例
        backtest_engine = BacktestEngine(
            data_with_signals,
            initial_capital=100000,
            transaction_cost=0.001,
            slippage=0.0005
        )
        
        # 执行回测
        results = backtest_engine.run(trade_logic='full')
        
        # 打印回测结果
        print("回测结果:")
        for key, value in results.items():
            print(f"{key}: {value}")
        
        # 检查回测数据
        backtest_data = backtest_engine.backtest_data
        print(f"策略收益率最大值: {backtest_data['策略收益率'].max()}")
        print(f"策略收益率最小值: {backtest_data['策略收益率'].min()}")
        print(f"策略累计收益率最终值: {backtest_data['策略累计收益率'].iloc[-1]}")
        print(f"总资金最终值: {backtest_data['总资金'].iloc[-1]}")

if __name__ == "__main__":
    test_strategy_signals()
    test_backtest_engine()
