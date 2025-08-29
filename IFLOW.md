# IFLOW.md - SEC EDGAR API 客户端项目文档

## 📋 项目概述

这是一个功能完整的Python库，用于访问美国证券交易委员会(SEC)的EDGAR数据库，获取公司的10-K、10-Q财务报告和XBRL结构化数据。

**项目类型**: Python代码项目
**主要技术栈**: Python 3.x, requests, pandas, numpy, beautifulsoup4, lxml
**项目状态**: 生产就绪，包含完整的功能模块和示例代码

## 🎯 核心功能

- **🔍 公司信息搜索**: 根据股票代码搜索公司基本信息
- **📋 10-K/10-Q文档获取**: 下载和解析年报、季报文档
- **💰 XBRL/Frames数据**: 获取结构化财务数据（资产负债表、损益表等）
- **📊 财务分析**: 计算财务比率、增长率、趋势分析
- **📈 同行对比**: 多公司财务数据对比分析

## 📁 项目结构

```
sec_api_client/
├── src/                     # 源代码目录
│   ├── sec_client.py        # SEC API核心客户端 (219行)
│   ├── xbrl_frames.py       # XBRL/Frames数据客户端 (284行)
│   ├── document_retriever.py # 10-K/10-Q文档获取器
│   ├── financial_analyzer.py # 财务数据分析器
│   ├── concept_explainer.py # 财务概念解释器
│   └── __init__.py          # 包初始化文件
├── examples/                # 使用示例目录
│   ├── basic_usage.py       # 基本使用示例
│   ├── xbrl_frames_demo.py  # XBRL数据演示
│   ├── financial_analysis_demo.py # 财务分析演示
│   ├── test_sec_api.py      # API测试
│   └── batch_sec_data_fetcher.py # 批量数据获取
├── tests/                   # 测试代码目录
│   └── test_sec_client.py   # 客户端测试
├── main.py                  # 主程序入口 (72行)
├── requirements.txt         # Python依赖 (8个包)
├── README.md               # 详细项目文档
└── IFLOW.md               # iFlow CLI交互文档
```

## ⚡ 快速开始命令

### 环境设置
```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行示例
```bash
# 基本使用示例
python examples/basic_usage.py

# XBRL数据演示
python examples/xbrl_frames_demo.py

# 财务分析演示
python examples/financial_analysis_demo.py

# 批量数据获取
python examples/batch_sec_data_fetcher.py
```

### 测试
```bash
# 运行测试
python -m pytest tests/
```

## 🔧 开发命令

### 代码质量检查
```bash
# 检查代码风格 (需要安装flake8)
flake8 src/ --max-line-length=120

# 类型检查 (需要安装mypy)
mypy src/
```

### 依赖管理
```bash
# 添加新依赖
pip install <package>
pip freeze > requirements.txt

# 更新所有依赖
pip install --upgrade -r requirements.txt
```

## 📊 核心模块说明

### SECClient (src/sec_client.py:1)
- 核心API客户端，处理HTTP请求和频率限制
- 支持公司搜索、文档获取等基础功能
- 自动处理SEC API的频率限制（每秒10次请求）

### XBRLFramesClient (src/xbrl_frames.py:1)
- XBRL结构化数据访问客户端
- 支持年度、季度和瞬时财务数据查询
- 包含常用US-GAAP财务指标定义

### FinancialAnalyzer (src/financial_analyzer.py)
- 财务数据分析工具
- 计算财务比率、增长率、趋势分析
- 支持同行对比和季节性分析

## 🎮 常用代码片段

### 初始化客户端
```python
from src import SECClient, XBRLFramesClient

# 必须提供有效的User-Agent（包含邮箱）
sec_client = SECClient(user_agent="您的姓名 your@email.com")
xbrl_client = XBRLFramesClient(sec_client)
```

### 获取公司信息
```python
# 搜索公司
company = sec_client.search_company_by_ticker('AAPL')
print(f"公司: {company['title']}, CIK: {company['cik']}")
```

### 获取财务数据
```python
# 获取年度财务指标
metrics = xbrl_client.get_financial_metrics('AAPL', period_type='annual')
print(metrics.head())

# 获取特定财务概念数据
revenue_data = xbrl_client.get_concept_data('Revenues', 'CY2023')
```

## ⚠️ 重要配置

### User-Agent要求
SEC API要求所有请求必须包含有效的User-Agent头，格式建议：`"您的姓名 your@email.com"`

### 频率限制
- 每秒最多10次API请求
- 客户端已内置频率限制机制
- 建议在美国业务时间外使用

### 数据格式
- 期间格式: `CY2023` (年度), `CY2023Q1` (季度), `CY2023Q1I` (瞬时)
- 财务指标使用US-GAAP标准概念

## 🔍 文件搜索模式

### 查找财务指标定义
```bash
# 搜索特定财务概念
grep -r "Revenues" src/
```

### 查找API端点
```bash
# 搜索API URL定义
grep -r "BASE_URL" src/
```

### 查找示例用法
```bash
# 搜索示例代码
grep -r "get_financial_metrics" examples/
```

## 📈 扩展建议

1. **添加缓存机制**: 减少重复API调用
2. **增强错误处理**: 处理网络异常和API限制
3. **添加数据验证**: 确保财务数据准确性
4. **支持更多财务指标**: 扩展US-GAAP概念覆盖
5. **添加可视化**: 集成matplotlib或plotly图表

## 🆘 故障排除

### 常见问题
1. **User-Agent错误**: 确保提供有效的User-Agent头
2. **频率限制**: 客户端已处理，如遇限制请稍后重试
3. **网络连接**: 检查网络连接和代理设置

### 调试模式
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

*本文档由iFlow CLI自动生成 - 最后更新: 2025-08-25*