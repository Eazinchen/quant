import pandas as pd
import numpy as np


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
        self.results['最终资金'] = self.backtest_data['总资金'].iloc[-1]
        self.results['累计收益率'] = self.backtest_data['策略累计收益率'].iloc[-1]
        
        # 年化收益率（假设一年252个交易日）
        total_days = len(self.backtest_data)
        if total_days > 0:
            self.results['年化收益率'] = (1 + self.results['累计收益率']) ** (252 / total_days) - 1
        else:
            self.results['年化收益率'] = 0
        
        # 最大回撤
        cumulative_returns = self.backtest_data['策略累计收益率']
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / (1 + running_max)
        self.results['最大回撤'] = drawdown.min()
        
        # 夏普比率（假设无风险利率为0）
        strategy_returns = self.backtest_data['策略收益率'].dropna()
        if len(strategy_returns) > 0:
            annualized_return = self.results['年化收益率']
            annualized_volatility = strategy_returns.std() * np.sqrt(252)
            if annualized_volatility > 0:
                self.results['夏普比率'] = annualized_return / annualized_volatility
            else:
                self.results['夏普比率'] = 0
        else:
            self.results['夏普比率'] = 0
        
        # 胜率和盈亏比
        trades = self.backtest_data[self.backtest_data['信号'] != 0]
        if len(trades) > 0:
            # 简化计算：假设每次信号都是一笔完整的交易（买入后卖出）
            # 这里仅作为示例，实际计算需要更复杂的逻辑
            profitable_trades = len(trades[trades['策略收益率'] > 0])
            self.results['胜率'] = profitable_trades / len(trades)
            
            # 计算盈亏比
            profit_sum = trades[trades['策略收益率'] > 0]['策略收益率'].sum()
            loss_sum = abs(trades[trades['策略收益率'] < 0]['策略收益率'].sum())
            if loss_sum > 0:
                self.results['盈亏比'] = profit_sum / loss_sum
            else:
                self.results['盈亏比'] = 0
        else:
            self.results['胜率'] = 0
            self.results['盈亏比'] = 0
    
    def print_results(self):
        """打印回测结果"""
        print(f"初始资金: {self.results['初始资金']:.2f}")
        print(f"最终资金: {self.results['最终资金']:.2f}")
        print(f"累计收益率: {self.results['累计收益率']:.2%}")
        print(f"年化收益率: {self.results['年化收益率']:.2%}")
        print(f"最大回撤: {self.results['最大回撤']:.2%}")
        print(f"夏普比率: {self.results['夏普比率']:.2f}")
        print(f"胜率: {self.results['胜率']:.2%}")
        print(f"盈亏比: {self.results['盈亏比']:.2f}")
    
    def plot_results(self):
        """绘制回测结果图表"""
        import matplotlib.pyplot as plt
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 绘制净值曲线
        ax1.plot(self.backtest_data.index, 1 + self.backtest_data['策略累计收益率'], label='策略净值')
        ax1.plot(self.backtest_data.index, 1 + self.backtest_data['基准累计收益率'], label='基准净值')
        ax1.set_title('策略净值 vs 基准净值')
        ax1.set_ylabel('净值')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 绘制回撤曲线
        cumulative_returns = self.backtest_data['策略累计收益率']
        running_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - running_max) / (1 + running_max)
        ax2.plot(self.backtest_data.index, drawdown, label='策略回撤')
        ax2.set_title('策略回撤')
        ax2.set_ylabel('回撤')
        ax2.set_xlabel('日期')
        ax2.legend()
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def get_results(self):
        """获取详细回测数据"""
        return {
            '回测数据': self.backtest_data,
            '绩效指标': self.results
        }
