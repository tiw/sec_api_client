#!/usr/bin/env python3
"""
Apple Inc. 2024年10-K年度报告数据获取

专门获取Apple公司2024年10-K年度报告的完整财务数据
User-Agent: Ting Wang <tting.wang@gmail.com>
"""

import sys
import os
from datetime import datetime

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, XBRLFramesClient, FinancialAnalyzer
import pandas as pd


def get_apple_10k_2024_data():
    """获取Apple 2024年10-K年度报告数据"""
    
    print("🍎 Apple Inc. 2024年10-K年度报告数据获取")
    print("="*70)
    
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
    print(f"📋 报告类型: 10-K 年度报告")
    print(f"📧 User-Agent: {user_agent}")
    
    # 初始化客户端
    sec_client = SECClient(user_agent=user_agent)
    xbrl_client = XBRLFramesClient(sec_client)
    analyzer = FinancialAnalyzer()
    
    print(f"\n🔍 正在获取Apple 2024年10-K年度报告数据...")
    
    # 完整的财务概念列表 - 按10-K报告结构组织
    financial_concepts = {
        # 损益表概念
        'income_statement': {
            'Revenues': '总营收',
            'RevenueFromContractWithCustomerExcludingAssessedTax': '客户合同收入',
            'SalesRevenueNet': '净销售收入',
            'CostOfRevenue': '营业成本',
            'CostOfGoodsAndServicesSold': '成本收入',
            'CostOfGoodsSold': '商品销售成本',
            'GrossProfit': '毛利润',
            'OperatingExpenses': '营业费用',
            'ResearchAndDevelopmentExpense': '研发费用',
            'SellingGeneralAndAdministrativeExpenses': '销售及管理费用',
            'SellingAndMarketingExpense': '销售及营销费用',
            'GeneralAndAdministrativeExpense': '管理费用',
            'OperatingIncomeLoss': '营业利润',
            'NonoperatingIncomeExpense': '非营业收益',
            'InterestExpense': '利息费用',
            'InterestIncomeExpenseNet': '净利息收入',
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest': '税前利润',
            'IncomeTaxExpenseBenefit': '所得税费用',
            'NetIncomeLoss': '净利润',
            'NetIncomeAvailableToCommonStockholdersBasic': '归属普通股股东净利润',
            'EarningsPerShareBasic': '基本每股收益',
            'EarningsPerShareDiluted': '稀释每股收益',
            'WeightedAverageNumberOfSharesOutstandingBasic': '基本加权平均股数',
            'WeightedAverageNumberOfDilutedSharesOutstanding': '稀释加权平均股数'
        },
        
        # 资产负债表概念
        'balance_sheet': {
            'Assets': '总资产',
            'AssetsCurrent': '流动资产',
            'CashAndCashEquivalentsAtCarryingValue': '现金及现金等价物',
            'Cash': '现金资产',
            'MarketableSecuritiesCurrent': '流动有价证券',
            'AccountsReceivableNetCurrent': '应收账款净额',
            'InventoryNet': '存货净额',
            'PrepaidExpenseAndOtherAssetsCurrent': '预付费用及其他流动资产',
            'AssetsNoncurrent': '非流动资产',
            'MarketableSecuritiesNoncurrent': '非流动有价证券',
            'PropertyPlantAndEquipmentNet': '固定资产净额',
            'Goodwill': '商誉',
            'IntangibleAssetsNetExcludingGoodwill': '无形资产净额',
            'OtherAssetsNoncurrent': '其他非流动资产',
            'Liabilities': '总负债',
            'LiabilitiesCurrent': '流动负债',
            'AccountsPayableCurrent': '应付账款',
            'AccruedLiabilitiesCurrent': '应计负债',
            'CommercialPaper': '商业票据',
            'CurrentDebtAndCapitalLeaseObligation': '流动债务及融资租赁',
            'LongTermDebtCurrent': '一年内到期的长期债务',
            'LiabilitiesNoncurrent': '非流动负债',
            'LongTermDebtNoncurrent': '长期债务',
            'OtherLiabilitiesNoncurrent': '其他非流动负债',
            'StockholdersEquity': '股东权益',
            'CommonStockValue': '普通股股本',
            'RetainedEarningsAccumulatedDeficit': '留存收益',
            'AccumulatedOtherComprehensiveIncomeLossNetOfTax': '其他综合收益累计额'
        },
        
        # 现金流量表概念
        'cash_flow': {
            'NetCashProvidedByUsedInOperatingActivities': '经营活动现金流',
            'NetCashProvidedByUsedInInvestingActivities': '投资活动现金流',
            'NetCashProvidedByUsedInFinancingActivities': '融资活动现金流',
            'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect': '现金及现金等价物净增加',
            'DepreciationDepletionAndAmortization': '折旧摊销',
            'ShareBasedCompensation': '股权激励费用',
            'PaymentsToAcquirePropertyPlantAndEquipment': '购建固定资产支出',
            'PaymentsToAcquireMarketableSecurities': '购买有价证券支出',
            'ProceedsFromMaturitiesPrepaymentsAndCallsOfMarketableSecurities': '有价证券到期回收',
            'PaymentsOfDividends': '支付股息',
            'PaymentsForRepurchaseOfCommonStock': '回购股票支出'
        }
    }
    
    apple_10k_data = {}
    
    print(f"\n📋 获取10-K年度报告财务概念数据:")
    
    # 按类别获取数据
    for category, concepts in financial_concepts.items():
        print(f"\n📊 {category.upper()} 部分:")
        print("-" * 50)
        
        for concept, chinese_name in concepts.items():
            try:
                print(f"  🔄 获取 {chinese_name} ({concept})...")
                
                # 获取公司特定概念的历史数据
                concept_data = xbrl_client.get_company_concept_data(
                    cik=apple_info['cik'], 
                    concept=concept
                )
                
                if concept_data and 'units' in concept_data:
                    # 对于每股收益等，查找shares单位
                    unit_key = 'USD'
                    if concept in ['EarningsPerShareBasic', 'EarningsPerShareDiluted']:
                        unit_key = 'USD/shares'
                    elif concept in ['WeightedAverageNumberOfSharesOutstandingBasic', 'WeightedAverageNumberOfDilutedSharesOutstanding']:
                        unit_key = 'shares'
                    
                    unit_data = concept_data['units'].get(unit_key, [])
                    
                    if not unit_data and concept in ['EarningsPerShareBasic', 'EarningsPerShareDiluted']:
                        # 尝试其他可能的单位
                        for possible_unit in concept_data['units'].keys():
                            if 'shares' in possible_unit.lower() or 'per' in possible_unit.lower():
                                unit_data = concept_data['units'][possible_unit]
                                unit_key = possible_unit
                                break
                    
                    if unit_data:
                        # 查找2024年10-K数据 (通常在2024年9月或10月结束的财年)
                        data_2024_10k = []
                        for item in unit_data:
                            end_date = item.get('end', '')
                            form = item.get('form', '')
                            fiscal_year = item.get('fy', 0)
                            
                            # 查找2024财年的10-K报告数据
                            if (('2024' in end_date or fiscal_year == 2024) and 
                                form == '10-K'):
                                data_2024_10k.append(item)
                        
                        if data_2024_10k:
                            # 按日期排序，取最新的
                            latest_10k = sorted(data_2024_10k, key=lambda x: x.get('end', ''), reverse=True)[0]
                            
                            apple_10k_data[concept] = {
                                'category': category,
                                'chinese_name': chinese_name,
                                'value': latest_10k.get('val', 0),
                                'end_date': latest_10k.get('end', ''),
                                'start_date': latest_10k.get('start', ''),
                                'form': latest_10k.get('form', ''),
                                'filed': latest_10k.get('filed', ''),
                                'frame': latest_10k.get('frame', ''),
                                'fiscal_year': latest_10k.get('fy', ''),
                                'fiscal_period': latest_10k.get('fp', ''),
                                'unit': unit_key,
                                'formatted_value': analyzer.format_financial_number(latest_10k.get('val', 0))
                            }
                            
                            print(f"    ✅ {chinese_name}: {apple_10k_data[concept]['formatted_value']} (FY{latest_10k.get('fy', 'N/A')})")
                        else:
                            # 如果没有找到10-K数据，查找2024年的其他表单数据
                            data_2024_any = []
                            for item in unit_data:
                                end_date = item.get('end', '')
                                fiscal_year = item.get('fy', 0)
                                if '2024' in end_date or fiscal_year == 2024:
                                    data_2024_any.append(item)
                            
                            if data_2024_any:
                                latest_any = sorted(data_2024_any, key=lambda x: x.get('end', ''), reverse=True)[0]
                                apple_10k_data[concept] = {
                                    'category': category,
                                    'chinese_name': chinese_name,
                                    'value': latest_any.get('val', 0),
                                    'end_date': latest_any.get('end', ''),
                                    'start_date': latest_any.get('start', ''),
                                    'form': latest_any.get('form', ''),
                                    'filed': latest_any.get('filed', ''),
                                    'frame': latest_any.get('frame', ''),
                                    'fiscal_year': latest_any.get('fy', ''),
                                    'fiscal_period': latest_any.get('fp', ''),
                                    'unit': unit_key,
                                    'formatted_value': analyzer.format_financial_number(latest_any.get('val', 0))
                                }
                                print(f"    ⚠️  {chinese_name}: {apple_10k_data[concept]['formatted_value']} ({latest_any.get('form', 'N/A')} - FY{latest_any.get('fy', 'N/A')})")
                            else:
                                print(f"    ❌ 未找到2024年的{chinese_name}数据")
                    else:
                        print(f"    ❌ 未找到{unit_key}单位数据")
                else:
                    print(f"    ❌ 获取{chinese_name}数据失败")
                    
            except Exception as e:
                print(f"    ❌ 获取{chinese_name}时出错: {e}")
    
    # 显示完整的10-K数据总结
    if apple_10k_data:
        print(f"\n📊 Apple Inc. 2024年10-K年度报告数据汇总")
        print("="*70)
        
        # 按类别分组显示
        categories = {
            'income_statement': '💰 损益表 (Income Statement)',
            'balance_sheet': '🏦 资产负债表 (Balance Sheet)', 
            'cash_flow': '💸 现金流量表 (Cash Flow Statement)'
        }
        
        for category, title in categories.items():
            category_data = {k: v for k, v in apple_10k_data.items() if v.get('category') == category}
            
            if category_data:
                print(f"\n{title}:")
                print("-" * 60)
                for concept, data in category_data.items():
                    fiscal_info = f"FY{data.get('fiscal_year', 'N/A')}"
                    form_info = data.get('form', 'N/A')
                    print(f"  {data['chinese_name']:25}: {data['formatted_value']:>15} ({form_info} - {fiscal_info})")
        
        # 计算关键财务比率
        print(f"\n📈 关键财务比率分析 (基于10-K数据):")
        print("-" * 60)
        
        try:
            # 营业收入 - 尝试不同的收入概念
            revenue_concepts = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'SalesRevenueNet']
            revenue_value = None
            revenue_name = None
            
            for concept in revenue_concepts:
                if concept in apple_10k_data:
                    revenue_value = apple_10k_data[concept]['value']
                    revenue_name = apple_10k_data[concept]['chinese_name']
                    break
            
            if revenue_value and 'Assets' in apple_10k_data:
                asset_turnover = revenue_value / apple_10k_data['Assets']['value']
                print(f"  资产周转率: {asset_turnover:.2f} (基于{revenue_name})")
            
            if 'AssetsCurrent' in apple_10k_data and 'LiabilitiesCurrent' in apple_10k_data:
                current_ratio = apple_10k_data['AssetsCurrent']['value'] / apple_10k_data['LiabilitiesCurrent']['value']
                print(f"  流动比率: {current_ratio:.2f}")
            
            if 'Liabilities' in apple_10k_data and 'Assets' in apple_10k_data:
                debt_ratio = apple_10k_data['Liabilities']['value'] / apple_10k_data['Assets']['value']
                print(f"  资产负债率: {debt_ratio:.2%}")
            
            if revenue_value and 'NetIncomeLoss' in apple_10k_data:
                net_margin = apple_10k_data['NetIncomeLoss']['value'] / revenue_value
                print(f"  净利润率: {net_margin:.2%}")
            
            if 'NetIncomeLoss' in apple_10k_data and 'Assets' in apple_10k_data:
                roa = apple_10k_data['NetIncomeLoss']['value'] / apple_10k_data['Assets']['value']
                print(f"  总资产收益率 (ROA): {roa:.2%}")
            
            if 'NetIncomeLoss' in apple_10k_data and 'StockholdersEquity' in apple_10k_data:
                roe = apple_10k_data['NetIncomeLoss']['value'] / apple_10k_data['StockholdersEquity']['value']
                print(f"  股东权益收益率 (ROE): {roe:.2%}")
                
        except Exception as e:
            print(f"  ⚠️ 计算财务比率时出错: {e}")
        
        # 保存10-K数据到文件
        try:
            print(f"\n💾 保存10-K数据到文件...")
            
            # 转换为DataFrame以便保存
            rows = []
            for concept, data in apple_10k_data.items():
                rows.append({
                    'concept': concept,
                    'category': data['category'],
                    'chinese_name': data['chinese_name'],
                    'value': data['value'],
                    'formatted_value': data['formatted_value'],
                    'end_date': data['end_date'],
                    'start_date': data.get('start_date', ''),
                    'form': data['form'],
                    'filed': data.get('filed', ''),
                    'frame': data.get('frame', ''),
                    'fiscal_year': data.get('fiscal_year', ''),
                    'fiscal_period': data.get('fiscal_period', ''),
                    'unit': data.get('unit', 'USD')
                })
            
            df = pd.DataFrame(rows)
            
            # 保存为CSV
            csv_file = "apple_2024_10k_financial_data.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"  ✅ CSV文件已保存: {csv_file}")
            
            # 按类别保存单独文件
            for category in ['income_statement', 'balance_sheet', 'cash_flow']:
                category_df = df[df['category'] == category]
                if not category_df.empty:
                    category_file = f"apple_2024_10k_{category}.csv"
                    category_df.to_csv(category_file, index=False, encoding='utf-8')
                    print(f"  ✅ {category.upper()}文件已保存: {category_file}")
            
        except Exception as e:
            print(f"  ⚠️ 保存文件时出错: {e}")
        
        # 显示报告期信息
        fiscal_years = set()
        forms = set()
        report_dates = set()
        
        for data in apple_10k_data.values():
            if data.get('fiscal_year'):
                fiscal_years.add(str(data['fiscal_year']))
            if data['form']:
                forms.add(data['form'])
            if data['end_date']:
                report_dates.add(data['end_date'])
        
        print(f"\n📋 10-K报告信息:")
        print("-" * 60)
        print(f"  财政年度: {', '.join(sorted(fiscal_years))}")
        print(f"  报告期: {', '.join(sorted(report_dates))}")
        print(f"  申报类型: {', '.join(forms)}")
        print(f"  数据来源: SEC EDGAR API")
        print(f"  获取概念数: {len(apple_10k_data)}")
        print(f"  获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    else:
        print(f"\n❌ 未成功获取到Apple 2024年10-K报告数据")
        print("🔍 可能的原因:")
        print("  • 2024年10-K报告尚未发布")
        print("  • SEC数据更新延迟")
        print("  • 网络连接问题")
        print("  • 概念名称变更")
    
    print(f"\n✅ Apple 2024年10-K数据获取完成!")
    return apple_10k_data


def main():
    """主函数"""
    try:
        apple_10k_data = get_apple_10k_2024_data()
        
        if apple_10k_data:
            print(f"\n🎉 成功获取到 {len(apple_10k_data)} 个财务概念的2024年10-K数据!")
            
            # 统计每个类别的数据量
            categories = {}
            for data in apple_10k_data.values():
                category = data.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
            
            print(f"\n📊 数据分布:")
            for category, count in categories.items():
                print(f"  {category}: {count} 个概念")
            
        else:
            print(f"\n😔 未能获取到Apple 2024年10-K数据")
            
    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断了数据获取")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    main()