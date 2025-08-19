#!/usr/bin/env python3
"""
SEC财务报告生成演示

使用模拟数据演示财务报告生成功能
邮箱: tting.wang@gmail.com
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import FinancialAnalyzer


def create_mock_financial_data(ticker="AAPL"):
    """创建模拟财务数据"""
    
    # 模拟3年的财务数据
    years = [2024, 2023, 2022]
    base_date = datetime(2024, 9, 30)
    
    data = []
    
    # 苹果公司的模拟财务数据（基于真实数据调整）
    financial_concepts = {
        'Revenues': [391035000000, 383285000000, 394328000000],  # 营收
        'CostOfRevenue': [210352000000, 214137000000, 223546000000],  # 销售成本
        'GrossProfit': [180683000000, 169148000000, 170782000000],  # 毛利润
        'OperatingExpenses': [57467000000, 54847000000, 51345000000],  # 营业费用
        'OperatingIncomeLoss': [123216000000, 114301000000, 119437000000],  # 营业利润
        'NetIncomeLoss': [93736000000, 96995000000, 99803000000],  # 净利润
        'EarningsPerShareBasic': [6.11, 6.16, 6.15],  # 基本每股收益
        'EarningsPerShareDiluted': [6.08, 6.13, 6.11],  # 稀释每股收益
        'Assets': [364980000000, 352755000000, 352583000000],  # 总资产
        'AssetsCurrent': [143566000000, 143700000000, 135405000000],  # 流动资产
        'Liabilities': [255020000000, 290020000000, 302083000000],  # 总负债
        'LiabilitiesCurrent': [133973000000, 145308000000, 153982000000],  # 流动负债
        'StockholdersEquity': [109960000000, 62146000000, 50672000000],  # 股东权益
        'CashAndCashEquivalentsAtCarryingValue': [67150000000, 73100000000, 48844000000]  # 现金
    }
    
    for i, year in enumerate(years):
        end_date = base_date.replace(year=year)
        
        for concept, values in financial_concepts.items():
            data.append({
                'ticker': ticker,
                'cik': '0000320193',
                'concept': concept,
                'concept_tag': concept,
                'value': values[i] if i < len(values) else values[-1],
                'start_date': end_date.replace(month=1, day=1),
                'end_date': end_date,
                'frame': f'CY{year}',
                'fiscal_year': year,
                'fiscal_period': 'FY',
                'form': '10-K',
                'filed_date': end_date + timedelta(days=30)
            })
    
    df = pd.DataFrame(data)
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    df['filed_date'] = pd.to_datetime(df['filed_date'])
    
    return df


def generate_markdown_report(data):
    """生成Markdown格式的财务报告"""
    
    company_name = data['company_name']
    ticker = data['ticker']
    cik = data['cik']
    financial_data = data.get('financial_data', {})
    ratios = data.get('ratios', {})
    trends = data.get('trends', {})
    
    # 获取最近3年的年份
    years = sorted(financial_data.keys(), reverse=True)[:3]
    
    markdown = f"""# {company_name} 财务报告
**股票代码**: {ticker} | **CIK**: {cik} | **报告生成**: {datetime.now().strftime('%Y-%m-%d')}

## 📊 综合损益表

*(金额单位：百万美元)*

| 财务指标 | {years[0] if len(years) > 0 else 'N/A'} | {years[1] if len(years) > 1 else 'N/A'} | {years[2] if len(years) > 2 else 'N/A'} |
|----------|------------------:|------------------:|------------------:|
"""
    
    # 财务指标行项目
    concept_mapping = {
        'Revenues': '**总营收**',
        'CostOfRevenue': '销售成本', 
        'GrossProfit': '**毛利润**',
        'OperatingExpenses': '营业费用',
        'OperatingIncomeLoss': '**营业利润**',
        'NetIncomeLoss': '**净利润**',
        'EarningsPerShareBasic': '基本每股收益',
        'EarningsPerShareDiluted': '稀释每股收益'
    }
    
    analyzer = FinancialAnalyzer()
    
    for concept, label in concept_mapping.items():
        row = f"| {label} |"
        
        for year in years:
            if year in financial_data and concept in financial_data[year]:
                value = financial_data[year][concept]['value']
                if concept.startswith('EarningsPerShare'):
                    # 每股收益保持原值
                    formatted_value = f"${value:.2f}"
                else:
                    # 其他金额转为百万美元
                    formatted_value = f"${value/1_000_000:,.0f}" if value else "N/A"
            else:
                formatted_value = "N/A"
            row += f" {formatted_value} |"
        
        markdown += row + "\n"
    
    # 资产负债表部分
    markdown += f"""
## 🏦 资产负债表概要

