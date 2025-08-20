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
        
        # 添加更详细的财务指标计算
        print(f"\n📊 详细财务指标分析:")
        print("=" * 70)
        
        # 创建一个列表来存储计算的指标
        calculated_metrics = []
        
        # 1. Profitability Ratios (盈利能力指标)
        print(f"\n1. Profitability Ratios (盈利能力指标)")
        print("-" * 50)
        
        # (1) Gross Margin (毛利率)
        if 'GrossProfit' in apple_10k_data and 'RevenueFromContractWithCustomerExcludingAssessedTax' in apple_10k_data:
            gross_margin = apple_10k_data['GrossProfit']['value'] / apple_10k_data['RevenueFromContractWithCustomerExcludingAssessedTax']['value']
            print(f"(1) Gross Margin (毛利率)")
            print(f"• Formula: GrossProfit / RevenueFromContractWithCustomerExcludingAssessedTax")
            print(f"• Calculation: {apple_10k_data['GrossProfit']['value']} / {apple_10k_data['RevenueFromContractWithCustomerExcludingAssessedTax']['value']} = {gross_margin:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Gross Margin (毛利率)',
                'formula': 'GrossProfit / RevenueFromContractWithCustomerExcludingAssessedTax',
                'value': gross_margin,
                'formatted_value': f"{gross_margin:.1%}",
                'components': 'GrossProfit, RevenueFromContractWithCustomerExcludingAssessedTax'
            })
        
        # (2) Operating Margin (营业利润率)
        if 'OperatingIncomeLoss' in apple_10k_data and 'RevenueFromContractWithCustomerExcludingAssessedTax' in apple_10k_data:
            operating_margin = apple_10k_data['OperatingIncomeLoss']['value'] / apple_10k_data['RevenueFromContractWithCustomerExcludingAssessedTax']['value']
            print(f"(2) Operating Margin (营业利润率)")
            print(f"• Formula: OperatingIncomeLoss / RevenueFromContractWithCustomerExcludingAssessedTax")
            print(f"• Calculation: {apple_10k_data['OperatingIncomeLoss']['value']} / {apple_10k_data['RevenueFromContractWithCustomerExcludingAssessedTax']['value']} = {operating_margin:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Operating Margin (营业利润率)',
                'formula': 'OperatingIncomeLoss / RevenueFromContractWithCustomerExcludingAssessedTax',
                'value': operating_margin,
                'formatted_value': f"{operating_margin:.1%}",
                'components': 'OperatingIncomeLoss, RevenueFromContractWithCustomerExcludingAssessedTax'
            })
        
        # (3) Net Profit Margin (净利润率)
        if 'NetIncomeLoss' in apple_10k_data and 'RevenueFromContractWithCustomerExcludingAssessedTax' in apple_10k_data:
            net_profit_margin = apple_10k_data['NetIncomeLoss']['value'] / apple_10k_data['RevenueFromContractWithCustomerExcludingAssessedTax']['value']
            print(f"(3) Net Profit Margin (净利润率)")
            print(f"• Formula: NetIncomeLoss / RevenueFromContractWithCustomerExcludingAssessedTax")
            print(f"• Calculation: {apple_10k_data['NetIncomeLoss']['value']} / {apple_10k_data['RevenueFromContractWithCustomerExcludingAssessedTax']['value']} = {net_profit_margin:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Net Profit Margin (净利润率)',
                'formula': 'NetIncomeLoss / RevenueFromContractWithCustomerExcludingAssessedTax',
                'value': net_profit_margin,
                'formatted_value': f"{net_profit_margin:.1%}",
                'components': 'NetIncomeLoss, RevenueFromContractWithCustomerExcludingAssessedTax'
            })
        
        # (4) Effective Tax Rate (实际税率)
        if 'IncomeTaxExpenseBenefit' in apple_10k_data and 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest' in apple_10k_data:
            effective_tax_rate = apple_10k_data['IncomeTaxExpenseBenefit']['value'] / apple_10k_data['IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest']['value']
            print(f"(4) Effective Tax Rate (实际税率)")
            print(f"• Formula: IncomeTaxExpenseBenefit / IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest")
            print(f"• Calculation: {apple_10k_data['IncomeTaxExpenseBenefit']['value']} / {apple_10k_data['IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest']['value']} = {effective_tax_rate:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Effective Tax Rate (实际税率)',
                'formula': 'IncomeTaxExpenseBenefit / IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
                'value': effective_tax_rate,
                'formatted_value': f"{effective_tax_rate:.1%}",
                'components': 'IncomeTaxExpenseBenefit, IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'
            })
        
        # (5) Earnings Per Share (每股收益)
        if 'EarningsPerShareBasic' in apple_10k_data:
            print(f"(5) Earnings Per Share (每股收益)")
            print(f"• Basic EPS (基本每股收益): {apple_10k_data['EarningsPerShareBasic']['formatted_value']}")
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Basic EPS (基本每股收益)',
                'formula': 'EarningsPerShareBasic',
                'value': apple_10k_data['EarningsPerShareBasic']['value'],
                'formatted_value': apple_10k_data['EarningsPerShareBasic']['formatted_value'],
                'components': 'EarningsPerShareBasic'
            })
        if 'EarningsPerShareDiluted' in apple_10k_data:
            print(f"• Diluted EPS (稀释每股收益): {apple_10k_data['EarningsPerShareDiluted']['formatted_value']}")
            print()
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Diluted EPS (稀释每股收益)',
                'formula': 'EarningsPerShareDiluted',
                'value': apple_10k_data['EarningsPerShareDiluted']['value'],
                'formatted_value': apple_10k_data['EarningsPerShareDiluted']['formatted_value'],
                'components': 'EarningsPerShareDiluted'
            })
        
        # 2. Liquidity Ratios (流动性指标)
        print(f"2. Liquidity Ratios (流动性指标)")
        print("-" * 50)
        
        # (1) Current Ratio (流动比率)
        if 'AssetsCurrent' in apple_10k_data and 'LiabilitiesCurrent' in apple_10k_data:
            current_ratio = apple_10k_data['AssetsCurrent']['value'] / apple_10k_data['LiabilitiesCurrent']['value']
            print(f"(1) Current Ratio (流动比率)")
            print(f"• Formula: AssetsCurrent / LiabilitiesCurrent")
            print(f"• Calculation: {apple_10k_data['AssetsCurrent']['value']} / {apple_10k_data['LiabilitiesCurrent']['value']} = {current_ratio:.2f}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Current Ratio (流动比率)',
                'formula': 'AssetsCurrent / LiabilitiesCurrent',
                'value': current_ratio,
                'formatted_value': f"{current_ratio:.2f}",
                'components': 'AssetsCurrent, LiabilitiesCurrent'
            })
        
        # (2) Quick Ratio (速动比率)
        if ('CashAndCashEquivalentsAtCarryingValue' in apple_10k_data and 
            'MarketableSecuritiesCurrent' in apple_10k_data and 
            'AccountsReceivableNetCurrent' in apple_10k_data and 
            'LiabilitiesCurrent' in apple_10k_data):
            quick_assets = (apple_10k_data['CashAndCashEquivalentsAtCarryingValue']['value'] + 
                           apple_10k_data['MarketableSecuritiesCurrent']['value'] + 
                           apple_10k_data['AccountsReceivableNetCurrent']['value'])
            liabilities_current = apple_10k_data['LiabilitiesCurrent']['value']
            quick_ratio = quick_assets / liabilities_current
            print(f"(2) Quick Ratio (速动比率)")
            print(f"• Formula: (CashAndCashEquivalentsAtCarryingValue + MarketableSecuritiesCurrent + AccountsReceivableNetCurrent) / LiabilitiesCurrent")
            print(f"• Calculation: ({apple_10k_data['CashAndCashEquivalentsAtCarryingValue']['value']} + {apple_10k_data['MarketableSecuritiesCurrent']['value']} + {apple_10k_data['AccountsReceivableNetCurrent']['value']}) / {apple_10k_data['LiabilitiesCurrent']['value']} = {quick_ratio:.2f}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Quick Ratio (速动比率)',
                'formula': '(CashAndCashEquivalentsAtCarryingValue + MarketableSecuritiesCurrent + AccountsReceivableNetCurrent) / LiabilitiesCurrent',
                'value': quick_ratio,
                'formatted_value': f"{quick_ratio:.2f}",
                'components': 'CashAndCashEquivalentsAtCarryingValue, MarketableSecuritiesCurrent, AccountsReceivableNetCurrent, LiabilitiesCurrent'
            })
        
        # 3. Leverage Ratios (杠杆比率)
        print(f"3. Leverage Ratios (杠杆比率)")
        print("-" * 50)
        
        # (1) Debt-to-Asset Ratio (资产负债率)
        if 'Liabilities' in apple_10k_data and 'Assets' in apple_10k_data:
            debt_to_asset_ratio = apple_10k_data['Liabilities']['value'] / apple_10k_data['Assets']['value']
            print(f"(1) Debt-to-Asset Ratio (资产负债率)")
            print(f"• Formula: Liabilities / Assets")
            print(f"• Calculation: {apple_10k_data['Liabilities']['value']} / {apple_10k_data['Assets']['value']} = {debt_to_asset_ratio:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Debt-to-Asset Ratio (资产负债率)',
                'formula': 'Liabilities / Assets',
                'value': debt_to_asset_ratio,
                'formatted_value': f"{debt_to_asset_ratio:.1%}",
                'components': 'Liabilities, Assets'
            })
        
        # (2) Equity Ratio (股东权益比率)
        if 'StockholdersEquity' in apple_10k_data and 'Assets' in apple_10k_data:
            equity_ratio = apple_10k_data['StockholdersEquity']['value'] / apple_10k_data['Assets']['value']
            print(f"(2) Equity Ratio (股东权益比率)")
            print(f"• Formula: StockholdersEquity / Assets")
            print(f"• Calculation: {apple_10k_data['StockholdersEquity']['value']} / {apple_10k_data['Assets']['value']} = {equity_ratio:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Equity Ratio (股东权益比率)',
                'formula': 'StockholdersEquity / Assets',
                'value': equity_ratio,
                'formatted_value': f"{equity_ratio:.1%}",
                'components': 'StockholdersEquity, Assets'
            })
        
        # 4. Cash Flow Metrics (现金流指标)
        print(f"4. Cash Flow Metrics (现金流指标)")
        print("-" * 50)
        
        # (1) Free Cash Flow (自由现金流)
        if 'NetCashProvidedByUsedInOperatingActivities' in apple_10k_data and 'PaymentsToAcquirePropertyPlantAndEquipment' in apple_10k_data:
            free_cash_flow = apple_10k_data['NetCashProvidedByUsedInOperatingActivities']['value'] - apple_10k_data['PaymentsToAcquirePropertyPlantAndEquipment']['value']
            print(f"(1) Free Cash Flow (自由现金流)")
            print(f"• Formula: NetCashProvidedByUsedInOperatingActivities - PaymentsToAcquirePropertyPlantAndEquipment")
            print(f"• Calculation: {apple_10k_data['NetCashProvidedByUsedInOperatingActivities']['value']} - {apple_10k_data['PaymentsToAcquirePropertyPlantAndEquipment']['value']} = {analyzer.format_financial_number(free_cash_flow)} USD")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Free Cash Flow (自由现金流)',
                'formula': 'NetCashProvidedByUsedInOperatingActivities - PaymentsToAcquirePropertyPlantAndEquipment',
                'value': free_cash_flow,
                'formatted_value': analyzer.format_financial_number(free_cash_flow),
                'components': 'NetCashProvidedByUsedInOperatingActivities, PaymentsToAcquirePropertyPlantAndEquipment'
            })
        
        # (2) Dividend Payout Ratio (股息支付率)
        if 'PaymentsOfDividends' in apple_10k_data and 'NetIncomeLoss' in apple_10k_data:
            dividend_payout_ratio = apple_10k_data['PaymentsOfDividends']['value'] / apple_10k_data['NetIncomeLoss']['value']
            print(f"(2) Dividend Payout Ratio (股息支付率)")
            print(f"• Formula: PaymentsOfDividends / NetIncomeLoss")
            print(f"• Calculation: {apple_10k_data['PaymentsOfDividends']['value']} / {apple_10k_data['NetIncomeLoss']['value']} = {dividend_payout_ratio:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Dividend Payout Ratio (股息支付率)',
                'formula': 'PaymentsOfDividends / NetIncomeLoss',
                'value': dividend_payout_ratio,
                'formatted_value': f"{dividend_payout_ratio:.1%}",
                'components': 'PaymentsOfDividends, NetIncomeLoss'
            })
        
        # (3) Share Buyback Ratio (股票回购比例)
        if 'PaymentsForRepurchaseOfCommonStock' in apple_10k_data and 'NetIncomeLoss' in apple_10k_data:
            share_buyback_ratio = apple_10k_data['PaymentsForRepurchaseOfCommonStock']['value'] / apple_10k_data['NetIncomeLoss']['value']
            print(f"(3) Share Buyback Ratio (股票回购比例)")
            print(f"• Formula: PaymentsForRepurchaseOfCommonStock / NetIncomeLoss")
            print(f"• Calculation: {apple_10k_data['PaymentsForRepurchaseOfCommonStock']['value']} / {apple_10k_data['NetIncomeLoss']['value']} = {share_buyback_ratio:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Share Buyback Ratio (股票回购比例)',
                'formula': 'PaymentsForRepurchaseOfCommonStock / NetIncomeLoss',
                'value': share_buyback_ratio,
                'formatted_value': f"{share_buyback_ratio:.1%}",
                'components': 'PaymentsForRepurchaseOfCommonStock, NetIncomeLoss'
            })
        
        # 5. Return Metrics (回报率指标)
        print(f"5. Return Metrics (回报率指标)")
        print("-" * 50)
        
        # (1) Return on Equity (ROE, 净资产收益率)
        if 'NetIncomeLoss' in apple_10k_data and 'StockholdersEquity' in apple_10k_data:
            roe = apple_10k_data['NetIncomeLoss']['value'] / apple_10k_data['StockholdersEquity']['value']
            print(f"(1) Return on Equity (ROE, 净资产收益率)")
            print(f"• Formula: NetIncomeLoss / StockholdersEquity")
            print(f"• Calculation: {apple_10k_data['NetIncomeLoss']['value']} / {apple_10k_data['StockholdersEquity']['value']} = {roe:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Return on Equity (ROE, 净资产收益率)',
                'formula': 'NetIncomeLoss / StockholdersEquity',
                'value': roe,
                'formatted_value': f"{roe:.1%}",
                'components': 'NetIncomeLoss, StockholdersEquity'
            })
        
        # (2) Return on Total Capital (ROTC, 总资本回报率)
        if ('NetIncomeLoss' in apple_10k_data and 
            'LongTermDebtNoncurrent' in apple_10k_data and 
            'Liabilities' in apple_10k_data and 
            'StockholdersEquity' in apple_10k_data):
            estimated_interest_expense = apple_10k_data['LongTermDebtNoncurrent']['value'] * 0.04  # 假设利率4%
            rotc_numerator = apple_10k_data['NetIncomeLoss']['value'] + estimated_interest_expense
            rotc_denominator = apple_10k_data['Liabilities']['value'] + apple_10k_data['StockholdersEquity']['value']
            rotc = rotc_numerator / rotc_denominator
            print(f"(2) Return on Total Capital (ROTC, 总资本回报率)")
            print(f"• Formula: (NetIncomeLoss + EstimatedInterestExpense) / (Liabilities + StockholdersEquity)")
            print(f"  (假设利息费用为长期债务的4%: LongTermDebtNoncurrent × 4% = {apple_10k_data['LongTermDebtNoncurrent']['value']} × 0.04 ≈ {analyzer.format_financial_number(estimated_interest_expense)} USD)")
            print(f"• Calculation: ({apple_10k_data['NetIncomeLoss']['value']} + {analyzer.format_financial_number(estimated_interest_expense)}) / ({apple_10k_data['Liabilities']['value']} + {apple_10k_data['StockholdersEquity']['value']}) ≈ {rotc:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Return on Total Capital (ROTC, 总资本回报率)',
                'formula': '(NetIncomeLoss + EstimatedInterestExpense) / (Liabilities + StockholdersEquity)',
                'value': rotc,
                'formatted_value': f"{rotc:.1%}",
                'components': 'NetIncomeLoss, LongTermDebtNoncurrent, Liabilities, StockholdersEquity',
                'note': 'EstimatedInterestExpense = LongTermDebtNoncurrent × 4%'
            })
        
        # (3) Retained Earnings Ratio (留存收益比率)
        if 'RetainedEarningsAccumulatedDeficit' in apple_10k_data and 'StockholdersEquity' in apple_10k_data:
            retained_earnings_ratio = apple_10k_data['RetainedEarningsAccumulatedDeficit']['value'] / apple_10k_data['StockholdersEquity']['value']
            print(f"(3) Retained Earnings Ratio (留存收益比率)")
            print(f"• Formula: RetainedEarningsAccumulatedDeficit / StockholdersEquity")
            print(f"• Calculation: {apple_10k_data['RetainedEarningsAccumulatedDeficit']['value']} / {apple_10k_data['StockholdersEquity']['value']} = {retained_earnings_ratio:.1%}")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Retained Earnings Ratio (留存收益比率)',
                'formula': 'RetainedEarningsAccumulatedDeficit / StockholdersEquity',
                'value': retained_earnings_ratio,
                'formatted_value': f"{retained_earnings_ratio:.1%}",
                'components': 'RetainedEarningsAccumulatedDeficit, StockholdersEquity'
            })
        
        # 6. Per-Share Metrics (每股指标)
        print(f"6. Per-Share Metrics (每股指标)")
        print("-" * 50)
        
        # (1) Sales per Share (每股销售额)
        if 'RevenueFromContractWithCustomerExcludingAssessedTax' in apple_10k_data and 'WeightedAverageNumberOfDilutedSharesOutstanding' in apple_10k_data:
            sales_per_share = apple_10k_data['RevenueFromContractWithCustomerExcludingAssessedTax']['value'] / apple_10k_data['WeightedAverageNumberOfDilutedSharesOutstanding']['value']
            print(f"(1) Sales per Share (每股销售额)")
            print(f"• Formula: RevenueFromContractWithCustomerExcludingAssessedTax / WeightedAverageNumberOfDilutedSharesOutstanding")
            print(f"• Calculation: {apple_10k_data['RevenueFromContractWithCustomerExcludingAssessedTax']['value']} / {apple_10k_data['WeightedAverageNumberOfDilutedSharesOutstanding']['value']} = {sales_per_share:.2f} USD")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Sales per Share (每股销售额)',
                'formula': 'RevenueFromContractWithCustomerExcludingAssessedTax / WeightedAverageNumberOfDilutedSharesOutstanding',
                'value': sales_per_share,
                'formatted_value': f"{sales_per_share:.2f}",
                'components': 'RevenueFromContractWithCustomerExcludingAssessedTax, WeightedAverageNumberOfDilutedSharesOutstanding'
            })
        
        # (2) Cash Flow per Share (每股现金流)
        if 'NetCashProvidedByUsedInOperatingActivities' in apple_10k_data and 'WeightedAverageNumberOfDilutedSharesOutstanding' in apple_10k_data:
            cash_flow_per_share = apple_10k_data['NetCashProvidedByUsedInOperatingActivities']['value'] / apple_10k_data['WeightedAverageNumberOfDilutedSharesOutstanding']['value']
            print(f"(2) Cash Flow per Share (每股现金流)")
            print(f"• Formula: NetCashProvidedByUsedInOperatingActivities / WeightedAverageNumberOfDilutedSharesOutstanding")
            print(f"• Calculation: {apple_10k_data['NetCashProvidedByUsedInOperatingActivities']['value']} / {apple_10k_data['WeightedAverageNumberOfDilutedSharesOutstanding']['value']} = {cash_flow_per_share:.2f} USD")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Cash Flow per Share (每股现金流)',
                'formula': 'NetCashProvidedByUsedInOperatingActivities / WeightedAverageNumberOfDilutedSharesOutstanding',
                'value': cash_flow_per_share,
                'formatted_value': f"{cash_flow_per_share:.2f}",
                'components': 'NetCashProvidedByUsedInOperatingActivities, WeightedAverageNumberOfDilutedSharesOutstanding'
            })
        
        # (3) Book Value per Share (每股账面价值)
        if 'StockholdersEquity' in apple_10k_data and 'WeightedAverageNumberOfDilutedSharesOutstanding' in apple_10k_data:
            book_value_per_share = apple_10k_data['StockholdersEquity']['value'] / apple_10k_data['WeightedAverageNumberOfDilutedSharesOutstanding']['value']
            print(f"(3) Book Value per Share (每股账面价值)")
            print(f"• Formula: StockholdersEquity / WeightedAverageNumberOfDilutedSharesOutstanding")
            print(f"• Calculation: {apple_10k_data['StockholdersEquity']['value']} / {apple_10k_data['WeightedAverageNumberOfDilutedSharesOutstanding']['value']} = {book_value_per_share:.2f} USD")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Book Value per Share (每股账面价值)',
                'formula': 'StockholdersEquity / WeightedAverageNumberOfDilutedSharesOutstanding',
                'value': book_value_per_share,
                'formatted_value': f"{book_value_per_share:.2f}",
                'components': 'StockholdersEquity, WeightedAverageNumberOfDilutedSharesOutstanding'
            })
        
        # (4) Capital Spending per Share (每股资本支出)
        if 'PaymentsToAcquirePropertyPlantAndEquipment' in apple_10k_data and 'WeightedAverageNumberOfDilutedSharesOutstanding' in apple_10k_data:
            capital_spending_per_share = apple_10k_data['PaymentsToAcquirePropertyPlantAndEquipment']['value'] / apple_10k_data['WeightedAverageNumberOfDilutedSharesOutstanding']['value']
            print(f"(4) Capital Spending per Share (每股资本支出)")
            print(f"• Formula: PaymentsToAcquirePropertyPlantAndEquipment / WeightedAverageNumberOfDilutedSharesOutstanding")
            print(f"• Calculation: {apple_10k_data['PaymentsToAcquirePropertyPlantAndEquipment']['value']} / {apple_10k_data['WeightedAverageNumberOfDilutedSharesOutstanding']['value']} = {capital_spending_per_share:.2f} USD")
            print()
            
            # 添加到计算指标列表
            calculated_metrics.append({
                'metric_name': 'Capital Spending per Share (每股资本支出)',
                'formula': 'PaymentsToAcquirePropertyPlantAndEquipment / WeightedAverageNumberOfDilutedSharesOutstanding',
                'value': capital_spending_per_share,
                'formatted_value': f"{capital_spending_per_share:.2f}",
                'components': 'PaymentsToAcquirePropertyPlantAndEquipment, WeightedAverageNumberOfDilutedSharesOutstanding'
            })
        
        # Key Notes (注意事项)
        print(f"Key Notes (注意事项)")
        print("-" * 50)
        print(f"1. Missing Data:")
        print(f"   • Price-Earnings Ratio (P/E) 和 Dividend Yield 需股价数据支持（表中未提供）。")
        print()
        print(f"2. Negative Retained Earnings:")
        if 'RetainedEarningsAccumulatedDeficit' in apple_10k_data:
            print(f"   留存收益为负（RetainedEarningsAccumulatedDeficit = {apple_10k_data['RetainedEarningsAccumulatedDeficit']['formatted_value']} USD），可能因历史亏损或大额分红/回购。")
        print(f"3. Interest Expense Assumption:")
        print(f"   ROTC 中的利息费用为估算值（假设长期债务利率4%），实际值需参考财报附注。")
        print()
        print(f"如需进一步分析（如杜邦分解、行业对比），可补充股价或历史数据。")
        print()
        
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
            
            # 保存计算的财务指标到CSV文件
            if calculated_metrics:
                metrics_df = pd.DataFrame(calculated_metrics)
                metrics_csv_file = "apple_2024_10k_calculated_metrics.csv"
                metrics_df.to_csv(metrics_csv_file, index=False, encoding='utf-8')
                print(f"  ✅ 计算财务指标文件已保存: {metrics_csv_file}")
            
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