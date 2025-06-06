import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def download_stock_data(symbol, start_date=None, end_date=None, period='1y'):
    """
    下载股票数据
    
    参数:
    symbol (str): 股票代码
    start_date (str): 开始日期，格式：'YYYY-MM-DD'
    end_date (str): 结束日期，格式：'YYYY-MM-DD'
    period (str): 如果未指定日期范围，则使用此参数，例如：'1d', '5d', '1mo', '3mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
    
    返回:
    pandas.DataFrame: 包含股票数据的DataFrame
    """
    if start_date is None and end_date is None:
        data = yf.download(symbol, period=period)
    else:
        data = yf.download(symbol, start=start_date, end=end_date)
    
    return data

def calculate_returns(data):
    """
    计算收益率
    
    参数:
    data (pandas.DataFrame): 包含股票数据的DataFrame
    
    返回:
    pandas.DataFrame: 添加了收益率列的DataFrame
    """
    data['Returns'] = data['Close'].pct_change()
    return data

def save_data_to_csv(data, filename):
    """
    将数据保存为CSV文件
    
    参数:
    data (pandas.DataFrame): 要保存的数据
    filename (str): 文件名
    """
    data.to_csv(f'data/{filename}.csv') 