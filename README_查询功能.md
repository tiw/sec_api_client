# SEC报告查询系统

一个强大的SEC财务报告数据查询系统，提供多维度、灵活的财务数据查询和分析功能。

## 功能特性

### 🔍 多维度查询
- **公司查询**: 支持ticker或CIK查询
- **报告类型**: 10-K、10-Q、8-K等14种报告类型  
- **年份过滤**: 支持单年或年份范围查询
- **指标查询**: 支持指定指标名称查询
- **数值过滤**: 支持最小值、最大值范围过滤
- **结果限制**: 可限制查询结果数量

### 📊 对比分析
- **多公司对比**: 支持多家公司同一指标的横向对比
- **趋势分析**: 支持年度变化率计算
- **可视化表格**: 自动生成对比表格显示

### 🏢 公司概览
- **财务数据概览**: 展示公司完整的财务数据情况
- **数据分布**: 按年份和报告类型统计
- **重要指标**: 自动识别和展示关键财务指标

### 📈 数据分析
- **统计信息**: 整体数据库统计和分析
- **年份分布**: 数据按年份的分布情况
- **公司排行**: 数据最丰富的公司排名

### 💾 数据导出
- **CSV格式**: 支持导出为CSV文件
- **Excel格式**: 支持导出为XLSX文件
- **完整数据**: 包含所有查询字段

## 安装和使用

### 系统要求
- Python 3.7+
- SQLite3 (默认) 或 PostgreSQL/MySQL
- pandas 库（用于数据导出）

### 快速开始

1. **查看帮助信息**
```bash
python sec_report_query.py --help
```

2. **查看数据库统计**
```bash
python sec_db_manager.py stats
```

3. **运行演示**
```bash
python demo_query.py
```

## 使用示例

### 1. 通用数据查询

```bash
# 查询苹果公司的10-K报告数据
python sec_report_query.py query --company AAPL --report-type 10-K

# 查询Balance Sheet部分的数据，限制10条结果
python sec_report_query.py query --section "Balance Sheet" --limit 10

# 查询2020-2024年的数据并导出
python sec_report_query.py query --year-range 2020-2024 --export results.csv

# 查询特定指标
python sec_report_query.py query --metrics Assets Revenue --years 2023 2024
```

### 2. 公司财务概览

```bash
# 查看苹果公司的财务数据概览
python sec_report_query.py company-overview --company AAPL

# 使用CIK查询
python sec_report_query.py company-overview --company 0000320193

# 只查看10-K报告的数据
python sec_report_query.py company-overview --company AAPL --report-type 10-K
```

### 3. 多公司指标对比

```bash
# 对比三家公司的Assets指标
python sec_report_query.py compare --metric Assets --companies AAPL MSFT GOOGL

# 对比特定年份的数据
python sec_report_query.py compare --metric "Total Revenue" --companies AAPL MSFT --years 2022 2023 2024

# 导出对比结果
python sec_report_query.py compare --metric Assets --companies AAPL MSFT --export comparison.csv
```

### 4. 数据统计分析

```bash
# 查看整体数据统计
python sec_report_query.py analytics

# 查看特定报告类型的统计
python sec_report_query.py analytics --report-type 10-K
```

### 5. 数据库管理

```bash
# 查看数据库统计信息
python sec_db_manager.py stats

# 查询特定公司的报告数据
python sec_db_manager.py query-reports --company AAPL --report-type 10-K

# 公司间指标对比
python sec_db_manager.py compare-metric --metric Assets --companies AAPL MSFT

# 查看特定公司的所有报告
python sec_db_manager.py query-company-reports --company AAPL
```

## 查询参数说明

### 通用查询参数
- `--company`: 公司标识，支持ticker (如AAPL) 或CIK (如0000320193)
- `--report-type`: 报告类型，如10-K、10-Q、8-K等
- `--section`: 报告部分名称，如"Balance Sheet"、"Income Statement"等
- `--metrics`: 指标名称列表，支持多个指标
- `--years`: 年份列表，支持多个年份
- `--year-range`: 年份范围，格式为"2020-2024"
- `--min-value`: 最小值过滤
- `--max-value`: 最大值过滤
- `--limit`: 结果数量限制
- `--export`: 导出文件路径，支持.csv和.xlsx格式

### 对比查询参数
- `--metric`: 要对比的指标名称
- `--companies`: 公司列表，支持多个公司
- `--years`: 年份列表（可选）
- `--report-type`: 报告类型过滤（可选）

## 数据库结构

系统支持以下主要数据表：
- **companies**: 公司信息
- **report_types**: 报告类型
- **report_sections**: 报告部分
- **metrics**: 财务指标
- **financial_data**: 财务数据
- **invalid_metric_cache**: 无效指标缓存
- **data_fetch_logs**: 数据获取日志

## 支持的报告类型

- **10-K**: 年度报告，包含完整财务报表
- **10-Q**: 季度报告，包含季度财务更新
- **8-K**: 重大事件报告
- **13-F**: 机构投资者持仓报告
- **Bank-Call Report**: 银行监管报告
- **Credit Risk**: 信用风险披露
- **Derivative**: 衍生品披露
- **Energy-Industry**: 能源行业报告
- **Fair Value**: 公允价值披露
- **Guarantee**: 担保披露
- **Healthcare**: 医疗保健报告
- **Insurance-SAP**: 保险公司法定会计报告
- **Investment Company**: 投资公司报告
- **Payment**: 支付系统披露

## 性能特性

- **缓存机制**: 智能缓存避免重复查询
- **分页查询**: 支持大数据量的分页处理
- **索引优化**: 数据库索引提升查询性能
- **并发支持**: 支持多用户并发查询

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库文件路径
   - 确认数据库权限

2. **查询结果为空**
   - 检查公司标识是否正确
   - 确认数据库中是否有相关数据
   - 验证查询条件是否过于严格

3. **导出失败**
   - 检查目标目录是否存在
   - 确认文件写入权限
   - 验证pandas库是否安装

### 日志调试
使用`--log-level DEBUG`参数可以查看详细的调试信息：

```bash
python sec_report_query.py query --company AAPL --log-level DEBUG
```

## 贡献

欢迎提交Issue和Pull Request来改进这个系统。

## 许可证

本项目采用MIT许可证。