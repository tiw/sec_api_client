# SEC API客户端项目命令行使用指南

## 🎯 项目概述

本项目提供访问美国证券交易委员会(SEC) EDGAR数据库的工具，用于获取公司10-K、10-Q财务报告和XBRL结构化数据。项目包含两个主要工具集：

1. **SEC API客户端** - 基础财务数据获取工具
2. **US-GAAP概念工具** - 高级财务概念下载和解释工具

## 🔧 SEC API客户端命令行工具

### 主要入口

```bash
# 查看项目基本信息和使用方法
python main.py
```

### 基础使用示例

```bash
# 运行基本使用示例
python examples/basic_usage.py

# 运行XBRL数据演示
python examples/xbrl_frames_demo.py

# 运行财务分析演示
python examples/financial_analysis_demo.py
```

## 📚 US-GAAP概念工具命令行使用方法

### 1. 运行完整演示

```bash
# 运行所有功能的完整演示
python demo_gaap_tools.py
```

### 2. 概念下载工具 (download_gaap_concepts.py)

#### 基本用法

```bash
# 仅下载概念列表
python download_gaap_concepts.py --concepts-only --output concepts.csv

# 下载包含详细定义的概念
python download_gaap_concepts.py --with-definitions --output concepts_full.csv

# 按分类下载概念
python download_gaap_concepts.py --category assets --output assets.csv
python download_gaap_concepts.py --category liabilities --output liabilities.csv
python download_gaap_concepts.py --category equity --output equity.csv
```

#### 高级用法

```bash
# 创建完整概念词典
python download_gaap_concepts.py --create-dictionary

# 指定用户代理
python download_gaap_concepts.py --user-agent "Your Name <your.email@domain.com>"
```

#### 支持的分类参数

- `assets` - 资产类概念
- `liabilities` - 负债类概念
- `equity` - 权益类概念
- `revenue` - 收入类概念
- `expenses` - 费用类概念
- `cash_flow` - 现金流类概念
- `per_share` - 每股数据概念
- `ratios` - 比率类概念

### 3. 概念解释工具 (gaap_concept_explainer.py)

#### 单个概念解释

```bash
# 解释单个概念
python gaap_concept_explainer.py --single-concept NetIncomeLoss

# 解释并保存结果
python gaap_concept_explainer.py --single-concept Assets --output assets_explanation.json
```

#### 批量概念解释

```bash
# 解释多个概念
python gaap_concept_explainer.py --concepts Assets Liabilities NetIncomeLoss --output batch.json

# 从文件读取概念列表进行解释
echo -e "Assets\\nLiabilities\\nStockholdersEquity" > concepts.txt
python gaap_concept_explainer.py --concepts-file concepts.txt --output explanations.csv
```

#### 估值分析相关概念

```bash
# 解释所有估值分析相关概念
python gaap_concept_explainer.py --valuation-concepts --output valuation.csv
```

### 4. 组合使用示例

```bash
# 1. 下载资产类概念列表
python download_gaap_concepts.py --category assets --concepts-only --output assets_list.csv

# 2. 提取概念名称到文本文件
cut -d',' -f1 assets_list.csv | tail -n +2 > assets_concepts.txt

# 3. 批量解释这些概念
python gaap_concept_explainer.py --concepts-file assets_concepts.txt --output assets_explained.json
```

## 📊 输出格式说明

### CSV格式
包含以下字段：
- `concept`: 概念名称
- `taxonomy`: 分类标准
- `chinese_name`: 中文名称
- `chinese_definition`: 中文定义
- `category`: 概念分类
- `data_type`: 数据类型

### JSON格式
包含完整的概念信息：
- 基本信息（名称、分类、数据类型）
- 中文对照信息
- 使用情况分析
- 估值分析上下文
- 实际数据示例

## ⚠️ 重要注意事项

### API使用限制
1. **速率限制**: 工具自动遵守SEC API的10次/秒限制
2. **用户代理**: 建议设置包含您邮箱的用户代理字符串
3. **网络连接**: 需要稳定的网络连接访问SEC API
4. **数据实时性**: 概念定义基于最新的GAAP标准

### 推荐使用流程
1. 先运行演示了解功能：`python demo_gaap_tools.py`
2. 根据需求选择下载或解释工具
3. 使用合适的参数和输出格式
4. 查看生成的文件进行后续分析

## 🎯 快速开始命令

```bash
# 1. 查看项目信息
python main.py

# 2. 运行基础示例
python examples/basic_usage.py

# 3. 运行US-GAAP工具演示
python demo_gaap_tools.py

# 4. 下载基本概念列表
python download_gaap_concepts.py --concepts-only --output basic_concepts.csv

# 5. 解释重要财务概念
python gaap_concept_explainer.py --single-concept NetIncomeLoss
```