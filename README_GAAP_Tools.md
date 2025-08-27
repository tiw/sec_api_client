# US-GAAP财务概念下载和解释工具

本工具集提供了下载和解释US-GAAP（美国公认会计准则）财务概念的完整解决方案，支持批量处理、分类筛选和详细解释。

## 功能特色

### 🔍 概念下载器 (`download_gaap_concepts.py`)
- 下载完整的US-GAAP概念列表
- 支持按分类筛选（资产、负债、权益等）
- 可选择包含或不包含详细定义
- 多种输出格式（CSV、JSON、Excel）

### 📖 概念解释器 (`gaap_concept_explainer.py`)
- 获取概念的详细定义和使用说明
- 分析实际公司使用该概念的模式
- 提供中英文对照解释
- 特别支持估值分析相关概念
- 包含SEC实际数据示例

### 🎯 估值分析支持
根据项目的估值分析规范，工具特别支持：
- 市盈率相关概念（EPS等）
- 股息率相关概念（分红数据）
- 市现率相关概念（现金流数据）
- 企业价值分析概念（营收、利润、资本结构等）

## 快速开始

### 1. 运行演示脚本
```bash
python demo_gaap_tools.py
```
这将运行完整的演示，展示所有主要功能。

### 2. 下载基本概念列表
```bash
# 仅下载概念名称
python download_gaap_concepts.py --concepts-only --output concepts.csv

# 下载包含定义的完整信息
python download_gaap_concepts.py --with-definitions --output concepts_full.csv
```

### 3. 按分类下载概念
```bash
# 下载资产类概念
python download_gaap_concepts.py --category assets --output assets.csv

# 下载负债类概念  
python download_gaap_concepts.py --category liabilities --output liabilities.csv

# 其他可用分类：equity, revenue, expenses, cash_flow, per_share, ratios
```

### 4. 解释单个概念
```bash
# 详细解释净利润概念
python gaap_concept_explainer.py --single-concept NetIncomeLoss

# 解释总资产概念并保存结果
python gaap_concept_explainer.py --single-concept Assets --output assets_explanation.json
```

### 5. 批量解释概念
```bash
# 解释多个概念
python gaap_concept_explainer.py --concepts Assets Liabilities NetIncomeLoss --output batch.json

# 从文件读取概念列表
echo -e "Assets\nLiabilities\nStockholdersEquity" > concepts.txt
python gaap_concept_explainer.py --concepts-file concepts.txt --output explanations.csv
```

### 6. 估值分析相关概念
```bash
# 解释所有估值分析相关概念
python gaap_concept_explainer.py --valuation-concepts --output valuation.csv
```

### 7. 创建完整概念词典
```bash
# 创建包含所有概念的完整词典
python download_gaap_concepts.py --create-dictionary
```

## 输出文件说明

### CSV格式
包含以下主要字段：
- `concept`: 概念名称
- `chinese_name`: 中文名称
- `chinese_definition`: 中文定义
- `category`: 概念分类
- `data_type`: 数据类型
- `valuation_relevance`: 估值分析相关性

### JSON格式
包含完整的概念信息：
- 基本信息（名称、分类、数据类型）
- 中文对照信息
- 使用情况分析
- 估值分析上下文
- 实际数据示例

## 支持的概念分类

| 分类 | 说明 | 示例概念 |
|------|------|----------|
| assets | 资产类 | Assets, Cash, AccountsReceivable |
| liabilities | 负债类 | Liabilities, LongTermDebt, AccountsPayable |
| equity | 权益类 | StockholdersEquity, RetainedEarnings |
| revenue | 收入类 | Revenues, RevenueFromContract |
| expenses | 费用类 | OperatingExpenses, CostOfRevenue |
| cash_flow | 现金流类 | NetCashProvidedByOperating |
| per_share | 每股数据 | EarningsPerShare, BookValuePerShare |
| ratios | 比率类 | 各种财务比率 |

## 估值分析概念映射

根据项目的估值分析规范，工具特别标识了以下概念组：

### 估值水平指标
- **市盈率分子**: EarningsPerShareBasic, EarningsPerShareDiluted
- **股息率**: CommonStockDividendsPerShareDeclared, PaymentsOfDividends
- **市现率**: NetCashProvidedByUsedInOperatingActivities, DepreciationDepletionAndAmortization

### 企业价值指标
- **股东价值**: 营收、净利润、分红等
- **营收水平**: 各类收入概念
- **现金流水平**: 经营现金流、折旧摊销
- **净利润水平**: 净利润、税收相关
- **资本结构**: 资产、负债、权益
- **资本回报率**: ROE、ROTC相关概念

## 高级用法

### 自定义用户代理
```bash
python download_gaap_concepts.py --user-agent "Your Name <your.email@domain.com>"
```

### 指定分类标准
```bash
python gaap_concept_explainer.py --taxonomy us-gaap --single-concept Assets
```

### 组合使用
```bash
# 1. 先下载资产类概念
python download_gaap_concepts.py --category assets --concepts-only --output assets_list.csv

# 2. 提取概念名称到文本文件
cut -d',' -f1 assets_list.csv | tail -n +2 > assets_concepts.txt

# 3. 批量解释这些概念
python gaap_concept_explainer.py --concepts-file assets_concepts.txt --output assets_explained.json
```

## 注意事项

1. **API限制**: 工具自动控制请求频率以遵守SEC API的限制（≤10次/秒）
2. **用户代理**: 建议设置包含您邮箱的用户代理字符串
3. **网络连接**: 需要稳定的网络连接访问SEC API
4. **数据实时性**: 概念定义基于最新的GAAP标准，数据示例来自实际公司报告

## 错误处理

工具包含完善的错误处理机制：
- 网络错误会自动重试
- 单个概念失败不会影响批量处理
- 详细的日志记录帮助诊断问题

## 依赖项目模块

本工具基于项目现有的模块：
- `src.SECClient`: SEC API客户端
- `src.XBRLFramesClient`: XBRL数据客户端  
- `src.ConceptExplainer`: 概念解释器

确保这些模块正常工作后再使用本工具集。

## 输出示例

### 概念解释示例（NetIncomeLoss）
```
📊 概念详细解释: NetIncomeLoss
============================================================
分类: revenue
数据类型: monetary
中文名称: 净利润
中文定义: 企业在一定会计期间的经营成果
估值分析相关性: 企业价值 - 股东价值
计算作用: 用于股东价值回报计算和ROE分析
使用该概念的公司数: 3
常见单位: USD

数据示例:
  Apple Inc.: $93.74B (2024-09-28)
  Apple Inc.: $99.80B (2023-09-30)
  Apple Inc.: $94.68B (2022-09-24)
```

有了这些工具，您可以轻松下载和理解US-GAAP财务概念，为财务分析和投资决策提供强有力的支持！