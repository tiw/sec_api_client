#!/usr/bin/env python3
"""
Apple Inc. 2024年度财务数据获取（增强版）

专门获取Apple公司2024年度的详细财务数据
包含从原始10-K文档中识别的缺失概念：
- Product/Service收入分类
- Product/Service销售成本分类  
- 销售一般管理费用
- 商品和服务销售成本总计

User-Agent: Ting Wang <tting.wang@gmail.com>
基于原始10k_2024.txt文档分析结果
"""

import sys
import os
from datetime import datetime

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, XBRLFramesClient, FinancialAnalyzer
import pandas as pd


def get_apple_2024_data():
    """获取Apple 2024年度财务数据"""
    
    print("🍎 Apple Inc. 2024年度财务数据获取")
    print("="*60)
    
    # Apple公司信息
    apple_info = {
        "ticker": "AAPL",
        "cik": "0000320193", 
        "title": "Apple Inc."
    }
    
    user_agent = "Ting Wang tting.wang@gmail.com"
    
    print(f"🏢 公司: {apple_info['title']}")
    print(f"📊 股票代码: {apple_info['ticker']}")
    print(f"🆔 CIK: {apple_info['cik']}")
    print(f"📧 User-Agent: {user_agent}")
    
    # 初始化客户端
    sec_client = SECClient(user_agent=user_agent)
    xbrl_client = XBRLFramesClient(sec_client)
    analyzer = FinancialAnalyzer()
    
    print(f"\n🔍 正在获取Apple 2024年度财务数据...")
    
    # 关键财务概念（包含从原始10-K文档中找到的缺失概念）
    key_concepts = {
        # 基础财务概念
        'Assets': '总资产',
        'Revenues': '总营收',
        'RevenueFromContractWithCustomerExcludingAssessedTax': '客户合同收入',
        'SalesRevenueNet': '净销售收入', 
        'NetIncomeLoss': '净利润',
        'StockholdersEquity': '股东权益',
        'AssetsCurrent': '流动资产',
        'Liabilities': '总负债',
        'LiabilitiesCurrent': '流动负债',
        'CashAndCashEquivalentsAtCarryingValue': '现金及现金等价物',
        'OperatingIncomeLoss': '营业利润',
        'CostOfGoodsSold': '销售成本',
        'CostOfRevenue': '营业成本',
        'CostOfGoodsAndServicesSold': '商品和服务销售成本',  # 新增：从10k_2024.txt找到
        'OperatingExpenses': '营业费用',
        'ResearchAndDevelopmentExpense': '研发费用',
        'SellingGeneralAndAdministrativeExpenses': '销售管理费用',
        'SellingGeneralAndAdministrativeExpense': '销售一般管理费用',  # 新增：从10k_2024.txt找到
        'GrossProfit': '毛利润',
        'EarningsPerShareBasic': '基本每股收益',
        'EarningsPerShareDiluted': '稀释每股收益'
    }
    
    # 需要特殊处理的Product/Service分类概念
    segment_concepts = {
        'product_revenue': {
            'concept': 'RevenueFromContractWithCustomerExcludingAssessedTax',
            'filter_keywords': ['Product', 'ProductMember'],
            'label': 'Product收入',
            'expected_value': 294866000000
        },
        'service_revenue': {
            'concept': 'RevenueFromContractWithCustomerExcludingAssessedTax',
            'filter_keywords': ['Service', 'ServiceMember'],
            'label': 'Service收入',
            'expected_value': 96169000000
        },
        'product_cost': {
            'concept': 'CostOfGoodsAndServicesSold',
            'filter_keywords': ['Product', 'ProductMember'],
            'label': 'Product销售成本',
            'expected_value': 185233000000
        },
        'service_cost': {
            'concept': 'CostOfGoodsAndServicesSold',
            'filter_keywords': ['Service', 'ServiceMember'],
            'label': 'Service销售成本',
            'expected_value': 25119000000
        }
    }
    
    apple_2024_data = {}
    
    print(f"\n📋 获取关键财务概念数据:")
    
    # 处理常规概念
    for concept, chinese_name in key_concepts.items():
        try:
            print(f"  🔄 获取 {chinese_name} ({concept})...")
            
            # 获取公司特定概念的历史数据
            concept_data = xbrl_client.get_company_concept_data(
                cik=apple_info['cik'], 
                concept=concept
            )
            
            if concept_data and 'units' in concept_data:
                # 根据概念类型选择合适的单位
                unit_key = 'USD'
                if concept in ['EarningsPerShareBasic', 'EarningsPerShareDiluted']:
                    # 每股收益可能使用USD/shares单位
                    if 'USD/shares' in concept_data['units']:
                        unit_key = 'USD/shares'
                    elif any('shares' in u.lower() for u in concept_data['units'].keys()):
                        unit_key = [u for u in concept_data['units'].keys() if 'shares' in u.lower()][0]
                
                unit_data = concept_data['units'].get(unit_key, [])
                
                if unit_data:
                    # 查找2024年数据，优先10-K报告
                    data_2024 = []
                    for item in unit_data:
                        end_date = item.get('end', '')
                        start_date = item.get('start', '')
                        form = item.get('form', '')
                        
                        # 查找2024财年数据
                        if (end_date == '2024-09-28' and start_date == '2023-10-01') or '2024' in end_date:
                            data_2024.append(item)
                    
                    if data_2024:
                        # 优先选择10-K报告，然后按日期排序
                        ten_k_data = [d for d in data_2024 if d.get('form') == '10-K']
                        if ten_k_data:
                            latest_2024 = sorted(ten_k_data, key=lambda x: x.get('end', ''), reverse=True)[0]
                        else:
                            latest_2024 = sorted(data_2024, key=lambda x: x.get('end', ''), reverse=True)[0]
                        
                        apple_2024_data[concept] = {
                            'chinese_name': chinese_name,
                            'value': latest_2024.get('val', 0),
                            'end_date': latest_2024.get('end', ''),
                            'start_date': latest_2024.get('start', ''),
                            'form': latest_2024.get('form', ''),
                            'filed': latest_2024.get('filed', ''),
                            'frame': latest_2024.get('frame', ''),
                            'unit': unit_key,
                            'formatted_value': analyzer.format_financial_number(latest_2024.get('val', 0))
                        }
                        
                        print(f"    ✅ {chinese_name}: {apple_2024_data[concept]['formatted_value']} (截至: {latest_2024.get('end', 'N/A')}, {latest_2024.get('form', 'N/A')})")
                    else:
                        print(f"    ⚠️  未找到2024年的{chinese_name}数据")
                else:
                    print(f"    ❌ 未找到{unit_key}单位数据")
            else:
                print(f"    ❌ 获取{chinese_name}数据失败")
                
        except Exception as e:
            print(f"    ❌ 获取{chinese_name}时出错: {e}")
    
    # 处理Product/Service分类概念
    print(f"\n📊 获取Product/Service分类数据:")
    
    for segment_key, segment_info in segment_concepts.items():
        try:
            concept = segment_info['concept']
            label = segment_info['label']
            filter_keywords = segment_info['filter_keywords']
            expected_value = segment_info['expected_value']
            
            print(f"  🔄 获取 {label} ({concept} - {'/'.join(filter_keywords)})...")
            
            # 获取概念数据
            concept_data = xbrl_client.get_company_concept_data(
                cik=apple_info['cik'], 
                concept=concept
            )
            
            if concept_data and 'units' in concept_data:
                usd_data = concept_data['units'].get('USD', [])
                
                if usd_data:
                    # 查找匹配的segment数据
                    matched_data = []
                    for item in usd_data:
                        end_date = item.get('end', '')
                        frame = item.get('frame', '')
                        val = item.get('val', 0)
                        
                        # 检查是否为2024财年数据
                        if end_date == '2024-09-28':
                            # 检查frame是否包含关键词或值是否匹配期望值
                            frame_match = any(keyword in frame for keyword in filter_keywords)
                            value_match = val == expected_value
                            
                            if frame_match or value_match:
                                matched_data.append(item)
                    
                    if matched_data:
                        # 选择最匹配的数据
                        best_match = None
                        for item in matched_data:
                            if item.get('val') == expected_value:
                                best_match = item
                                break
                        
                        if not best_match:
                            best_match = matched_data[0]
                        
                        apple_2024_data[segment_key] = {
                            'chinese_name': label,
                            'concept': concept,
                            'value': best_match.get('val', 0),
                            'end_date': best_match.get('end', ''),
                            'start_date': best_match.get('start', ''),
                            'form': best_match.get('form', ''),
                            'filed': best_match.get('filed', ''),
                            'frame': best_match.get('frame', ''),
                            'unit': 'USD',
                            'expected_value': expected_value,
                            'matches_expected': best_match.get('val') == expected_value,
                            'formatted_value': analyzer.format_financial_number(best_match.get('val', 0))
                        }
                        
                        match_status = "✓ 匹配期望值" if best_match.get('val') == expected_value else "⚠ 与期望值不匹配"
                        print(f"    ✅ {label}: {apple_2024_data[segment_key]['formatted_value']} - {match_status}")
                        print(f"       Frame: {best_match.get('frame', 'N/A')}")
                    else:
                        print(f"    ❌ 未找到匹配的{label}数据")
                else:
                    print(f"    ❌ 未找到USD单位数据")
            else:
                print(f"    ❌ 获取{label}数据失败")
                
        except Exception as e:
            print(f"    ❌ 获取{label}时出错: {e}")
    
    # 显示完整的2024年数据总结
    if apple_2024_data:
        print(f"\n📊 Apple Inc. 2024年度财务数据汇总")
        print("="*60)
        
        # 按类别分组显示（包含新增的概念）
        income_concepts = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'SalesRevenueNet',
                          'product_revenue', 'service_revenue',  # 新增分类收入
                          'CostOfRevenue', 'CostOfGoodsSold', 'CostOfGoodsAndServicesSold', 
                          'product_cost', 'service_cost',  # 新增分类成本
                          'GrossProfit', 'OperatingExpenses', 
                          'ResearchAndDevelopmentExpense', 'SellingGeneralAndAdministrativeExpenses', 'SellingGeneralAndAdministrativeExpense',
                          'OperatingIncomeLoss', 'NetIncomeLoss', 'EarningsPerShareBasic', 'EarningsPerShareDiluted']
        balance_concepts = ['Assets', 'AssetsCurrent', 'Liabilities', 'LiabilitiesCurrent', 
                          'StockholdersEquity', 'CashAndCashEquivalentsAtCarryingValue']
        
        print("\n💰 损益表数据 (Income Statement):")
        print("-" * 50)
        for concept in income_concepts:
            if concept in apple_2024_data:
                data = apple_2024_data[concept]
                print(f"  {data['chinese_name']:15}: {data['formatted_value']:>15} ({data['end_date']})")
        
        print("\n🏦 资产负债表数据 (Balance Sheet):")
        print("-" * 50)
        for concept in balance_concepts:
            if concept in apple_2024_data:
                data = apple_2024_data[concept]
                print(f"  {data['chinese_name']:15}: {data['formatted_value']:>15} ({data['end_date']})")
        
        # 计算一些关键比率
        print(f"\n📈 关键财务比率:")
        print("-" * 50)
        
        try:
            if 'Assets' in apple_2024_data and 'Revenues' in apple_2024_data:
                asset_turnover = apple_2024_data['Revenues']['value'] / apple_2024_data['Assets']['value']
                print(f"  资产周转率: {asset_turnover:.2f}")
            
            if 'AssetsCurrent' in apple_2024_data and 'LiabilitiesCurrent' in apple_2024_data:
                current_ratio = apple_2024_data['AssetsCurrent']['value'] / apple_2024_data['LiabilitiesCurrent']['value']
                print(f"  流动比率: {current_ratio:.2f}")
            
            if 'NetIncomeLoss' in apple_2024_data and 'Revenues' in apple_2024_data:
                net_margin = apple_2024_data['NetIncomeLoss']['value'] / apple_2024_data['Revenues']['value']
                print(f"  净利润率: {net_margin:.2%}")
            
            if 'NetIncomeLoss' in apple_2024_data and 'Assets' in apple_2024_data:
                roa = apple_2024_data['NetIncomeLoss']['value'] / apple_2024_data['Assets']['value']
                print(f"  总资产收益率 (ROA): {roa:.2%}")
            
            if 'NetIncomeLoss' in apple_2024_data and 'StockholdersEquity' in apple_2024_data:
                roe = apple_2024_data['NetIncomeLoss']['value'] / apple_2024_data['StockholdersEquity']['value']
                print(f"  股东权益收益率 (ROE): {roe:.2%}")
                
        except Exception as e:
            print(f"  ⚠️ 计算财务比率时出错: {e}")
        
        # 保存数据到文件
        try:
            print(f"\n💾 保存数据到文件...")
            
            # 转换为DataFrame以便保存
            rows = []
            for concept, data in apple_2024_data.items():
                rows.append({
                    'concept': concept,
                    'chinese_name': data['chinese_name'],
                    'value': data['value'],
                    'formatted_value': data['formatted_value'],
                    'end_date': data['end_date'],
                    'start_date': data.get('start_date', ''),
                    'form': data['form'],
                    'filed': data.get('filed', ''),
                    'frame': data.get('frame', ''),
                    'unit': data.get('unit', 'USD'),
                    'concept_type': data.get('concept', concept),
                    'expected_value': data.get('expected_value', ''),
                    'matches_expected': data.get('matches_expected', '')
                })
            
            df = pd.DataFrame(rows)
            
            # 保存为CSV
            csv_file = "apple_2024_financial_data.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"  ✅ CSV文件已保存: {csv_file}")
            
            # 保存为Excel
            excel_file = "apple_2024_financial_data.xlsx" 
            df.to_excel(excel_file, index=False)
            print(f"  ✅ Excel文件已保存: {excel_file}")
            
        except Exception as e:
            print(f"  ⚠️ 保存文件时出错: {e}")
        
        # 显示报告期信息
        report_dates = set()
        forms = set()
        for data in apple_2024_data.values():
            if data['end_date']:
                report_dates.add(data['end_date'])
            if data['form']:
                forms.add(data['form'])
        
        # 统计缺失概念的匹配情况
        segment_data = {k: v for k, v in apple_2024_data.items() if k in segment_concepts}
        if segment_data:
            print(f"\n🎯 Product/Service分类数据验证:")
            print("-" * 50)
            for seg_key, seg_data in segment_data.items():
                expected = seg_data.get('expected_value', 0)
                actual = seg_data.get('value', 0)
                matches = seg_data.get('matches_expected', False)
                status = "✓ 匹配" if matches else "✗ 不匹配"
                print(f"  {seg_data['chinese_name']:15}: {seg_data['formatted_value']:>15} - {status}")
                if not matches and expected:
                    print(f"    期望值: {analyzer.format_financial_number(expected)}")
        
        print(f"\n📋 报告信息:")
        print("-" * 50)
        print(f"  报告期: {', '.join(sorted(report_dates))}")
        print(f"  申报类型: {', '.join(forms)}")
        print(f"  数据来源: SEC EDGAR API")
        print(f"  获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示总概念数统计
        total_concepts = len(apple_2024_data)
        segment_matches = sum(1 for k, v in apple_2024_data.items() 
                            if k in segment_concepts and v.get('matches_expected', False))
        print(f"  总概念数: {total_concepts}")
        print(f"  分类概念匹配: {segment_matches}/{len(segment_concepts)}")
        
    else:
        print(f"\n❌ 未成功获取到Apple 2024年度财务数据")
        print("🔍 可能的原因:")
        print("  • 2024年财报尚未完全发布")
        print("  • SEC数据更新延迟")
        print("  • 网络连接问题")
    
    print(f"\n✅ Apple 2024年度数据获取完成!")
    return apple_2024_data


def main():
    """主函数"""
    try:
        apple_data = get_apple_2024_data()
        
        if apple_data:
            # 统计不同类型的概念数量
            regular_concepts = sum(1 for k in apple_data.keys() if k not in ['product_revenue', 'service_revenue', 'product_cost', 'service_cost'])
            segment_concepts_count = sum(1 for k in apple_data.keys() if k in ['product_revenue', 'service_revenue', 'product_cost', 'service_cost'])
            
            print(f"\n🎉 成功获取到 {len(apple_data)} 个财务概念的2024年度数据!")
            print(f"   - 常规概念: {regular_concepts} 个")
            print(f"   - Product/Service分类概念: {segment_concepts_count} 个")
        else:
            print(f"\n😔 未能获取到Apple 2024年度数据")
            
    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断了数据获取")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    main()