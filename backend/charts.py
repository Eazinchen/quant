import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# 设置全局中文字体
plt.rcParams['font.family'] = ['SimHei', 'Georgia', 'Cambria', 'serif']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def generate_equity_curve(data):
    """
    生成净值曲线图表
    
    参数:
    data: pandas DataFrame, 包含回测数据，必须有'策略累计收益率'和'基准累计收益率'列
    
    返回:
    str, Base64编码的PNG图片
    """
    # 设置WSJ风格
    plt.style.use('default')
    # 重新设置中文字体
    plt.rcParams['font.family'] = ['SimHei', 'Georgia', 'Cambria', 'serif']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.rcParams['axes.grid'] = True
    plt.rcParams['axes.grid.axis'] = 'y'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.7
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.left'] = True
    plt.rcParams['axes.spines.bottom'] = True
    plt.rcParams['axes.linewidth'] = 0.5
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绘制净值曲线
    ax.plot(data.index, 1 + data['策略累计收益率'], label='策略净值', linewidth=2, color='#0066cc')
    ax.plot(data.index, 1 + data['基准累计收益率'], label='基准净值', linewidth=2, color='#666666', linestyle='--')
    
    # 计算回撤
    cumulative_returns = data['策略累计收益率']
    running_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - running_max) / (1 + running_max)
    
    # 绘制回撤阴影区域
    ax.fill_between(data.index, 1 + cumulative_returns, 1 + running_max, where=(drawdown < 0), 
                   color='#ffcccc', alpha=0.5, label='回撤')
    
    # 设置标题和标签
    ax.set_title('净值曲线 vs 基准', fontsize=16, fontweight='bold', loc='left')
    ax.set_ylabel('净值', fontsize=12)
    ax.set_xlabel('日期', fontsize=12)
    
    # 添加图例
    ax.legend(loc='best', frameon=False)
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表转换为Base64编码的PNG
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"


def generate_heatmap(data):
    """
    生成月度收益热力图
    
    参数:
    data: pandas DataFrame, 包含回测数据，必须有'策略收益率'列
    
    返回:
    str, Base64编码的PNG图片
    """
    # 设置WSJ风格
    plt.style.use('default')
    
    # 计算月度收益率
    monthly_returns = data['策略收益率'].resample('ME').sum()
    
    # 构建月度收益矩阵
    monthly_returns_df = monthly_returns.to_frame()
    monthly_returns_df['year'] = monthly_returns_df.index.year
    monthly_returns_df['month'] = monthly_returns_df.index.month
    
    # 创建透视表
    heatmap_data = monthly_returns_df.pivot(index='year', columns='month', values='策略收益率')
    
    # 月份标签
    month_labels = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    heatmap_data.columns = month_labels
    # 重新设置中文字体
    plt.rcParams['font.family'] = ['SimHei', 'Georgia', 'Cambria', 'serif']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绘制热力图
    im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=-0.1, vmax=0.1)
    
    # 添加颜色条
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.set_label('月度收益率', rotation=-90, va="bottom")
    
    # 设置标题和标签
    ax.set_title('月度收益热力图', fontsize=16, fontweight='bold', loc='left')
    ax.set_xlabel('月份', fontsize=12)
    ax.set_ylabel('年份', fontsize=12)
    
    # 设置刻度标签
    ax.set_xticks(np.arange(len(month_labels)))
    ax.set_xticklabels(month_labels, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(heatmap_data.index)))
    ax.set_yticklabels(heatmap_data.index)
    
    # 在热力图上添加数值
    for i in range(len(heatmap_data.index)):
        for j in range(len(month_labels)):
            value = heatmap_data.iloc[i, j]
            if not pd.isna(value):
                text = ax.text(j, i, f"{value:.2%}", 
                              ha="center", va="center", 
                              color="black" if abs(value) < 0.05 else "white",
                              fontsize=10)
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表转换为Base64编码的PNG
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"


def generate_sharpe_ratio_chart(data):
    """
    生成滚动夏普比率图表
    
    参数:
    data: pandas DataFrame, 包含回测数据，必须有'策略收益率'列
    
    返回:
    str, Base64编码的PNG图片
    """
    # 设置WSJ风格
    plt.style.use('default')
    # 重新设置中文字体
    plt.rcParams['font.family'] = ['SimHei', 'Georgia', 'Cambria', 'serif']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.rcParams['axes.grid'] = True
    plt.rcParams['axes.grid.axis'] = 'y'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.7
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.left'] = True
    plt.rcParams['axes.spines.bottom'] = True
    plt.rcParams['axes.linewidth'] = 0.5
    
    # 计算滚动夏普比率（252天）
    window = 252
    daily_returns = data['策略收益率'].dropna()
    rolling_mean = daily_returns.rolling(window=window).mean()
    rolling_std = daily_returns.rolling(window=window).std()
    rolling_sharpe = rolling_mean / rolling_std * np.sqrt(252)  # 年化
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绘制滚动夏普比率
    ax.plot(rolling_sharpe.index, rolling_sharpe, label='滚动夏普比率', linewidth=2, color='#0066cc')
    
    # 添加零轴参考线
    ax.axhline(y=0, color='#666666', linestyle='--', linewidth=1)
    
    # 设置标题和标签
    ax.set_title('滚动夏普比率（252天）', fontsize=16, fontweight='bold', loc='left')
    ax.set_ylabel('夏普比率', fontsize=12)
    ax.set_xlabel('日期', fontsize=12)
    
    # 添加图例
    ax.legend(loc='best', frameon=False)
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表转换为Base64编码的PNG
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"
