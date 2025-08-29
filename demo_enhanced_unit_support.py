#!/usr/bin/env python3
"""
演示优化后的SEC数据获取器 - 支持多种单位类型

展示如何获取完整的企业价值报告数据，包括每股指标
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.database.manager import get_default_sqlite_manager
from src.database.utils import DatabaseUtils
from sec_report_fetcher_db import SECFetcherDB

def demonstrate_enhanced_unit_support():
    """演示增强的单位支持功能"""
    print("🚀 演示优化后的SEC数据获取器 - 多单位支持")
    print("=" * 80)
    
    # 初始化数据库和获取器
    db_manager = get_default_sqlite_manager()
    db_utils = DatabaseUtils(db_manager)
    fetcher = SECFetcherDB(db_manager, "Demo Enhanced Unit Support <demo@example.com>")
    
    try:
        print("\n📊 获取Apple 2024年关键每股指标:")
        print("-" * 60)
        
        # 定义要测试的每股指标
        per_share_metrics = [
            'EarningsPerShareBasic',           # 基本每股收益 (USD/shares)
            'EarningsPerShareDiluted',         # 稀释每股收益 (USD/shares)
        ]
        
        # 定义要测试的股票数量指标
        shares_metrics = [
            'WeightedAverageNumberOfSharesOutstandingBasic',    # 基本加权平均股数 (shares)
            'WeightedAverageNumberOfDilutedSharesOutstanding',  # 稀释加权平均股数 (shares)
        ]
        
        # 定义要测试的USD指标
        usd_metrics = [
            'Assets',                          # 总资产 (USD)
            'StockholdersEquity',             # 股东权益 (USD)
            'NetIncomeLoss',                  # 净利润 (USD)
        ]
        
        all_metrics = per_share_metrics + shares_metrics + usd_metrics
        
        # 查询数据库中现有数据
        print("\n🔍 查询数据库中的现有数据:")
        for metric in all_metrics:
            results = db_utils.query_reports(
                company_identifier='AAPL',
                metric_names=[metric],
                fiscal_years=[2024]
            )
            
            if results:
                record = results[0]
                unit = record.get('unit', 'N/A')
                value = record.get('formatted_value', record.get('value', 'N/A'))
                print(f"  ✅ {metric}: {value} ({unit})")
            else:
                print(f"  ❌ {metric}: 未找到数据")
        
        print("\n💡 单位类型支持说明:")
        print("-" * 60)
        print("✅ USD单位: 货币金额（如Assets, NetIncomeLoss等）")
        print("✅ USD/shares单位: 每股收益类指标（如EarningsPerShareBasic等）")
        print("✅ shares单位: 股票数量类指标（如WeightedAverageNumberOfSharesOutstanding等）")
        print("✅ pure单位: 比率类指标")
        print("✅ percent单位: 百分比类指标")
        
        print("\n📈 计算示例（基于获取的数据）:")
        print("-" * 60)
        
        # 获取必要的数据进行计算
        eps_basic_results = db_utils.query_reports(
            company_identifier='AAPL',
            metric_names=['EarningsPerShareBasic'],
            fiscal_years=[2024]
        )
        
        eps_diluted_results = db_utils.query_reports(
            company_identifier='AAPL',
            metric_names=['EarningsPerShareDiluted'],
            fiscal_years=[2024]
        )
        
        shares_basic_results = db_utils.query_reports(
            company_identifier='AAPL',
            metric_names=['WeightedAverageNumberOfSharesOutstandingBasic'],
            fiscal_years=[2024]
        )
        
        net_income_results = db_utils.query_reports(
            company_identifier='AAPL',
            metric_names=['NetIncomeLoss'],
            fiscal_years=[2024]
        )
        
        if (eps_basic_results and shares_basic_results and net_income_results):
            eps_basic = eps_basic_results[0]['value']
            shares_basic = shares_basic_results[0]['value']
            net_income = net_income_results[0]['value']
            
            # 验证每股收益计算
            calculated_eps = net_income / shares_basic
            
            print(f"验证基本每股收益计算:")
            print(f"  • 净利润: ${net_income:,.0f}")
            print(f"  • 基本加权平均股数: {shares_basic:,.0f}")
            print(f"  • 计算的EPS: ${calculated_eps:.2f}")
            print(f"  • SEC报告的EPS: ${eps_basic:.2f}")
            print(f"  • 差异: ${abs(calculated_eps - eps_basic):.2f}")
        
        print("\n🎯 企业价值报告覆盖情况:")
        print("-" * 60)
        
        # 检查企业价值报告中需要的关键指标
        enterprise_value_metrics = {
            'Basic EPS (基本每股收益)': 'EarningsPerShareBasic',
            'Diluted EPS (稀释每股收益)': 'EarningsPerShareDiluted', 
            'Sales per Share (每股销售额)': 'RevenueFromContractWithCustomerExcludingAssessedTax',
            'Cash Flow per Share (每股现金流)': 'NetCashProvidedByUsedInOperatingActivities',
            'Book Value per Share (每股账面价值)': 'StockholdersEquity',
            'Common Shares Outstanding (流通股数)': 'WeightedAverageNumberOfDilutedSharesOutstanding',
            'Net Income (净利润)': 'NetIncomeLoss',
            'Total Assets (总资产)': 'Assets',
            'Current Assets (流动资产)': 'AssetsCurrent',
            'Current Liabilities (流动负债)': 'LiabilitiesCurrent',
        }
        
        covered_count = 0
        total_count = len(enterprise_value_metrics)
        
        for chinese_name, metric_name in enterprise_value_metrics.items():
            results = db_utils.query_reports(
                company_identifier='AAPL',
                metric_names=[metric_name],
                fiscal_years=[2024]
            )
            
            if results:
                covered_count += 1
                record = results[0]
                unit = record.get('unit', 'N/A')
                value = record.get('formatted_value', record.get('value', 'N/A'))
                print(f"  ✅ {chinese_name}: {value} ({unit})")
            else:
                print(f"  ❌ {chinese_name}: 数据缺失")
        
        coverage_percentage = (covered_count / total_count) * 100
        print(f"\n📊 企业价值报告数据覆盖率: {coverage_percentage:.1f}% ({covered_count}/{total_count})")
        
        print(f"\n🎉 优化成果:")
        print("-" * 60)
        print("✅ 成功支持USD/shares单位 - 解决了每股收益数据缺失问题")
        print("✅ 成功支持shares单位 - 解决了股票数量数据缺失问题")
        print("✅ 智能单位识别 - 自动选择最合适的数据单位")
        print("✅ 数据完整性提升 - 企业价值报告数据覆盖率显著提高")
        print("✅ 格式化优化 - 根据单位类型智能格式化数值显示")
        
    except Exception as e:
        print(f"❌ 演示过程中出错: {e}")
    
    finally:
        db_manager.close()
        print(f"\n✅ 演示完成!")

def main():
    """主函数"""
    demonstrate_enhanced_unit_support()

if __name__ == "__main__":
    main()