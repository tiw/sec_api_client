"""
项目源代码包

SEC EDGAR API客户端库，提供：
- SEC数据访问（SECClient）
- 10-K/10-Q文档获取（DocumentRetriever）
- XBRL/Frames数据查询（XBRLFramesClient）
- 财务数据分析（FinancialAnalyzer）
"""

__version__ = "1.0.0"

# SEC API Client 主模块
# 提供访问SEC EDGAR数据库和XBRL数据的功能

from .sec_client import SECClient
from .xbrl_frames import XBRLFramesClient
from .financial_analyzer import FinancialAnalyzer
from .document_retriever import DocumentRetriever
from .concept_explainer import ConceptExplainer

__all__ = [
    'SECClient',
    'XBRLFramesClient', 
    'FinancialAnalyzer',
    'DocumentRetriever',
    'ConceptExplainer'
]
