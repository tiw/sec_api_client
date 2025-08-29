#!/usr/bin/env python3
"""
SEC报告数据库工具类

提供数据库查询、统计、管理等实用功能
支持财务数据查询、缓存管理、性能统计等
"""

import os
import sys
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.database.manager import DatabaseManager
from src.database.models import (
    Company, ReportType, ReportSection, Metric, 
    FinancialData, InvalidMetricCache, DataFetchLog
)
from sqlalchemy import func, desc, asc, and_, or_
from sqlalchemy.orm import joinedload

# 配置日志
logger = logging.getLogger(__name__)


class DatabaseUtils:
    """数据库工具类"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化数据库工具
        
        Args:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
    
    # ==================== 公司相关查询 ====================
    
    def get_company_by_ticker(self, ticker: str) -> Optional[Company]:
        """
        根据股票代码获取公司信息
        
        Args:
            ticker: 股票代码
            
        Returns:
            公司对象或None
        """
        with self.db_manager.get_session() as session:
            return session.query(Company).filter_by(ticker=ticker.upper()).first()
    
    def get_company_by_cik(self, cik: str) -> Optional[Company]:
        """
        根据CIK获取公司信息
        
        Args:
            cik: CIK号码
            
        Returns:
            公司对象或None
        """
        cik_formatted = cik.zfill(10)  # 确保10位格式
        with self.db_manager.get_session() as session:
            return session.query(Company).filter_by(cik=cik_formatted).first()
    
    def search_companies(self, keyword: str, limit: int = 20) -> List[Company]:
        """
        搜索公司（按名称或ticker）
        
        Args:
            keyword: 搜索关键词
            limit: 结果限制
            
        Returns:
            公司列表
        """
        with self.db_manager.get_session() as session:
            keyword = f"%{keyword}%"
            return session.query(Company).filter(
                or_(
                    Company.name.ilike(keyword),
                    Company.ticker.ilike(keyword)
                )
            ).limit(limit).all()
    
    # ==================== 报告结构查询 ====================
    
    def get_report_types(self, active_only: bool = True) -> List[ReportType]:
        """
        获取所有报告类型
        
        Args:
            active_only: 是否只返回活跃的报告类型
            
        Returns:
            报告类型列表
        """
        with self.db_manager.get_session() as session:
            query = session.query(ReportType)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.order_by(ReportType.type_code).all()
    
    def get_report_sections(self, report_type_code: str) -> List[ReportSection]:
        """
        获取指定报告类型的所有部分
        
        Args:
            report_type_code: 报告类型代码
            
        Returns:
            报告部分列表
        """
        with self.db_manager.get_session() as session:
            return session.query(ReportSection)\
                .join(ReportType)\
                .filter(ReportType.type_code == report_type_code)\
                .filter(ReportSection.is_active == True)\
                .order_by(ReportSection.section_order, ReportSection.section_name)\
                .all()
    
    def get_section_metrics(self, report_type_code: str, section_name: str) -> List[Metric]:
        """
        获取指定报告部分的所有指标
        
        Args:
            report_type_code: 报告类型代码
            section_name: 报告部分名称
            
        Returns:
            指标列表
        """
        with self.db_manager.get_session() as session:
            return session.query(Metric)\
                .join(ReportSection)\
                .join(ReportType)\
                .filter(ReportType.type_code == report_type_code)\
                .filter(ReportSection.section_name == section_name)\
                .filter(Metric.is_active == True)\
                .order_by(Metric.metric_name)\
                .all()
    
    def get_metric_by_name(self, metric_name: str, report_type_code: Optional[str] = None) -> List[Metric]:
        """
        根据指标名称查找指标
        
        Args:
            metric_name: 指标名称
            report_type_code: 可选的报告类型过滤
            
        Returns:
            指标列表（可能在不同报告类型中存在）
        """
        with self.db_manager.get_session() as session:
            query = session.query(Metric)\
                .join(ReportSection)\
                .join(ReportType)\
                .filter(Metric.metric_name == metric_name)
            
            if report_type_code:
                query = query.filter(ReportType.type_code == report_type_code)
            
            return query.all()
    
    # ==================== 财务数据查询 ====================
    
    def get_financial_data(
        self,
        company_identifier: str,  # ticker或CIK
        report_type_code: str,
        fiscal_year: Optional[int] = None,
        metric_names: Optional[List[str]] = None,
        section_name: Optional[str] = None
    ) -> List[FinancialData]:
        """
        获取财务数据
        
        Args:
            company_identifier: 公司标识（ticker或CIK）
            report_type_code: 报告类型代码
            fiscal_year: 财政年度（可选）
            metric_names: 指标名称列表（可选）
            section_name: 报告部分名称（可选）
            
        Returns:
            财务数据列表
        """
        # 获取公司
        company = self._get_company_by_identifier(company_identifier)
        if not company:
            return []
        
        with self.db_manager.get_session() as session:
            query = session.query(FinancialData)\
                .join(Company)\
                .join(ReportType)\
                .join(Metric)\
                .filter(Company.id == company.id)\
                .filter(ReportType.type_code == report_type_code)
            
            if fiscal_year:
                query = query.filter(FinancialData.fiscal_year == fiscal_year)
            
            if metric_names:
                query = query.filter(Metric.metric_name.in_(metric_names))
            
            if section_name:
                query = query.join(ReportSection)\
                    .filter(ReportSection.section_name == section_name)
            
            return query.order_by(
                FinancialData.fiscal_year.desc(),
                Metric.metric_name
            ).all()
    
    def get_company_financial_summary(
        self,
        company_identifier: str,
        years: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        获取公司财务数据概览
        
        Args:
            company_identifier: 公司标识
            years: 年份列表（可选）
            
        Returns:
            财务数据概览
        """
        company = self._get_company_by_identifier(company_identifier)
        if not company:
            return {}
        
        with self.db_manager.get_session() as session:
            query = session.query(FinancialData)\
                .filter_by(company_id=company.id)
            
            if years:
                query = query.filter(FinancialData.fiscal_year.in_(years))
            
            financial_data = query.all()
            
            # 按年份和报告类型组织数据
            summary = {
                'company': {
                    'cik': company.cik,
                    'ticker': company.ticker,
                    'name': company.name
                },
                'data_by_year': {},
                'available_years': [],
                'available_report_types': set(),
                'total_records': len(financial_data)
            }
            
            for data in financial_data:
                year = data.fiscal_year
                if year not in summary['data_by_year']:
                    summary['data_by_year'][year] = {}
                    summary['available_years'].append(year)
                
                # 获取报告类型
                report_type = session.query(ReportType).filter_by(id=data.report_type_id).first()
                report_code = report_type.type_code if report_type else 'Unknown'
                summary['available_report_types'].add(report_code)
                
                if report_code not in summary['data_by_year'][year]:
                    summary['data_by_year'][year][report_code] = []
                
                # 获取指标信息
                metric = session.query(Metric).filter_by(id=data.metric_id).first()
                
                summary['data_by_year'][year][report_code].append({
                    'metric_name': metric.metric_name if metric else 'Unknown',
                    'value': data.value,
                    'formatted_value': data.formatted_value,
                    'period_end_date': data.period_end_date
                })
            
            summary['available_years'].sort(reverse=True)
            summary['available_report_types'] = list(summary['available_report_types'])
            
            return summary
    
    # ==================== 报告查询功能 ====================
    
    def query_reports(
        self,
        company_identifier: Optional[str] = None,
        report_type_code: Optional[str] = None,
        section_name: Optional[str] = None,
        metric_names: Optional[List[str]] = None,
        fiscal_years: Optional[List[int]] = None,
        fiscal_year_range: Optional[Tuple[int, int]] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        sort_by: str = 'fiscal_year',
        sort_order: str = 'desc',
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        通用报告查询功能
        
        Args:
            company_identifier: 公司标识（ticker或CIK，可选）
            report_type_code: 报告类型代码（可选）
            section_name: 报告部分名称（可选）
            metric_names: 指标名称列表（可选）
            fiscal_years: 财政年度列表（可选）
            fiscal_year_range: 财政年度范围 (start_year, end_year)（可选）
            min_value: 最小值过滤（可选）
            max_value: 最大值过滤（可选）
            sort_by: 排序字段 ('fiscal_year', 'value', 'metric_name', 'company_name')
            sort_order: 排序顺序 ('asc', 'desc')
            limit: 结果数量限制（可选）
            
        Returns:
            查询结果列表
        """
        with self.db_manager.get_session() as session:
            # 构建查询
            query = session.query(FinancialData)\
                .join(Company, FinancialData.company_id == Company.id)\
                .join(ReportType, FinancialData.report_type_id == ReportType.id)\
                .join(ReportSection, FinancialData.section_id == ReportSection.id)\
                .join(Metric, FinancialData.metric_id == Metric.id)
            
            # 应用过滤条件
            if company_identifier:
                company = self._get_company_by_identifier(company_identifier)
                if company:
                    query = query.filter(Company.id == company.id)
                else:
                    return []  # 公司不存在
            
            if report_type_code:
                query = query.filter(ReportType.type_code == report_type_code)
            
            if section_name:
                query = query.filter(ReportSection.section_name == section_name)
            
            if metric_names:
                query = query.filter(Metric.metric_name.in_(metric_names))
            
            if fiscal_years:
                query = query.filter(FinancialData.fiscal_year.in_(fiscal_years))
            
            if fiscal_year_range:
                start_year, end_year = fiscal_year_range
                query = query.filter(
                    and_(
                        FinancialData.fiscal_year >= start_year,
                        FinancialData.fiscal_year <= end_year
                    )
                )
            
            if min_value is not None:
                query = query.filter(FinancialData.value >= min_value)
            
            if max_value is not None:
                query = query.filter(FinancialData.value <= max_value)
            
            # 应用排序
            if sort_by == 'fiscal_year':
                sort_column = FinancialData.fiscal_year
            elif sort_by == 'value':
                sort_column = FinancialData.value
            elif sort_by == 'metric_name':
                sort_column = Metric.metric_name
            elif sort_by == 'company_name':
                sort_column = Company.name
            else:
                sort_column = FinancialData.fiscal_year
            
            if sort_order.lower() == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # 应用限制
            if limit:
                query = query.limit(limit)
            
            # 执行查询并格式化结果
            results = query.all()
            formatted_results = []
            
            for data in results:
                company = session.query(Company).filter_by(id=data.company_id).first()
                report_type = session.query(ReportType).filter_by(id=data.report_type_id).first()
                section = session.query(ReportSection).filter_by(id=data.section_id).first()
                metric = session.query(Metric).filter_by(id=data.metric_id).first()
                
                formatted_results.append({
                    'company_name': company.name,
                    'company_ticker': company.ticker,
                    'company_cik': company.cik,
                    'report_type': report_type.type_code,
                    'section_name': section.section_name,
                    'metric_name': metric.metric_name,
                    'metric_label': metric.label,
                    'fiscal_year': data.fiscal_year,
                    'fiscal_period': data.fiscal_period,
                    'value': data.value,
                    'formatted_value': data.formatted_value,
                    'unit': data.unit,
                    'period_start_date': data.period_start_date,
                    'period_end_date': data.period_end_date,
                    'filed_date': data.filed_date,
                    'data_source': data.data_source,
                    'created_at': data.created_at
                })
            
            return formatted_results
    
    def query_reports_by_company(
        self,
        company_identifier: str,
        report_type_code: Optional[str] = None,
        fiscal_years: Optional[List[int]] = None,
        sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        查询特定公司的报告数据
        
        Args:
            company_identifier: 公司标识
            report_type_code: 报告类型（可选）
            fiscal_years: 年份列表（可选）
            sections: 报告部分列表（可选）
            
        Returns:
            公司报告数据字典
        """
        company = self._get_company_by_identifier(company_identifier)
        if not company:
            return {}
        
        with self.db_manager.get_session() as session:
            query = session.query(FinancialData).filter_by(company_id=company.id)
            
            if report_type_code:
                report_type = session.query(ReportType).filter_by(type_code=report_type_code).first()
                if report_type:
                    query = query.filter_by(report_type_id=report_type.id)
            
            if fiscal_years:
                query = query.filter(FinancialData.fiscal_year.in_(fiscal_years))
            
            if sections:
                section_ids = session.query(ReportSection.id)\
                    .filter(ReportSection.section_name.in_(sections)).all()
                section_ids = [s.id for s in section_ids]
                if section_ids:
                    query = query.filter(FinancialData.section_id.in_(section_ids))
            
            results = query.order_by(
                FinancialData.fiscal_year.desc(),
                FinancialData.section_id,
                FinancialData.metric_id
            ).all()
            
            # 组织数据
            organized_data = {
                'company': {
                    'name': company.name,
                    'ticker': company.ticker,
                    'cik': company.cik
                },
                'total_records': len(results),
                'data_by_year': {},
                'available_years': set(),
                'available_report_types': set(),
                'available_sections': set()
            }
            
            for data in results:
                year = data.fiscal_year
                organized_data['available_years'].add(year)
                
                # 获取相关信息
                report_type = session.query(ReportType).filter_by(id=data.report_type_id).first()
                section = session.query(ReportSection).filter_by(id=data.section_id).first()
                metric = session.query(Metric).filter_by(id=data.metric_id).first()
                
                report_code = report_type.type_code if report_type else 'Unknown'
                section_name = section.section_name if section else 'Unknown'
                
                organized_data['available_report_types'].add(report_code)
                organized_data['available_sections'].add(section_name)
                
                if year not in organized_data['data_by_year']:
                    organized_data['data_by_year'][year] = {}
                
                if report_code not in organized_data['data_by_year'][year]:
                    organized_data['data_by_year'][year][report_code] = {}
                
                if section_name not in organized_data['data_by_year'][year][report_code]:
                    organized_data['data_by_year'][year][report_code][section_name] = []
                
                organized_data['data_by_year'][year][report_code][section_name].append({
                    'metric_name': metric.metric_name if metric else 'Unknown',
                    'metric_label': metric.label if metric else '',
                    'value': data.value,
                    'formatted_value': data.formatted_value,
                    'unit': data.unit,
                    'period_start_date': data.period_start_date,
                    'period_end_date': data.period_end_date,
                    'filed_date': data.filed_date
                })
            
            # 转换集合为排序后的列表
            organized_data['available_years'] = sorted(list(organized_data['available_years']), reverse=True)
            organized_data['available_report_types'] = sorted(list(organized_data['available_report_types']))
            organized_data['available_sections'] = sorted(list(organized_data['available_sections']))
            
            return organized_data
    
    def query_reports_by_metric(
        self,
        metric_name: str,
        report_type_code: Optional[str] = None,
        companies: Optional[List[str]] = None,
        fiscal_years: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        查询特定指标的跨公司数据
        
        Args:
            metric_name: 指标名称
            report_type_code: 报告类型（可选）
            companies: 公司列表（可选）
            fiscal_years: 年份列表（可选）
            
        Returns:
            指标数据列表
        """
        with self.db_manager.get_session() as session:
            query = session.query(FinancialData)\
                .join(Metric, FinancialData.metric_id == Metric.id)\
                .join(Company, FinancialData.company_id == Company.id)\
                .filter(Metric.metric_name == metric_name)
            
            if report_type_code:
                query = query.join(ReportType, FinancialData.report_type_id == ReportType.id)\
                    .filter(ReportType.type_code == report_type_code)
            
            if companies:
                # 支持ticker或CIK列表
                company_ids = []
                for company_id in companies:
                    company = self._get_company_by_identifier(company_id)
                    if company:
                        company_ids.append(company.id)
                
                if company_ids:
                    query = query.filter(Company.id.in_(company_ids))
                else:
                    return []  # 没有找到任何公司
            
            if fiscal_years:
                query = query.filter(FinancialData.fiscal_year.in_(fiscal_years))
            
            results = query.order_by(
                Company.name,
                FinancialData.fiscal_year.desc()
            ).all()
            
            formatted_results = []
            for data in results:
                company = session.query(Company).filter_by(id=data.company_id).first()
                report_type = session.query(ReportType).filter_by(id=data.report_type_id).first()
                
                formatted_results.append({
                    'company_name': company.name,
                    'company_ticker': company.ticker,
                    'company_cik': company.cik,
                    'report_type': report_type.type_code if report_type else 'Unknown',
                    'metric_name': metric_name,
                    'fiscal_year': data.fiscal_year,
                    'value': data.value,
                    'formatted_value': data.formatted_value,
                    'unit': data.unit,
                    'period_end_date': data.period_end_date,
                    'filed_date': data.filed_date
                })
            
            return formatted_results
    
    def query_reports_comparison(
        self,
        companies: List[str],
        metric_names: List[str],
        fiscal_years: Optional[List[int]] = None,
        report_type_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        多公司指标对比查询
        
        Args:
            companies: 公司列表
            metric_names: 指标名称列表
            fiscal_years: 年份列表（可选）
            report_type_code: 报告类型（可选）
            
        Returns:
            对比数据字典
        """
        with self.db_manager.get_session() as session:
            # 获取公司ID映射
            company_map = {}
            for company_id in companies:
                company = self._get_company_by_identifier(company_id)
                if company:
                    company_map[company.id] = {
                        'name': company.name,
                        'ticker': company.ticker,
                        'cik': company.cik
                    }
            
            if not company_map:
                return {}
            
            query = session.query(FinancialData)\
                .join(Metric, FinancialData.metric_id == Metric.id)\
                .join(Company, FinancialData.company_id == Company.id)\
                .filter(Company.id.in_(company_map.keys()))\
                .filter(Metric.metric_name.in_(metric_names))
            
            if report_type_code:
                query = query.join(ReportType, FinancialData.report_type_id == ReportType.id)\
                    .filter(ReportType.type_code == report_type_code)
            
            if fiscal_years:
                query = query.filter(FinancialData.fiscal_year.in_(fiscal_years))
            
            results = query.order_by(
                Company.name,
                Metric.metric_name,
                FinancialData.fiscal_year.desc()
            ).all()
            
            # 组织对比数据
            comparison_data = {
                'companies': list(company_map.values()),
                'metrics': metric_names,
                'data': {},
                'summary': {}
            }
            
            for data in results:
                company = session.query(Company).filter_by(id=data.company_id).first()
                metric = session.query(Metric).filter_by(id=data.metric_id).first()
                
                company_name = company.name
                metric_name = metric.metric_name
                year = data.fiscal_year
                
                if metric_name not in comparison_data['data']:
                    comparison_data['data'][metric_name] = {}
                
                if year not in comparison_data['data'][metric_name]:
                    comparison_data['data'][metric_name][year] = {}
                
                comparison_data['data'][metric_name][year][company_name] = {
                    'value': data.value,
                    'formatted_value': data.formatted_value,
                    'unit': data.unit
                }
            
            return comparison_data
    
    def get_report_analytics(self, report_type_code: Optional[str] = None) -> Dict[str, Any]:
        """
        获取报告分析统计
        
        Args:
            report_type_code: 报告类型（可选）
            
        Returns:
            分析统计字典
        """
        with self.db_manager.get_session() as session:
            query = session.query(FinancialData)
            
            if report_type_code:
                query = query.join(ReportType, FinancialData.report_type_id == ReportType.id)\
                    .filter(ReportType.type_code == report_type_code)
            
            total_records = query.count()
            
            # 按年份统计
            year_stats = session.query(
                FinancialData.fiscal_year,
                func.count(FinancialData.id).label('count')
            )
            
            if report_type_code:
                year_stats = year_stats.join(ReportType, FinancialData.report_type_id == ReportType.id)\
                    .filter(ReportType.type_code == report_type_code)
            
            year_stats = year_stats.group_by(FinancialData.fiscal_year)\
                .order_by(FinancialData.fiscal_year.desc()).all()
            
            # 按公司统计
            company_stats = session.query(
                Company.name,
                Company.ticker,
                func.count(FinancialData.id).label('count')
            ).join(FinancialData, Company.id == FinancialData.company_id)
            
            if report_type_code:
                company_stats = company_stats.join(ReportType, FinancialData.report_type_id == ReportType.id)\
                    .filter(ReportType.type_code == report_type_code)
            
            company_stats = company_stats.group_by(Company.id)\
                .order_by(desc('count')).limit(10).all()
            
            # 最新数据日期
            latest_data = query.order_by(FinancialData.created_at.desc()).first()
            latest_date = latest_data.created_at if latest_data else None
            
            return {
                'total_records': total_records,
                'report_type': report_type_code or 'All',
                'data_by_year': [
                    {'year': stat.fiscal_year, 'count': stat.count}
                    for stat in year_stats
                ],
                'top_companies_by_data': [
                    {
                        'name': stat.name,
                        'ticker': stat.ticker,
                        'record_count': stat.count
                    }
                    for stat in company_stats
                ],
                'latest_data_date': latest_date,
                'year_range': {
                    'min_year': year_stats[-1].fiscal_year if year_stats else None,
                    'max_year': year_stats[0].fiscal_year if year_stats else None
                }
            }
    
    def is_metric_cached_invalid(
        self,
        company_identifier: str,
        report_type_code: str,
        fiscal_year: int,
        metric_name: str
    ) -> bool:
        """
        检查指标是否在无效缓存中
        
        Args:
            company_identifier: 公司标识
            report_type_code: 报告类型代码
            fiscal_year: 财政年度
            metric_name: 指标名称
            
        Returns:
            是否在无效缓存中
        """
        company = self._get_company_by_identifier(company_identifier)
        if not company:
            return False
        
        with self.db_manager.get_session() as session:
            cache_entry = session.query(InvalidMetricCache)\
                .join(ReportType, InvalidMetricCache.report_type_id == ReportType.id)\
                .join(Metric, InvalidMetricCache.metric_id == Metric.id)\
                .filter(InvalidMetricCache.company_id == company.id)\
                .filter(ReportType.type_code == report_type_code)\
                .filter(InvalidMetricCache.fiscal_year == fiscal_year)\
                .filter(Metric.metric_name == metric_name)\
                .first()
            
            if cache_entry and not cache_entry.is_expired():
                return True
            elif cache_entry and cache_entry.is_expired():
                # 删除过期缓存
                session.delete(cache_entry)
                session.commit()
            
            return False
    
    def add_invalid_metric_cache(
        self,
        company_identifier: str,
        report_type_code: str,
        fiscal_year: int,
        metric_name: str,
        reason: str = "NOT_FOUND"
    ) -> bool:
        """
        添加无效指标到缓存
        
        Args:
            company_identifier: 公司标识
            report_type_code: 报告类型代码
            fiscal_year: 财政年度
            metric_name: 指标名称
            reason: 无效原因
            
        Returns:
            是否添加成功
        """
        try:
            company = self._get_company_by_identifier(company_identifier)
            if not company:
                return False
            
            with self.db_manager.get_session() as session:
                # 获取报告类型和指标
                report_type = session.query(ReportType).filter_by(type_code=report_type_code).first()
                metric = session.query(Metric).filter_by(metric_name=metric_name).first()
                
                if not report_type or not metric:
                    return False
                
                # 检查是否已存在
                existing = session.query(InvalidMetricCache).filter_by(
                    company_id=company.id,
                    report_type_id=report_type.id,
                    metric_id=metric.id,
                    fiscal_year=fiscal_year
                ).first()
                
                if existing:
                    # 更新现有记录
                    existing.reason = reason
                    existing.cached_at = datetime.now()
                else:
                    # 创建新记录
                    cache_entry = InvalidMetricCache(
                        company_id=company.id,
                        report_type_id=report_type.id,
                        metric_id=metric.id,
                        fiscal_year=fiscal_year,
                        reason=reason
                    )
                    session.add(cache_entry)
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to add invalid metric cache: {e}")
            return False
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计字典
        """
        with self.db_manager.get_session() as session:
            # 总缓存数
            total_cache = session.query(InvalidMetricCache).count()
            
            # 过期缓存数
            expired_count = 0
            all_cache = session.query(InvalidMetricCache).all()
            for cache in all_cache:
                if cache.is_expired():
                    expired_count += 1
            
            # 按公司统计
            company_stats = session.query(
                Company.ticker,
                Company.name,
                func.count(InvalidMetricCache.id).label('cache_count')
            ).join(InvalidMetricCache)\
            .group_by(Company.id)\
            .order_by(desc('cache_count'))\
            .limit(10).all()
            
            # 按报告类型统计
            report_stats = session.query(
                ReportType.type_code,
                func.count(InvalidMetricCache.id).label('cache_count')
            ).join(InvalidMetricCache)\
            .group_by(ReportType.id)\
            .order_by(desc('cache_count')).all()
            
            return {
                'total_cache_entries': total_cache,
                'expired_entries': expired_count,
                'active_entries': total_cache - expired_count,
                'top_companies_by_cache': [
                    {
                        'ticker': stat.ticker,
                        'name': stat.name,
                        'cache_count': stat.cache_count
                    }
                    for stat in company_stats
                ],
                'cache_by_report_type': [
                    {
                        'report_type': stat.type_code,
                        'cache_count': stat.cache_count
                    }
                    for stat in report_stats
                ]
            }
    
    def cleanup_expired_cache(self) -> int:
        """
        清理过期缓存
        
        Returns:
            清理的记录数
        """
        with self.db_manager.get_session() as session:
            expired_cache = []
            all_cache = session.query(InvalidMetricCache).all()
            
            for cache in all_cache:
                if cache.is_expired():
                    expired_cache.append(cache)
            
            count = len(expired_cache)
            for cache in expired_cache:
                session.delete(cache)
            
            session.commit()
            logger.info(f"Cleaned up {count} expired cache entries")
            return count
    
    # ==================== 数据统计 ====================
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            数据库统计字典
        """
        with self.db_manager.get_session() as session:
            stats = {}
            
            # 基本表统计
            stats['companies'] = session.query(Company).count()
            stats['report_types'] = session.query(ReportType).count()
            stats['report_sections'] = session.query(ReportSection).count()
            stats['metrics'] = session.query(Metric).count()
            stats['financial_data_records'] = session.query(FinancialData).count()
            stats['invalid_cache_entries'] = session.query(InvalidMetricCache).count()
            stats['fetch_logs'] = session.query(DataFetchLog).count()
            
            # 数据覆盖统计
            companies_with_data = session.query(FinancialData.company_id).distinct().count()
            stats['companies_with_data'] = companies_with_data
            stats['data_coverage_percentage'] = (
                (companies_with_data / stats['companies'] * 100) 
                if stats['companies'] > 0 else 0
            )
            
            # 年份覆盖
            year_range = session.query(
                func.min(FinancialData.fiscal_year).label('min_year'),
                func.max(FinancialData.fiscal_year).label('max_year')
            ).first()
            
            stats['year_range'] = {
                'min_year': year_range.min_year,
                'max_year': year_range.max_year
            } if year_range.min_year else None
            
            return stats
    
    def get_data_fetch_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        获取数据获取摘要
        
        Args:
            days: 查看最近多少天的数据
            
        Returns:
            数据获取摘要
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.db_manager.get_session() as session:
            logs = session.query(DataFetchLog)\
                .filter(DataFetchLog.started_at >= cutoff_date)\
                .all()
            
            if not logs:
                return {'message': f'No fetch logs in the last {days} days'}
            
            total_logs = len(logs)
            successful_logs = len([log for log in logs if log.status == 'SUCCESS'])
            total_api_requests = sum(log.api_requests_count or 0 for log in logs)
            total_metrics_fetched = sum(log.successful_metrics or 0 for log in logs)
            total_cache_skips = sum(log.cached_skips or 0 for log in logs)
            
            return {
                'period_days': days,
                'total_fetch_attempts': total_logs,
                'successful_fetches': successful_logs,
                'success_rate': (successful_logs / total_logs * 100) if total_logs > 0 else 0,
                'total_api_requests': total_api_requests,
                'total_metrics_fetched': total_metrics_fetched,
                'total_cache_skips': total_cache_skips,
                'cache_efficiency': (
                    (total_cache_skips / (total_cache_skips + total_api_requests) * 100)
                    if (total_cache_skips + total_api_requests) > 0 else 0
                )
            }
    
    # ==================== 辅助方法 ====================
    
    def _get_company_by_identifier(self, identifier: str) -> Optional[Company]:
        """
        根据标识符（ticker或CIK）获取公司
        
        Args:
            identifier: 公司标识符
            
        Returns:
            公司对象或None
        """
        # 判断是CIK还是ticker
        if identifier.isdigit() or len(identifier) == 10:
            return self.get_company_by_cik(identifier)
        else:
            return self.get_company_by_ticker(identifier)
    
    def save_financial_data(self, financial_data_list: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        批量保存财务数据
        
        Args:
            financial_data_list: 财务数据字典列表
            
        Returns:
            (成功保存的记录数, 跳过的记录数)
        """
        saved_count = 0
        skipped_count = 0
        
        try:
            with self.db_manager.get_session() as session:
                for data_dict in financial_data_list:
                    # 获取相关对象的ID
                    company = self._get_company_by_identifier(data_dict.get('company_identifier', ''))
                    if not company:
                        skipped_count += 1
                        continue
                    
                    report_type = session.query(ReportType).filter_by(
                        type_code=data_dict.get('report_type_code', '')
                    ).first()
                    if not report_type:
                        skipped_count += 1
                        continue
                    
                    metric = session.query(Metric).filter_by(
                        metric_name=data_dict.get('metric_name', '')
                    ).first()
                    if not metric:
                        skipped_count += 1
                        continue
                    
                    section = session.query(ReportSection).filter_by(id=metric.section_id).first()
                    if not section:
                        skipped_count += 1
                        continue
                    
                    # 检查是否已存在
                    existing = session.query(FinancialData).filter_by(
                        company_id=company.id,
                        metric_id=metric.id,
                        fiscal_year=data_dict.get('fiscal_year'),
                        period_end_date=data_dict.get('period_end_date')
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.value = data_dict.get('value')
                        existing.formatted_value = data_dict.get('formatted_value')
                        existing.unit = data_dict.get('unit', 'USD')
                        existing.updated_at = datetime.now()
                    else:
                        # 创建新记录
                        financial_data = FinancialData(
                            company_id=company.id,
                            report_type_id=report_type.id,
                            section_id=section.id,
                            metric_id=metric.id,
                            fiscal_year=data_dict.get('fiscal_year'),
                            fiscal_period=data_dict.get('fiscal_period'),
                            period_start_date=data_dict.get('period_start_date'),
                            period_end_date=data_dict.get('period_end_date'),
                            filed_date=data_dict.get('filed_date'),
                            value=data_dict.get('value'),
                            formatted_value=data_dict.get('formatted_value'),
                            unit=data_dict.get('unit', 'USD'),
                            frame=data_dict.get('frame'),
                            form_type=data_dict.get('form_type'),
                            accession_number=data_dict.get('accession_number'),
                            data_source=data_dict.get('data_source', 'SEC_API')
                        )
                        session.add(financial_data)
                    
                    saved_count += 1
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Failed to save financial data: {e}")
            
        return saved_count, skipped_count


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    from src.database.manager import get_default_sqlite_manager
    
    print("Testing DatabaseUtils...")
    
    # 获取数据库管理器
    db_manager = get_default_sqlite_manager()
    
    # 创建工具实例
    utils = DatabaseUtils(db_manager)
    
    # 测试统计功能
    stats = utils.get_database_statistics()
    print(f"Database statistics: {stats}")
    
    # 测试缓存统计
    cache_stats = utils.get_cache_statistics()
    print(f"Cache statistics: {cache_stats}")
    
    db_manager.close()
    print("✅ Test completed")