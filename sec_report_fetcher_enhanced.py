#!/usr/bin/env python3
"""
SEC报告数据获取工具（增强版）

根据公司代码(AAPL)或CIK、报告类型(10-K, 10-Q等)、年份等参数从SEC获取具体财务数据
支持从report_metrics_analysis.json中获取的全面报告类型和指标

使用示例:
    python sec_report_fetcher_enhanced.py --company AAPL --report 10-K --year 2025
    python sec_report_fetcher_enhanced.py --cik 0000320193 --report 10-K --section "Balance Sheet" --year 2020-2025
    python sec_report_fetcher_enhanced.py --company MSFT --report 10-Q --year 2024 --section "Balance Sheet Summary"
"""

import argparse
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Union

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src import SECClient, XBRLFramesClient, DocumentRetriever
import pandas as pd


def load_ticker_cik_mapping() -> Dict[str, str]:
    """
    从data/ticker.txt文件加载股票代码到CIK的映射
    
    Returns:
        股票代码到CIK的映射字典
    """
    ticker_cik_map = {}
    try:
        ticker_file_path = os.path.join(os.path.dirname(__file__), 'data', 'ticker.txt')
        with open(ticker_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        ticker = parts[0].upper()  # 统一转换为大写
                        cik = parts[1].zfill(10)  # 确保CIK是10位数字
                        ticker_cik_map[ticker] = cik
        print(f"📊 已加载 {len(ticker_cik_map)} 个公司的股票代码-CIK映射")
        return ticker_cik_map
    except Exception as e:
        print(f"⚠️  无法加载ticker映射文件: {e}")
        return {}


def load_report_metrics_mapping() -> Dict:
    """
    加载报告指标映射数据
    
    Returns:
        包含报告类型和指标映射的字典
    """
    try:
        with open(os.path.join(os.path.dirname(__file__), 'data', 'report_metrics_analysis.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('detailed_metrics', {})
    except Exception as e:
        print(f"⚠️  无法加载报告指标映射文件: {e}")
        return {}


def parse_year_range(year_arg: str) -> List[int]:
    """
    解析年份参数，支持单一年份或年份范围
    
    Args:
        year_arg: 年份参数，如 "2025" 或 "2020-2025"
        
    Returns:
        年份列表
    """
    if '-' in year_arg:
        start_year, end_year = map(int, year_arg.split('-'))
        if start_year > end_year:
            raise ValueError("起始年份不能大于结束年份")
        return list(range(start_year, end_year + 1))
    else:
        return [int(year_arg)]


def get_company_info(sec_client: SECClient, company_id: str, is_cik: bool = False, ticker_cik_map: Dict[str, str] = None) -> Dict:
    """
    获取公司信息
    
    Args:
        sec_client: SEC客户端
        company_id: 公司标识（股票代码或CIK）
        is_cik: 是否为CIK
        ticker_cik_map: 股票代码到CIK的映射
        
    Returns:
        公司信息字典
    """
    if is_cik:
        # 验证CIK格式
        cik = company_id.zfill(10)  # 确保是10位数字
        # 尝试获取公司提交信息来验证CIK
        try:
            submissions = sec_client.get_company_submissions(cik)
            company_name = submissions.get('names', ['Unknown Company'])[0] if submissions.get('names') else 'Unknown Company'
            # 从 ticker_cik_map 中反向查找 ticker
            ticker = 'N/A'
            if ticker_cik_map:
                for t, c in ticker_cik_map.items():
                    if c == cik:
                        ticker = t
                        break
            return {
                'cik': cik,
                'ticker': ticker,
                'title': company_name
            }
        except Exception as e:
            raise ValueError(f"无效的CIK {company_id}: {e}")
    else:
        # 通过股票代码查找公司
        ticker_upper = company_id.upper()
        
        # 优先从本地ticker映射中查找
        if ticker_cik_map and ticker_upper in ticker_cik_map:
            cik = ticker_cik_map[ticker_upper]
            print(f"📄 从本地数据找到 {ticker_upper} 的CIK: {cik}")
            
            # 获取公司名称
            try:
                submissions = sec_client.get_company_submissions(cik)
                company_name = submissions.get('names', ['Unknown Company'])[0] if submissions.get('names') else 'Unknown Company'
                return {
                    'cik': cik,
                    'ticker': ticker_upper,
                    'title': company_name
                }
            except Exception as e:
                print(f"⚠️  无法从 SEC API 获取公司名称: {e}")
                return {
                    'cik': cik,
                    'ticker': ticker_upper,
                    'title': f'{ticker_upper} Inc.'
                }
        
        # 如果本地数据中没有，则通过SEC API查找
        print(f"🔍 本地数据中未找到 {ticker_upper}，尝试通过SEC API查找...")
        company_info = sec_client.search_company_by_ticker(company_id)
        if not company_info:
            raise ValueError(f"未找到股票代码 {company_id} 对应的公司")
        return company_info


def get_financial_concepts_by_section(section: str, report_type: str, metrics_mapping: Dict) -> List[str]:
    """
    根据报表部分和报告类型获取对应的财务概念列表
    
    Args:
        section: 报表部分名称
        report_type: 报告类型
        metrics_mapping: 报告指标映射数据
        
    Returns:
        财务概念列表
    """
    # 默认的财务概念映射（保持向后兼容）
    default_concept_mapping = {
        'balance_sheet': [
            'Assets', 'AssetsCurrent', 'AssetsNoncurrent',
            'Liabilities', 'LiabilitiesCurrent', 'LiabilitiesNoncurrent',
            'StockholdersEquity',
            'CashAndCashEquivalentsAtCarryingValue',
            'AccountsReceivableNetCurrent',
            'InventoryNet',
            'PropertyPlantAndEquipmentNet',
            'LongTermDebtNoncurrent',
            'AccountsPayableCurrent'
        ],
        'income_statement': [
            'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
            'CostOfRevenue', 'GrossProfit',
            'OperatingExpenses', 'OperatingIncomeLoss',
            'NetIncomeLoss',
            'EarningsPerShareBasic', 'EarningsPerShareDiluted'
        ],
        'cash_flow': [
            'NetCashProvidedByUsedInOperatingActivities',
            'NetCashProvidedByUsedInInvestingActivities',
            'NetCashProvidedByUsedInFinancingActivities',
            'PaymentsToAcquirePropertyPlantAndEquipment',
            'PaymentsOfDividends',
            'PaymentsForRepurchaseOfCommonStock'
        ]
    }
    
    # 从report_metrics_analysis.json中获取指标
    if report_type in metrics_mapping and 'sections' in metrics_mapping[report_type]:
        sections = metrics_mapping[report_type]['sections']
        if section in sections:
            # 获取该部分的所有指标名称
            section_metrics = sections[section]
            if isinstance(section_metrics, list) and len(section_metrics) > 0:
                # 提取指标名称
                concept_names = []
                for metric in section_metrics:
                    if isinstance(metric, dict) and 'metric_name' in metric:
                        concept_names.append(metric['metric_name'])
                    elif isinstance(metric, str):
                        concept_names.append(metric)
                return concept_names
    
    # 回退到默认映射
    section_key = section.lower().replace(' ', '_')
    return default_concept_mapping.get(section_key, default_concept_mapping.get('balance_sheet', []))


def get_all_report_types(metrics_mapping: Dict) -> List[str]:
    """
    获取所有支持的报告类型
    
    Args:
        metrics_mapping: 报告指标映射数据
        
    Returns:
        报告类型列表
    """
    return list(metrics_mapping.keys()) if metrics_mapping else ['10-K', '10-Q']


def get_all_sections_for_report(report_type: str, metrics_mapping: Dict) -> List[str]:
    """
    获取指定报告类型的所有部分
    
    Args:
        report_type: 报告类型
        metrics_mapping: 报告指标映射数据
        
    Returns:
        部分名称列表
    """
    if report_type in metrics_mapping and 'sections' in metrics_mapping[report_type]:
        return list(metrics_mapping[report_type]['sections'].keys())
    return []


def fetch_sec_report_data(company_id: str, report_type: str, years: List[int], 
                         section: Optional[str] = None, is_cik: bool = False,
                         user_agent: str = "SEC Report Fetcher <sec.report@example.com>",
                         ticker_cik_map: Dict[str, str] = None) -> pd.DataFrame:
    """
    获取SEC报告数据
    
    Args:
        company_id: 公司标识（股票代码或CIK）
        report_type: 报告类型（如10-K, 10-Q）
        years: 年份列表
        section: 报告部分
        is_cik: 是否为CIK
        user_agent: 用户代理字符串
        ticker_cik_map: 股票代码到CIK的映射
        
    Returns:
        包含财务数据的DataFrame
    """
    # 初始化客户端
    sec_client = SECClient(user_agent=user_agent)
    xbrl_client = XBRLFramesClient(sec_client)
    
    # 加载报告指标映射
    metrics_mapping = load_report_metrics_mapping()
    
    # 获取公司信息
    print(f"🔍 正在获取公司信息...")
    company_info = get_company_info(sec_client, company_id, is_cik, ticker_cik_map)
    print(f"🏢 公司: {company_info['title']} (CIK: {company_info['cik']})")
    
    # 确定要获取的财务概念
    if section:
        concepts = get_financial_concepts_by_section(section, report_type, metrics_mapping)
        print(f"📄 报告部分: {section}")
        print(f"📈 该部分包含 {len(concepts)} 个指标")
    else:
        # 如果没有指定部分，获取所有主要财务概念
        concepts = [
            'Assets', 'Liabilities', 'StockholdersEquity',
            'Revenues', 'NetIncomeLoss', 'OperatingIncomeLoss',
            'CashAndCashEquivalentsAtCarryingValue',
            'AccountsReceivableNetCurrent', 'InventoryNet',
            'PropertyPlantAndEquipmentNet', 'LongTermDebtNoncurrent',
            'EarningsPerShareBasic', 'EarningsPerShareDiluted',
            'NetCashProvidedByUsedInOperatingActivities'
        ]
        print(f"📄 获取所有主要财务概念")
    
    print(f"📊 报告类型: {report_type}")
    print(f"📅 年份: {', '.join(map(str, years))}")
    
    # 收集数据
    all_data = []
    
    for year in years:
        print(f"\n📅 正在获取 {year} 年数据...")
        
        for concept in concepts:
            try:
                print(f"  🔄 获取 {concept}...")
                
                # 获取公司特定概念的历史数据
                concept_data = xbrl_client.get_company_concept_data(
                    cik=company_info['cik'], 
                    concept=concept
                )
                
                if concept_data and 'units' in concept_data:
                    # 查找USD单位数据
                    unit_data = concept_data['units'].get('USD', [])
                    
                    if unit_data:
                        # 查找指定年份的数据
                        for item in unit_data:
                            fiscal_year = item.get('fy', 0)
                            form_type = item.get('form', '')
                            
                            # 匹配年份和报告类型
                            if fiscal_year == year and form_type.upper() == report_type.upper():
                                # 格式化数值
                                value = item.get('val', 0)
                                if isinstance(value, (int, float)):
                                    if abs(value) >= 1e9:
                                        formatted_value = f"${value/1e9:.2f}B"
                                    elif abs(value) >= 1e6:
                                        formatted_value = f"${value/1e6:.2f}M"
                                    elif abs(value) >= 1e3:
                                        formatted_value = f"${value/1e3:.2f}K"
                                    else:
                                        formatted_value = f"${value:,.2f}"
                                else:
                                    formatted_value = str(value)
                                
                                all_data.append({
                                    'company': company_info['title'],
                                    'ticker': company_info.get('ticker', 'N/A'),
                                    'cik': company_info['cik'],
                                    'concept': concept,
                                    'value': value,
                                    'formatted_value': formatted_value,
                                    'year': fiscal_year,
                                    'report_type': form_type,
                                    'end_date': item.get('end', ''),
                                    'start_date': item.get('start', ''),
                                    'filed_date': item.get('filed', ''),
                                    'frame': item.get('frame', '')
                                })
                                print(f"    ✅ {concept}: {formatted_value}")
                                break  # 找到匹配的数据后跳出循环
                        else:
                            print(f"    ⚠️  未找到 {year} 年 {report_type} 报告中的 {concept} 数据")
                    else:
                        print(f"    ⚠️  {concept} 没有USD单位数据")
                else:
                    print(f"    ⚠️  无法获取 {concept} 数据")
                    
            except Exception as e:
                print(f"    ❌ 获取 {concept} 时出错: {e}")
    
    if not all_data:
        print(f"\n❌ 未获取到任何数据")
        return pd.DataFrame()
    
    # 创建DataFrame
    df = pd.DataFrame(all_data)
    
    # 按年份和概念排序
    df = df.sort_values(['year', 'concept'])
    
    print(f"\n✅ 成功获取 {len(df)} 条记录")
    return df


def main():
    """主函数"""
    # 加载报告指标映射
    metrics_mapping = load_report_metrics_mapping()
    
    # 加载ticker-CIK映射
    ticker_cik_map = load_ticker_cik_mapping()
    
    parser = argparse.ArgumentParser(
        description="SEC报告数据获取工具（增强版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python sec_report_fetcher_enhanced.py --company AAPL --report 10-K --year 2025
  python sec_report_fetcher_enhanced.py --cik 0000320193 --report 10-K --section "Balance Sheet" --year 2020-2025
  python sec_report_fetcher_enhanced.py --company MSFT --report 10-Q --year 2024 --section "Balance Sheet Summary"
        """
    )
    
    # 显示帮助信息的特殊选项
    help_parser = argparse.ArgumentParser(add_help=False)
    help_parser.add_argument('--help-sections', 
                            action='store_true',
                            help='显示可用的报告部分')
    help_parser.add_argument('--help-reports', 
                            action='store_true',
                            help='显示支持的报告类型')
    
    # 先解析帮助选项
    help_args, _ = help_parser.parse_known_args()
    
    # 显示报告部分帮助信息
    if help_args.help_sections:
        print("可用的报告部分:")
        if metrics_mapping:
            for report_type, report_data in metrics_mapping.items():
                print(f"\n{report_type}:")
                if 'sections' in report_data:
                    for section_name, metrics in report_data['sections'].items():
                        metric_count = len(metrics) if isinstance(metrics, list) else 0
                        print(f"  {section_name}: {metric_count} metrics")
        else:
            print("  Balance Sheet     - 资产负债表")
            print("  Income Statement  - 损益表")
            print("  Cash Flow         - 现金流量表")
        return
    
    # 显示报告类型帮助信息
    if help_args.help_reports:
        print("支持的报告类型:")
        if metrics_mapping:
            for report_type, report_data in metrics_mapping.items():
                description = report_data.get('description', 'N/A')
                total_metrics = report_data.get('total_metrics', 0)
                print(f"  {report_type}: {description} ({total_metrics} metrics)")
        else:
            print("  10-K: 年度报告")
            print("  10-Q: 季度报告")
        return
    
    # 公司标识参数组
    company_group = parser.add_mutually_exclusive_group(required=True)
    company_group.add_argument('--company', '-c', 
                              help='公司股票代码 (如: AAPL, MSFT)')
    company_group.add_argument('--cik', 
                              help='公司CIK号码 (如: 0000320193)')
    
    # 获取所有支持的报告类型
    all_report_types = get_all_report_types(metrics_mapping)
    
    # 必需参数
    parser.add_argument('--report', '-r', 
                       required=True,
                       choices=all_report_types,
                       help='SEC报告类型')
    
    parser.add_argument('--year', '-y', 
                       required=True,
                       help='年份 (如: 2025 或 2020-2025)')
    
    # 获取指定报告类型的所有部分
    all_sections = []
    if '--report' in sys.argv:
        try:
            report_index = sys.argv.index('--report')
            if len(sys.argv) > report_index + 1:
                report_type = sys.argv[report_index + 1]
                all_sections = get_all_sections_for_report(report_type, metrics_mapping)
        except:
            pass
    
    # 可选参数
    parser.add_argument('--section', '-s',
                       choices=all_sections if all_sections else None,
                       help='报告部分')
    
    parser.add_argument('--output', '-o',
                       help='输出文件路径 (支持 .csv, .xlsx)')
    
    parser.add_argument('--user-agent',
                       default="SEC Report Fetcher <sec.report@example.com>",
                       help='User-Agent字符串')
    
    args = parser.parse_args()
    
    try:
        # 解析年份参数
        years = parse_year_range(args.year)
        
        # 确定公司标识
        company_id = args.cik if args.cik else args.company
        is_cik = bool(args.cik)
        
        # 获取数据
        df = fetch_sec_report_data(
            company_id=company_id,
            report_type=args.report,
            years=years,
            section=args.section,
            is_cik=is_cik,
            user_agent=args.user_agent,
            ticker_cik_map=ticker_cik_map
        )
        
        if df.empty:
            print("❌ 未获取到任何数据")
            return
        
        # 显示结果
        print(f"\n📊 数据预览:")
        print("=" * 100)
        if args.section:
            print(f"公司: {df.iloc[0]['company']}")
            print(f"报告类型: {args.report}")
            print(f"报告部分: {args.section}")
            print(f"年份: {', '.join(map(str, years))}")
            print("=" * 100)
            
            # 按年份分组显示
            for year in sorted(df['year'].unique()):
                year_data = df[df['year'] == year]
                print(f"\n{year}年数据:")
                for _, row in year_data.iterrows():
                    print(f"  {row['concept']:40}: {row['formatted_value']:>15}")
        else:
            # 显示所有数据
            print(df[['year', 'concept', 'formatted_value', 'end_date']].to_string(index=False))
        
        # 保存到文件
        if args.output:
            try:
                if args.output.endswith('.csv'):
                    df.to_csv(args.output, index=False, encoding='utf-8')
                    print(f"\n💾 数据已保存到: {args.output}")
                elif args.output.endswith('.xlsx'):
                    df.to_excel(args.output, index=False)
                    print(f"\n💾 数据已保存到: {args.output}")
                else:
                    # 默认保存为CSV
                    output_file = args.output + '.csv'
                    df.to_csv(output_file, index=False, encoding='utf-8')
                    print(f"\n💾 数据已保存到: {output_file}")
            except Exception as e:
                print(f"⚠️  保存文件时出错: {e}")
        
        print(f"\n✅ 完成!")
        
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()