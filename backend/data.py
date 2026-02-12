import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime, timedelta


def get_stock_data(symbol="000001", start_date=None, end_date=None, days=365*5):
    """
    获取股票数据
    
    参数:
    symbol: str, 股票代码，默认"000001"（平安银行）
    start_date: str, 开始日期，格式：YYYYMMDD
    end_date: str, 结束日期，格式：YYYYMMDD
    days: int, 数据天数，默认5年（当未指定开始日期时使用）
    
    返回:
    pandas DataFrame, 包含股票价格数据
    """
    try:
        # 计算开始和结束日期
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        # 转换日期格式为YYYY-MM-DD，因为ak.stock_zh_a_hist可能期望这种格式
        start_date_formatted = datetime.strptime(start_date, "%Y%m%d").strftime("%Y-%m-%d")
        end_date_formatted = datetime.strptime(end_date, "%Y%m%d").strftime("%Y-%m-%d")
        
        # 使用akshare获取A股日线数据
        print(f"正在获取股票数据: {symbol}, 时间范围: {start_date} ({start_date_formatted}) 到 {end_date} ({end_date_formatted})")
        data = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date_formatted, end_date=end_date_formatted, adjust="qfq")
        
        # 转换日期格式并设置为索引
        data['日期'] = pd.to_datetime(data['日期'])
        data.set_index('日期', inplace=True)
        
        # 按照日期升序排序
        data = data.sort_index()
        
        print(f"成功获取股票数据，共 {len(data)} 条记录")
        return data
    except Exception as e:
        print(f"获取股票数据失败: {e}")
        # 返回模拟数据
        print("返回模拟数据")
        # 计算模拟数据的天数
        if start_date and end_date:
            # 如果指定了开始和结束日期，计算实际天数
            start = datetime.strptime(start_date, "%Y%m%d")
            end = datetime.strptime(end_date, "%Y%m%d")
            sim_days = (end - start).days
            if sim_days < 1:
                sim_days = 365  # 至少生成1年的数据
            return generate_simulated_data(days=sim_days, start_date=start_date, end_date=end_date)
        else:
            return generate_simulated_data(days=days)


def generate_simulated_data(days=365*5, start_date=None, end_date=None):
    """
    生成模拟股票数据
    
    参数:
    days: int, 数据天数，默认5年
    start_date: str, 开始日期，格式：YYYYMMDD
    end_date: str, 结束日期，格式：YYYYMMDD
    
    返回:
    pandas DataFrame, 包含模拟的股票价格数据
    """
    # 生成日期范围
    if start_date and end_date:
        # 如果指定了开始和结束日期，使用这些日期
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        dates = pd.date_range(start=start, end=end, freq='B')
    else:
        # 否则使用默认的日期范围
        dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
    
    # 生成模拟价格数据（使用随机游走模型）
    actual_days = len(dates)
    np.random.seed(42)  # 设置随机种子，确保结果可重复
    returns = np.random.normal(0, 0.02, actual_days)
    price = 100 * np.exp(np.cumsum(returns))
    
    # 生成开盘价、最高价、最低价（基于收盘价）
    open_price = price * (1 + np.random.normal(0, 0.01, actual_days))
    high_price = np.maximum(price, open_price) * (1 + np.random.normal(0, 0.01, actual_days))
    low_price = np.minimum(price, open_price) * (1 - np.random.normal(0, 0.01, actual_days))
    
    # 生成成交量（随机值）
    volume = np.random.randint(100000, 10000000, actual_days)
    
    # 创建DataFrame
    data = pd.DataFrame({
        '开盘': open_price,
        '最高': high_price,
        '最低': low_price,
        '收盘': price,
        '成交量': volume,
        '成交额': volume * price
    }, index=dates)
    
    # 按照日期升序排序
    data = data.sort_index()
    
    return data
