import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime

def analyze_results(strategy_name, results_dict):
    """
    分析回测结果并生成报告
    
    参数:
    strategy_name (str): 策略名称
    results_dict (dict): 包含回测结果的字典
    """
    # 创建结果目录（如果不存在）
    if not os.path.exists('results'):
        os.makedirs('results')
        
    # 创建结果数据框
    results_df = pd.DataFrame([results_dict])
    
    # 保存结果到CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'results/{strategy_name}_{timestamp}.csv'
    results_df.to_csv(filename)
    
    print(f'分析结果已保存到 {filename}')
    return results_df

def plot_equity_curve(equity_curve, strategy_name):
    """
    绘制权益曲线
    
    参数:
    equity_curve (pandas.Series): 权益曲线数据
    strategy_name (str): 策略名称
    """
    plt.figure(figsize=(12, 6))
    plt.plot(equity_curve)
    plt.title(f'{strategy_name} - 权益曲线')
    plt.xlabel('日期')
    plt.ylabel('账户价值')
    plt.grid(True)
    
    # 保存图表
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'results/{strategy_name}_equity_curve_{timestamp}.png'
    plt.savefig(filename)
    plt.close()
    
    print(f'权益曲线图表已保存到 {filename}')

def calculate_performance_metrics(returns):
    """
    计算性能指标
    
    参数:
    returns (pandas.Series): 收益率序列
    
    返回:
    dict: 包含性能指标的字典
    """
    # 年化收益率
    annual_return = (1 + returns).prod() ** (252 / len(returns)) - 1
    
    # 波动率
    volatility = returns.std() * np.sqrt(252)
    
    # 夏普比率
    sharpe_ratio = annual_return / volatility if volatility != 0 else 0
    
    # 最大回撤
    cum_returns = (1 + returns).cumprod()
    max_drawdown = ((cum_returns.cummax() - cum_returns) / cum_returns.cummax()).max()
    
    # 胜率
    win_rate = len(returns[returns > 0]) / len(returns[returns != 0]) if len(returns[returns != 0]) > 0 else 0
    
    return {
        'annual_return': annual_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate
    }

def compare_strategies(strategies_results):
    """
    比较多个策略的性能
    
    参数:
    strategies_results (dict): 键为策略名称，值为策略结果的字典
    """
    # 创建比较数据框
    comparison_df = pd.DataFrame(strategies_results).T
    
    # 保存比较结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'results/strategies_comparison_{timestamp}.csv'
    comparison_df.to_csv(filename)
    
    # 绘制比较图表
    plt.figure(figsize=(14, 10))
    
    # 年化收益率比较
    plt.subplot(2, 2, 1)
    comparison_df['annual_return'].plot(kind='bar')
    plt.title('年化收益率比较')
    plt.grid(True)
    
    # 夏普比率比较
    plt.subplot(2, 2, 2)
    comparison_df['sharpe_ratio'].plot(kind='bar')
    plt.title('夏普比率比较')
    plt.grid(True)
    
    # 最大回撤比较
    plt.subplot(2, 2, 3)
    comparison_df['max_drawdown'].plot(kind='bar')
    plt.title('最大回撤比较')
    plt.grid(True)
    
    # 胜率比较
    plt.subplot(2, 2, 4)
    comparison_df['win_rate'].plot(kind='bar')
    plt.title('胜率比较')
    plt.grid(True)
    
    plt.tight_layout()
    
    # 保存比较图表
    chart_filename = f'results/strategies_comparison_{timestamp}.png'
    plt.savefig(chart_filename)
    plt.close()
    
    print(f'策略比较结果已保存到 {filename}')
    print(f'策略比较图表已保存到 {chart_filename}')
    
    return comparison_df 