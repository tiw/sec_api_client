#!/usr/bin/env python3
"""
SEC报告数据库模型定义

基于 report_metrics_analysis.json 的结构设计，支持：
- 公司信息管理
- 报告类型和部分结构
- 财务指标定义
- 实际财务数据存储
- 缓存机制和数据完整性

支持SQLite、PostgreSQL和MySQL
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()


class Company(Base):
    """公司信息表"""
    __tablename__ = 'companies'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 公司标识
    cik = Column(String(10), unique=True, nullable=False, index=True, comment='SEC CIK号码，10位数字')
    ticker = Column(String(10), nullable=True, index=True, comment='股票代码')
    
    # 公司信息
    name = Column(String(500), nullable=False, comment='公司名称')
    industry = Column(String(100), nullable=True, comment='行业分类')
    sector = Column(String(100), nullable=True, comment='行业板块')
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment='是否活跃公司')
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关系
    financial_data = relationship("FinancialData", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(cik='{self.cik}', ticker='{self.ticker}', name='{self.name}')>"


class ReportType(Base):
    """报告类型表（如10-K、10-Q等）"""
    __tablename__ = 'report_types'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 报告类型信息
    type_code = Column(String(20), unique=True, nullable=False, index=True, comment='报告类型代码，如10-K')
    name = Column(String(100), nullable=False, comment='报告类型名称')
    description = Column(Text, nullable=True, comment='报告类型描述')
    frequency = Column(String(20), nullable=True, comment='报告频率：Annual, Quarterly, Event-based等')
    
    # 统计信息
    total_metrics = Column(Integer, default=0, comment='该报告类型包含的指标总数')
    unique_metrics = Column(Integer, default=0, comment='该报告类型的唯一指标数')
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment='是否活跃的报告类型')
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关系
    sections = relationship("ReportSection", back_populates="report_type", cascade="all, delete-orphan")
    financial_data = relationship("FinancialData", back_populates="report_type")
    
    def __repr__(self):
        return f"<ReportType(code='{self.type_code}', name='{self.name}')>"


class ReportSection(Base):
    """报告部分表（如资产负债表、损益表等）"""
    __tablename__ = 'report_sections'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 外键
    report_type_id = Column(Integer, ForeignKey('report_types.id', ondelete='CASCADE'), nullable=False)
    
    # 部分信息
    section_name = Column(String(200), nullable=False, comment='报告部分名称')
    section_order = Column(Integer, default=0, comment='部分在报告中的顺序')
    
    # 统计信息
    metrics_count = Column(Integer, default=0, comment='该部分包含的指标数量')
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment='是否活跃的报告部分')
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关系
    report_type = relationship("ReportType", back_populates="sections")
    metrics = relationship("Metric", back_populates="section", cascade="all, delete-orphan")
    financial_data = relationship("FinancialData", back_populates="section")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('report_type_id', 'section_name', name='uq_report_section'),
        Index('idx_report_section_name', 'section_name'),
    )
    
    def __repr__(self):
        return f"<ReportSection(section='{self.section_name}', report_type_id={self.report_type_id})>"


class Metric(Base):
    """财务指标表"""
    __tablename__ = 'metrics'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 外键
    section_id = Column(Integer, ForeignKey('report_sections.id', ondelete='CASCADE'), nullable=False)
    
    # 指标信息
    metric_name = Column(String(500), nullable=False, index=True, comment='指标名称（GAAP概念名）')
    label = Column(String(1000), nullable=True, comment='指标标签描述')
    role = Column(String(10), nullable=True, comment='指标角色，如bc（Balance Sheet Credit）')
    
    # 指标属性
    data_type = Column(String(50), default='monetary', comment='数据类型：monetary, shares, ratio, percentage等')
    unit = Column(String(20), default='USD', comment='单位：USD, shares, pure等')
    
    # 统计信息
    usage_frequency = Column(Integer, default=0, comment='该指标的使用频率')
    
    # 状态信息
    is_common = Column(Boolean, default=False, comment='是否为常见指标')
    is_active = Column(Boolean, default=True, comment='是否活跃指标')
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关系
    section = relationship("ReportSection", back_populates="metrics")
    financial_data = relationship("FinancialData", back_populates="metric")
    invalid_cache = relationship("InvalidMetricCache", back_populates="metric")
    
    # 索引
    __table_args__ = (
        Index('idx_metric_name', 'metric_name'),
        Index('idx_metric_section_name', 'section_id', 'metric_name'),
    )
    
    def __repr__(self):
        return f"<Metric(name='{self.metric_name}', section_id={self.section_id})>"


class FinancialData(Base):
    """财务数据表 - 存储从SEC获取的实际财务数据"""
    __tablename__ = 'financial_data'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 外键
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    report_type_id = Column(Integer, ForeignKey('report_types.id', ondelete='CASCADE'), nullable=False)
    section_id = Column(Integer, ForeignKey('report_sections.id', ondelete='CASCADE'), nullable=False)
    metric_id = Column(Integer, ForeignKey('metrics.id', ondelete='CASCADE'), nullable=False)
    
    # 时间信息
    fiscal_year = Column(Integer, nullable=False, comment='财政年度')
    fiscal_period = Column(String(10), nullable=True, comment='财政期间：FY, Q1, Q2, Q3, Q4')
    period_start_date = Column(String(10), nullable=True, comment='期间开始日期 YYYY-MM-DD')
    period_end_date = Column(String(10), nullable=True, comment='期间结束日期 YYYY-MM-DD')
    filed_date = Column(String(10), nullable=True, comment='提交日期 YYYY-MM-DD')
    
    # 数据值
    value = Column(Float, nullable=True, comment='数值（原始值）')
    formatted_value = Column(String(50), nullable=True, comment='格式化显示值')
    unit = Column(String(20), default='USD', comment='单位')
    
    # SEC相关信息
    frame = Column(String(50), nullable=True, comment='SEC frame信息')
    form_type = Column(String(20), nullable=True, comment='表单类型')
    accession_number = Column(String(25), nullable=True, comment='SEC accession number')
    
    # 数据来源和状态
    data_source = Column(String(20), default='SEC_API', comment='数据来源：SEC_API, MANUAL等')
    is_verified = Column(Boolean, default=False, comment='数据是否已验证')
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关系
    company = relationship("Company", back_populates="financial_data")
    report_type = relationship("ReportType", back_populates="financial_data")
    section = relationship("ReportSection", back_populates="financial_data")
    metric = relationship("Metric", back_populates="financial_data")
    
    # 唯一约束：同一公司、同一指标、同一时间期间只能有一条记录
    __table_args__ = (
        UniqueConstraint('company_id', 'metric_id', 'fiscal_year', 'fiscal_period', 'period_end_date', 
                        name='uq_financial_data'),
        Index('idx_financial_data_company_year', 'company_id', 'fiscal_year'),
        Index('idx_financial_data_metric_year', 'metric_id', 'fiscal_year'),
        Index('idx_financial_data_lookup', 'company_id', 'report_type_id', 'fiscal_year'),
    )
    
    def __repr__(self):
        return f"<FinancialData(company_id={self.company_id}, metric_id={self.metric_id}, year={self.fiscal_year}, value={self.value})>"


class InvalidMetricCache(Base):
    """无效指标缓存表 - 记录已知无效的指标组合"""
    __tablename__ = 'invalid_metric_cache'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 外键
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    report_type_id = Column(Integer, ForeignKey('report_types.id', ondelete='CASCADE'), nullable=False)
    metric_id = Column(Integer, ForeignKey('metrics.id', ondelete='CASCADE'), nullable=False)
    
    # 缓存信息
    fiscal_year = Column(Integer, nullable=False, comment='财政年度')
    reason = Column(String(100), nullable=True, comment='无效原因：404_NOT_FOUND, EMPTY_RESPONSE等')
    
    # 缓存管理
    cache_expiry_days = Column(Integer, default=7, comment='缓存有效期（天）')
    
    # 时间戳
    cached_at = Column(DateTime, default=func.now(), comment='缓存时间')
    
    # 关系
    company = relationship("Company")
    report_type = relationship("ReportType")
    metric = relationship("Metric", back_populates="invalid_cache")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('company_id', 'report_type_id', 'metric_id', 'fiscal_year', 
                        name='uq_invalid_cache'),
        Index('idx_invalid_cache_lookup', 'company_id', 'report_type_id', 'fiscal_year'),
        Index('idx_invalid_cache_expiry', 'cached_at'),
    )
    
    def is_expired(self) -> bool:
        """检查缓存是否过期"""
        if not self.cached_at:
            return True
        
        from datetime import datetime, timedelta
        expiry_date = self.cached_at + timedelta(days=self.cache_expiry_days)
        return datetime.now() > expiry_date
    
    def __repr__(self):
        return f"<InvalidMetricCache(company_id={self.company_id}, metric_id={self.metric_id}, year={self.fiscal_year})>"


class DataFetchLog(Base):
    """数据获取日志表 - 记录SEC数据获取的历史"""
    __tablename__ = 'data_fetch_logs'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 获取信息
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    report_type_id = Column(Integer, ForeignKey('report_types.id', ondelete='CASCADE'), nullable=False)
    fiscal_year = Column(Integer, nullable=False, comment='财政年度')
    
    # 获取结果
    status = Column(String(20), nullable=False, comment='获取状态：SUCCESS, FAILED, PARTIAL')
    total_metrics = Column(Integer, default=0, comment='尝试获取的指标总数')
    successful_metrics = Column(Integer, default=0, comment='成功获取的指标数')
    cached_skips = Column(Integer, default=0, comment='缓存跳过的指标数')
    new_invalid_cache = Column(Integer, default=0, comment='新增无效缓存的指标数')
    
    # 性能统计
    fetch_duration_seconds = Column(Float, nullable=True, comment='获取耗时（秒）')
    api_requests_count = Column(Integer, default=0, comment='API请求次数')
    
    # 错误信息
    error_message = Column(Text, nullable=True, comment='错误信息')
    
    # 时间戳
    started_at = Column(DateTime, default=func.now(), comment='开始时间')
    completed_at = Column(DateTime, nullable=True, comment='完成时间')
    
    # 关系
    company = relationship("Company")
    report_type = relationship("ReportType")
    
    # 索引
    __table_args__ = (
        Index('idx_fetch_log_company_year', 'company_id', 'fiscal_year'),
        Index('idx_fetch_log_status', 'status'),
        Index('idx_fetch_log_started', 'started_at'),
    )
    
    def __repr__(self):
        return f"<DataFetchLog(company_id={self.company_id}, year={self.fiscal_year}, status='{self.status}')>"


# 数据库初始化帮助函数
def create_all_tables(engine):
    """创建所有表"""
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    """删除所有表"""
    Base.metadata.drop_all(engine)