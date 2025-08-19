#!/usr/bin/env python3
"""
Apple 2024 10-K Missing Concepts - Updated Script
基于原始10-K文档中找到的XBRL概念名称来获取缺失的财务数据项
"""

import requests
import sys
import json
from pathlib import Path

# Add src directory to Python path
parent_dir = Path(__file__).parent.parent
src_dir = parent_dir / 'src'
sys.path.insert(0, str(src_dir))

from sec_client import SECClient

def get_missing_concepts_data():
    """获取基于原始10-K文档找到的缺失概念数据"""
    
    user_agent = "Ting Wang tting.wang@gmail.com"
    client = SECClient(user_agent=user_agent)
    
    # Apple基本信息
    cik = "0000320193"  # Apple Inc
    
    # 基于10k_2024.txt文档分析找到的缺失概念
    missing_concepts = {
        # Product和Service细分收入 - 使用相同概念但不同contextRef
        "product_revenue": {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "context_filter": "ProductMember",
            "expected_value": 294866000000,
            "label": "Product Revenue"
        },
        "service_revenue": {
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax", 
            "context_filter": "ServiceMember",
            "expected_value": 96169000000,
            "label": "Service Revenue"
        },
        
        # Product和Service细分销售成本
        "product_cost": {
            "concept": "us-gaap:CostOfGoodsAndServicesSold",
            "context_filter": "ProductMember", 
            "expected_value": 185233000000,
            "label": "Product Cost of Sales"
        },
        "service_cost": {
            "concept": "us-gaap:CostOfGoodsAndServicesSold",
            "context_filter": "ServiceMember",
            "expected_value": 25119000000, 
            "label": "Service Cost of Sales"
        },
        
        # 销售管理费用
        "selling_admin_expense": {
            "concept": "us-gaap:SellingGeneralAndAdministrativeExpense",
            "context_filter": None,
            "expected_value": 26097000000,
            "label": "Selling, General and Administrative Expenses"
        }
    }
    
    print("=== Apple 2024 10-K Missing Concepts Data ===\n")
    
    results = {}
    
    for concept_key, concept_info in missing_concepts.items():
        concept_name = concept_info["concept"]
        context_filter = concept_info["context_filter"]
        expected_value = concept_info["expected_value"]
        label = concept_info["label"]
        
        print(f"🔍 正在获取: {label}")
        print(f"   概念名称: {concept_name}")
        print(f"   上下文过滤: {context_filter}")
        print(f"   期望值: ${expected_value:,}")
        
        try:
            # 获取概念数据
            concept_data = client.get_company_concept(
                cik=cik,
                taxonomy="us-gaap", 
                concept=concept_name.split(":")[-1]
            )
            
            if concept_data and 'units' in concept_data:
                # 查找2024财年数据
                usd_data = concept_data['units'].get('USD', [])
                
                found_values = []
                for item in usd_data:
                    # 检查是否为2024财年数据
                    if (item.get('end') == '2024-09-28' and 
                        item.get('start') == '2023-10-01'):
                        
                        # 如果有上下文过滤器，检查frame
                        if context_filter:
                            frame = item.get('frame', '')
                            if context_filter not in frame:
                                continue
                        else:
                            # 对于没有上下文过滤的概念，确保没有segment
                            if 'frame' in item and item['frame']:
                                continue
                        
                        found_values.append({
                            'value': item.get('val'),
                            'frame': item.get('frame', 'N/A'),
                            'accession': item.get('accn', 'N/A')
                        })
                
                if found_values:
                    print(f"   ✅ 找到 {len(found_values)} 个匹配值:")
                    for val_info in found_values:
                        value = val_info['value']
                        frame = val_info['frame']
                        accession = val_info['accession']
                        
                        # 检查是否匹配期望值
                        match_status = "✓ 匹配" if value == expected_value else "✗ 不匹配"
                        print(f"      ${value:,} ({frame}) - {match_status}")
                        print(f"        来源: {accession}")
                        
                        results[concept_key] = {
                            'label': label,
                            'concept': concept_name,
                            'value': value,
                            'frame': frame,
                            'expected': expected_value,
                            'matches': value == expected_value
                        }
                else:
                    print(f"   ❌ 未找到2024财年数据")
                    results[concept_key] = {
                        'label': label,
                        'concept': concept_name,
                        'value': None,
                        'error': 'No 2024 data found'
                    }
            else:
                print(f"   ❌ 无法获取概念数据")
                results[concept_key] = {
                    'label': label,
                    'concept': concept_name,
                    'value': None,
                    'error': 'No concept data available'
                }
                
        except Exception as e:
            print(f"   ❌ 获取失败: {str(e)}")
            results[concept_key] = {
                'label': label,
                'concept': concept_name,
                'value': None,
                'error': str(e)
            }
        
        print()
    
    # 保存结果
    output_file = Path(__file__).parent / "apple_2024_missing_concepts_results.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📁 结果已保存到: {output_file}")
    
    # 统计匹配情况
    total_concepts = len(results)
    successful_matches = sum(1 for r in results.values() 
                           if r.get('value') is not None and r.get('matches', False))
    
    print(f"\n📊 统计结果:")
    print(f"   总概念数: {total_concepts}")
    print(f"   成功匹配: {successful_matches}")
    print(f"   匹配率: {successful_matches/total_concepts*100:.1f}%")
    
    return results

if __name__ == "__main__":
    results = get_missing_concepts_data()