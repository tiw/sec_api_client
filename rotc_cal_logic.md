🎯 ROTC计算更新成功！
✅ 主要更新内容：
分母更新：从 (Liabilities + StockholdersEquity) 改为 (LongTermDebtNoncurrent + StockholdersEquity)
EstimatedInterestExpense计算公式更新：
原公式：LongTermDebtNoncurrent × 4%
新公式：LongTermDebtNoncurrent × 4% × (1-Effective Tax Rate)
实际税率计算：自动从财务数据中计算实际税率 = 24.1%
📊 计算结果对比：
从输出中可以看到，新的ROTC计算结果为：

Effective Tax Rate: 24.1% (所得税费用 ÷ 税前利润)
EstimatedInterestExpense: $85.75B × 4% × (1-24.1%) = $2.60B
ROTC: (净利润 + 估算利息费用) ÷ (长期债务 + 股东权益) = ($93.74B + $2.60B) ÷ ($85.75B + $56.95B) ≈ 67.5%
🔄 技术改进：
更精确的利息费用估算：考虑了税收效应
更合理的资本基础：使用有息债务而非总负债
自动化税率计算：无需手动输入，直接从财务数据计算
详细的计算过程展示：每一步都有清晰的说明
这个更新让ROTC指标更加符合财务分析的最佳实践，能够更准确地反映Apple的总资本回报率。