| 财务指标 | {years[0] if len(years) > 0 else 'N/A'} | {years[1] if len(years) > 1 else 'N/A'} | {years[2] if len(years) > 2 else 'N/A'} |
|----------|------------------:|------------------:|------------------:|
"""
    
    balance_concepts = {
        'Assets': '**总资产**',
        'AssetsCurrent': '流动资产',
        'Liabilities': '**总负债**', 
        'LiabilitiesCurrent': '流动负债',
        'StockholdersEquity': '**股东权益**',
        'CashAndCashEquivalentsAtCarryingValue': '现金及现金等价物'
    }
    
    for concept, label in balance_concepts.items():
        row = f"| {label} |"
        
        for year in years:
            if year in financial_data and concept in financial_data[year]:
                value = financial_data[year][concept]['value']
                formatted_value = f"${value/1_000_000:,.0f}" if value else "N/A"
            else:
                formatted_value = "N/A"
            row += f" {formatted_value} |"
        
        markdown += row + "\n"
    
    # 财务比率分析
    if ratios:
        markdown += "\\n## 📈 财务比率分析\\n\\n"
        
        ratio_items = [
            ('current_ratio', '流动比率', ''),
            ('debt_to_assets', '资产负债率', '%'),
            ('equity_ratio', '股东权益比率', '%'), 
            ('net_profit_margin', '净利润率', '%'),
            ('roa', '总资产收益率(ROA)', '%'),
            ('roe', '股东权益收益率(ROE)', '%')
        ]
        
        for ratio_key, ratio_name, unit in ratio_items:
            if ratio_key in ratios and not pd.isna(ratios[ratio_key]):
                value = ratios[ratio_key]
                if unit == '%':
                    markdown += f"- **{ratio_name}**: {value:.2%}\\n"
                else:
                    markdown += f"- **{ratio_name}**: {value:.2f}\\n"
    
    # 趋势分析
    if trends:
        markdown += "\\n## 📊 趋势分析\\n\\n"
        
        trend_names = {
            'Revenues': '营业收入',
            'NetIncomeLoss': '净利润', 
            'Assets': '总资产'
        }
        
        for concept, trend_info in trends.items():
            concept_name = trend_names.get(concept, concept)
            markdown += f"### {concept_name}\\n\\n"
            
            if 'data_points' in trend_info:
                markdown += f"- **数据点数**: {trend_info['data_points']}\\n"
            
            if 'latest_value' in trend_info:
                latest_formatted = analyzer.format_financial_number(trend_info['latest_value'])
                markdown += f"- **最新值**: {latest_formatted}\\n"
            
            if 'overall_change_pct' in trend_info:
                change = trend_info['overall_change_pct']
                direction = "📈" if change > 0 else "📉"
                markdown += f"- **总体变化**: {direction} {change:+.1f}%\\n"
            
            if 'trend_direction' in trend_info:
                direction_map = {
                    'increasing': '📈 上升趋势',
                    'decreasing': '📉 下降趋势', 
                    'mixed': '📊 震荡趋势'
                }
                trend_desc = direction_map.get(trend_info['trend_direction'], '未知趋势')
                markdown += f"- **近期趋势**: {trend_desc}\\n"
            
            markdown += "\\n"
    
    # 投资亮点
    markdown += """
## 💡 投资亮点

### 📱 产品组合
- **iPhone**: 全球领先的智能手机产品线
- **Mac**: 高端个人电脑和笔记本电脑
- **iPad**: 平板电脑市场领导者
- **Apple Watch**: 智能可穿戴设备
- **AirPods**: 无线耳机产品

### 🔧 服务业务
- **App Store**: 应用程序商店生态系统
- **iCloud**: 云存储和服务
- **Apple Music**: 音乐流媒体服务
- **Apple Pay**: 移动支付解决方案
- **AppleCare**: 设备保修和技术支持

### 🌟 竞争优势
- **品牌价值**: 全球最有价值的品牌之一
- **生态系统**: 硬件、软件、服务一体化
- **创新能力**: 持续的研发投入和技术领先
- **客户忠诚度**: 极高的用户粘性和重复购买率
- **供应链管理**: 全球化的高效供应链体系

## ⚠️ 风险提示

- **市场竞争**: 智能手机市场竞争激烈
- **供应链风险**: 全球供应链中断的影响
- **汇率波动**: 国际业务面临汇率风险
- **监管风险**: 各国政府监管政策变化
- **技术变革**: 新技术可能影响现有产品需求

"""
    
    # 报告信息
    markdown += f"""
---

## 📋 报告信息

- **数据来源**: SEC EDGAR数据库
- **User-Agent**: Ting Wang <tting.wang@gmail.com>
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **报告版本**: 演示版本 v1.0

