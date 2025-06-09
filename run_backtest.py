import backtrader as bt
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime
import importlib
import sys

# 导入策略
sys.path.append('.')
from strategies.sma_cross_strategy import SMACrossStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from utils.analyzer import analyze_results, compare_strategies

def load_data(symbol='000001'):
    """
    加载数据
    
    参数:
    symbol (str): 股票代码
    
    返回:
    pandas.DataFrame: 股票数据
    """
    data_path = f'data/{symbol}.csv'
    
    if os.path.exists(data_path):
        print(f'正在读取{symbol}本地数据...')
        data = pd.read_csv(data_path, index_col=0, parse_dates=True)
        
        # 确保数据列名为小写
        data.columns = [col.lower() for col in data.columns]
        return data
    else:
        print(f'本地数据{symbol}不存在，请先下载数据')
        return None

def run_strategy(strategy_class, strategy_params=None, data=None, initial_cash=100000.0):
    """
    运行单个策略的回测
    
    参数:
    strategy_class: 策略类
    strategy_params (dict): 策略参数
    data (pandas.DataFrame): 股票数据
    initial_cash (float): 初始资金
    
    返回:
    dict: 回测结果
    """
    if data is None or data.empty:
        print('数据无效，无法回测。')
        return None
        
    cerebro = bt.Cerebro()
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(data_feed)
    
    # 添加策略
    if strategy_params:
        cerebro.addstrategy(strategy_class, **strategy_params)
    else:
        cerebro.addstrategy(strategy_class)
    
    # 设置初始资金和手续费
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 记录初始资金
    start_cash = cerebro.broker.getvalue()
    print(f'初始资金: {start_cash:.2f}')
    
    # 运行回测
    results = cerebro.run()
    strat = results[0]
    
    # 记录最终资金
    end_cash = cerebro.broker.getvalue()
    print(f'最终资金: {end_cash:.2f}')
    
    # 计算收益率
    returns = strat.analyzers.returns.get_analysis()
    total_return = end_cash / start_cash - 1
    annual_return = returns.get('rnorm', 0)
    
    # 计算夏普比率
    sharpe = strat.analyzers.sharpe.get_analysis()
    sharpe_ratio = sharpe.get('sharperatio', 0)
    
    # 计算最大回撤
    drawdown = strat.analyzers.drawdown.get_analysis()
    max_drawdown = drawdown.get('max', {}).get('drawdown', 0)
    
    # 交易分析
    trades = strat.analyzers.trades.get_analysis()
    total_trades = trades.get('total', {}).get('total', 0)
    won_trades = trades.get('won', {}).get('total', 0)
    lost_trades = trades.get('lost', {}).get('total', 0)
    win_rate = won_trades / total_trades if total_trades > 0 else 0
    
    # 整理结果
    results_dict = {
        'initial_cash': start_cash,
        'final_cash': end_cash,
        'total_return': total_return,
        'annual_return': annual_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'total_trades': total_trades,
        'won_trades': won_trades,
        'lost_trades': lost_trades,
        'win_rate': win_rate
    }
    
    return results_dict

def main():
    # 创建结果目录
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # 加载数据
    data = load_data('000001')
    if data is None:
        return
    
    # 定义要测试的策略及其参数
    strategies = [
        {
            'name': 'SMA交叉策略',
            'class': SMACrossStrategy,
            'params': {'fast_period': 10, 'slow_period': 30}
        },
        {
            'name': 'SMA交叉策略(5,20)',
            'class': SMACrossStrategy,
            'params': {'fast_period': 5, 'slow_period': 20}
        },
        {
            'name': 'RSI策略',
            'class': RSIStrategy,
            'params': {'rsi_period': 14, 'rsi_overbought': 70, 'rsi_oversold': 30}
        },
        {
            'name': 'RSI策略(改进版)',
            'class': RSIStrategy,
            'params': {'rsi_period': 10, 'rsi_overbought': 75, 'rsi_oversold': 25}
        },
        {
            'name': 'MACD策略',
            'class': MACDStrategy,
            'params': {'macd1': 12, 'macd2': 26, 'macdsig': 9, 'trail': True, 'trailamount': 0.02}
        },
        {
            'name': 'MACD策略(无追踪止损)',
            'class': MACDStrategy,
            'params': {'macd1': 12, 'macd2': 26, 'macdsig': 9, 'trail': False}
        }
    ]
    
    # 运行每个策略并收集结果
    all_results = {}
    for strategy in strategies:
        print(f"\n运行 {strategy['name']}...")
        result = run_strategy(
            strategy['class'], 
            strategy['params'], 
            data
        )
        if result:
            all_results[strategy['name']] = result
            # 分析并保存单个策略结果
            analyze_results(strategy['name'].replace(' ', '_'), result)
    
    # 比较所有策略
    if all_results:
        compare_strategies(all_results)
        print("\n所有策略回测完成！")

if __name__ == '__main__':
    main() 