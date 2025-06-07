import backtrader as bt
import akshare as ak
from datetime import datetime, timedelta
import time
import os
import pandas as pd

class SMACrossStrategy(bt.Strategy):
    params = (
        ('fast_period', 10),  # 快速移动平均线周期
        ('slow_period', 30),  # 慢速移动平均线周期
    )

    def __init__(self):
        # 计算快速和慢速移动平均线
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        
        # 交叉信号
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if not self.position:  # 没有持仓
            if self.crossover > 0:  # 金叉，买入信号
                self.buy()
        else:  # 有持仓
            if self.crossover < 0:  # 死叉，卖出信号
                self.sell()

def run_backtest():
    cerebro = bt.Cerebro()
    data_path = 'data/000001.csv'  # 使用平安银行股票数据
    data = None
    # 优先读取本地数据
    if os.path.exists(data_path):
        print('正在读取本地数据...')
        data = pd.read_csv(data_path, index_col=0, parse_dates=True)
    else:
        print('本地数据不存在，尝试下载...')
        try:
            # 使用akshare获取平安银行的历史数据
            data = ak.stock_zh_a_hist(symbol="000001", period="daily", 
                                    start_date=(datetime.now() - timedelta(days=365)).strftime('%Y%m%d'),
                                    end_date=datetime.now().strftime('%Y%m%d'),
                                    adjust="qfq")
            print("原始数据列名:", data.columns.tolist())
            # 重命名列以匹配backtrader的要求
            data = data.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change',
                '换手率': 'turnover'
            })
            # 将日期列转换为datetime格式
            data['date'] = pd.to_datetime(data['date'])
            data.set_index('date', inplace=True)
            data.to_csv(data_path)
            print('数据下载成功并已保存到本地。')
        except Exception as e:
            print(f"下载数据失败: {str(e)}")
            return

    if data is None or data.empty:
        print('数据无效，无法回测。')
        return

    # 确保数据列名为小写
    data.columns = [col.lower() for col in data.columns]

    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(SMACrossStrategy)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    print(f'初始资金: {cerebro.broker.getvalue():.2f}')
    cerebro.run()
    print(f'最终资金: {cerebro.broker.getvalue():.2f}')
    cerebro.plot()

if __name__ == '__main__':
    run_backtest() 