# 量化回测项目

这是一个用于量化交易策略回测的项目。该项目使用Python实现，主要功能包括：

- 数据获取和处理
- 策略实现
- 回测执行
- 性能分析

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yidadayi/test.git
cd test
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行示例策略：
```bash
python strategies/sma_cross_strategy.py
```

2. 查看回测结果：
回测结果将保存在 `results` 目录下。

## 项目结构

```
.
├── data/               # 数据存储目录
├── strategies/         # 策略实现
├── utils/             # 工具函数
├── results/           # 回测结果
└── requirements.txt   # 项目依赖
``` 