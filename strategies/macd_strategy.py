import backtrader as bt
import os
import pandas as pd
from datetime import datetime, timedelta

class MACDStrategy(bt.Strategy):
    params = (
        ('macd1', 12),     # 快线周期
        ('macd2', 26),     # 慢线周期
        ('macdsig', 9),    # 信号线周期
        ('trail', True),   # 是否使用追踪止损
        ('trailamount', 0.02),  # 追踪止损比例
    )

    def __init__(self):
        # 计算MACD指标
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.macd1,
            period_me2=self.params.macd2,
            period_signal=self.params.macdsig
        )
        
        # MACD柱状图
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        
        # 用于记录交易
        self.order = None
        self.price = None
        self.comm = None
        
        # 追踪止损
        self.trailing_stop = None
        self.highest_price = 0

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行, 价格: {order.executed.price:.2f}, 成本: {order.executed.value:.2f}, 手续费: {order.executed.comm:.2f}')
                self.price = order.executed.price
                self.comm = order.executed.comm
                
                # 设置追踪止损
                if self.params.trail:
                    self.highest_price = self.price
                    self.trailing_stop = self.highest_price * (1 - self.params.trailamount)
            else:
                self.log(f'卖出执行, 价格: {order.executed.price:.2f}, 成本: {order.executed.value:.2f}, 手续费: {order.executed.comm:.2f}')
                self.trailing_stop = None
                self.highest_price = 0

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单被取消/拒绝')

        self.order = None

    def next(self):
        # 如果有未完成的订单，不操作
        if self.order:
            return

        # 更新追踪止损
        if self.position and self.params.trail and self.trailing_stop is not None:
            if self.data.close[0] > self.highest_price:
                self.highest_price = self.data.close[0]
                self.trailing_stop = self.highest_price * (1 - self.params.trailamount)
            
            # 触发追踪止损
            if self.data.close[0] < self.trailing_stop:
                self.log(f'触发追踪止损, 当前价格: {self.data.close[0]:.2f}, 止损价: {self.trailing_stop:.2f}')
                self.order = self.sell(size=self.position.size)
                return

        # 没有持仓
        if not self.position:
            # MACD金叉，买入信号
            if self.mcross > 0 and self.macd.macd[0] < 0:  # 在0轴下方金叉
                self.log(f'买入信号, MACD: {self.macd.macd[0]:.4f}, Signal: {self.macd.signal[0]:.4f}')
                # 使用全部资金的90%买入
                size = int(self.broker.getcash() * 0.9 / self.data.close[0])
                self.order = self.buy(size=size)
        
        # 有持仓
        else:
            # MACD死叉，卖出信号
            if self.mcross < 0:
                self.log(f'卖出信号, MACD: {self.macd.macd[0]:.4f}, Signal: {self.macd.signal[0]:.4f}')
                self.order = self.sell(size=self.position.size)

def run_backtest():
    cerebro = bt.Cerebro()
    data_path = 'data/000001.csv'  # 使用平安银行股票数据
    
    # 优先读取本地数据
    if os.path.exists(data_path):
        print('正在读取本地数据...')
        data = pd.read_csv(data_path, index_col=0, parse_dates=True)
    else:
        print('本地数据不存在，请先运行sma_cross_strategy.py下载数据')
        return

    if data is None or data.empty:
        print('数据无效，无法回测。')
        return

    # 确保数据列名为小写
    data.columns = [col.lower() for col in data.columns]

    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(MACDStrategy)
    
    # 设置初始资金和手续费
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    print(f'初始资金: {cerebro.broker.getvalue():.2f}')
    results = cerebro.run()
    strat = results[0]
    
    # 输出分析结果
    print(f'最终资金: {cerebro.broker.getvalue():.2f}')
    print(f'总收益率: {strat.analyzers.returns.get_analysis()["rtot"]:.2%}')
    print(f'年化收益率: {strat.analyzers.returns.get_analysis()["rnorm"]:.2%}')
    print(f'夏普比率: {strat.analyzers.sharpe.get_analysis()["sharperatio"]:.3f}')
    print(f'最大回撤: {strat.analyzers.drawdown.get_analysis()["max"]["drawdown"]:.2%}')
    
    # 绘制结果图表
    cerebro.plot()

if __name__ == '__main__':
    run_backtest() 