#!/usr/bin/env python3
"""
Apple Inc. 缺失财务概念数据获取

尝试获取与sample_apple_2024.md对比中缺失的财务概念
User-Agent: Ting Wang <tting.wang@gmail.com>
"""

import sys
import os
from datetime import datetime

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, XBRLFramesClient, FinancialAnalyzer
import pandas as pd


def try_alternative_concepts():
    """尝试获取缺失的财务概念数据"""
    
    print("🔍 Apple Inc. 缺失财务概念数据获取")
    print("="*60)
    
    apple_info = {
        "ticker": "AAPL",
        "cik": "0000320193", 
        "title": "Apple Inc."
    }
    
    user_agent = "Ting Wang tting.wang@gmail.com"
    
    # 初始化客户端
    sec_client = SECClient(user_agent=user_agent)
    xbrl_client = XBRLFramesClient(sec_client)
    analyzer = FinancialAnalyzer()
    
    # 缺失概念的可能替代名称
    missing_concepts = {
        # 收入相关
        'product_revenue': [
            'ProductRevenues',
            'ProductSales', 
            'RevenueFromProductSales',
            'SalesRevenue',
            'ProductRevenue'
        ],
        
        'service_revenue': [
            'ServiceRevenues',
            'ServicesRevenues',
            'RevenueFromServices',
            'ServiceRevenue'
        ],
        
        # 成本相关
        'total_cost_of_sales': [
            'CostOfRevenue',
            'CostOfSales',
            'CostOfGoodsAndServicesSold',
            'TotalCostOfRevenue'
        ],
        
        'product_cost': [
            'CostOfProductRevenues', 
            'CostOfProductSales',
            'ProductCosts',
            'CostOfProducts'
        ],
        
        'service_cost': [
            'CostOfServiceRevenues',
            'CostOfServices',
            'ServiceCosts'
        ],
        
        # 费用相关  
        'selling_admin': [
            'SellingGeneralAndAdministrativeExpenses',
            'SellingAndAdministrativeExpenses',
            'GeneralAndAdministrativeExpense',
            'SellingExpenses',
            'AdministrativeExpenses'
        ]
    }
    
    found_concepts = {}
    
    print(f"\n🔄 尝试获取缺失的财务概念...")
    
    for category, concept_list in missing_concepts.items():
        print(f"\n📋 {category.upper().replace('_', ' ')} 类别:")
        print("-" * 40)
        
        for concept in concept_list:
            try:
                print(f"  🔍 尝试概念: {concept}...")
                
                concept_data = xbrl_client.get_company_concept_data(
                    cik=apple_info['cik'], 
                    concept=concept
                )
                
                if concept_data and 'units' in concept_data:
                    usd_data = concept_data['units'].get('USD', [])
                    
                    if usd_data:
                        # 查找2024年数据
                        data_2024 = []
                        for item in usd_data:
                            fiscal_year = item.get('fy', 0)
                            end_date = item.get('end', '')
                            form = item.get('form', '')
                            
                            if fiscal_year == 2024 and form == '10-K':
                                data_2024.append(item)
                        
                        if data_2024:
                            latest = sorted(data_2024, key=lambda x: x.get('end', ''), reverse=True)[0]
                            
                            found_concepts[concept] = {
                                'category': category,
                                'value': latest.get('val', 0),
                                'formatted_value': analyzer.format_financial_number(latest.get('val', 0)),
                                'end_date': latest.get('end', ''),
                                'form': latest.get('form', ''),
                                'fiscal_year': latest.get('fy', '')
                            }
                            
                            print(f"    ✅ 找到数据: {found_concepts[concept]['formatted_value']} (FY{latest.get('fy', 'N/A')})")
                            break
                        else:
                            print(f"    ⚠️  概念存在但无2024年10-K数据")
                    else:
                        print(f"    ⚠️  概念存在但无USD单位数据")
                else:
                    print(f"    ❌ 概念不存在或无数据")
                    
            except Exception as e:
                if "404" in str(e):
                    print(f"    ❌ 概念不存在 (404)")
                else:
                    print(f"    ❌ 获取失败: {str(e)[:50]}...")
    
    # 显示找到的概念汇总
    if found_concepts:
        print(f"\n📊 找到的概念数据汇总")
        print("="*60)
        
        categories = {}
        for concept, data in found_concepts.items():
            category = data['category']
            if category not in categories:
                categories[category] = []
            categories[category].append((concept, data))
        
        for category, concepts in categories.items():
            print(f"\n💰 {category.upper().replace('_', ' ')}:")
            print("-" * 40)
            for concept, data in concepts:
                print(f"  {concept:35}: {data['formatted_value']:>12}")
        
        # 验证数据一致性
        print(f"\n🔍 数据验证:")
        print("-" * 40)
        
        # 验证收入分解
        product_rev = None
        service_rev = None
        
        for concept, data in found_concepts.items():
            if data['category'] == 'product_revenue':
                product_rev = data['value']
            elif data['category'] == 'service_revenue':
                service_rev = data['value']
        
        if product_rev and service_rev:
            total_calc = product_rev + service_rev
            print(f"  产品收入 + 服务收入 = {analyzer.format_financial_number(total_calc)}")
            print(f"  已知总收入 (客户合同收入) = $391.04B")
            
            if abs(total_calc - 391035000000) < 1000000:  # 1M容差
                print(f"  ✅ 收入分解验证通过")
            else:
                print(f"  ⚠️  收入分解不匹配")
        
        # 保存找到的概念数据
        try:
            rows = []
            for concept, data in found_concepts.items():
                rows.append({
                    'concept': concept,
                    'category': data['category'], 
                    'value': data['value'],
                    'formatted_value': data['formatted_value'],
                    'end_date': data['end_date'],
                    'form': data['form'],
                    'fiscal_year': data['fiscal_year']
                })
            
            if rows:
                df = pd.DataFrame(rows)
                csv_file = "apple_2024_missing_concepts.csv"
                df.to_csv(csv_file, index=False, encoding='utf-8')
                print(f"\n💾 找到的概念已保存至: {csv_file}")
        
        except Exception as e:
            print(f"\n⚠️ 保存文件时出错: {e}")
    
    else:
        print(f"\n❌ 未找到任何缺失的概念数据")
        print("🔍 可能的原因:")
        print("  • Apple使用非标准XBRL概念名称")
        print("  • 数据被聚合在其他概念中")
        print("  • 需要从Apple的扩展分类标准中查找")
    
    # 尝试计算缺失数据
    print(f"\n🧮 通过计算推导缺失数据:")
    print("-" * 60)
    
    known_data = {
        'total_revenue': 391035000000,
        'gross_profit': 180683000000, 
        'operating_expenses': 57467000000,
        'rd_expense': 31370000000
    }
    
    # 计算总销售成本
    calculated_cost_of_sales = known_data['total_revenue'] - known_data['gross_profit']
    print(f"  总销售成本 = 总收入 - 毛利润")
    print(f"  {analyzer.format_financial_number(calculated_cost_of_sales)} = {analyzer.format_financial_number(known_data['total_revenue'])} - {analyzer.format_financial_number(known_data['gross_profit'])}")
    print(f"  Sample文件中的总销售成本: $210.35B")
    
    if abs(calculated_cost_of_sales - 210352000000) < 1000000:
        print(f"  ✅ 计算验证通过")
    else:
        print(f"  ⚠️  计算不匹配")
    
    # 计算销售管理费用
    calculated_sg_a = known_data['operating_expenses'] - known_data['rd_expense']
    print(f"\n  销售管理费用 = 总营业费用 - 研发费用")
    print(f"  {analyzer.format_financial_number(calculated_sg_a)} = {analyzer.format_financial_number(known_data['operating_expenses'])} - {analyzer.format_financial_number(known_data['rd_expense'])}")
    print(f"  Sample文件中的销售管理费用: $26.10B")
    
    if abs(calculated_sg_a - 26097000000) < 1000000:
        print(f"  ✅ 计算验证通过")
    else:
        print(f"  ⚠️  计算不匹配")
    
    print(f"\n✅ 缺失概念数据获取完成!")
    return found_concepts


def main():
    """主函数"""
    try:
        found_data = try_alternative_concepts()
        
        if found_data:
            print(f"\n🎉 成功找到 {len(found_data)} 个缺失的财务概念!")
        else:
            print(f"\n💡 虽然未找到直接的概念数据，但可以通过计算获得缺失信息")
            
    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断了数据获取")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    main()