"""
项目源代码包

SEC EDGAR API客户端库，提供：
- SEC数据访问（SECClient）
- 10-K/10-Q文档获取（DocumentRetriever）
- XBRL/Frames数据查询（XBRLFramesClient）
- 财务数据分析（FinancialAnalyzer）
"""

__version__ = "1.0.0"

from .sec_client import SECClient
from .document_retriever import DocumentRetriever
from .xbrl_frames import XBRLFramesClient
from .financial_analyzer import FinancialAnalyzer

__all__ = [
    'SECClient',
    'DocumentRetriever', 
    'XBRLFramesClient',
    'FinancialAnalyzer'
]