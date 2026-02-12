import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt
from strategy import moving_average_crossover_strategy, bollinger_band_strategy, BacktestEngine

# 设置Matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 获取股票数据
symbol = "000001"  # 昆仑万维A股代码
start_date = "20240101"  # akshare需要YYYYMMDD格式
date_today = pd.Timestamp.today().strftime("%Y%m%d")

# 使用akshare获取A股日线数据
data = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=date_today, adjust="qfq")

# 转换日期格式并设置为索引
data['日期'] = pd.to_datetime(data['日期'])
data.set_index('日期', inplace=True)

# 应用布林线策略
window = 20
num_std = 2
data_with_signals = bollinger_band_strategy(
    data, window=window, num_std=num_std
)

# 绘制图表
plt.figure(figsize=(12, 8))

# 绘制收盘价
plt.plot(data_with_signals.index, data_with_signals['收盘'], label='收盘价', alpha=0.7)

# 绘制布林线指标
plt.plot(data_with_signals.index, data_with_signals['中轨'], label='中轨', alpha=0.7)
plt.plot(data_with_signals.index, data_with_signals['上轨'], label='上轨', alpha=0.7)
plt.plot(data_with_signals.index, data_with_signals['下轨'], label='下轨', alpha=0.7)

# 标记买卖信号（使用收盘价作为标记位置，更直观）
plt.scatter(
    data_with_signals[data_with_signals['信号'] == 1].index,
    data_with_signals[data_with_signals['信号'] == 1]['收盘'],
    marker='^',
    color='green',
    s=100,
    label='买入信号'
)
plt.scatter(
    data_with_signals[data_with_signals['信号'] == -1].index,
    data_with_signals[data_with_signals['信号'] == -1]['收盘'],
    marker='v',
    color='red',
    s=100,
    label='卖出信号'
)

# 设置图表标题和标签
plt.title(f"{symbol} 股票价格与布林线策略")
plt.xlabel("日期")
plt.ylabel("价格")
plt.legend(loc='best')
plt.grid(True)  # 添加网格线
plt.tight_layout()  # 调整布局
plt.xticks(rotation=45)  # 旋转日期标签，避免重叠

# 显示图表
plt.show()

# 调用回测函数
print("\n开始回测布林线策略...")

# 创建回测引擎实例
initial_capital = 100000  # 初始资金10万元
# 创建回测引擎实例
backtest_engine = BacktestEngine(
    data_with_signals,
    initial_capital=100000,  # 初始资金10万元
    transaction_cost=0.001,   # 0.1%交易成本
    slippage=0.0005,         # 0.05%滑点
    dynamic_position=True    # 启用动态仓位控制
)

# 执行回测
backtest_engine.run(trade_logic='full')  # 使用全仓进行交易

# 打印回测结果
print("\n=== 回测结果 ===")
backtest_engine.print_results()

# 绘制回测图表
print("\n绘制回测结果图表...")
fig = backtest_engine.plot_results()
plt.show()

# 获取详细回测数据
results = backtest_engine.get_results()
print("\n回测完成！")

# 保存回测数据
results['回测数据'].to_csv('backtest_results.csv', encoding='utf-8-sig')
print("回测数据已保存到 backtest_results.csv")