#!/usr/bin/env python3
"""
SEC API客户端基本使用示例

演示如何使用SEC API客户端获取公司财务数据
"""

import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, DocumentRetriever, XBRLFramesClient, FinancialAnalyzer


def generate_financial_report(ticker="AAPL", output_file=None):
    """生成财务报告"""
    
    # 初始化客户端
    user_agent = "Ting Wang tting.wang@gmail.com"
    
    print(f"🔍 正在从 SEC API 获取 {ticker} 的真实数据...")
    sec_client = SECClient(user_agent=user_agent)
    
    # 使用已知的公司信息（避免 ticker 文件问题）
    known_companies = {
        "AAPL": {"cik": "0000320193", "title": "Apple Inc."},
        "MSFT": {"cik": "0000789019", "title": "Microsoft Corporation"},
        "GOOGL": {"cik": "0001652044", "title": "Alphabet Inc."},
        "AMZN": {"cik": "0001018724", "title": "Amazon.com Inc."},
        "TSLA": {"cik": "0001318605", "title": "Tesla Inc."}
    }
    
    if ticker not in known_companies:
        print(f"未知的股票代码: {ticker}，请使用: {list(known_companies.keys())}")
        return None
    
    company_info = {
        'cik': known_companies[ticker]['cik'],
        'ticker': ticker,
        'title': known_companies[ticker]['title']
    }
    
    print(f"\n🏢 公司信息:")
    print(f"公司名称: {company_info['title']}")
    print(f"CIK: {company_info['cik']}")
    print(f"股票代码: {company_info['ticker']}")
    
    # 获取真实的XBRL财务数据
    print(f"\n💰 从 SEC XBRL API 获取 {ticker} 的真实财务数据...")
    xbrl_client = XBRLFramesClient(sec_client)
    analyzer = FinancialAnalyzer()
    
    # 收集报告数据
    report_data = {
        'company_name': company_info['title'],
        'ticker': ticker,
        'cik': company_info['cik']
    }
    
    try:
        print(f"🔍 调用 SEC XBRL/Frames API 获取年度数据...")
        # 获取年度财务指标（最近3年）
        annual_metrics = xbrl_client.get_financial_metrics(ticker, period_type='annual', years=3)
        
        if annual_metrics.empty:
            print(f"⚠️  没有获取到 {ticker} 的年度数据，尝试获取单个概念数据...")
            
            # 尝试获取单个概念数据来验证API连接
            test_concepts = ['Assets', 'Revenues', 'NetIncomeLoss']
            test_periods = ['CY2023', 'CY2022', 'CY2021']
            
            all_data = []
            for concept in test_concepts:
                for period in test_periods:
                    print(f"  • 获取 {concept} - {period}...")
                    try:
                        concept_data = xbrl_client.get_concept_data(concept, period + 'I')  # 瞬时数据
                        if not concept_data.empty:
                            # 查找目标公司数据
                            company_data = concept_data[concept_data['cik'] == int(company_info['cik'])]
                            if not company_data.empty:
                                row = company_data.iloc[0]
                                all_data.append({
                                    'ticker': ticker,
                                    'cik': company_info['cik'],
                                    'concept': concept,
                                    'value': row['val'],
                                    'end_date': pd.to_datetime(row['end']),
                                    'period': period
                                })
                                print(f"    ✓ 找到数据: {analyzer.format_financial_number(row['val'])}")
                            else:
                                print(f"    ✗ 未找到 {ticker} 在此期间的数据")
                        else:
                            print(f"    ✗ {period} 无数据")
                    except Exception as e:
                        print(f"    ✗ 获取 {concept}-{period} 失败: {e}")
            
            if all_data:
                annual_metrics = pd.DataFrame(all_data)
                print(f"\n✅ 成功从 SEC API 获取到 {len(annual_metrics)} 条数据")
            else:
                print(f"\n❌ 未能从 SEC API 获取到任何 {ticker} 数据")
                return None
        else:
            print(f"\n✅ 成功从 SEC XBRL API 获取到 {len(annual_metrics)} 条年度数据")
        
        # 显示获取到的数据概要
        print(f"\n📊 获取到的财务数据概要:")
        concepts = annual_metrics['concept'].unique()
        periods = sorted(annual_metrics['end_date'].dt.year.unique(), reverse=True)
        
        print(f"  • 财务概念: {len(concepts)} 个 - {list(concepts)[:5]}{'...' if len(concepts) > 5 else ''}")
        print(f"  • 时间范围: {periods}")
        
        # 显示部分数据样本
        print(f"\n📊 数据样本 (前5条):")
        for _, row in annual_metrics.head(5).iterrows():
            formatted_value = analyzer.format_financial_number(row['value'])
            print(f"  {row['concept']}: {formatted_value} ({row['end_date'].strftime('%Y-%m-%d')})")
        
        # 获取最近的文档信息
        print(f"\n📋 获取最近的 SEC 文档信息...")
        try:
            doc_retriever = DocumentRetriever(sec_client)
            recent_filings = doc_retriever.get_10k_10q_filings(ticker, years=1)
            if not recent_filings.empty:
                latest_filing = recent_filings.iloc[0]
                report_data['latest_filing'] = {
                    'form': latest_filing['form'],
                    'filing_date': latest_filing['filingDate'],
                    'report_date': latest_filing['reportDate'],
                    'accession_number': latest_filing['accessionNumber']
                }
                print(f"  • 最新文档: {latest_filing['form']} - {latest_filing['filingDate'].strftime('%Y-%m-%d')}")
            else:
                print(f"  • 未获取到文档信息")
        except Exception as e:
            print(f"  • 获取文档信息失败: {e}")
        
    except Exception as e:
        print(f"\n❌ 获取SEC数据时出错: {e}")
        print(f"   请检查网络连接和 SEC API 状态")
        return None
    
    # 生成报告
    print(f"\n📈 生成基于SEC真实数据的财务报告...")
    
    try:
        # 计算财务比率
        ratios = analyzer.calculate_financial_ratios(annual_metrics)
        if not ratios.empty:
            report_data['ratios'] = ratios.iloc[0].to_dict()
        
        # 趋势分析
        trends = analyzer.trend_analysis(annual_metrics, ['Revenues', 'NetIncomeLoss', 'Assets'])
        report_data['trends'] = trends
        
        # 生成Markdown报告
        markdown_report = generate_markdown_report(report_data)
        
        # 保存报告文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            print(f"\n✅ 报告已保存至: {output_file}")
        
        print(f"\n✅ 成功生成基于SEC真实数据的报告")
        return markdown_report
        
    except Exception as e:
        print(f"\n❌ 生成报告时出错: {e}")
        return None


