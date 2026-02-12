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
    
    # 使用akshare获取A股日线数据
    print(f"正在获取股票数据: {symbol}, 时间范围: {start_date} ({start_date_formatted}) 到 {end_date} ({end_date_formatted})")
    
    # 确保股票代码格式正确，移除可能的后缀
    clean_symbol = symbol.replace('.ss', '').replace('.sz', '')
    print(f"清理后的股票代码: {clean_symbol}")
    
    # 尝试使用不同的方法获取数据
    try:
        # 方法1：直接使用股票代码
        print("尝试方法1：直接使用股票代码")
        data = ak.stock_zh_a_hist(symbol=clean_symbol, start_date=start_date_formatted, end_date=end_date_formatted, adjust="qfq")
    except Exception as e1:
        print(f"方法1失败: {e1}")
        try:
            # 方法2：使用akshare的股票搜索功能获取正确的代码
            print("尝试方法2：使用股票搜索功能")
            stock_info = ak.stock_zh_a_spot_em()
            stock_code = stock_info[stock_info['代码'] == clean_symbol]['代码'].iloc[0]
            print(f"通过搜索获取的股票代码: {stock_code}")
            data = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date_formatted, end_date=end_date_formatted, adjust="qfq")
        except Exception as e2:
            print(f"方法2失败: {e2}")
            try:
                # 方法3：使用akshare的另一个API
                print("尝试方法3：使用stock_zh_a_daily API")
                data = ak.stock_zh_a_daily(symbol=clean_symbol, start_date=start_date_formatted, end_date=end_date_formatted, adjust="qfq")
            except Exception as e3:
                print(f"方法3失败: {e3}")
                # 所有方法都失败，重新抛出原始异常
                raise Exception(f"获取股票数据失败，尝试了多种方法: {e1}, {e2}, {e3}")
    
    # 转换日期格式并设置为索引
    data['日期'] = pd.to_datetime(data['日期'])
    data.set_index('日期', inplace=True)
    
    # 按照日期升序排序
    data = data.sort_index()
    
    print(f"成功获取股票数据，共 {len(data)} 条记录")
    return data



