# SEC EDGAR API 客户端

🚀 一个功能完整的Python库，用于访问美国证券交易委员会(SEC)的EDGAR数据库，获取公司的10-K、10-Q财务报告和XBRL结构化数据。

## 🎯 主要功能

- **🔍 公司信息搜索**: 根据股票代码搜索公司基本信息
- **📋 10-K/10-Q文档获取**: 下载和解析年报、季报文档
- **💰 XBRL/Frames数据**: 获取结构化财务数据（资产负债表、损益表等）
- **📊 财务分析**: 计算财务比率、增长率、趋势分析
- **📈 同行对比**: 多公司财务数据对比分析
- **📅 季节性分析**: 基于季度数据的周期性分析

## 📺 项目结构

```
.
├── venv/                    # Python虚拟环境
├── src/                     # 源代码目录
│   ├── __init__.py          # 包初始化文件
│   ├── sec_client.py        # SEC API核心客户端
│   ├── document_retriever.py # 10-K/10-Q文档获取器
│   ├── xbrl_frames.py       # XBRL/Frames数据客户端
│   └── financial_analyzer.py # 财务数据分析器
├── examples/                # 使用示例
│   ├── basic_usage.py       # 基本使用示例
│   ├── xbrl_frames_demo.py  # XBRL数据演示
│   └── financial_analysis_demo.py # 财务分析演示
├── tests/                   # 测试代码目录
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
├── README.md              # 项目文档
└── .gitignore             # Git忽略文件配置
```

## ⚡ 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 基本使用

```python
from src import SECClient, XBRLFramesClient

# 初始化客户端（请使用您的真实邮箱）
sec_client = SECClient(user_agent="您的姓名 your@email.com")
xbrl_client = XBRLFramesClient(sec_client)

# 搜索公司信息
company = sec_client.search_company_by_ticker('AAPL')
print(f"公司: {company['title']}")

# 获取财务数据
metrics = xbrl_client.get_financial_metrics('AAPL', period_type='annual')
print(metrics.head())
```

### 3. 运行示例

```bash
# 基本使用示例
python examples/basic_usage.py

# XBRL数据演示
python examples/xbrl_frames_demo.py

# 财务分析演示
python examples/financial_analysis_demo.py
```

## 📚 API使用指南

### SECClient - 核心客户端

```python
from src import SECClient

client = SECClient(user_agent="您的邮箱@example.com")

# 搜索公司
company = client.search_company_by_ticker('TSLA')

# 获取最近的文档提交
filings = client.get_recent_filings(
    cik=company['cik'], 
    form_types=['10-K', '10-Q'], 
    limit=5
)
```

### DocumentRetriever - 文档获取器

```python
from src import DocumentRetriever

retriever = DocumentRetriever(sec_client)

# 获取公司的10-K/10-Q文档
filings = retriever.get_10k_10q_filings('AMZN', years=2)

# 获取财务亮点
highlights = retriever.get_financial_highlights('AMZN', form_type='10-Q')
```

### XBRLFramesClient - XBRL数据客户端

```python
from src import XBRLFramesClient

xbrl = XBRLFramesClient(sec_client)

# 获取特定财务概念的数据
revenue_data = xbrl.get_concept_data('Revenues', 'CY2023Q1I')

# 获取公司财务指标
metrics = xbrl.get_financial_metrics('GOOGL', period_type='quarterly')

# 季度数据对比
quarterly = xbrl.get_quarterly_comparison('Assets', 2023)
```

### FinancialAnalyzer - 财务分析器

```python
from src import FinancialAnalyzer

analyzer = FinancialAnalyzer()

# 计算财务比率
ratios = analyzer.calculate_financial_ratios(financial_data)

# 计算增长率
growth = analyzer.calculate_growth_rates(financial_data, 'Revenues')

# 趋势分析
trends = analyzer.trend_analysis(financial_data, ['Revenues', 'NetIncomeLoss'])

# 同行对比
comparison = analyzer.peer_comparison(companies_data, 'Revenues')
```

## 📊 支持的财务指标

### 资产负债表项目
- `Assets` - 总资产
- `AssetsCurrent` - 流动资产
- `CashAndCashEquivalentsAtCarryingValue` - 现金及现金等价物
- `AccountsReceivableNetCurrent` - 应收账款净额
- `Liabilities` - 总负债
- `LiabilitiesCurrent` - 流动负债
- `AccountsPayableCurrent` - 应付账款
- `StockholdersEquity` - 股东权益

### 损益表项目
- `Revenues` - 营业收入
- `CostOfRevenue` - 销售成本
- `GrossProfit` - 毛利润
- `OperatingIncomeLoss` - 营业利润
- `NetIncomeLoss` - 净利润
- `EarningsPerShareBasic` - 基本每股收益

### 现金流量表项目
- `NetCashProvidedByUsedInOperatingActivities` - 经营活动现金流
- `NetCashProvidedByUsedInInvestingActivities` - 投资活动现金流
- `NetCashProvidedByUsedInFinancingActivities` - 筹资活动现金流

## 🔄 期间格式说明

在XBRL/Frames API中，期间字符串格式如下：

- `CY2023` - 2023年年度数据
- `CY2023Q1` - 2023年第一季度数据（约为91天期间）
- `CY2023Q1I` - 2023年第一季度的瞬时数据（特定时点）

## ⚠️ 重要提醒

1. **User-Agent要求**: SEC要求所有API请求必须包含有效的User-Agent头，建议包含您的姓名和邮箱地址

2. **频率限制**: SEC API每秒最多允许10次请求，本客户端已自动处理频率限制

3. **服务时间**: 建议在美国业务时间外使用，以避免影响SEC服务器性能

4. **数据准确性**: 请以SEC官方数据为准，本工具仅作为数据获取和分析的便利工具

## 🔧 开发指南

1. 在`src/`目录下编写您的源代码
2. 在`tests/`目录下编写测试代码
3. 添加新依赖时，请更新`requirements.txt`文件
4. 提交代码前运行测试确保代码质量

## 📖 参考资料

- [SEC EDGAR API文档](https://www.sec.gov/edgar/sec-api-documentation)
- [XBRL US-GAAP分类标准](https://xbrl.us/xbrl-taxonomy/2021-us-gaap/)
- [SEC数据使用政策](https://www.sec.gov/privacy.htm#dissemination)

## 📜 许可证

本项目仅用于教育和研究目的。使用本工具获取的数据不构成投资建议，请谨慎解读和使用财务数据。