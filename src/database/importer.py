#!/usr/bin/env python3
"""
SEC报告数据导入工具

从 report_metrics_analysis.json 导入报告结构到数据库
支持报告类型、报告部分和财务指标的批量导入
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.database.manager import DatabaseManager, get_default_sqlite_manager
from src.database.models import ReportType, ReportSection, Metric, Company
from sqlalchemy.exc import IntegrityError

# 配置日志
logger = logging.getLogger(__name__)


class DataImporter:
    """数据导入器 - 从JSON文件导入报告结构"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化数据导入器
        
        Args:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
        self.stats = {
            'report_types': {'created': 0, 'updated': 0, 'skipped': 0},
            'sections': {'created': 0, 'updated': 0, 'skipped': 0},
            'metrics': {'created': 0, 'updated': 0, 'skipped': 0},
            'companies': {'created': 0, 'updated': 0, 'skipped': 0}
        }
    
    def load_report_metrics_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        加载 report_metrics_analysis.json 文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            解析后的JSON数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Successfully loaded report metrics analysis from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
    
    def import_report_structure(self, json_file_path: str) -> bool:
        """
        导入报告结构到数据库
        
        Args:
            json_file_path: report_metrics_analysis.json 文件路径
            
        Returns:
            导入是否成功
        """
        try:
            # 加载JSON数据
            data = self.load_report_metrics_analysis(json_file_path)
            
            logger.info("Starting report structure import...")
            
            with self.db_manager.get_session() as session:
                # 导入报告类型和详细结构
                self._import_report_types(session, data)
                
                # 提交事务
                session.commit()
            
            logger.info("Report structure import completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Report structure import failed: {e}")
            return False
    
    def _import_report_types(self, session, data: Dict[str, Any]):
        """导入报告类型、部分和指标"""
        
        # 从summary部分获取报告类型信息
        summary = data.get('summary', {})
        detailed_metrics = data.get('detailed_metrics', {})
        
        for report_code, summary_info in summary.items():
            logger.info(f"Processing report type: {report_code}")
            
            # 创建或更新报告类型
            report_type = self._create_or_update_report_type(
                session, report_code, summary_info
            )
            
            # 处理详细指标信息
            if report_code in detailed_metrics:
                detailed_info = detailed_metrics[report_code]
                self._import_sections_and_metrics(
                    session, report_type, detailed_info
                )
    
    def _create_or_update_report_type(self, session, report_code: str, summary_info: Dict) -> ReportType:
        """创建或更新报告类型"""
        
        # 查找现有报告类型
        report_type = session.query(ReportType).filter_by(type_code=report_code).first()
        
        if report_type:
            # 更新现有记录
            report_type.name = report_code
            report_type.description = summary_info.get('description', '')
            report_type.frequency = summary_info.get('frequency', '')
            report_type.total_metrics = summary_info.get('total_metrics', 0)
            report_type.unique_metrics = summary_info.get('unique_metrics', 0)
            report_type.updated_at = datetime.now()
            
            self.stats['report_types']['updated'] += 1
            logger.debug(f"Updated report type: {report_code}")
        else:
            # 创建新记录
            report_type = ReportType(
                type_code=report_code,
                name=report_code,
                description=summary_info.get('description', ''),
                frequency=summary_info.get('frequency', ''),
                total_metrics=summary_info.get('total_metrics', 0),
                unique_metrics=summary_info.get('unique_metrics', 0),
                is_active=True
            )
            session.add(report_type)
            session.flush()  # 获取ID
            
            self.stats['report_types']['created'] += 1
            logger.debug(f"Created report type: {report_code}")
        
        return report_type
    
    def _import_sections_and_metrics(self, session, report_type: ReportType, detailed_info: Dict):
        """导入报告部分和指标"""
        
        sections_data = detailed_info.get('sections', {})
        
        section_order = 0
        for section_name, metrics_list in sections_data.items():
            section_order += 1
            
            logger.debug(f"Processing section: {section_name} with {len(metrics_list)} metrics")
            
            # 创建或更新报告部分
            section = self._create_or_update_section(
                session, report_type, section_name, section_order, len(metrics_list)
            )
            
            # 导入该部分的指标
            self._import_metrics(session, section, metrics_list)
    
    def _create_or_update_section(self, session, report_type: ReportType, 
                                section_name: str, section_order: int, metrics_count: int) -> ReportSection:
        """创建或更新报告部分"""
        
        # 查找现有部分
        section = session.query(ReportSection).filter_by(
            report_type_id=report_type.id,
            section_name=section_name
        ).first()
        
        if section:
            # 更新现有记录
            section.section_order = section_order
            section.metrics_count = metrics_count
            section.updated_at = datetime.now()
            
            self.stats['sections']['updated'] += 1
            logger.debug(f"Updated section: {section_name}")
        else:
            # 创建新记录
            section = ReportSection(
                report_type_id=report_type.id,
                section_name=section_name,
                section_order=section_order,
                metrics_count=metrics_count,
                is_active=True
            )
            session.add(section)
            session.flush()  # 获取ID
            
            self.stats['sections']['created'] += 1
            logger.debug(f"Created section: {section_name}")
        
        return section
    
    def _import_metrics(self, session, section: ReportSection, metrics_list: List[Dict]):
        """导入指标列表"""
        
        for metric_info in metrics_list:
            if isinstance(metric_info, dict):
                metric_name = metric_info.get('metric_name', '')
                label = metric_info.get('label', '')
                role = metric_info.get('role', '')
            elif isinstance(metric_info, str):
                # 如果是字符串，直接作为metric_name
                metric_name = metric_info
                label = ''
                role = ''
            else:
                logger.warning(f"Unexpected metric format: {metric_info}")
                continue
            
            if not metric_name:
                continue
            
            # 创建或更新指标
            self._create_or_update_metric(session, section, metric_name, label, role)
    
    def _create_or_update_metric(self, session, section: ReportSection, 
                               metric_name: str, label: str, role: str) -> Metric:
        """创建或更新指标"""
        
        # 查找现有指标
        metric = session.query(Metric).filter_by(
            section_id=section.id,
            metric_name=metric_name
        ).first()
        
        if metric:
            # 更新现有记录
            metric.label = label
            metric.role = role
            metric.updated_at = datetime.now()
            
            self.stats['metrics']['updated'] += 1
            logger.debug(f"Updated metric: {metric_name}")
        else:
            # 创建新记录
            metric = Metric(
                section_id=section.id,
                metric_name=metric_name,
                label=label,
                role=role,
                data_type='monetary',  # 默认为货币类型
                unit='USD',  # 默认单位
                is_active=True
            )
            session.add(metric)
            
            self.stats['metrics']['created'] += 1
            logger.debug(f"Created metric: {metric_name}")
        
        return metric
    
    def import_ticker_companies(self, ticker_file_path: str) -> bool:
        """
        从ticker.txt文件导入公司信息
        
        Args:
            ticker_file_path: ticker.txt文件路径
            
        Returns:
            导入是否成功
        """
        try:
            logger.info(f"Starting company import from {ticker_file_path}")
            
            with self.db_manager.get_session() as session:
                with open(ticker_file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        
                        if not line or '\t' not in line:
                            continue
                        
                        parts = line.split('\t')
                        if len(parts) < 2:
                            continue
                        
                        ticker = parts[0].upper().strip()
                        cik = parts[1].strip().zfill(10)  # 确保CIK是10位
                        company_name = parts[2].strip() if len(parts) > 2 else f"{ticker} Inc."
                        
                        # 创建或更新公司
                        self._create_or_update_company(session, cik, ticker, company_name)
                        
                        # 每1000条记录提交一次
                        if line_num % 1000 == 0:
                            session.commit()
                            logger.info(f"Processed {line_num} companies...")
                
                # 最终提交
                session.commit()
            
            logger.info("Company import completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Company import failed: {e}")
            return False
    
    def _create_or_update_company(self, session, cik: str, ticker: str, name: str) -> Company:
        """创建或更新公司"""
        
        # 查找现有公司（按CIK）
        company = session.query(Company).filter_by(cik=cik).first()
        
        if company:
            # 更新现有记录
            if ticker and ticker != 'N/A':
                company.ticker = ticker
            company.name = name
            company.updated_at = datetime.now()
            
            self.stats['companies']['updated'] += 1
            logger.debug(f"Updated company: {cik} - {ticker}")
        else:
            # 创建新记录
            company = Company(
                cik=cik,
                ticker=ticker if ticker and ticker != 'N/A' else None,
                name=name,
                is_active=True
            )
            session.add(company)
            
            self.stats['companies']['created'] += 1
            logger.debug(f"Created company: {cik} - {ticker}")
        
        return company
    
    def get_import_statistics(self) -> Dict[str, Any]:
        """
        获取导入统计信息
        
        Returns:
            导入统计字典
        """
        total_created = sum(stat['created'] for stat in self.stats.values())
        total_updated = sum(stat['updated'] for stat in self.stats.values())
        total_skipped = sum(stat['skipped'] for stat in self.stats.values())
        
        return {
            'detailed_stats': self.stats,
            'summary': {
                'total_created': total_created,
                'total_updated': total_updated,
                'total_skipped': total_skipped,
                'total_processed': total_created + total_updated + total_skipped
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_statistics(self):
        """重置统计信息"""
        for table_stats in self.stats.values():
            table_stats['created'] = 0
            table_stats['updated'] = 0
            table_stats['skipped'] = 0


def import_full_structure(
    json_file_path: str,
    ticker_file_path: Optional[str] = None,
    db_manager: Optional[DatabaseManager] = None
) -> Tuple[bool, Dict[str, Any]]:
    """
    完整导入报告结构和公司信息
    
    Args:
        json_file_path: report_metrics_analysis.json 文件路径
        ticker_file_path: ticker.txt 文件路径（可选）
        db_manager: 数据库管理器（可选，默认使用SQLite）
        
    Returns:
        (成功标志, 统计信息)
    """
    # 使用提供的数据库管理器或创建默认的
    if db_manager is None:
        db_manager = get_default_sqlite_manager()
        should_close = True
    else:
        should_close = False
    
    try:
        # 创建导入器
        importer = DataImporter(db_manager)
        
        # 导入报告结构
        logger.info("Importing report structure...")
        if not importer.import_report_structure(json_file_path):
            return False, importer.get_import_statistics()
        
        # 导入公司信息（如果提供了ticker文件）
        if ticker_file_path and os.path.exists(ticker_file_path):
            logger.info("Importing company information...")
            if not importer.import_ticker_companies(ticker_file_path):
                logger.warning("Company import failed, but continuing...")
        
        # 获取统计信息
        stats = importer.get_import_statistics()
        
        logger.info("Full structure import completed successfully")
        logger.info(f"Import summary: {stats['summary']}")
        
        return True, stats
        
    except Exception as e:
        logger.error(f"Full structure import failed: {e}")
        return False, {}
        
    finally:
        if should_close:
            db_manager.close()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 文件路径
    json_file = os.path.join(os.path.dirname(__file__), '../../data/report_metrics_analysis.json')
    ticker_file = os.path.join(os.path.dirname(__file__), '../../data/ticker.txt')
    
    print("Starting data import test...")
    
    # 获取数据库管理器
    db_manager = get_default_sqlite_manager()
    
    # 确保表已创建
    if not db_manager.create_tables():
        print("❌ Failed to create tables")
        exit(1)
    
    # 执行导入
    success, stats = import_full_structure(
        json_file_path=json_file,
        ticker_file_path=ticker_file if os.path.exists(ticker_file) else None,
        db_manager=db_manager
    )
    
    if success:
        print("✅ Import completed successfully")
        print(f"Statistics: {stats}")
    else:
        print("❌ Import failed")
    
    # 获取数据库信息
    db_info = db_manager.get_database_info()
    print(f"Database info: {db_info}")
    
    db_manager.close()