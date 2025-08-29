#!/usr/bin/env python3
"""
SEC报告数据库管理工具

提供数据库初始化、数据导入、查询和管理的命令行界面
支持SQLite、PostgreSQL和MySQL

使用示例:
    python sec_db_manager.py init  # 初始化数据库
    python sec_db_manager.py import-structure  # 导入报告结构
    python sec_db_manager.py import-companies  # 导入公司信息
    python sec_db_manager.py stats  # 显示统计信息
    python sec_db_manager.py query --company AAPL  # 查询公司数据
"""

import argparse
import sys
import os
import logging
import json
from typing import Dict, List, Any, Optional

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.database.manager import DatabaseManager, get_default_sqlite_manager
from src.database.utils import DatabaseUtils
from src.database.importer import DataImporter, import_full_structure
from src.database.models import Company, ReportType, ReportSection, Metric

# 配置日志
logger = logging.getLogger(__name__)


class SECDatabaseCLI:
    """SEC数据库命令行界面"""
    
    def __init__(self, db_url: Optional[str] = None):
        """
        初始化CLI
        
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
    
    def init_database(self) -> bool:
        """初始化数据库（创建表）"""
        try:
            print("🚀 正在初始化数据库...")
            
            if self.db_manager.create_tables():
                print("✅ 数据库表创建成功")
                
                # 显示数据库信息
                db_info = self.db_manager.get_database_info()
                print(f"📊 数据库信息:")
                print(f"  类型: {db_info.get('database_type', 'Unknown')}")
                print(f"  状态: {db_info.get('status', 'Unknown')}")
                
                return True
            else:
                print("❌ 数据库表创建失败")
                return False
                
        except Exception as e:
            print(f"❌ 初始化数据库时出错: {e}")
            return False
    
    def import_structure(self, json_file: Optional[str] = None) -> bool:
        """导入报告结构"""
        try:
            # 默认文件路径
            if not json_file:
                json_file = os.path.join(os.path.dirname(__file__), 'data', 'report_metrics_analysis.json')
            
            if not os.path.exists(json_file):
                print(f"❌ 文件不存在: {json_file}")
                return False
            
            print(f"📥 正在导入报告结构从: {json_file}")
            
            importer = DataImporter(self.db_manager)
            
            if importer.import_report_structure(json_file):
                stats = importer.get_import_statistics()
                print("✅ 报告结构导入成功")
                print("📊 导入统计:")
                for table, table_stats in stats['detailed_stats'].items():
                    print(f"  {table}:")
                    print(f"    创建: {table_stats['created']}")
                    print(f"    更新: {table_stats['updated']}")
                    print(f"    跳过: {table_stats['skipped']}")
                
                return True
            else:
                print("❌ 报告结构导入失败")
                return False
                
        except Exception as e:
            print(f"❌ 导入报告结构时出错: {e}")
            return False
    
    def import_companies(self, ticker_file: Optional[str] = None) -> bool:
        """导入公司信息"""
        try:
            # 默认文件路径
            if not ticker_file:
                ticker_file = os.path.join(os.path.dirname(__file__), 'data', 'ticker.txt')
            
            if not os.path.exists(ticker_file):
                print(f"❌ 文件不存在: {ticker_file}")
                return False
            
            print(f"📥 正在导入公司信息从: {ticker_file}")
            
            importer = DataImporter(self.db_manager)
            
            if importer.import_ticker_companies(ticker_file):
                stats = importer.get_import_statistics()
                print("✅ 公司信息导入成功")
                print("📊 导入统计:")
                company_stats = stats['detailed_stats']['companies']
                print(f"  公司:")
                print(f"    创建: {company_stats['created']}")
                print(f"    更新: {company_stats['updated']}")
                print(f"    跳过: {company_stats['skipped']}")
                
                return True
            else:
                print("❌ 公司信息导入失败")
                return False
                
        except Exception as e:
            print(f"❌ 导入公司信息时出错: {e}")
            return False
    
    def show_statistics(self) -> bool:
        """显示数据库统计信息"""
        try:
            print("📊 数据库统计信息:")
            print("=" * 60)
            
            # 基本统计
            stats = self.db_utils.get_database_statistics()
            
            print("📈 表记录统计:")
            print(f"  公司数量: {stats.get('companies', 0):,}")
            print(f"  报告类型: {stats.get('report_types', 0):,}")
            print(f"  报告部分: {stats.get('report_sections', 0):,}")
            print(f"  财务指标: {stats.get('metrics', 0):,}")
            print(f"  财务数据: {stats.get('financial_data_records', 0):,}")
            print(f"  无效缓存: {stats.get('invalid_cache_entries', 0):,}")
            print(f"  获取日志: {stats.get('fetch_logs', 0):,}")
            
            # 数据覆盖
            print(f"\n📊 数据覆盖:")
            print(f"  有数据的公司: {stats.get('companies_with_data', 0):,}")
            print(f"  数据覆盖率: {stats.get('data_coverage_percentage', 0):.1f}%")
            
            # 年份范围
            year_range = stats.get('year_range')
            if year_range and year_range['min_year']:
                print(f"  数据年份范围: {year_range['min_year']} - {year_range['max_year']}")
            
            # 缓存统计
            print(f"\n💾 缓存统计:")
            cache_stats = self.db_utils.get_cache_statistics()
            print(f"  总缓存条目: {cache_stats.get('total_cache_entries', 0):,}")
            print(f"  活跃缓存: {cache_stats.get('active_entries', 0):,}")
            print(f"  过期缓存: {cache_stats.get('expired_entries', 0):,}")
            
            # 数据库信息
            print(f"\n🗄️ 数据库信息:")
            db_info = self.db_manager.get_database_info()
            print(f"  数据库类型: {db_info.get('database_type', 'Unknown')}")
            print(f"  连接状态: {db_info.get('status', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 获取统计信息时出错: {e}")
            return False
    
    def query_company(self, company_identifier: str) -> bool:
        """查询公司信息和数据"""
        try:
            print(f"🔍 查询公司: {company_identifier}")
            print("=" * 60)
            
            # 获取公司信息
            company = self.db_utils.get_company_by_ticker(company_identifier) or \
                     self.db_utils.get_company_by_cik(company_identifier)
            
            if not company:
                # 尝试搜索
                companies = self.db_utils.search_companies(company_identifier, limit=5)
                if companies:
                    print("🔍 找到相似的公司:")
                    for comp in companies:
                        print(f"  {comp.ticker or 'N/A'}: {comp.name} (CIK: {comp.cik})")
                else:
                    print(f"❌ 未找到公司: {company_identifier}")
                return False
            
            # 显示公司基本信息
            print("🏢 公司信息:")
            print(f"  CIK: {company.cik}")
            print(f"  Ticker: {company.ticker or 'N/A'}")
            print(f"  名称: {company.name}")
            print(f"  行业: {company.industry or 'N/A'}")
            status_text = "活跃" if company.is_active else "非活跃"
            print(f"  状态: {status_text}")
            
            # 获取财务数据概览
            summary = self.db_utils.get_company_financial_summary(company.cik)
            
            if summary and summary.get('total_records', 0) > 0:
                print(f"\n📊 财务数据概览:")
                print(f"  总记录数: {summary['total_records']:,}")
                print(f"  可用年份: {', '.join(map(str, summary['available_years']))}")
                print(f"  报告类型: {', '.join(summary['available_report_types'])}")
                
                # 显示最近年份的数据样例
                if summary['available_years']:
                    latest_year = summary['available_years'][0]
                    year_data = summary['data_by_year'].get(latest_year, {})
                    
                    print(f"\n📈 {latest_year}年数据样例:")
                    for report_type, records in year_data.items():
                        print(f"  {report_type}: {len(records)} 个指标")
                        # 显示前3个指标
                        for i, record in enumerate(records[:3]):
                            print(f"    {record['metric_name']}: {record['formatted_value']}")
                        if len(records) > 3:
                            print(f"    ... 还有 {len(records) - 3} 个指标")
            else:
                print("\n📊 暂无财务数据")
            
            return True
            
        except Exception as e:
            print(f"❌ 查询公司时出错: {e}")
            return False
    
    def list_report_types(self) -> bool:
        """列出所有报告类型"""
        try:
            print("📋 支持的报告类型:")
            print("=" * 60)
            
            report_types = self.db_utils.get_report_types()
            
            if not report_types:
                print("❌ 未找到任何报告类型，请先导入报告结构")
                return False
            
            for report_type in report_types:
                print(f"\n📄 {report_type.type_code}")
                print(f"  名称: {report_type.name}")
                print(f"  描述: {report_type.description or 'N/A'}")
                print(f"  频率: {report_type.frequency or 'N/A'}")
                print(f"  总指标数: {report_type.total_metrics:,}")
                print(f"  唯一指标数: {report_type.unique_metrics:,}")
                
                # 显示部分信息
                sections = self.db_utils.get_report_sections(report_type.type_code)
                if sections:
                    print(f"  报告部分 ({len(sections)}):")
                    for section in sections[:5]:  # 只显示前5个
                        print(f"    - {section.section_name} ({section.metrics_count} 指标)")
                    if len(sections) > 5:
                        print(f"    ... 还有 {len(sections) - 5} 个部分")
            
            return True
            
        except Exception as e:
            print(f"❌ 列出报告类型时出错: {e}")
            return False
    
    def cleanup_cache(self) -> bool:
        """清理过期缓存"""
        try:
            print("🧹 正在清理过期缓存...")
            
            cleaned_count = self.db_utils.cleanup_expired_cache()
            
            if cleaned_count > 0:
                print(f"✅ 已清理 {cleaned_count} 条过期缓存")
            else:
                print("✅ 没有过期缓存需要清理")
            
            return True
            
        except Exception as e:
            print(f"❌ 清理缓存时出错: {e}")
            return False
    
    def query_reports(
        self,
        company: Optional[str] = None,
        report_type: Optional[str] = None,
        section: Optional[str] = None,
        metrics: Optional[List[str]] = None,
        years: Optional[List[int]] = None,
        year_range: Optional[str] = None,
        limit: Optional[int] = None,
        export_file: Optional[str] = None
    ) -> bool:
        """查询报告数据"""
        try:
            print("🔍 正在查询报告数据...")
            print("=" * 60)
            
            # 解析年份范围
            fiscal_year_range = None
            if year_range:
                try:
                    start_year, end_year = map(int, year_range.split('-'))
                    fiscal_year_range = (start_year, end_year)
                    print(f"📅 年份范围: {start_year} - {end_year}")
                except ValueError:
                    print(f"⚠️  无效的年份范围格式: {year_range}，应为 '2020-2024'")
                    return False
            
            # 打印查询条件
            if company:
                print(f"🏢 公司: {company}")
            if report_type:
                print(f"📄 报告类型: {report_type}")
            if section:
                print(f"📊 报告部分: {section}")
            if metrics:
                print(f"📈 指标: {', '.join(metrics)}")
            if years:
                print(f"📅 年份: {', '.join(map(str, years))}")
            if limit:
                print(f"🔢 结果限制: {limit}")
            
            print()
            
            # 执行查询
            results = self.db_utils.query_reports(
                company_identifier=company,
                report_type_code=report_type,
                section_name=section,
                metric_names=metrics,
                fiscal_years=years,
                fiscal_year_range=fiscal_year_range,
                limit=limit
            )
            
            if not results:
                print("❌ 未找到匹配的报告数据")
                return False
            
            print(f"✅ 找到 {len(results)} 条记录")
            print("=" * 60)
            
            # 显示结果
            for i, record in enumerate(results[:50], 1):  # 最多显示50条
                print(f"\n{i}. {record['company_name']} ({record['company_ticker'] or 'N/A'})")
                print(f"   报告: {record['report_type']} - {record['section_name']}")
                print(f"   指标: {record['metric_name']}")
                print(f"   年份: {record['fiscal_year']} | 值: {record['formatted_value'] or record['value']}")
                if record['period_end_date']:
                    print(f"   期间: {record['period_end_date']}")
            
            if len(results) > 50:
                print(f"\n... 还有 {len(results) - 50} 条记录未显示")
            
            # 导出功能
            if export_file:
                try:
                    import pandas as pd
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
                    
                except Exception as e:
                    print(f"\n⚠️  导出数据时出错: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ 查询报告数据时出错: {e}")
            return False
    
    def query_company_reports(self, company_identifier: str, report_type: Optional[str] = None) -> bool:
        """查询公司的所有报告数据"""
        try:
            print(f"🔍 查询公司报告: {company_identifier}")
            print("=" * 60)
            
            data = self.db_utils.query_reports_by_company(
                company_identifier=company_identifier,
                report_type_code=report_type
            )
            
            if not data or data.get('total_records', 0) == 0:
                print(f"❌ 未找到公司 {company_identifier} 的报告数据")
                return False
            
            # 显示公司信息
            company_info = data['company']
            print(f"🏢 公司: {company_info['name']}")
            print(f"   Ticker: {company_info['ticker'] or 'N/A'}")
            print(f"   CIK: {company_info['cik']}")
            print(f"   总记录数: {data['total_records']:,}")
            print(f"   年份范围: {', '.join(map(str, data['available_years']))}")
            print(f"   报告类型: {', '.join(data['available_report_types'])}")
            print(f"   报告部分: {len(data['available_sections'])} 个")
            
            # 显示每年数据概览
            print(f"\n📅 年度数据概览:")
            for year in sorted(data['available_years'], reverse=True)[:5]:  # 最近5年
                year_data = data['data_by_year'].get(year, {})
                total_year_records = sum(
                    sum(len(sections.get(section, [])) for section in sections.values())
                    for sections in year_data.values()
                )
                print(f"  {year}年: {total_year_records} 条记录")
                
                for report_type, sections in year_data.items():
                    for section_name, metrics in sections.items():
                        if metrics:  # 只显示有数据的部分
                            print(f"    {report_type} - {section_name}: {len(metrics)} 个指标")
            
            if len(data['available_years']) > 5:
                print(f"  ... 还有 {len(data['available_years']) - 5} 年的数据")
            
            return True
            
        except Exception as e:
            print(f"❌ 查询公司报告时出错: {e}")
            return False
    
    def query_metric_comparison(self, metric_name: str, companies: List[str], years: Optional[List[int]] = None) -> bool:
        """查询多公司指标对比"""
        try:
            print(f"🔍 指标对比分析: {metric_name}")
            print("=" * 60)
            
            results = self.db_utils.query_reports_by_metric(
                metric_name=metric_name,
                companies=companies,
                fiscal_years=years
            )
            
            if not results:
                print(f"❌ 未找到指标 {metric_name} 的数据")
                return False
            
            print(f"✅ 找到 {len(results)} 条记录")
            print(f"📈 指标: {metric_name}")
            
            # 按公司分组显示
            company_data = {}
            for record in results:
                company_name = record['company_name']
                if company_name not in company_data:
                    company_data[company_name] = []
                company_data[company_name].append(record)
            
            print(f"\n🏢 对比结果 ({len(company_data)} 家公司):")
            
            for company_name, records in company_data.items():
                print(f"\n  {company_name}:")
                for record in sorted(records, key=lambda x: x['fiscal_year'], reverse=True)[:3]:  # 最近3年
                    print(f"    {record['fiscal_year']}年: {record['formatted_value'] or record['value']} ({record['unit']})")
            
            return True
            
        except Exception as e:
            print(f"❌ 指标对比查询时出错: {e}")
            return False
    
    def show_report_analytics(self, report_type: Optional[str] = None) -> bool:
        """显示报告分析统计"""
        try:
            print(f"📈 报告分析统计: {report_type or '所有报告'}")
            print("=" * 60)
            
            analytics = self.db_utils.get_report_analytics(report_type)
            
            print(f"📊 总记录数: {analytics['total_records']:,}")
            print(f"📅 数据年份范围: {analytics['year_range']['min_year']} - {analytics['year_range']['max_year']}")
            
            if analytics['latest_data_date']:
                print(f"🕰️ 最新数据: {analytics['latest_data_date'].strftime('%Y-%m-%d %H:%M')}")
            
            # 年份分布
            print(f"\n📅 年份数据分布:")
            for year_data in analytics['data_by_year'][:10]:  # 最近10年
                print(f"  {year_data['year']}年: {year_data['count']:,} 条记录")
            
            if len(analytics['data_by_year']) > 10:
                print(f"  ... 还有 {len(analytics['data_by_year']) - 10} 年的数据")
            
            # 公司数据排行
            print(f"\n🏆 数据最丰富的公司 (Top 10):")
            for i, company in enumerate(analytics['top_companies_by_data'], 1):
                print(f"  {i}. {company['name']} ({company['ticker'] or 'N/A'}): {company['record_count']:,} 条")
            
            return True
            
        except Exception as e:
            print(f"❌ 获取报告分析时出错: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.db_manager:
            self.db_manager.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="SEC报告数据库管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python sec_db_manager.py init
  python sec_db_manager.py import-structure
  python sec_db_manager.py import-companies
  python sec_db_manager.py stats
  python sec_db_manager.py query --company AAPL
  python sec_db_manager.py list-reports
        """
    )
    
    # 全局参数
    parser.add_argument('--db-url',
                       help='数据库连接URL（默认使用SQLite）')
    
    parser.add_argument('--log-level',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='日志级别')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化数据库')
    
    # import-structure 命令
    import_structure_parser = subparsers.add_parser('import-structure', help='导入报告结构')
    import_structure_parser.add_argument('--file', 
                                       help='JSON文件路径（默认: data/report_metrics_analysis.json）')
    
    # import-companies 命令
    import_companies_parser = subparsers.add_parser('import-companies', help='导入公司信息')
    import_companies_parser.add_argument('--file',
                                       help='ticker文件路径（默认: data/ticker.txt）')
    
    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='显示数据库统计信息')
    
    # query 命令
    query_parser = subparsers.add_parser('query', help='查询公司信息')
    query_parser.add_argument('--company', required=True,
                            help='公司标识（ticker或CIK）')
    
    # list-reports 命令
    list_reports_parser = subparsers.add_parser('list-reports', help='列出报告类型')
    
    # cleanup 命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理过期缓存')
    
    # query-reports 命令
    query_reports_parser = subparsers.add_parser('query-reports', help='查询报告数据')
    query_reports_parser.add_argument('--company', help='公司标识（ticker或CIK）')
    query_reports_parser.add_argument('--report-type', help='报告类型（如10-K, 10-Q）')
    query_reports_parser.add_argument('--section', help='报告部分名称')
    query_reports_parser.add_argument('--metrics', nargs='+', help='指标名称列表')
    query_reports_parser.add_argument('--years', type=int, nargs='+', help='年份列表')
    query_reports_parser.add_argument('--year-range', help='年份范围（如2020-2024）')
    query_reports_parser.add_argument('--limit', type=int, help='结果数量限制')
    query_reports_parser.add_argument('--export', help='导出文件路径')
    
    # query-company-reports 命令
    query_company_parser = subparsers.add_parser('query-company-reports', help='查询特定公司的所有报告')
    query_company_parser.add_argument('--company', required=True, help='公司标识（ticker或CIK）')
    query_company_parser.add_argument('--report-type', help='报告类型过滤')
    
    # compare-metric 命令
    compare_metric_parser = subparsers.add_parser('compare-metric', help='多公司指标对比')
    compare_metric_parser.add_argument('--metric', required=True, help='指标名称')
    compare_metric_parser.add_argument('--companies', required=True, nargs='+', help='公司列表')
    compare_metric_parser.add_argument('--years', type=int, nargs='+', help='年份列表')
    
    # analytics 命令
    analytics_parser = subparsers.add_parser('analytics', help='显示报告分析统计')
    analytics_parser.add_argument('--report-type', help='报告类型过滤')
    
    # full-import 命令
    full_import_parser = subparsers.add_parser('full-import', help='完整导入（结构+公司）')
    full_import_parser.add_argument('--structure-file',
                                   help='报告结构JSON文件')
    full_import_parser.add_argument('--companies-file',
                                   help='公司ticker文件')
    
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
        # 创建CLI实例
        cli = SECDatabaseCLI(args.db_url)
        
        # 执行命令
        success = False
        
        if args.command == 'init':
            success = cli.init_database()
        
        elif args.command == 'import-structure':
            success = cli.import_structure(getattr(args, 'file', None))
        
        elif args.command == 'import-companies':
            success = cli.import_companies(getattr(args, 'file', None))
        
        elif args.command == 'stats':
            success = cli.show_statistics()
        
        elif args.command == 'query':
            success = cli.query_company(args.company)
        
        elif args.command == 'list-reports':
            success = cli.list_report_types()
        
        elif args.command == 'cleanup':
            success = cli.cleanup_cache()
        
        elif args.command == 'query-reports':
            success = cli.query_reports(
                company=getattr(args, 'company', None),
                report_type=getattr(args, 'report_type', None),
                section=getattr(args, 'section', None),
                metrics=getattr(args, 'metrics', None),
                years=getattr(args, 'years', None),
                year_range=getattr(args, 'year_range', None),
                limit=getattr(args, 'limit', None),
                export_file=getattr(args, 'export', None)
            )
        
        elif args.command == 'query-company-reports':
            success = cli.query_company_reports(
                company_identifier=args.company,
                report_type=getattr(args, 'report_type', None)
            )
        
        elif args.command == 'compare-metric':
            success = cli.query_metric_comparison(
                metric_name=args.metric,
                companies=args.companies,
                years=getattr(args, 'years', None)
            )
        
        elif args.command == 'analytics':
            success = cli.show_report_analytics(
                report_type=getattr(args, 'report_type', None)
            )
        
        elif args.command == 'full-import':
            print("🚀 开始完整导入...")
            
            # 先初始化数据库
            if not cli.init_database():
                return 1
            
            # 导入结构
            if not cli.import_structure(getattr(args, 'structure_file', None)):
                return 1
            
            # 导入公司
            if not cli.import_companies(getattr(args, 'companies_file', None)):
                print("⚠️ 公司导入失败，但继续...")
            
            print("✅ 完整导入完成")
            success = True
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"命令执行失败: {e}")
        print(f"❌ 命令执行失败: {e}")
        return 1
    
    finally:
        if 'cli' in locals():
            cli.close()


if __name__ == "__main__":
    exit(main())