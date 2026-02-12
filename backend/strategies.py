import pandas as pd
import numpy as np


def moving_average_crossover_strategy(data, short_window=50, long_window=200):
    """
    双均线金叉死叉策略
    
    参数:
    data: pandas DataFrame, 包含股票价格数据，必须有'收盘'列
    short_window: int, 短期移动平均线的窗口大小，默认50天
    long_window: int, 长期移动平均线的窗口大小，默认200天
    
    返回:
    data: pandas DataFrame, 包含原始数据和策略信号
    """
    # 计算短期和长期移动平均线
    data['短期MA'] = data['收盘'].rolling(window=short_window, min_periods=short_window).mean()
    data['长期MA'] = data['收盘'].rolling(window=long_window, min_periods=long_window).mean()
    
    # 计算MA差值和前一天的差值
    data['MA差值'] = data['短期MA'] - data['长期MA']
    data['MA差值_前一天'] = data['MA差值'].shift(1)
    
    # 创建信号列，初始化为0
    data['信号'] = 0
    
    # 买入信号：前一天短期MA < 长期MA，当天短期MA > 长期MA（金叉）
    data.loc[(data['MA差值_前一天'] < 0) & (data['MA差值'] > 0), '信号'] = 1
    
    # 卖出信号：前一天短期MA > 长期MA，当天短期MA < 长期MA（死叉）
    data.loc[(data['MA差值_前一天'] > 0) & (data['MA差值'] < 0), '信号'] = -1
    
    return data


def rsi_strategy(data, rsi_period=14, overbought=70, oversold=30):
    """
    RSI超卖反转策略
    
    参数:
    data: pandas DataFrame, 包含股票价格数据，必须有'收盘'列
    rsi_period: int, RSI计算周期，默认14天
    overbought: int, 超买阈值，默认70
    oversold: int, 超卖阈值，默认30
    
    返回:
    data: pandas DataFrame, 包含原始数据和策略信号
    """
    # 计算RSI指标
    delta = data['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # 计算RSI前一天的值
    data['RSI_前一天'] = data['RSI'].shift(1)
    
    # 创建信号列，初始化为0
    data['信号'] = 0
    
    # 买入信号：前一天RSI < 超卖阈值，当天RSI > 前一天RSI（反弹）
    data.loc[(data['RSI_前一天'] < oversold) & (data['RSI'] > data['RSI_前一天']), '信号'] = 1
    
    # 卖出信号：前一天RSI > 超买阈值，当天RSI < 前一天RSI（回落）
    data.loc[(data['RSI_前一天'] > overbought) & (data['RSI'] < data['RSI_前一天']), '信号'] = -1
    
    return data


def bollinger_band_strategy(data, window=20, num_std=2):
    """
    布林带突破策略
    
    参数:
    data: pandas DataFrame, 包含股票价格数据，必须有'收盘'列
    window: int, 移动平均线窗口大小，默认20天
    num_std: int, 标准差倍数，默认2倍
    
    返回:
    data: pandas DataFrame, 包含原始数据和策略信号
    """
    # 计算布林线指标
    data['中轨'] = data['收盘'].rolling(window=window, min_periods=window).mean()
    data['标准差'] = data['收盘'].rolling(window=window, min_periods=window).std()
    data['上轨'] = data['中轨'] + num_std * data['标准差']
    data['下轨'] = data['中轨'] - num_std * data['标准差']
    
    # 创建信号列，初始化为0
    data['信号'] = 0
    
    # 买入信号：价格突破下轨
    data.loc[(data['收盘'].shift(1) < data['下轨'].shift(1)) & (data['收盘'] > data['下轨']), '信号'] = 1
    
    # 卖出信号：价格突破上轨
    data.loc[(data['收盘'].shift(1) > data['上轨'].shift(1)) & (data['收盘'] < data['上轨']), '信号'] = -1
    
    return data
