#!/usr/bin/env python3
"""
SEC报告数据获取工具（数据库版）

基于数据库的SEC报告数据获取，支持：
- 数据库缓存机制，避免重复获取已有数据
- 智能的无效指标缓存
- 完整的数据管理和统计
- 支持SQLite、PostgreSQL和MySQL

使用示例:
    python sec_report_fetcher_db.py --company AAPL --report 10-K --year 2024
    python sec_report_fetcher_db.py --cik 0000320193 --report 10-K --section "Balance Sheet" --year 2020-2024
    python sec_report_fetcher_db.py --company MSFT --report 10-Q --year 2024 --section "Balance Sheet Summary"
"""

import argparse
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src import SECClient, XBRLFramesClient, DocumentRetriever
from src.database.manager import DatabaseManager, get_default_sqlite_manager
from src.database.utils import DatabaseUtils
from src.database.models import Company, ReportType, ReportSection, Metric, FinancialData, DataFetchLog
import pandas as pd

# 配置日志
logger = logging.getLogger(__name__)


class SECFetcherDB:
    """基于数据库的SEC数据获取器"""
    
    def __init__(self, db_manager: DatabaseManager, user_agent: str = "SEC Report Fetcher (please-set-your-email@example.com)"):
        """
        初始化SEC数据获取器
        
        Args:
            db_manager: 数据库管理器
            user_agent: User-Agent字符串
        """
        self.db_manager = db_manager
        self.db_utils = DatabaseUtils(db_manager)
        self.user_agent = user_agent
        
        # 初始化SEC客户端
        self.sec_client = SECClient(user_agent=user_agent)
        self.xbrl_client = XBRLFramesClient(self.sec_client)
        
        # 统计信息
        self.fetch_stats = {
            'total_metrics_requested': 0,
            'database_hits': 0,
            'cache_skips': 0,
            'api_requests': 0,
            'successful_fetches': 0,
            'new_cache_entries': 0,
            'errors': 0
        }
    
    def fetch_company_data(
        self,
        company_identifier: str,  # ticker或CIK
        report_type_code: str,
        fiscal_years: List[int],
        section_name: Optional[str] = None,
        metric_names: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        获取公司财务数据
        
        Args:
            company_identifier: 公司标识（ticker或CIK）
            report_type_code: 报告类型代码
            fiscal_years: 财政年度列表
            section_name: 报告部分名称（可选）
            metric_names: 指定的指标名称列表（可选）
            force_refresh: 是否强制刷新（忽略缓存）
            
        Returns:
            (DataFrame, 统计信息字典)
        """
        start_time = datetime.now()
        
        # 重置统计信息
        self._reset_stats()
        
        # 获取公司信息
        company = self.db_utils.get_company_by_ticker(company_identifier) or \
                 self.db_utils.get_company_by_cik(company_identifier)
        
        if not company:
            # 尝试通过SEC API获取公司信息
            logger.info(f"🔍 公司 {company_identifier} 在数据库中未找到，尝试通过SEC API获取...")
            company = self._fetch_and_save_company(company_identifier)
            if not company:
                raise ValueError(f"未找到公司: {company_identifier}")
        
        logger.info(f"🏢 公司: {company.name} (CIK: {company.cik}, Ticker: {company.ticker})")
        
        # 获取指标列表
        metrics = self._get_metrics_to_fetch(report_type_code, section_name, metric_names)
        if not metrics:
            if metric_names:
                raise ValueError(f"指定的指标 {metric_names} 无法创建")
            else:
                raise ValueError(f"未找到 {report_type_code} 报告的指标")
        
        logger.info(f"📊 报告类型: {report_type_code}")
        logger.info(f"📅 年份: {', '.join(map(str, fiscal_years))}")
        logger.info(f"📈 总计 {len(metrics)} 个指标需要处理")
        
        if section_name:
            logger.info(f"📄 报告部分: {section_name}")
        
        # 创建数据获取日志
        fetch_log = self._create_fetch_log(company, report_type_code, fiscal_years)
        
        try:
            # 收集所有数据
            all_data = []
            
            for year in fiscal_years:
                logger.info(f"\n📅 正在处理 {year} 年数据...")
                year_data = self._fetch_year_data(
                    company, report_type_code, year, metrics, force_refresh
                )
                all_data.extend(year_data)
            
            # 更新获取日志
            self._update_fetch_log(fetch_log, 'SUCCESS', start_time)
            
            # 创建DataFrame
            if all_data:
                df = pd.DataFrame(all_data)
                df = df.sort_values(['fiscal_year', 'metric_name'])
                logger.info(f"\n✅ 成功获取 {len(df)} 条记录")
            else:
                df = pd.DataFrame()
                logger.info(f"\n❌ 未获取到任何数据")
            
            return df, self.fetch_stats
            
        except Exception as e:
            # 更新获取日志为失败状态
            self._update_fetch_log(fetch_log, 'FAILED', start_time, str(e))
            raise
    
    def _fetch_and_save_company(self, company_identifier: str) -> Optional[Company]:
        """通过SEC API获取并保存公司信息"""
        try:
            # 判断是CIK还是ticker
            if company_identifier.isdigit() or len(company_identifier) == 10:
                # CIK格式
                cik = company_identifier.zfill(10)
                submissions = self.sec_client.get_company_submissions(cik)
                company_name = submissions.get('names', ['Unknown Company'])[0] if submissions.get('names') else 'Unknown Company'
                ticker = None  # 从submissions中可能可以获取ticker，这里简化处理
            else:
                # ticker格式
                company_info = self.sec_client.search_company_by_ticker(company_identifier)
                if not company_info:
                    return None
                cik = company_info['cik']
                company_name = company_info['title']
                ticker = company_identifier.upper()
            
            # 保存到数据库
            with self.db_manager.get_session() as session:
                company = Company(
                    cik=cik,
                    ticker=ticker,
                    name=company_name,
                    is_active=True
                )
                session.add(company)
                session.commit()
                session.refresh(company)
                
                logger.info(f"✅ 已保存新公司到数据库: {company_name} (CIK: {cik})")
                return company
                
        except Exception as e:
            logger.error(f"获取公司信息失败: {e}")
            return None
    
    def _get_metrics_to_fetch(
        self, 
        report_type_code: str, 
        section_name: Optional[str] = None,
        metric_names: Optional[List[str]] = None
    ) -> List[Metric]:
        """
        获取需要抓取的指标列表
        
        Args:
            report_type_code: 报告类型代码
            section_name: 报告部分名称（可选）
            metric_names: 指定的指标名称列表（可选）
            
        Returns:
            Metric对象列表
        """
        if metric_names:
            # 如果指定了具体的指标名称，创建虚拟Metric对象
            metrics = []
            for metric_name in metric_names:
                # 创建一个虚拟Metric对象用于API获取
                # 注意：这里我们不需要真实的数据库ID，只需要metric_name
                class VirtualMetric:
                    def __init__(self, name):
                        self.id = -1  # 虚拟ID
                        self.metric_name = name
                        self.section_id = -1  # 虚拟ID
                
                metrics.append(VirtualMetric(metric_name))
            return metrics
            
        elif section_name:
            # 获取指定部分的指标
            return self.db_utils.get_section_metrics(report_type_code, section_name)
        else:
            # 获取该报告类型的所有指标
            sections = self.db_utils.get_report_sections(report_type_code)
            all_metrics = []
            for section in sections:
                metrics = self.db_utils.get_section_metrics(report_type_code, section.section_name)
                all_metrics.extend(metrics)
            return all_metrics
    
    def _fetch_year_data(
        self,
        company: Company,
        report_type_code: str,
        fiscal_year: int,
        metrics: List[Metric],
        force_refresh: bool
    ) -> List[Dict]:
        """获取指定年份的数据"""
        year_data = []
        
        self.fetch_stats['total_metrics_requested'] += len(metrics)
        
        for metric in metrics:
            try:
                # 检查数据库中是否已有数据
                if not force_refresh:
                    existing_data = self._check_existing_data(company, metric, fiscal_year)
                    if existing_data:
                        # 从数据库获取
                        year_data.append(self._format_data_from_db(existing_data))
                        self.fetch_stats['database_hits'] += 1
                        logger.debug(f"  💾 从数据库获取 {metric.metric_name}")
                        continue
                    
                    # 检查无效缓存
                    if self.db_utils.is_metric_cached_invalid(
                        company.cik, report_type_code, fiscal_year, metric.metric_name
                    ):
                        logger.debug(f"  ⏩ 跳过 {metric.metric_name} (缓存中已知无效)")
                        self.fetch_stats['cache_skips'] += 1
                        continue
                
                # 从SEC API获取数据
                logger.debug(f"  🔄 从SEC API获取 {metric.metric_name}...")
                self.fetch_stats['api_requests'] += 1
                
                data = self._fetch_metric_from_api(company, metric, fiscal_year, report_type_code)
                if data:
                    # 保存到数据库
                    self._save_financial_data(data)
                    year_data.append(data)
                    self.fetch_stats['successful_fetches'] += 1
                    logger.debug(f"    ✅ {metric.metric_name}: {data.get('formatted_value', 'N/A')}")
                else:
                    # 添加到无效缓存
                    self.db_utils.add_invalid_metric_cache(
                        company.cik, report_type_code, fiscal_year, metric.metric_name, "NO_DATA"
                    )
                    self.fetch_stats['new_cache_entries'] += 1
                    logger.debug(f"    ❌ {metric.metric_name} 无数据，已加入缓存")
                    
            except Exception as e:
                logger.error(f"获取 {metric.metric_name} 时出错: {e}")
                self.fetch_stats['errors'] += 1
                
                # 如果是404错误，加入无效缓存
                if "404" in str(e) or "Not Found" in str(e):
                    self.db_utils.add_invalid_metric_cache(
                        company.cik, report_type_code, fiscal_year, metric.metric_name, "404_NOT_FOUND"
                    )
                    self.fetch_stats['new_cache_entries'] += 1
        
        return year_data
    
    def _check_existing_data(self, company: Company, metric: Metric, fiscal_year: int) -> Optional[FinancialData]:
        """检查数据库中是否已有数据"""
        # 如果是虚拟Metric对象，则不检查数据库
        if hasattr(metric, 'id') and metric.id == -1:
            return None
            
        with self.db_manager.get_session() as session:
            return session.query(FinancialData).filter_by(
                company_id=company.id,
                metric_id=metric.id,
                fiscal_year=fiscal_year
            ).first()
    
    def _fetch_metric_from_api(
        self,
        company: Company,
        metric: Metric,
        fiscal_year: int,
        report_type_code: str
    ) -> Optional[Dict]:
        """从SEC API获取指标数据（支持多种单位类型）"""
        try:
            # 获取公司特定概念的历史数据
            concept_data = self.xbrl_client.get_company_concept_data(
                cik=company.cik,
                concept=metric.metric_name
            )
            
            if not concept_data or 'units' not in concept_data:
                return None
            
            # 智能单位识别 - 参考apple_2024_10k_data.py的处理方式
            unit_key, unit_data = self._determine_best_unit(concept_data['units'], metric.metric_name)
            
            if not unit_data:
                logger.debug(f"未找到适合的单位数据，指标: {metric.metric_name}")
                return None
            
            # 查找指定年份和报告类型的数据
            for item in unit_data:
                item_year = item.get('fy', 0)
                item_form = item.get('form', '').upper()
                
                if item_year == fiscal_year and item_form == report_type_code.upper():
                    # 找到匹配的数据
                    value = item.get('val', 0)
                    
                    # 根据单位类型格式化数值
                    formatted_value = self._format_value_by_unit(value, unit_key)
                    
                    return {
                        'company_id': company.id,
                        'company_cik': company.cik,
                        'company_ticker': company.ticker,
                        'company_name': company.name,
                        'metric_id': metric.id,
                        'metric_name': metric.metric_name,
                        'section_id': metric.section_id,
                        'fiscal_year': fiscal_year,
                        'fiscal_period': item.get('fp', 'FY'),
                        'period_start_date': item.get('start', ''),
                        'period_end_date': item.get('end', ''),
                        'filed_date': item.get('filed', ''),
                        'value': value,
                        'formatted_value': formatted_value,
                        'unit': unit_key,
                        'frame': item.get('frame', ''),
                        'form_type': item.get('form', ''),
                        'accession_number': item.get('accn', ''),
                        'data_source': 'SEC_API'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"API获取失败: {e}")
            raise
    
    def _determine_best_unit(self, units_dict: Dict, metric_name: str) -> Tuple[str, List[Dict]]:
        """
        智能单位识别 - 基于apple_2024_10k_data.py的逻辑
        
        Args:
            units_dict: SEC返回的units字典
            metric_name: 指标名称
            
        Returns:
            (unit_key, unit_data): 最佳单位键和对应的数据列表
        """
        # 定义每股收益相关指标
        earnings_per_share_metrics = [
            'EarningsPerShareBasic', 'EarningsPerShareDiluted',
            'EarningsPerShareBasicAndDiluted', 'EarningsPerShare'
        ]
        
        # 定义股票数量相关指标
        shares_metrics = [
            'WeightedAverageNumberOfSharesOutstandingBasic',
            'WeightedAverageNumberOfDilutedSharesOutstanding', 
            'WeightedAverageNumberOfSharesOutstanding',
            'CommonStockSharesIssued', 'CommonStockSharesOutstanding',
            'CommonStockSharesAuthorized', 'PreferredStockSharesIssued',
            'PreferredStockSharesOutstanding', 'PreferredStockSharesAuthorized'
        ]
        
        # 1. 首先尝试根据指标名称确定期望的单位类型
        if metric_name in earnings_per_share_metrics:
            # 每股收益类指标，优先查找 USD/shares 类型
            preferred_units = ['USD/shares', 'usd/shares']
            for unit_key in preferred_units:
                if unit_key in units_dict and units_dict[unit_key]:
                    return unit_key, units_dict[unit_key]
            
            # 如果没有找到，尝试查找包含'shares'或'per'的单位
            for unit_key, unit_data in units_dict.items():
                if unit_data and ('shares' in unit_key.lower() or 'per' in unit_key.lower()):
                    return unit_key, unit_data
                    
        elif metric_name in shares_metrics:
            # 股票数量类指标，优先查找 shares 类型
            preferred_units = ['shares', 'Shares']
            for unit_key in preferred_units:
                if unit_key in units_dict and units_dict[unit_key]:
                    return unit_key, units_dict[unit_key]
            
            # 如果没有找到，尝试查找包含'shares'的单位
            for unit_key, unit_data in units_dict.items():
                if unit_data and 'shares' in unit_key.lower():
                    return unit_key, unit_data
        
        # 2. 默认查找USD单位（最常见的财务数据单位）
        if 'USD' in units_dict and units_dict['USD']:
            return 'USD', units_dict['USD']
        
        # 3. 如果没有USD，查找其他可用的单位（按优先级）
        unit_priority = ['usd', 'pure', 'shares', 'percent', 'per']
        for priority_unit in unit_priority:
            for unit_key, unit_data in units_dict.items():
                if unit_data and priority_unit in unit_key.lower():
                    return unit_key, unit_data
        
        # 4. 最后返回第一个有数据的单位
        for unit_key, unit_data in units_dict.items():
            if unit_data:
                return unit_key, unit_data
        
        # 如果所有单位都没有数据，返回空
        return '', []
    
    def _format_value_by_unit(self, value: Union[int, float, str], unit_key: str) -> str:
        """
        根据单位类型格式化数值
        
        Args:
            value: 原始数值
            unit_key: 单位键
            
        Returns:
            格式化后的字符串
        """
        if not isinstance(value, (int, float)):
            return str(value)
        
        # 每股收益和类似的USD/shares指标
        if 'usd/shares' in unit_key.lower() or '/shares' in unit_key.lower():
            return f"${value:.2f}"
        
        # 股票数量（shares）
        elif 'shares' in unit_key.lower():
            return f"{value:,.0f}"
        
        # 百分比
        elif 'percent' in unit_key.lower() or '%' in unit_key:
            return f"{value:.2%}"
        
        # Pure数值（比率等）
        elif unit_key.lower() in ['pure', 'ratio']:
            return f"{value:.4f}"
        
        # USD货币单位（默认处理）
        elif 'usd' in unit_key.lower() or unit_key == 'USD':
            if abs(value) >= 1e9:
                return f"${value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"${value/1e6:.2f}M"
            elif abs(value) >= 1e3:
                return f"${value/1e3:.2f}K"
            else:
                return f"${value:,.2f}"
        
        # 其他单位类型
        else:
            # 对于大数值，使用科学计数法或简化表示
            if abs(value) >= 1e9:
                return f"{value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"{value/1e6:.2f}M"
            elif abs(value) >= 1e3:
                return f"{value/1e3:.2f}K"
            else:
                return f"{value:,.2f}"
    
    def _save_financial_data(self, data: Dict):
        """保存财务数据到数据库"""
        try:
            # 如果是虚拟Metric对象（metric_id = -1），则不保存到数据库
            if data.get('metric_id', 0) == -1 or data.get('section_id', 0) == -1:
                logger.debug(f"跳过保存虚拟指标 {data.get('metric_name', 'Unknown')} 到数据库")
                return
            
            with self.db_manager.get_session() as session:
                # 获取报告类型
                report_type = session.query(ReportType).join(ReportSection).filter(
                    ReportSection.id == data['section_id']
                ).first()
                
                if not report_type:
                    logger.error(f"未找到对应的报告类型，section_id: {data['section_id']}")
                    return
                
                # 检查是否已存在
                existing = session.query(FinancialData).filter_by(
                    company_id=data['company_id'],
                    metric_id=data['metric_id'],
                    fiscal_year=data['fiscal_year'],
                    period_end_date=data['period_end_date']
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.value = data['value']
                    existing.formatted_value = data['formatted_value']
                    existing.updated_at = datetime.now()
                else:
                    # 创建新记录
                    financial_data = FinancialData(
                        company_id=data['company_id'],
                        report_type_id=report_type.id,
                        section_id=data['section_id'],
                        metric_id=data['metric_id'],
                        fiscal_year=data['fiscal_year'],
                        fiscal_period=data.get('fiscal_period'),
                        period_start_date=data.get('period_start_date'),
                        period_end_date=data.get('period_end_date'),
                        filed_date=data.get('filed_date'),
                        value=data['value'],
                        formatted_value=data['formatted_value'],
                        unit=data.get('unit', 'USD'),
                        frame=data.get('frame'),
                        form_type=data.get('form_type'),
                        accession_number=data.get('accession_number'),
                        data_source=data.get('data_source', 'SEC_API')
                    )
                    session.add(financial_data)
                
                session.commit()
                
        except Exception as e:
            logger.error(f"保存财务数据失败: {e}")
    
    def _format_data_from_db(self, financial_data: FinancialData) -> Dict:
        """格式化数据库中的数据为统一格式"""
        with self.db_manager.get_session() as session:
            company = session.query(Company).filter_by(id=financial_data.company_id).first()
            metric = session.query(Metric).filter_by(id=financial_data.metric_id).first()
            
            return {
                'company_id': company.id,
                'company_cik': company.cik,
                'company_ticker': company.ticker,
                'company_name': company.name,
                'metric_id': metric.id,
                'metric_name': metric.metric_name,
                'section_id': metric.section_id,
                'fiscal_year': financial_data.fiscal_year,
                'fiscal_period': financial_data.fiscal_period,
                'period_start_date': financial_data.period_start_date,
                'period_end_date': financial_data.period_end_date,
                'filed_date': financial_data.filed_date,
                'value': financial_data.value,
                'formatted_value': financial_data.formatted_value,
                'unit': financial_data.unit,
                'frame': financial_data.frame,
                'form_type': financial_data.form_type,
                'accession_number': financial_data.accession_number,
                'data_source': financial_data.data_source
            }
    
    def _create_fetch_log(self, company: Company, report_type_code: str, fiscal_years: List[int]) -> DataFetchLog:
        """创建数据获取日志"""
        with self.db_manager.get_session() as session:
            report_type = session.query(ReportType).filter_by(type_code=report_type_code).first()
            
            fetch_log = DataFetchLog(
                company_id=company.id,
                report_type_id=report_type.id if report_type else None,
                fiscal_year=fiscal_years[0] if len(fiscal_years) == 1 else None,  # 如果是多年，留空
                status='IN_PROGRESS'
            )
            session.add(fetch_log)
            session.commit()
            session.refresh(fetch_log)
            
            return fetch_log
    
    def _update_fetch_log(
        self,
        fetch_log: DataFetchLog,
        status: str,
        start_time: datetime,
        error_message: Optional[str] = None
    ):
        """更新数据获取日志"""
        try:
            with self.db_manager.get_session() as session:
                log = session.query(DataFetchLog).filter_by(id=fetch_log.id).first()
                if log:
                    log.status = status
                    log.completed_at = datetime.now()
                    log.fetch_duration_seconds = (datetime.now() - start_time).total_seconds()
                    log.total_metrics = self.fetch_stats['total_metrics_requested']
                    log.successful_metrics = self.fetch_stats['successful_fetches']
                    log.cached_skips = self.fetch_stats['cache_skips']
                    log.new_invalid_cache = self.fetch_stats['new_cache_entries']
                    log.api_requests_count = self.fetch_stats['api_requests']
                    log.error_message = error_message
                    
                    session.commit()
                    
        except Exception as e:
            logger.error(f"更新获取日志失败: {e}")
    
    def _reset_stats(self):
        """重置统计信息"""
        for key in self.fetch_stats:
            self.fetch_stats[key] = 0
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计信息"""
        total_requests = self.fetch_stats['database_hits'] + self.fetch_stats['api_requests']
        cache_efficiency = 0
        if total_requests > 0:
            cache_efficiency = (self.fetch_stats['database_hits'] + self.fetch_stats['cache_skips']) / total_requests * 100
        
        return {
            **self.fetch_stats,
            'total_requests': total_requests,
            'cache_efficiency_percentage': cache_efficiency,
            'api_success_rate': (
                self.fetch_stats['successful_fetches'] / self.fetch_stats['api_requests'] * 100
                if self.fetch_stats['api_requests'] > 0 else 0
            )
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="SEC报告数据获取工具（数据库版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python sec_report_fetcher_db.py --company AAPL --report 10-K --year 2024
  python sec_report_fetcher_db.py --cik 0000320193 --report 10-K --section "Balance Sheet" --year 2020-2024
  python sec_report_fetcher_db.py --company MSFT --report 10-Q --year 2024 --section "Balance Sheet Summary"
  python sec_report_fetcher_db.py --company AAPL --report 10-K --year 2024 --metrics EarningsPerShareBasic NetIncomeLoss
  python sec_report_fetcher_db.py --company AAPL --report 10-K --year 2024 --metrics "RevenueFromContractWithCustomerExcludingAssessedTax"
  python sec_report_fetcher_db.py --db-stats  # 显示数据库统计信息
        """
    )
    
    # 公司标识参数组
    company_group = parser.add_mutually_exclusive_group()
    company_group.add_argument('--company', '-c', 
                              help='公司股票代码 (如: AAPL, MSFT)')
    company_group.add_argument('--cik', 
                              help='公司CIK号码 (如: 0000320193)')
    
    # 查询参数
    parser.add_argument('--report', '-r', 
                       help='SEC报告类型 (如: 10-K, 10-Q)')
    
    parser.add_argument('--year', '-y', 
                       help='年份 (如: 2024 或 2020-2024)')
    
    parser.add_argument('--section', '-s',
                       help='报告部分 (如: Balance Sheet)')
    
    parser.add_argument('--metrics', '-m',
                       nargs='+',
                       help='指定具体的指标名称列表 (如: EarningsPerShareBasic NetIncomeLoss)')
    
    # 输出和行为参数
    parser.add_argument('--output', '-o',
                       help='输出文件路径 (支持 .csv, .xlsx)')
    
    parser.add_argument('--force-refresh', 
                       action='store_true',
                       help='强制刷新数据，忽略缓存')
    
    # 数据库参数
    parser.add_argument('--db-url',
                       help='数据库连接URL (默认使用SQLite)')
    
    # 统计信息参数
    parser.add_argument('--db-stats', 
                       action='store_true',
                       help='显示数据库统计信息')
    
    parser.add_argument('--cache-stats', 
                       action='store_true',
                       help='显示缓存统计信息')
    
    parser.add_argument('--user-agent',
                       default="SEC Report Fetcher (please-set-your-email@example.com)",
                       help='User-Agent字符串，建议格式："您的姓名 <your@email.com>"')
    
    # 日志级别
    parser.add_argument('--log-level',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='日志级别')
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 获取数据库管理器
        if args.db_url:
            db_manager = DatabaseManager(args.db_url)
            if not db_manager.connect():
                print("❌ 数据库连接失败")
                return 1
        else:
            db_manager = get_default_sqlite_manager()
        
        # 确保表已创建
        if not db_manager.create_tables():
            print("⚠️  创建数据库表失败")
        
        db_utils = DatabaseUtils(db_manager)
        
        # 显示统计信息
        if args.db_stats:
            stats = db_utils.get_database_statistics()
            print("📊 数据库统计信息:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            return 0
        
        if args.cache_stats:
            cache_stats = db_utils.get_cache_statistics()
            print("💾 缓存统计信息:")
            for key, value in cache_stats.items():
                print(f"  {key}: {value}")
            return 0
        
        # 验证必需参数
        if not (args.company or args.cik):
            print("❌ 请指定公司标识 (--company 或 --cik)")
            return 1
        
        if not args.report:
            print("❌ 请指定报告类型 (--report)")
            return 1
        
        if not args.year:
            print("❌ 请指定年份 (--year)")
            return 1
        
        # 解析年份
        if '-' in args.year:
            start_year, end_year = map(int, args.year.split('-'))
            years = list(range(start_year, end_year + 1))
        else:
            years = [int(args.year)]
        
        # 创建获取器
        fetcher = SECFetcherDB(db_manager, args.user_agent)
        
        # 确定公司标识
        company_id = args.cik if args.cik else args.company
        
        print(f"🚀 开始获取数据...")
        print(f"   公司: {company_id}")
        print(f"   报告类型: {args.report}")
        print(f"   年份: {', '.join(map(str, years))}")
        if args.section:
            print(f"   报告部分: {args.section}")
        if args.metrics:
            print(f"   指定指标: {', '.join(args.metrics)}")
        if args.force_refresh:
            print(f"   🔄 强制刷新模式")
        print(f"\n⚠️  提示: 为遵守SEC服务器政策，建议在美国业务时间外使用")
        
        # 获取数据
        df, stats = fetcher.fetch_company_data(
            company_identifier=company_id,
            report_type_code=args.report,
            fiscal_years=years,
            section_name=args.section,
            metric_names=args.metrics,
            force_refresh=args.force_refresh
        )
        
        # 显示结果
        if not df.empty:
            print(f"\n📊 数据预览:")
            print("=" * 100)
            
            # 显示按年份分组的数据
            for year in sorted(df['fiscal_year'].unique()):
                year_data = df[df['fiscal_year'] == year]
                print(f"\n{year}年数据 ({len(year_data)} 条记录):")
                
                # 显示前10条记录
                display_data = year_data.head(10)
                for _, row in display_data.iterrows():
                    print(f"  {row['metric_name']:40}: {row['formatted_value']:>15}")
                
                if len(year_data) > 10:
                    print(f"  ... 还有 {len(year_data) - 10} 条记录")
            
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
        else:
            print(f"\n❌ 未获取到任何数据")
        
        # 显示性能统计
        perf_stats = fetcher.get_performance_stats()
        print(f"\n📈 性能统计:")
        print(f"  数据库命中: {perf_stats['database_hits']} 次")
        print(f"  缓存跳过: {perf_stats['cache_skips']} 次")
        print(f"  API请求: {perf_stats['api_requests']} 次")
        print(f"  成功获取: {perf_stats['successful_fetches']} 次")
        print(f"  缓存效率: {perf_stats['cache_efficiency_percentage']:.1f}%")
        
        print(f"\n✅ 完成!")
        return 0
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        print(f"❌ 程序执行出错: {e}")
        return 1
    
    finally:
        if 'db_manager' in locals():
            db_manager.close()


if __name__ == "__main__":
    exit(main())