def generate_markdown_report(data):
    """生成Markdown格式的财务报告"""
    
    company_name = data['company_name']
    ticker = data['ticker']
    cik = data['cik']
    financial_data = data.get('financial_data', {})
    ratios = data.get('ratios', {})
    trends = data.get('trends', {})
    latest_filing = data.get('latest_filing', {})
    
    # 获取最近3年的年份
    years = sorted(financial_data.keys(), reverse=True)[:3]
    
    markdown = f"""# {company_name} 财务报告
**股票代码**: {ticker} | **CIK**: {cik}

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
        markdown += "\n## 📈 财务比率分析\n\n"
        
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
                    markdown += f"- **{ratio_name}**: {value:.2%}\n"
                else:
                    markdown += f"- **{ratio_name}**: {value:.2f}\n"
    
    # 趋势分析
    if trends:
        markdown += "\n## 📊 趋势分析\n\n"
        
        trend_names = {
            'Revenues': '营业收入',
            'NetIncomeLoss': '净利润', 
            'Assets': '总资产'
        }
        
        for concept, trend_info in trends.items():
            concept_name = trend_names.get(concept, concept)
            markdown += f"### {concept_name}\n\n"
            
            if 'data_points' in trend_info:
                markdown += f"- **数据点数**: {trend_info['data_points']}\n"
            
            if 'latest_value' in trend_info:
                latest_formatted = analyzer.format_financial_number(trend_info['latest_value'])
                markdown += f"- **最新值**: {latest_formatted}\n"
            
            if 'overall_change_pct' in trend_info:
                change = trend_info['overall_change_pct']
                direction = "📈" if change > 0 else "📉"
                markdown += f"- **总体变化**: {direction} {change:+.1f}%\n"
            
            if 'trend_direction' in trend_info:
                direction_map = {
                    'increasing': '📈 上升趋势',
                    'decreasing': '📉 下降趋势', 
                    'mixed': '📊 震荡趋势'
                }
                trend_desc = direction_map.get(trend_info['trend_direction'], '未知趋势')
                markdown += f"- **近期趋势**: {trend_desc}\n"
            
            markdown += "\n"
    
    # 报告信息
    if latest_filing:
        filing_date = latest_filing.get('filing_date')
        report_date = latest_filing.get('report_date')
        form_type = latest_filing.get('form')
        
        if filing_date:
            markdown += f"\n## 📋 报告信息\n\n"
            markdown += f"- **最新申报**: {form_type}\n"
            markdown += f"- **申报日期**: {filing_date.strftime('%Y-%m-%d')}\n"
            markdown += f"- **报告期**: {report_date.strftime('%Y-%m-%d')}\n"
    
    markdown += f"\n---\n*报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    markdown += "*数据来源: SEC EDGAR数据库*\n"
    
    return markdown


def main():
    """主函数"""
    print("🚀 SEC财务报告生成器 - 真实 API 测试")
    print("📧 User-Agent: Ting Wang <tting.wang@gmail.com>")
    print("=" * 60)
    
    
    # 生成苹果公司报告
    ticker = "AAPL"
    output_file = f"{ticker.lower()}_financial_report.md"
    
    report = generate_financial_report(ticker, output_file)
    
    if report:
        print(f"\n✅ {ticker} 财务报告生成完成！(基于 SEC 真实数据)")
        print(f"\n📄 报告预览:")
        print("=" * 50)
        # 显示报告前500个字符
        print(report[:800] + "..." if len(report) > 800 else report)
        print("=" * 50)
        print(f"\n📁 完整报告已保存至: {output_file}")
        print(f"\n🌐 数据来源: SEC EDGAR API (真实数据)")
        print(f"📧 API User-Agent: Ting Wang <tting.wang@gmail.com>")
    else:
        print(f"\n❌ {ticker} 财务报告生成失败 - 请检查SEC API连接")


if __name__ == "__main__":
    import pandas as pd
    main()