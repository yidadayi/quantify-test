import backtrader as bt
import yfinance as yf
from datetime import datetime, timedelta

class SMACrossStrategy(bt.Strategy):
    params = (
        ('fast_period', 10),  # 快速移动平均线周期
        ('slow_period', 30),  # 慢速移动平均线周期
    )

    def __init__(self):
        # 计算快速和慢速移动平均线
        self.fast_ma = bt.indicators.SMA(
            self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(
            self.data.close, period=self.params.slow_period)
        
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
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    
    # 获取数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    data = yf.download('AAPL', start=start_date, end=end_date)
    
    # 将数据转换为 Backtrader 数据格式
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    
    # 添加策略
    cerebro.addstrategy(SMACrossStrategy)
    
    # 设置初始资金
    cerebro.broker.setcash(100000.0)
    
    # 设置交易手续费
    cerebro.broker.setcommission(commission=0.001)
    
    # 打印初始资金
    print(f'初始资金: {cerebro.broker.getvalue():.2f}')
    
    # 运行回测
    cerebro.run()
    
    # 打印最终资金
    print(f'最终资金: {cerebro.broker.getvalue():.2f}')
    
    # 绘制结果
    cerebro.plot()

if __name__ == '__main__':
    run_backtest() 