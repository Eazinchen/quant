import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def moving_average_crossover_strategy(data, short_window=50, middle_window=100, long_window=200):
    """
    实现短期、中期和长期移动平均交叉策略
    
    参数:
    data: pandas DataFrame, 包含股票价格数据，必须有'收盘'列
    short_window: int, 短期移动平均线的窗口大小，默认50天
    middle_window: int, 中期移动平均线的窗口大小，默认100天
    long_window: int, 长期移动平均线的窗口大小，默认200天
    
    返回:
    data: pandas DataFrame, 包含原始数据和策略信号
    """
    # 计算短期和长期移动平均线
    data['短期MA'] = data['收盘'].rolling(window=short_window, min_periods=short_window).mean()
    data['中期MA'] = data['收盘'].rolling(window=middle_window, min_periods=middle_window).mean()
    data['长期MA'] = data['收盘'].rolling(window=long_window, min_periods=long_window).mean()
    
    # 计算MA差值和前一天的差值
    data['中短MA差值'] = data['短期MA'] - data['中期MA']
    # data['长中MA差值'] = data['中期MA'] - data['长期MA']
    data['中短MA差值_前一天'] = data['中短MA差值'].shift(1)
    # data['长中MA差值_前一天'] = data['长中MA差值'].shift(1)
    
    # 创建信号列，初始化为0
    data['信号'] = 0
    
    # 买入信号：前一天短期MA < 中期MA，当天短期MA > 中期MA（金叉）,且长期MA > 中期MA
    data.loc[(data['中短MA差值_前一天'] < 0) & (data['中短MA差值'] > 0) & (data['长期MA'] > data['中期MA']), '信号'] = 1
    
    # 卖出信号：前一天短期MA > 中期MA，当天短期MA < 中期MA（死叉）,且长期MA < 中期MA
    data.loc[(data['中短MA差值_前一天'] > 0) & (data['中短MA差值'] < 0) & (data['长期MA'] > data['中期MA']), '信号'] = -1
    
    print(f"\n策略调试：")
    print(f"数据总天数: {len(data)}")
    print(f"短期MA有效天数: {data['短期MA'].notna().sum()}")
    print(f"中期MA有效天数: {data['中期MA'].notna().sum()}")
    print(f"长期MA有效天数: {data['长期MA'].notna().sum()}")
    print(f"买入信号数量: {len(data[data['信号'] == 1])}")
    print(f"卖出信号数量: {len(data[data['信号'] == -1])}")
    
    # 显示信号详情
    if len(data[data['信号'] == 1]) > 0:
        print(f"\n买入信号详情:")
        print(data[data['信号'] == 1][['收盘', '短期MA', '中期MA', '长期MA', '中短MA差值', '中短MA差值_前一天']])
    
    if len(data[data['信号'] == -1]) > 0:
        print(f"\n卖出信号详情:")
        print(data[data['信号'] == -1][['收盘', '短期MA', '中期MA', '长期MA', '中短MA差值', '中短MA差值_前一天']])
    
    return data


