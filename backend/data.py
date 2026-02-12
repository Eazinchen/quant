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
    # 计算开始和结束日期
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    
    # 转换日期格式为YYYY-MM-DD，因为ak.stock_zh_a_hist可能期望这种格式
    start_date_formatted = datetime.strptime(start_date, "%Y%m%d").strftime("%Y-%m-%d")
    end_date_formatted = datetime.strptime(end_date, "%Y%m%d").strftime("%Y-%m-%d")
    
    # 确保股票代码格式正确，移除可能的后缀
    clean_symbol = symbol.replace('.ss', '').replace('.sz', '')
    print(f"正在获取股票数据: {clean_symbol}, 时间范围: {start_date} ({start_date_formatted}) 到 {end_date} ({end_date_formatted})")
    
    # 验证日期范围，确保结束日期不晚于今天
    today = datetime.now().strftime("%Y-%m-%d")
    if end_date_formatted > today:
        print(f"警告: 结束日期 {end_date_formatted} 晚于今天 {today}，将使用今天作为结束日期")
        end_date_formatted = today
    
    try:
        # 使用akshare获取A股日线数据
        data = ak.stock_zh_a_hist(symbol=clean_symbol, start_date=start_date_formatted, end_date=end_date_formatted, adjust="qfq")
    except Exception as e:
        print(f"首次尝试获取数据失败: {e}")
        # 尝试使用不同的股票代码格式
        try:
            print(f"尝试使用 {clean_symbol}.ss 格式获取数据")
            data = ak.stock_zh_a_hist(symbol=f"{clean_symbol}.ss", start_date=start_date_formatted, end_date=end_date_formatted, adjust="qfq")
        except Exception as e2:
            print(f"第二次尝试获取数据失败: {e2}")
            try:
                print(f"尝试使用 {clean_symbol}.sz 格式获取数据")
                data = ak.stock_zh_a_hist(symbol=f"{clean_symbol}.sz", start_date=start_date_formatted, end_date=end_date_formatted, adjust="qfq")
            except Exception as e3:
                print(f"第三次尝试获取数据失败: {e3}")
                raise
    
    # 转换日期格式并设置为索引
    data['日期'] = pd.to_datetime(data['日期'])
    data.set_index('日期', inplace=True)
    
    # 按照日期升序排序
    data = data.sort_index()
    
    print(f"成功获取股票数据，共 {len(data)} 条记录")
    return data



