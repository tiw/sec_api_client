#!/usr/bin/env python3
"""
SEC报告查询功能演示脚本

展示如何使用SEC报告查询系统的各种功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.database.manager import get_default_sqlite_manager
from src.database.utils import DatabaseUtils

def main():
    """演示报告查询功能"""
    print("🚀 SEC报告查询功能演示")
    print("=" * 80)
    
    # 连接数据库
    db_manager = get_default_sqlite_manager()
    db_utils = DatabaseUtils(db_manager)
    
    try:
        # 1. 展示数据库统计信息
        print("\n📊 数据库统计信息:")
        print("-" * 40)
        stats = db_utils.get_database_statistics()
        print(f"公司数量: {stats.get('companies', 0):,}")
        print(f"报告类型: {stats.get('report_types', 0):,}")
        print(f"财务指标: {stats.get('metrics', 0):,}")
        print(f"财务数据记录: {stats.get('financial_data_records', 0):,}")
        
        # 2. 展示可用的报告类型
        print("\n📋 可用的报告类型:")
        print("-" * 40)
        report_types = db_utils.get_report_types()
        for rt in report_types[:5]:  # 显示前5个
            print(f"• {rt.type_code}: {rt.name}")
        if len(report_types) > 5:
            print(f"... 还有 {len(report_types) - 5} 个报告类型")
        
        # 3. 展示示例公司
        print("\n🏢 示例公司:")
        print("-" * 40)
        # 查找一些知名公司
        companies = []
        for ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']:
            company = db_utils.get_company_by_ticker(ticker)
            if company:
                companies.append(company)
        
        for company in companies[:5]:
            print(f"• {company.ticker}: {company.name} (CIK: {company.cik})")
        
        # 4. 展示10-K报告的部分
        print("\n📄 10-K报告部分:")
        print("-" * 40)
        sections = db_utils.get_report_sections('10-K')
        for section in sections[:5]:
            print(f"• {section.section_name} ({section.metrics_count} 个指标)")
        if len(sections) > 5:
            print(f"... 还有 {len(sections) - 5} 个部分")
        
        # 5. 展示Balance Sheet的部分指标
        print("\n📈 Balance Sheet 示例指标:")
        print("-" * 40)
        metrics = db_utils.get_section_metrics('10-K', 'Balance Sheet')
        important_metrics = [
            m for m in metrics 
            if any(keyword in m.metric_name.lower() 
                  for keyword in ['assets', 'liabilities', 'equity', 'cash'])
        ][:5]
        
        for metric in important_metrics:
            print(f"• {metric.metric_name}")
        
        print("\n🔍 查询功能说明:")
        print("=" * 80)
        
        print("\n1. 通用查询功能:")
        print("   python sec_report_query.py query --company AAPL --report-type 10-K")
        print("   python sec_report_query.py query --section 'Balance Sheet' --limit 10")
        print("   python sec_report_query.py query --year-range 2020-2024 --export results.csv")
        
        print("\n2. 公司概览功能:")
        print("   python sec_report_query.py company-overview --company AAPL")
        print("   python sec_report_query.py company-overview --company 0000320193")
        
        print("\n3. 指标对比功能:")
        print("   python sec_report_query.py compare --metric Assets --companies AAPL MSFT GOOGL")
        print("   python sec_report_query.py compare --metric 'Total Revenue' --companies AAPL MSFT --years 2022 2023 2024")
        
        print("\n4. 数据分析功能:")
        print("   python sec_report_query.py analytics")
        print("   python sec_report_query.py analytics --report-type 10-K")
        
        print("\n5. 数据库管理功能:")
        print("   python sec_db_manager.py stats")
        print("   python sec_db_manager.py query-reports --company AAPL --report-type 10-K")
        print("   python sec_db_manager.py compare-metric --metric Assets --companies AAPL MSFT")
        
        print("\n💡 查询特性:")
        print("=" * 80)
        print("• 支持多维度查询：公司、报告类型、年份、指标、数值范围")
        print("• 支持数据导出：CSV、Excel格式")
        print("• 支持灵活过滤：按最小值、最大值、年份范围等")
        print("• 支持公司间对比：多公司指标横向对比")
        print("• 支持统计分析：数据分布、趋势分析")
        print("• 支持缓存机制：避免重复查询，提高性能")
        
        print("\n📋 查询示例场景:")
        print("=" * 80)
        print("• 查询苹果公司2023年10-K报告的所有Balance Sheet指标")
        print("• 对比AAPL、MSFT、GOOGL三家公司的总资产变化趋势")
        print("• 查询2020-2024年所有公司的收入数据，按金额排序")
        print("• 分析10-K报告中哪些公司的数据最完整")
        print("• 导出特定指标的历史数据用于进一步分析")
        
    except Exception as e:
        print(f"❌ 演示过程中出错: {e}")
    
    finally:
        db_manager.close()
        print(f"\n✅ 演示完成！")

if __name__ == "__main__":
    main()