def bollinger_band_strategy(data, window=20, num_std=2):
    """
    实现基于布林线的交易策略
    
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
    
    # 条件1: 当前一天收盘价在布林线上轨上方，当天在布林线上轨下方，标记卖出信号
    condition1 = (data['收盘'].shift(1) > data['上轨'].shift(1)) & (data['收盘'] < data['上轨'])
    
    # 条件2: 当前一天收盘价在布林线中轨下方，当天在布林线中轨上方，标记买入信号
    condition2 = (data['收盘'].shift(1) < data['中轨'].shift(1)) & (data['收盘'] > data['中轨'])
    
    # 条件3: 当前一天收盘价在布林线下轨下方，当天在布林线下轨上方，标记买入信号
    condition3 = (data['收盘'].shift(1) < data['下轨'].shift(1)) & (data['收盘'] > data['下轨'])
    
    # 条件4: 当前两天收盘价在布林线中轨上方，前一天在布林线中轨下方，当天仍在布林线中轨下方，标记卖出信号
    condition4 = (data['收盘'].shift(2) > data['中轨'].shift(2)) & (data['收盘'].shift(1) < data['中轨'].shift(1)) & (data['收盘'] < data['中轨'])
    
    # 应用信号条件
    data.loc[condition1 | condition4, '信号'] = -1  # 卖出信号
    data.loc[condition2 | condition3, '信号'] = 1   # 买入信号
    
    # 调试信息
    print(f"\n布林线策略调试：")
    print(f"数据总天数: {len(data)}")
    print(f"中轨有效天数: {data['中轨'].notna().sum()}")
    print(f"买入信号数量: {len(data[data['信号'] == 1])}")
    print(f"卖出信号数量: {len(data[data['信号'] == -1])}")
    
    # 显示信号详情
    if len(data[data['信号'] == 1]) > 0:
        print(f"\n买入信号详情:")
        print(data[data['信号'] == 1][['收盘', '中轨', '上轨', '下轨']])
    
    if len(data[data['信号'] == -1]) > 0:
        print(f"\n卖出信号详情:")
        print(data[data['信号'] == -1][['收盘', '中轨', '上轨', '下轨']])
    
    return data


class BacktestEngine:
    """
    通用回测引擎，支持多种交易策略
    
    参数:
    data: pandas DataFrame, 包含股票价格和交易信号
    initial_capital: float, 初始资金
    signal_col: str, 信号列名称，默认'信号'
    price_col: str, 价格列名称，默认'收盘'
    transaction_cost: float, 交易成本（佣金+印花税），默认0.001（0.1%）
    slippage: float, 滑点，默认0.0005（0.05%）
    """
    
    def __init__(self, data, initial_capital=100000, signal_col='信号', price_col='收盘', 
                transaction_cost=0.001, slippage=0.0005):
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.signal_col = signal_col
        self.price_col = price_col
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        
        # 验证数据
        self._validate_data()
        
        # 初始化回测结果
        self.backtest_data = None
        self.results = {}
    
    def _validate_data(self):
        """验证输入数据的完整性"""
        required_cols = [self.price_col, self.signal_col]
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"数据中缺少必要列: {col}")
    
    def run(self, trade_logic='full', trade_param=None):
        """
        执行回测
        
        参数:
        trade_logic: str, 交易逻辑类型
            - 'full': 全仓交易
            - 'fixed': 固定数量交易
            - 'percent': 百分比交易
        trade_param: dict, 交易逻辑参数
            - 'full': 无需参数
            - 'fixed': {'quantity': int} - 固定交易数量
            - 'percent': {'percent': float} - 交易资金百分比(0-1)
        
        返回:
        dict: 回测结果
        """
        # 初始化回测数据
        self.backtest_data = self.data.copy()
        
        # 计算基础指标
        self._calculate_base_metrics()
        
        # 初始化账户
        self._initialize_account()
        
        # 执行回测循环
        for i in range(1, len(self.backtest_data)):
            self._process_trade(i, trade_logic, trade_param)
        
        # 计算回测指标
        self._calculate_backtest_metrics()
        
        return self.results
    
    def _calculate_base_metrics(self):
        """计算基础指标"""
        # 日收益率
        self.backtest_data['日收益率'] = self.backtest_data[self.price_col].pct_change()
        
        # 基准收益率（买入持有）
        self.backtest_data['基准累计收益率'] = (1 + self.backtest_data['日收益率']).cumprod() - 1
    
    def _initialize_account(self):
        """初始化账户信息"""
        # 持仓数量使用整数类型
        self.backtest_data['持仓数量'] = 0
        # 资金相关列使用浮点数类型
        self.backtest_data['持仓价值'] = 0.0
        self.backtest_data['可用资金'] = 0.0
        self.backtest_data['总资金'] = 0.0
        self.backtest_data['交易成本'] = 0.0
    
        # 设置初始资金（转换为浮点数）
        first_date = self.backtest_data.index[0]
        self.backtest_data.loc[first_date, '可用资金'] = float(self.initial_capital)
        self.backtest_data.loc[first_date, '总资金'] = float(self.initial_capital)
    
    def _process_trade(self, i, trade_logic, trade_param):
        """处理每笔交易"""
        prev_row = self.backtest_data.iloc[i-1]
        curr_row = self.backtest_data.iloc[i]
        
        # 当前价格（考虑滑点）
        current_price = curr_row[self.price_col]
        
        # 复制前一天的持仓和资金
        self.backtest_data.loc[curr_row.name, '持仓数量'] = prev_row['持仓数量']
        self.backtest_data.loc[curr_row.name, '可用资金'] = prev_row['可用资金']
        self.backtest_data.loc[curr_row.name, '交易成本'] = 0
        
        # 更新持仓价值和总资金
        self._update_account_values(curr_row.name, current_price)
        
        # 获取当前信号
        signal = curr_row[self.signal_col]
        
        # 检查买入信号
        if signal == 1 and self.backtest_data.loc[curr_row.name, '可用资金'] > 0:
            # 根据交易逻辑计算买入数量
            buy_quantity = self._calculate_buy_quantity(self.backtest_data.loc[curr_row.name], current_price, trade_logic, trade_param)
            
            if buy_quantity > 0:
                # 计算实际交易价格（考虑滑点）
                buy_price = current_price * (1 + self.slippage)
                # 计算交易成本
                cost = buy_quantity * buy_price * self.transaction_cost
                # 更新账户
                self.backtest_data.loc[curr_row.name, '持仓数量'] += buy_quantity
                self.backtest_data.loc[curr_row.name, '可用资金'] -= (buy_quantity * buy_price) + cost
                self.backtest_data.loc[curr_row.name, '交易成本'] += cost
                # 重新计算总资金和仓位
                self._update_account_values(curr_row.name, current_price)
        
        # 处理卖出信号
        elif signal == -1 and self.backtest_data.loc[curr_row.name, '持仓数量'] > 0:
            # 根据交易逻辑计算卖出数量
            sell_quantity = self._calculate_sell_quantity(self.backtest_data.loc[curr_row.name], trade_logic, trade_param)
            if sell_quantity > 0:
                # 计算实际交易价格（考虑滑点）
                sell_price = current_price * (1 - self.slippage)
                # 计算交易成本
                cost = sell_quantity * sell_price * self.transaction_cost
                # 更新账户
                self.backtest_data.loc[curr_row.name, '持仓数量'] -= sell_quantity
                self.backtest_data.loc[curr_row.name, '可用资金'] += (sell_quantity * sell_price) - cost
                self.backtest_data.loc[curr_row.name, '交易成本'] += cost
                # 重新计算总资金和仓位
                self._update_account_values(curr_row.name, current_price)
        
    def _calculate_buy_quantity(self, prev_row, current_price, trade_logic, trade_param):
        """计算买入数量"""
        if trade_logic == 'full':
            # 全仓买入
            available_funds = prev_row['可用资金']
            buy_quantity = int(available_funds / (current_price * (1 + self.slippage) * (1 + self.transaction_cost)))
        elif trade_logic == 'fixed' and trade_param and 'quantity' in trade_param:
            # 固定数量买入
            buy_quantity = trade_param['quantity']
        elif trade_logic == 'percent' and trade_param and 'percent' in trade_param:
            # 百分比买入
            percent = trade_param['percent']
            available_funds = prev_row['可用资金'] * percent
            buy_quantity = int(available_funds / (current_price * (1 + self.slippage) * (1 + self.transaction_cost)))
        else:
            buy_quantity = 0
        
        return max(0, buy_quantity)
    
    def _calculate_sell_quantity(self, prev_row, trade_logic, trade_param):
        """计算卖出数量"""
        if trade_logic == 'full':
            # 全仓卖出
            sell_quantity = prev_row['持仓数量']
        elif trade_logic == 'fixed' and trade_param and 'quantity' in trade_param:
            # 固定数量卖出
            sell_quantity = min(prev_row['持仓数量'], trade_param['quantity'])
        elif trade_logic == 'percent' and trade_param and 'percent' in trade_param:
            # 百分比卖出
            percent = trade_param['percent']
            sell_quantity = int(prev_row['持仓数量'] * percent)
        else:
            sell_quantity = 0
        
        return max(0, sell_quantity)
    
    def _update_account_values(self, index, current_price):
        """更新账户价值"""
        position_quantity = self.backtest_data.loc[index, '持仓数量']
        available_cash = self.backtest_data.loc[index, '可用资金']
        
        position_value = position_quantity * current_price
        total_capital = position_value + available_cash
        
        self.backtest_data.loc[index, '持仓价值'] = position_value
        self.backtest_data.loc[index, '总资金'] = total_capital
    
    def _calculate_backtest_metrics(self):
        """计算回测指标"""
        # 策略收益率
        self.backtest_data['策略收益率'] = self.backtest_data['总资金'].pct_change()
        self.backtest_data['策略累计收益率'] = (1 + self.backtest_data['策略收益率']).cumprod() - 1
        
        # 计算核心指标
        self.results['初始资金'] = self.initial_capital
