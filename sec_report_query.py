#!/usr/bin/env python3
"""
SEC报告查询工具

提供强大的报告数据查询功能，支持：
- 灵活的多维度查询
- 公司财务数据对比
- 指标趋势分析
- 数据导出功能

使用示例:
    python sec_report_query.py --help
    python sec_report_query.py query --company AAPL --report-type 10-K --years 2022 2023 2024
    python sec_report_query.py compare --metric Assets --companies AAPL MSFT GOOGL --years 2023 2024
    python sec_report_query.py company-overview --company AAPL
"""

import argparse
import sys
import os
import logging
from typing import List, Optional, Dict, Any
import pandas as pd

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.database.manager import DatabaseManager, get_default_sqlite_manager
from src.database.utils import DatabaseUtils

# 配置日志
logger = logging.getLogger(__name__)


class SECReportQuery:
    """SEC报告查询器"""
    
    def __init__(self, db_url: Optional[str] = None):
        """
        初始化查询器
        
        Args:
            db_url: 数据库连接URL，如果为None则使用默认SQLite
        """
        if db_url:
            self.db_manager = DatabaseManager(db_url)
            if not self.db_manager.connect():
                raise RuntimeError(f"无法连接到数据库: {db_url}")
        else:
            self.db_manager = get_default_sqlite_manager()
        
        self.db_utils = DatabaseUtils(self.db_manager)
    
    def query_reports(
        self,
        company: Optional[str] = None,
        report_type: Optional[str] = None,
        section: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        years: Optional[List[int]] = None,
        year_range: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        limit: Optional[int] = None,
        export_file: Optional[str] = None
    ) -> bool:
        """通用报告查询"""
        print("🔍 SEC报告数据查询")
        print("=" * 60)
        
        # 解析年份范围
        fiscal_year_range = None
        if year_range:
            try:
                start_year, end_year = map(int, year_range.split('-'))
                fiscal_year_range = (start_year, end_year)
                print(f"📅 年份范围: {start_year} - {end_year}")
            except ValueError:
                print(f"❌ 无效的年份范围格式: {year_range}")
                return False
        
        # 显示查询条件
        conditions = []
        if company:
            conditions.append(f"公司: {company}")
        if report_type:
            conditions.append(f"报告类型: {report_type}")
        if section:
            conditions.append(f"报告部分: {section}")
        if metrics:
            conditions.append(f"指标: {', '.join(metrics)}")
        if years:
            conditions.append(f"年份: {', '.join(map(str, years))}")
        if min_value is not None:
            conditions.append(f"最小值: {min_value:,.2f}")
        if max_value is not None:
            conditions.append(f"最大值: {max_value:,.2f}")
        if limit:
            conditions.append(f"结果限制: {limit}")
        
        if conditions:
            print("🔎 查询条件:")
            for condition in conditions:
                print(f"  • {condition}")
            print()
        
        try:
            # 执行查询
            results = self.db_utils.query_reports(
                company_identifier=company,
                report_type_code=report_type,
                section_name=section,
                metric_names=metrics,
                fiscal_years=years,
                fiscal_year_range=fiscal_year_range,
                min_value=min_value,
                max_value=max_value,
                limit=limit
            )
            
            if not results:
                print("❌ 未找到匹配的数据")
                return False
            
            print(f"✅ 找到 {len(results)} 条记录")
            print("=" * 60)
            
            # 显示结果摘要
            companies_set = set(r['company_name'] for r in results)
            years_set = set(r['fiscal_year'] for r in results)
            metrics_set = set(r['metric_name'] for r in results)
            
            print(f"📊 结果摘要:")
            print(f"  • 涉及公司: {len(companies_set)} 家")
            print(f"  • 年份范围: {min(years_set)} - {max(years_set)}")
            print(f"  • 指标数量: {len(metrics_set)} 个")
            print()
            
            # 按公司分组显示前几条结果
            company_groups = {}
            for record in results:
                company_name = record['company_name']
                if company_name not in company_groups:
                    company_groups[company_name] = []
                company_groups[company_name].append(record)
            
            print("📈 查询结果预览:")
            shown_count = 0
            max_show = 20
            
            for company_name, records in list(company_groups.items())[:5]:  # 最多显示5家公司
                print(f"\n🏢 {company_name}:")
                for record in sorted(records, key=lambda x: x['fiscal_year'], reverse=True)[:4]:  # 每家公司最多4条
                    if shown_count >= max_show:
                        break
                    print(f"   {record['fiscal_year']} | {record['metric_name']}: {record['formatted_value'] or record['value']}")
                    shown_count += 1
                if shown_count >= max_show:
                    break
            
            if len(results) > shown_count:
                print(f"\n... 还有 {len(results) - shown_count} 条记录未显示")
            
            # 导出功能
            if export_file:
                self._export_results(results, export_file)
            
            return True
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            logger.error(f"Query failed: {e}")
            return False
    
    def compare_metrics(
        self,
        metric_name: str,
        companies: List[str],
        years: Optional[List[int]] = None,
        report_type: Optional[str] = None,
        export_file: Optional[str] = None
    ) -> bool:
        """多公司指标对比"""
        print(f"📊 指标对比分析: {metric_name}")
        print("=" * 60)
        
        try:
            results = self.db_utils.query_reports_by_metric(
                metric_name=metric_name,
                companies=companies,
                fiscal_years=years,
                report_type_code=report_type
            )
            
            if not results:
                print(f"❌ 未找到指标 {metric_name} 的数据")
                return False
            
            print(f"✅ 找到 {len(results)} 条记录")
            
            # 按公司分组
            company_data = {}
            for record in results:
                company_name = record['company_name']
                ticker = record['company_ticker']
                company_key = f"{company_name} ({ticker})" if ticker else company_name
                
                if company_key not in company_data:
                    company_data[company_key] = []
                company_data[company_key].append(record)
            
            print(f"\n📈 对比结果 ({len(company_data)} 家公司):")
            
            # 创建对比表格
            comparison_table = {}
            all_years = set()
            
            for company_key, records in company_data.items():
                comparison_table[company_key] = {}
                for record in records:
                    year = record['fiscal_year']
                    all_years.add(year)
                    comparison_table[company_key][year] = {
                        'value': record['value'],
                        'formatted_value': record['formatted_value'],
                        'unit': record['unit']
                    }
            
            # 按年份排序显示
            sorted_years = sorted(all_years, reverse=True)
            
            print(f"\n📊 {metric_name} 对比表格:")
            header_years = [f'{year}年' for year in sorted_years[:5]]
            print(f"{'公司':<30} | {' | '.join(f'{h:<15}' for h in header_years)}")
            print("-" * (30 + len(sorted_years[:5]) * 18))
            
            for company_key in sorted(company_data.keys()):
                row_data = [company_key[:28].ljust(30)]
                for year in sorted_years[:5]:
                    data = comparison_table[company_key].get(year)
                    if data:
                        value_str = data['formatted_value'] or f"{data['value']:,.0f}"
                        row_data.append(value_str[:15].ljust(15))
                    else:
                        row_data.append("-".ljust(15))
                print(" | ".join(row_data))
            
            # 计算增长率（如果有多年数据）
            if len(sorted_years) >= 2:
                print(f"\n📈 年度变化分析 ({sorted_years[1]} → {sorted_years[0]}):")
                for company_key, records in company_data.items():
                    current_year_data = comparison_table[company_key].get(sorted_years[0])
                    prev_year_data = comparison_table[company_key].get(sorted_years[1])
                    
                    if current_year_data and prev_year_data:
                        current_val = current_year_data['value']
                        prev_val = prev_year_data['value']
                        
                        if prev_val and prev_val != 0:
                            growth_rate = ((current_val - prev_val) / abs(prev_val)) * 100
                            print(f"  {company_key}: {growth_rate:+.1f}%")
            
            # 导出功能
            if export_file:
                self._export_results(results, export_file)
            
            return True
            
        except Exception as e:
            print(f"❌ 对比分析失败: {e}")
            logger.error(f"Comparison failed: {e}")
            return False
    
    def company_overview(self, company_identifier: str, report_type: Optional[str] = None) -> bool:
        """公司财务数据概览"""
        print(f"🏢 公司财务数据概览: {company_identifier}")
        print("=" * 60)
        
        try:
            data = self.db_utils.query_reports_by_company(
                company_identifier=company_identifier,
                report_type_code=report_type
            )
            
            if not data or data.get('total_records', 0) == 0:
                print(f"❌ 未找到公司 {company_identifier} 的数据")
                return False
            
            # 公司基本信息
            company_info = data['company']
            print(f"📋 基本信息:")
            print(f"  • 公司名称: {company_info['name']}")
            print(f"  • 股票代码: {company_info['ticker'] or 'N/A'}")
            print(f"  • CIK: {company_info['cik']}")
            print(f"  • 总记录数: {data['total_records']:,}")
            print(f"  • 数据年份: {min(data['available_years'])} - {max(data['available_years'])}")
            print(f"  • 报告类型: {', '.join(data['available_report_types'])}")
            print(f"  • 报告部分: {len(data['available_sections'])} 个")
            
            # 年度数据分布
            print(f"\n📅 年度数据分布:")
            for year in sorted(data['available_years'], reverse=True)[:10]:
                year_data = data['data_by_year'].get(year, {})
                total_metrics = sum(
                    sum(len(section_data) for section_data in report_data.values())
                    for report_data in year_data.values()
                )
                print(f"  • {year}年: {total_metrics} 个指标")
            
            if len(data['available_years']) > 10:
                print(f"  ... 还有 {len(data['available_years']) - 10} 年的数据")
            
            # 报告类型分布
            print(f"\n📊 报告类型分布:")
            for report_type in data['available_report_types']:
                type_count = 0
                for year_data in data['data_by_year'].values():
                    if report_type in year_data:
                        type_count += sum(len(section_data) for section_data in year_data[report_type].values())
                print(f"  • {report_type}: {type_count} 个指标")
            
            # 最新年份详细数据
            if data['available_years']:
                latest_year = max(data['available_years'])
                latest_data = data['data_by_year'].get(latest_year, {})
                
                print(f"\n📈 {latest_year}年详细数据:")
                for report_type, sections in latest_data.items():
                    print(f"  📄 {report_type}:")
                    for section_name, metrics in sections.items():
                        if metrics:
                            print(f"    • {section_name}: {len(metrics)} 个指标")
                            # 显示前几个重要指标
                            important_metrics = [
                                m for m in metrics 
                                if any(keyword in m['metric_name'].lower() 
                                      for keyword in ['assets', 'revenue', 'income', 'equity', 'cash'])
                            ][:3]
                            
                            for metric in important_metrics:
                                print(f"      - {metric['metric_name']}: {metric['formatted_value']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 获取公司概览失败: {e}")
            logger.error(f"Company overview failed: {e}")
            return False
    
    def show_analytics(self, report_type: Optional[str] = None) -> bool:
        """显示数据分析统计"""
        print(f"📊 数据分析统计: {report_type or '所有报告'}")
        print("=" * 60)
        
        try:
            analytics = self.db_utils.get_report_analytics(report_type)
            
            print(f"📈 整体统计:")
            print(f"  • 总记录数: {analytics['total_records']:,}")
            print(f"  • 数据年份范围: {analytics['year_range']['min_year']} - {analytics['year_range']['max_year']}")
            
            if analytics['latest_data_date']:
                print(f"  • 最新数据: {analytics['latest_data_date'].strftime('%Y-%m-%d %H:%M')}")
            
            # 年份分布
            print(f"\n📅 年份数据分布:")
            for year_data in analytics['data_by_year'][:15]:
                percentage = (year_data['count'] / analytics['total_records']) * 100
                bar = '█' * int(percentage // 2)
                print(f"  {year_data['year']}: {year_data['count']:>6,} ({percentage:4.1f}%) {bar}")
            
            # 公司排行
            print(f"\n🏆 数据最丰富的公司 (Top 15):")
            for i, company in enumerate(analytics['top_companies_by_data'], 1):
                percentage = (company['record_count'] / analytics['total_records']) * 100
                print(f"  {i:2d}. {company['name'][:40]:<40} ({company['ticker'] or 'N/A':<5}): {company['record_count']:>6,} ({percentage:4.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"❌ 获取分析统计失败: {e}")
            logger.error(f"Analytics failed: {e}")
            return False
    
    def _export_results(self, results: List[Dict[str, Any]], export_file: str):
        """导出查询结果"""
        try:
            df = pd.DataFrame(results)
            
            if export_file.endswith('.csv'):
                df.to_csv(export_file, index=False, encoding='utf-8')
            elif export_file.endswith('.xlsx'):
                df.to_excel(export_file, index=False)
            else:
                # 默认CSV
                export_file = export_file + '.csv'
                df.to_csv(export_file, index=False, encoding='utf-8')
            
            print(f"\n💾 数据已导出到: {export_file}")
            print(f"   • 记录数: {len(results):,}")
            print(f"   • 列数: {len(df.columns)}")
            
        except Exception as e:
            print(f"⚠️ 导出数据时出错: {e}")
    
    def close(self):
        """关闭数据库连接"""
        if self.db_manager:
            self.db_manager.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="SEC报告查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python sec_report_query.py query --company AAPL --report-type 10-K --years 2022 2023 2024
  python sec_report_query.py compare --metric Assets --companies AAPL MSFT GOOGL --years 2023 2024
  python sec_report_query.py company-overview --company AAPL
  python sec_report_query.py analytics --report-type 10-K
        """
    )
    
    # 全局参数
    parser.add_argument('--db-url', help='数据库连接URL（默认使用SQLite）')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='日志级别')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # query 命令
    query_parser = subparsers.add_parser('query', help='通用数据查询')
    query_parser.add_argument('--company', help='公司标识（ticker或CIK）')
    query_parser.add_argument('--report-type', help='报告类型（如10-K, 10-Q）')
    query_parser.add_argument('--section', help='报告部分名称')
    query_parser.add_argument('--metrics', nargs='+', help='指标名称列表')
    query_parser.add_argument('--years', type=int, nargs='+', help='年份列表')
    query_parser.add_argument('--year-range', help='年份范围（如2020-2024）')
    query_parser.add_argument('--min-value', type=float, help='最小值过滤')
    query_parser.add_argument('--max-value', type=float, help='最大值过滤')
    query_parser.add_argument('--limit', type=int, help='结果数量限制')
    query_parser.add_argument('--export', help='导出文件路径')
    
    # compare 命令
    compare_parser = subparsers.add_parser('compare', help='多公司指标对比')
    compare_parser.add_argument('--metric', required=True, help='指标名称')
    compare_parser.add_argument('--companies', required=True, nargs='+', help='公司列表')
    compare_parser.add_argument('--years', type=int, nargs='+', help='年份列表')
    compare_parser.add_argument('--report-type', help='报告类型过滤')
    compare_parser.add_argument('--export', help='导出文件路径')
    
    # company-overview 命令
    overview_parser = subparsers.add_parser('company-overview', help='公司财务数据概览')
    overview_parser.add_argument('--company', required=True, help='公司标识（ticker或CIK）')
    overview_parser.add_argument('--report-type', help='报告类型过滤')
    
    # analytics 命令
    analytics_parser = subparsers.add_parser('analytics', help='数据分析统计')
    analytics_parser.add_argument('--report-type', help='报告类型过滤')
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # 创建查询器
        query_tool = SECReportQuery(args.db_url)
        
        success = False
        
        if args.command == 'query':
            success = query_tool.query_reports(
                company=getattr(args, 'company', None),
                report_type=getattr(args, 'report_type', None),
                section=getattr(args, 'section', None),
                metrics=getattr(args, 'metrics', None),
                years=getattr(args, 'years', None),
                year_range=getattr(args, 'year_range', None),
                min_value=getattr(args, 'min_value', None),
                max_value=getattr(args, 'max_value', None),
                limit=getattr(args, 'limit', None),
                export_file=getattr(args, 'export', None)
            )
        
        elif args.command == 'compare':
            success = query_tool.compare_metrics(
                metric_name=args.metric,
                companies=args.companies,
                years=getattr(args, 'years', None),
                report_type=getattr(args, 'report_type', None),
                export_file=getattr(args, 'export', None)
            )
        
        elif args.command == 'company-overview':
            success = query_tool.company_overview(
                company_identifier=args.company,
                report_type=getattr(args, 'report_type', None)
            )
        
        elif args.command == 'analytics':
            success = query_tool.show_analytics(
                report_type=getattr(args, 'report_type', None)
            )
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        print(f"❌ 程序执行失败: {e}")
        return 1
    
    finally:
        if 'query_tool' in locals():
            query_tool.close()


if __name__ == "__main__":
    exit(main())