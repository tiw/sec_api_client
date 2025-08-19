#!/usr/bin/env python3
"""
XBRL/Frames API使用示例

演示如何使用XBRL/Frames API获取结构化财务数据
基于文章中的示例代码改进
"""

import sys
import os
import pandas as pd

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, XBRLFramesClient


def demonstrate_frames_api():
    """演示XBRL/Frames API的使用"""
    
    # 初始化客户端
    user_agent = "XBRL示例 xbrl@example.com"
    sec_client = SECClient(user_agent=user_agent)
    xbrl_client = XBRLFramesClient(sec_client)
    
    print("🔍 XBRL/Frames API演示")
    print("=" * 50)
    
    # 1. 获取特定概念的行业数据 - 复现文章示例
    print("\n1️⃣  获取应付账款数据 (复现文章示例)")
    print("-" * 30)
    
    try:
        # 获取2023年Q1的应付账款数据
        accounts_payable_data = xbrl_client.get_concept_data(
            concept='AccountsPayableCurrent',
            period='CY2023Q1I',  # 瞬时数据
            unit='USD'
        )
        
        if not accounts_payable_data.empty:
            print(f"数据条数: {len(accounts_payable_data)}")
            print(f"标签: {accounts_payable_data['label'].iloc[0] if 'label' in accounts_payable_data.columns else 'N/A'}")
            print(f"描述: {accounts_payable_data['description'].iloc[0][:100] if 'description' in accounts_payable_data.columns else 'N/A'}...")
            
            # 显示前5个公司的数据
            if 'val' in accounts_payable_data.columns:
                top_companies = accounts_payable_data.nlargest(5, 'val')
                print("\n💰 应付账款最高的5家公司:")
                for idx, row in top_companies.iterrows():
                    entity_name = row.get('entityName', 'Unknown')
                    value = row.get('val', 0)
                    print(f"  {entity_name}: ${value:,.0f}")
        else:
            print("未获取到数据")
            
    except Exception as e:
        print(f"获取应付账款数据时出错: {e}")
    
    # 2. 季度对比分析
    print(f"\n2️⃣  2023年营收季度对比分析")
    print("-" * 30)
    
    try:
        quarterly_revenues = xbrl_client.get_quarterly_comparison('Revenues', 2023)
        
        if not quarterly_revenues.empty:
            print(f"总数据条数: {len(quarterly_revenues)}")
            
            # 按季度统计
            quarterly_stats = quarterly_revenues.groupby('quarter')['val'].agg(['count', 'mean', 'sum'])
            print("\n📊 各季度统计:")
            for quarter, stats in quarterly_stats.iterrows():
                print(f"  Q{quarter}: {stats['count']} 家公司, 平均营收: ${stats['mean']:,.0f}, 总营收: ${stats['sum']:,.0f}")
            
            # 显示每季度前3名
            print(f"\n🏆 各季度营收前3名:")
            for quarter in [1, 2, 3, 4]:
                quarter_data = quarterly_revenues[quarterly_revenues['quarter'] == quarter]
                if not quarter_data.empty:
                    top3 = quarter_data.nlargest(3, 'val')
                    print(f"\n  Q{quarter}:")
                    for idx, row in top3.iterrows():
                        entity_name = row.get('entityName', 'Unknown')
                        value = row.get('val', 0)
                        print(f"    {entity_name}: ${value:,.0f}")
        else:
            print("未获取到季度数据")
            
    except Exception as e:
        print(f"季度对比分析时出错: {e}")
    
    # 3. 构建不同类型的期间字符串
    print(f"\n3️⃣  期间字符串构建示例")
    print("-" * 30)
    
    # 演示不同的期间格式
    period_examples = [
        (2023, None, False, "年度数据"),
        (2023, 1, False, "Q1季度数据"),
        (2023, 1, True, "Q1瞬时数据"),
        (2022, 4, True, "2022年Q4瞬时数据")
    ]
    
    for year, quarter, instant, description in period_examples:
        period_str = xbrl_client.build_period_string(year, quarter, instant)
        print(f"  {description}: {period_str}")
    
    # 4. 获取公司历史数据
    print(f"\n4️⃣  苹果公司资产历史数据")
    print("-" * 30)
    
    try:
        # 搜索苹果公司
        company_info = sec_client.search_company_by_ticker('AAPL')
        if company_info:
            print(f"公司: {company_info['title']} (CIK: {company_info['cik']})")
            
            # 获取总资产历史数据
            assets_data = xbrl_client.get_company_concept_data(
                cik=company_info['cik'],
                concept='Assets'
            )
            
            if assets_data and 'units' in assets_data:
                usd_data = assets_data['units'].get('USD', [])
                
                if usd_data:
                    print(f"\n📈 总资产历史数据 (最近5期):")
                    # 按日期排序，显示最近5期
                    sorted_data = sorted(usd_data, key=lambda x: x.get('end', ''), reverse=True)
                    
                    for i, item in enumerate(sorted_data[:5]):
                        end_date = item.get('end', 'N/A')
                        value = item.get('val', 0)
                        form = item.get('form', 'N/A')
                        fy = item.get('fy', 'N/A')
                        fp = item.get('fp', 'N/A')
                        
                        print(f"  {end_date}: ${value:,.0f} ({form}, FY{fy}-{fp})")
                else:
                    print("未找到USD单位的资产数据")
            else:
                print("未获取到资产历史数据")
        else:
            print("未找到苹果公司信息")
            
    except Exception as e:
        print(f"获取公司历史数据时出错: {e}")
    
    # 5. 常用财务概念列表
    print(f"\n5️⃣  常用财务概念说明")
    print("-" * 30)
    
    print("💡 资产负债表概念:")
    balance_sheet_concepts = {
        'Assets': '总资产',
        'AssetsCurrent': '流动资产', 
        'CashAndCashEquivalentsAtCarryingValue': '现金及现金等价物',
        'AccountsReceivableNetCurrent': '应收账款净额',
        'Liabilities': '总负债',
        'LiabilitiesCurrent': '流动负债',
        'AccountsPayableCurrent': '应付账款',
        'StockholdersEquity': '股东权益'
    }
    
    for concept, description in balance_sheet_concepts.items():
        print(f"  {concept}: {description}")
    
    print(f"\n💡 损益表概念:")
    income_concepts = {
        'Revenues': '营业收入',
        'CostOfRevenue': '销售成本',
        'GrossProfit': '毛利润',
        'OperatingIncomeLoss': '营业利润',
        'NetIncomeLoss': '净利润',
        'EarningsPerShareBasic': '基本每股收益'
    }
    
    for concept, description in income_concepts.items():
        print(f"  {concept}: {description}")
    
    print(f"\n✅ XBRL/Frames API演示完成!")


if __name__ == "__main__":
    demonstrate_frames_api()