*本报告仅供参考，不构成投资建议。投资有风险，决策需谨慎。*
"""
    
    return markdown


def generate_financial_report_demo(ticker="AAPL", output_file=None):
    """生成演示版财务报告"""
    
    print(f"🔍 正在生成 {ticker} 的财务报告演示...")
    
    # 创建模拟数据
    mock_data = create_mock_financial_data(ticker)
    
    # 公司信息
    company_info = {
        'AAPL': {'title': 'Apple Inc.', 'cik': '0000320193'},
        'MSFT': {'title': 'Microsoft Corporation', 'cik': '0000789019'},
        'GOOGL': {'title': 'Alphabet Inc.', 'cik': '0001652044'}
    }
    
    company = company_info.get(ticker, {'title': f'{ticker} Corp', 'cik': '0000000000'})
    
    print(f"公司名称: {company['title']}")
    print(f"CIK: {company['cik']}")
    print(f"股票代码: {ticker}")
    
    # 收集报告数据
    report_data = {
        'company_name': company['title'],
        'ticker': ticker,
        'cik': company['cik']
    }
    
    print(f"\\n💰 处理财务数据...")
    
    # 整理财务数据
    financial_data = {}
    
    # 按年度和概念整理数据
    for _, row in mock_data.iterrows():
        year = row['end_date'].year
        concept = row['concept']
        
        if year not in financial_data:
            financial_data[year] = {}
        
        financial_data[year][concept] = {
            'value': row['value'],
            'end_date': row['end_date'],
            'form': row.get('form', 'N/A')
        }
    
    report_data['financial_data'] = financial_data
    
    # 财务分析
    print(f"\\n📈 进行财务分析...")
    analyzer = FinancialAnalyzer()
    
    try:
        # 计算财务比率
        ratios = analyzer.calculate_financial_ratios(mock_data)
        if not ratios.empty:
            report_data['ratios'] = ratios.iloc[0].to_dict()
            
            print("\\n主要财务比率:")
            latest_ratios = ratios.iloc[0]
            if 'current_ratio' in latest_ratios:
                print(f"  流动比率: {latest_ratios['current_ratio']:.2f}")
            if 'debt_to_assets' in latest_ratios:
                print(f"  资产负债率: {latest_ratios['debt_to_assets']:.2%}")
            if 'roa' in latest_ratios:
                print(f"  总资产收益率: {latest_ratios['roa']:.2%}")
            if 'roe' in latest_ratios:
                print(f"  股东权益收益率: {latest_ratios['roe']:.2%}")
        
        # 趋势分析
        trends = analyzer.trend_analysis(mock_data, ['Revenues', 'NetIncomeLoss', 'Assets'])
        report_data['trends'] = trends
        
        if trends:
            print("\\n趋势分析:")
            trend_names = {'Revenues': '营收', 'NetIncomeLoss': '净利润', 'Assets': '总资产'}
            for concept, trend_info in trends.items():
                concept_name = trend_names.get(concept, concept)
                if 'overall_change_pct' in trend_info:
                    change_pct = trend_info['overall_change_pct']
                    direction = "📈" if change_pct > 0 else "📉"
                    print(f"  {concept_name}: {direction} {change_pct:+.1f}%")
        
        # 生成Markdown报告
        print(f"\\n📄 生成报告...")
        markdown_report = generate_markdown_report(report_data)
        
        # 保存报告文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            print(f"\\n✅ 报告已保存至: {output_file}")
        
        return markdown_report
        
    except Exception as e:
        print(f"生成报告时出错: {e}")
        return None


def main():
    """主函数"""
    print("🚀 SEC财务报告生成器演示版")
    print("📧 User-Agent: Ting Wang <tting.wang@gmail.com>")
    print("=" * 60)
    
    # 生成苹果公司报告
    ticker = "AAPL"
    output_file = f"{ticker.lower()}_financial_report_demo.md"
    
    report = generate_financial_report_demo(ticker, output_file)
    
    if report:
        print(f"\\n✅ {ticker} 财务报告演示生成完成!")
        print(f"\\n📄 报告预览:")
        print("=" * 60)
        # 显示报告前1000个字符
        preview_length = 1200
        print(report[:preview_length] + "..." if len(report) > preview_length else report)
        print("=" * 60)
        print(f"\\n📁 完整报告已保存至: {output_file}")
        print(f"📊 报告总长度: {len(report):,} 字符")
        
        # 显示文件大小
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📦 文件大小: {file_size:,} 字节")
    else:
        print(f"\\n❌ {ticker} 财务报告生成失败")
    
    print(f"\\n🎯 演示说明:")
    print("  - 本演示使用模拟数据展示报告生成功能")
    print("  - 真实API调用需要有效的网络连接和SEC服务器访问")
    print("  - 模拟数据基于Apple Inc.的真实财务数据调整")
    print("  - 报告格式类似于sample_apple_2024.md")


if __name__ == "__main__":
    main()