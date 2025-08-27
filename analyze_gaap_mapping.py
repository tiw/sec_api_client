#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析CSV文件中的财务指标与US-GAAP标准的对应关系
为Neo4j知识图谱准备数据映射
"""

import pandas as pd
import json
from pathlib import Path

def load_us_gaap_metrics():
    """加载US-GAAP指标列表"""
    gaap_file = Path("/Users/tingwang/work/sec_api_client/data/us_gaap_metrics.txt")
    
    if not gaap_file.exists():
        # 如果文件不存在，使用工作目录下的文件
        gaap_file = Path("/Users/tingwang/work/sec_api_client/us_gaap_metrics.txt")
    
    with open(gaap_file, 'r', encoding='utf-8') as f:
        gaap_metrics = [line.strip() for line in f.readlines() if line.strip()]
    
    return gaap_metrics

def create_gaap_mapping():
    """创建指标到US-GAAP的映射关系"""
    # 基于常见的财务指标命名规则创建映射
    mapping = {
        # 资产类指标
        'cash_and_cash_equivalents': 'us-gaap:CashAndCashEquivalentsAtCarryingValue',
        'marketable_securities': 'us-gaap:MarketableSecuritiesCurrent',
        'receivables': 'us-gaap:AccountsReceivableNetCurrent',
        'inventory_fifo': 'us-gaap:InventoryNet',
        'current_assets': 'us-gaap:AssetsCurrent',
        'other_current_assets': 'us-gaap:OtherAssetsCurrent',
        'assets': 'us-gaap:Assets',
        'property_plant_equipment': 'us-gaap:PropertyPlantAndEquipmentNet',
        'cash_assets': 'us-gaap:CashAndCashEquivalentsAtCarryingValue',
        
        # 负债类指标
        'accounts_payable': 'us-gaap:AccountsPayableCurrent',
        'current_liability': 'us-gaap:LiabilitiesCurrent',
        'other_current_liability': 'us-gaap:OtherLiabilitiesCurrent',
        'long_term_debt': 'us-gaap:LongTermDebtNoncurrent',
        'short_term_debt': 'us-gaap:LongTermDebtCurrent',
        'debt_due': 'us-gaap:LongTermDebtCurrent',
        'total_debt': 'us-gaap:LongTermDebt',
        'liabilities': 'us-gaap:Liabilities',
        
        # 权益类指标
        'shareholders_equity': 'us-gaap:StockholdersEquity',
        'retained_earnings': 'us-gaap:RetainedEarningsAccumulatedDeficit',
        'common_stock': 'us-gaap:CommonStockSharesOutstanding',
        'shares_outstanding': 'us-gaap:CommonStockSharesIssued',
        
        # 收入和费用类指标
        'revenue': 'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax',
        'quarterly_revenue': 'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax',
        'operating_income': 'us-gaap:OperatingIncomeLoss',
        'net_profit': 'us-gaap:NetIncomeLoss',
        'income_tax': 'us-gaap:IncomeTaxExpenseBenefit',
        'pretax_income': 'us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
        'gross_profit': 'us-gaap:GrossProfit',
        'cost_of_goods_sold': 'us-gaap:CostOfGoodsAndServicesSold',
        'operating_expenses': 'us-gaap:OperatingExpenses',
        'research_development': 'us-gaap:ResearchAndDevelopmentExpense',
        'depreciation_amortization': 'us-gaap:DepreciationDepletionAndAmortization',
        
        # 现金流类指标
        'operating_cash_flow': 'us-gaap:NetCashProvidedByUsedInOperatingActivities',
        'capital_expenditure': 'us-gaap:PaymentsToAcquirePropertyPlantAndEquipment',
        'investing_cash_flow': 'us-gaap:NetCashProvidedByUsedInInvestingActivities',
        'financing_cash_flow': 'us-gaap:NetCashProvidedByUsedInFinancingActivities',
        
        # 每股指标
        'eps': 'us-gaap:EarningsPerShareDiluted',
        'quarterly_eps': 'us-gaap:EarningsPerShareDiluted',
        'eps_basic': 'us-gaap:EarningsPerShareBasic',
        'diluted_shares_outstanding': 'us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding',
        'basic_shares_outstanding': 'us-gaap:WeightedAverageNumberOfSharesOutstandingBasic',
        
        # 股息相关
        'total_dividends': 'us-gaap:PaymentsOfDividends',
        'dividends': 'us-gaap:Dividends',
        'dividend_per_share': 'us-gaap:CommonStockDividendsPerShareDeclared',
        'dividends_per_share': 'us-gaap:CommonStockDividendsPerShareDeclared',
        'annual_dividends': 'us-gaap:CommonStockDividendsPerShareDeclared',
        'quarterly_dividends': 'us-gaap:CommonStockDividendsPerShareDeclared',
        
        # 计算指标 - 这些通常没有直接的GAAP对应，但可以标记为计算类型
        'working_capital': None,  # 计算指标：流动资产-流动负债
        'sales_per_share': None,  # 计算指标
        'cash_flow_per_share': None,  # 计算指标
        'book_value_per_share': None,  # 计算指标
        'cap_spending_per_share': None,  # 计算指标
        'return_on_total_capital': None,  # 计算指标
        'roe': None,  # 计算指标
        'retained_earnings_to_equity': None,  # 计算指标
        'dividends_to_net_profit': None,  # 计算指标
        'operating_margin': None,  # 计算指标
        'net_profit_margin': None,  # 计算指标
        'income_tax_rate': None,  # 计算指标
        
        # 市场数据类 - 这些不是GAAP概念
        'recent_price': None,
        'avg_pe_ratio': None,
        'relative_pe_ratio': None,
        'median_pe': None,
        'avg_dividend_yield': None,
        'beta': None,
        'month_open': None,
        'month_close': None,
        'month_high': None,
        'month_low': None,
        'relative_price_strength': None,
        'percent_shares_traded': None,
        'volume_traded': None,
        'average_annual_price': None,
        'market_avg_pe': None,
        'average_share_price': None,
        'market_cap': None,
        
        # 增长率类 - 计算指标
        'sales_growth_10y': None,
        'sales_growth_5y': None,
        'cash_flow_growth_10y': None,
        'cash_flow_growth_5y': None,
        'earnings_growth_10y': None,
        'earnings_growth_5y': None,
        'dividends_growth_10y': None,
        'dividends_growth_5y': None,
        'book_value_growth_10y': None,
        'book_value_growth_5y': None,
        
        # 其他基础指标
        'preferred_stock': None,  # 可能对应优先股相关GAAP概念，但在提供的列表中未找到
        'uncapitalized_leases': None,  # 租赁相关，可能对应OperatingLease概念
        'pension_liability': None,  # 可能对应养老金负债
        
        # 其他
        'share_repurchase': 'us-gaap:PaymentsForRepurchaseOfCommonStock',
    }
    
    return mapping

def analyze_metrics_mapping():
    """分析指标映射关系"""
    data_dir = Path("/Users/tingwang/work/sec_api_client/data")
    
    # 加载US-GAAP指标
    us_gaap_metrics = load_us_gaap_metrics()
    gaap_mapping = create_gaap_mapping()
    
    # 读取CSV文件
    metrics_df = pd.read_csv(data_dir / "1.metrics_nodes - 工作表1.csv")
    process_df = pd.read_csv(data_dir / "5.过程指标_nodes - 工作表1.csv")
    
    # 合并所有指标
    all_metrics = []
    
    # 处理主要指标
    for _, row in metrics_df.iterrows():
        metric_id = row[':ID']
        metric_name = row['name']
        chinese_name = row['name_chinese']
        metric_type = row['metrics_type']
        
        all_metrics.append({
            'id': metric_id,
            'name': metric_name,
            'chinese_name': chinese_name,
            'type': metric_type,
            'source': 'main_metrics'
        })
    
    # 处理过程指标
    for _, row in process_df.iterrows():
        metric_id = row[':ID']
        metric_name = row['name']
        chinese_name = row['name_chinese']
        metric_type = row['metrics_type']
        
        all_metrics.append({
            'id': metric_id,
            'name': metric_name,
            'chinese_name': chinese_name,
            'type': metric_type,
            'source': 'process_metrics'
        })
    
    # 分析映射关系
    mapped_metrics = []
    unmapped_metrics = []
    calculated_metrics = []  # 计算指标，不需要GAAP映射
    market_data_metrics = []  # 市场数据，不需要GAAP映射
    
    for metric in all_metrics:
        metric_id = metric['id']
        gaap_concept = gaap_mapping.get(metric_id)
        
        if gaap_concept is None:
            # 检查是否是计算指标或市场数据
            if metric_id in ['working_capital', 'sales_per_share', 'cash_flow_per_share', 
                           'book_value_per_share', 'cap_spending_per_share', 'return_on_total_capital',
                           'roe', 'retained_earnings_to_equity', 'dividends_to_net_profit', 
                           'operating_margin', 'net_profit_margin', 'income_tax_rate'] or \
               'growth' in metric_id:
                calculated_metrics.append({
                    **metric,
                    'category': 'calculated',
                    'mapping_status': 'calculated_metric'
                })
            elif metric_id in ['recent_price', 'avg_pe_ratio', 'relative_pe_ratio', 'median_pe',
                             'avg_dividend_yield', 'beta', 'month_open', 'month_close', 'month_high',
                             'month_low', 'relative_price_strength', 'percent_shares_traded',
                             'volume_traded', 'average_annual_price', 'market_avg_pe',
                             'average_share_price', 'market_cap']:
                market_data_metrics.append({
                    **metric,
                    'category': 'market_data',
                    'mapping_status': 'market_data'
                })
            else:
                unmapped_metrics.append({
                    **metric,
                    'us_gaap_concept': None,
                    'mapping_status': 'unmapped'
                })
        elif gaap_concept and gaap_concept in us_gaap_metrics:
            mapped_metrics.append({
                **metric,
                'us_gaap_concept': gaap_concept,
                'mapping_status': 'mapped'
            })
        else:
            # 尝试模糊匹配
            fuzzy_match = find_fuzzy_match(metric_id, us_gaap_metrics)
            if fuzzy_match:
                mapped_metrics.append({
                    **metric,
                    'us_gaap_concept': fuzzy_match,
                    'mapping_status': 'fuzzy_mapped'
                })
            else:
                unmapped_metrics.append({
                    **metric,
                    'us_gaap_concept': None,
                    'mapping_status': 'unmapped'
                })
    
    return mapped_metrics, unmapped_metrics, calculated_metrics, market_data_metrics, us_gaap_metrics

def find_fuzzy_match(metric_id, us_gaap_metrics):
    """尝试模糊匹配US-GAAP指标"""
    # 定义关键词映射
    keyword_mapping = {
        'revenue': ['Revenue', 'RevenueFromContract'],
        'assets': ['Assets'],
        'liability': ['Liabilities'],
        'equity': ['StockholdersEquity', 'Equity'],
        'cash': ['Cash', 'CashAndCashEquivalents'],
        'debt': ['Debt', 'LongTermDebt'],
        'income': ['Income', 'NetIncome'],
        'profit': ['NetIncome', 'Income'],
        'earnings': ['Earnings', 'EarningsPerShare'],
        'shares': ['Shares', 'SharesOutstanding'],
        'dividend': ['Dividend', 'Dividends'],
        'tax': ['Tax', 'IncomeTax'],
        'depreciation': ['Depreciation', 'DepreciationDepletion'],
        'operating': ['Operating', 'OperatingIncome'],
        'receivables': ['Receivable', 'AccountsReceivable'],
        'payable': ['Payable', 'AccountsPayable'],
        'inventory': ['Inventory'],
        'marketable': ['MarketableSecurities'],
    }
    
    for keyword, gaap_keywords in keyword_mapping.items():
        if keyword in metric_id.lower():
            for gaap_metric in us_gaap_metrics:
                for gaap_keyword in gaap_keywords:
                    if gaap_keyword.lower() in gaap_metric.lower():
                        return gaap_metric
    
    return None

def generate_neo4j_files(mapped_metrics, unmapped_metrics):
    """生成Neo4j导入文件"""
    data_dir = Path("/Users/tingwang/work/sec_api_client/data")
    
    # 生成映射关系文件
    mapping_data = []
    for metric in mapped_metrics:
        mapping_data.append({
            'metric_id': metric['id'],
            'metric_name': metric['name'],
            'chinese_name': metric['chinese_name'],
            'us_gaap_concept': metric['us_gaap_concept'],
            'mapping_status': metric['mapping_status'],
            'metric_type': metric['type'],
            'source': metric['source']
        })
    
    mapping_df = pd.DataFrame(mapping_data)
    mapping_df.to_csv(data_dir / "gaap_metric_mapping.csv", index=False, encoding='utf-8')
    
    # 生成未映射指标文件
    unmapped_data = []
    for metric in unmapped_metrics:
        unmapped_data.append({
            'metric_id': metric['id'],
            'metric_name': metric['name'],
            'chinese_name': metric['chinese_name'],
            'metric_type': metric['type'],
            'source': metric['source'],
            'reason': 'No matching US-GAAP concept found'
        })
    
    unmapped_df = pd.DataFrame(unmapped_data)
    unmapped_df.to_csv(data_dir / "unmapped_metrics.csv", index=False, encoding='utf-8')
    
    # 生成Neo4j节点文件
    neo4j_nodes = []
    
    # US-GAAP概念节点
    gaap_concepts = set()
    for metric in mapped_metrics:
        if metric['us_gaap_concept']:
            gaap_concepts.add(metric['us_gaap_concept'])
    
    for concept in gaap_concepts:
        neo4j_nodes.append({
            'id': concept,
            'name': concept.replace('us-gaap:', ''),
            'type': 'GAAP_CONCEPT',
            'namespace': 'us-gaap'
        })
    
    # 指标节点
    for metric in mapped_metrics + unmapped_metrics:
        neo4j_nodes.append({
            'id': f"metric_{metric['id']}",
            'name': metric['name'],
            'chinese_name': metric['chinese_name'],
            'type': 'FINANCIAL_METRIC',
            'metric_type': metric['type'],
            'source': metric['source']
        })
    
    nodes_df = pd.DataFrame(neo4j_nodes)
    nodes_df.to_csv(data_dir / "neo4j_nodes.csv", index=False, encoding='utf-8')
    
    # 生成Neo4j关系文件
    neo4j_relationships = []
    
    for metric in mapped_metrics:
        if metric['us_gaap_concept']:
            neo4j_relationships.append({
                'from_id': f"metric_{metric['id']}",
                'to_id': metric['us_gaap_concept'],
                'relationship_type': 'MAPS_TO_GAAP',
                'mapping_status': metric['mapping_status']
            })
    
    relationships_df = pd.DataFrame(neo4j_relationships)
    relationships_df.to_csv(data_dir / "neo4j_relationships.csv", index=False, encoding='utf-8')
    
    return mapping_df, unmapped_df, nodes_df, relationships_df

def main():
    """主函数"""
    print("开始分析财务指标与US-GAAP的映射关系...")
    
    # 分析映射关系
    mapped_metrics, unmapped_metrics, calculated_metrics, market_data_metrics, us_gaap_metrics = analyze_metrics_mapping()
    
    # 生成Neo4j文件
    mapping_df, unmapped_df, nodes_df, relationships_df = generate_neo4j_files(
        mapped_metrics, unmapped_metrics
    )
    
    # 输出统计信息
    total_metrics = len(mapped_metrics) + len(unmapped_metrics) + len(calculated_metrics) + len(market_data_metrics)
    print(f"\n=== 映射分析结果 ===")
    print(f"总US-GAAP指标数量: {len(us_gaap_metrics)}")
    print(f"总财务指标数量: {total_metrics}")
    print(f"成功映射的指标数量: {len(mapped_metrics)}")
    print(f"计算指标数量: {len(calculated_metrics)}")
    print(f"市场数据指标数量: {len(market_data_metrics)}")
    print(f"未映射的指标数量: {len(unmapped_metrics)}")
    print(f"GAAP映射成功率: {len(mapped_metrics)/(len(mapped_metrics)+len(unmapped_metrics))*100:.1f}%")
    
    print(f"\n=== 成功映射的指标 ===")
    for metric in mapped_metrics:
        status_text = "精确匹配" if metric['mapping_status'] == 'mapped' else "模糊匹配"
        print(f"• {metric['id']} ({metric['chinese_name']}) -> {metric['us_gaap_concept']} [{status_text}]")
    
    print(f"\n=== 计算指标（不需GAAP映射） ===")
    for metric in calculated_metrics:
        print(f"• {metric['id']} ({metric['chinese_name']}) - {metric['type']}")
    
    print(f"\n=== 市场数据指标（不是GAAP概念） ===")
    for metric in market_data_metrics:
        print(f"• {metric['id']} ({metric['chinese_name']}) - {metric['type']}")
    
    print(f"\n=== 未映射的指标 ===")
    for metric in unmapped_metrics:
        print(f"• {metric['id']} ({metric['chinese_name']}) - {metric['type']}")
    
    print(f"\n=== 生成的文件 ===")
    print("• gaap_metric_mapping.csv - 映射关系文件")
    print("• unmapped_metrics.csv - 未映射指标文件")
    print("• neo4j_nodes.csv - Neo4j节点文件")
    print("• neo4j_relationships.csv - Neo4j关系文件")
    
    # 生成扩展的分类文件
    data_dir = Path("/Users/tingwang/work/sec_api_client/data")
    
    # 保存计算指标
    calculated_df = pd.DataFrame([
        {
            'metric_id': m['id'],
            'metric_name': m['name'],
            'chinese_name': m['chinese_name'],
            'metric_type': m['type'],
            'category': 'calculated',
            'note': '计算指标，依赖其他基础指标计算得出'
        } for m in calculated_metrics
    ])
    calculated_df.to_csv(data_dir / "calculated_metrics.csv", index=False, encoding='utf-8')
    
    # 保存市场数据指标
    market_df = pd.DataFrame([
        {
            'metric_id': m['id'],
            'metric_name': m['name'],
            'chinese_name': m['chinese_name'],
            'metric_type': m['type'],
            'category': 'market_data',
            'note': '市场数据，非GAAP财务报表概念'
        } for m in market_data_metrics
    ])
    market_df.to_csv(data_dir / "market_data_metrics.csv", index=False, encoding='utf-8')
    
    print("\n额外生成的文件:")
    print("• calculated_metrics.csv - 计算指标文件")
    print("• market_data_metrics.csv - 市场数据指标文件")
    
    return mapped_metrics, unmapped_metrics, calculated_metrics, market_data_metrics

if __name__ == "__main__":
    main()