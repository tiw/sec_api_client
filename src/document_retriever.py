"""
SEC 10-K和10-Q文档获取模块

提供获取和解析10-K（年报）和10-Q（季报）文档的功能
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime
from .sec_client import SECClient


class DocumentRetriever:
    """10-K和10-Q文档获取器"""
    
    EDGAR_BASE_URL = "https://www.sec.gov/Archives/edgar/data/"
    
    def __init__(self, sec_client: SECClient):
        """
        初始化文档获取器
        
        Args:
            sec_client: SEC客户端实例
        """
        self.client = sec_client
    
    def get_filing_documents(self, cik: str, accession_number: str) -> Dict:
        """
        获取指定申报的所有文档列表
        
        Args:
            cik: 公司CIK号码
            accession_number: 申报访问号码
            
        Returns:
            包含文档信息的字典
        """
        # 构造文档索引URL
        accession_clean = accession_number.replace('-', '')
        index_url = f"{self.EDGAR_BASE_URL}{cik}/{accession_clean}/{accession_number}-index.html"
        
        try:
            response = self.client._make_request(index_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            documents = []
            # 查找文档表格
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # 跳过表头
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        doc_info = {
                            'sequence': cells[0].get_text(strip=True),
                            'description': cells[1].get_text(strip=True),
                            'document': cells[2].get_text(strip=True),
                            'type': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                            'size': cells[4].get_text(strip=True) if len(cells) > 4 else ''
                        }
                        
                        # 构造文档URL
                        doc_link = cells[2].find('a')
                        if doc_link:
                            doc_info['url'] = f"{self.EDGAR_BASE_URL}{cik}/{accession_clean}/{doc_link['href']}"
                        
                        documents.append(doc_info)
            
            return {
                'cik': cik,
                'accession_number': accession_number,
                'documents': documents
            }
            
        except Exception as e:
            print(f"获取文档列表失败: {e}")
            return {'cik': cik, 'accession_number': accession_number, 'documents': []}
    
    def get_10k_10q_filings(self, ticker: str, years: int = 3) -> pd.DataFrame:
        """
        获取公司的10-K和10-Q文档
        
        Args:
            ticker: 股票代码
            years: 获取最近几年的数据
            
        Returns:
            包含10-K和10-Q文档信息的DataFrame
        """
        # 搜索公司信息
        company_info = self.client.search_company_by_ticker(ticker)
        if not company_info:
            raise ValueError(f"未找到股票代码 {ticker} 对应的公司")
        
        cik = company_info['cik']
        
        # 获取最近的10-K和10-Q文档
        filings = self.client.get_recent_filings(
            cik=cik,
            form_types=['10-K', '10-Q'],
            limit=years * 5  # 每年大约4个季报+1个年报
        )
        
        if filings.empty:
            return pd.DataFrame()
        
        # 添加公司信息
        filings['ticker'] = company_info['ticker']
        filings['company_name'] = company_info['title']
        filings['cik'] = cik
        
        return filings
    
    def download_document_content(self, document_url: str) -> Optional[str]:
        """
        下载文档内容
        
        Args:
            document_url: 文档URL
            
        Returns:
            文档内容字符串，失败时返回None
        """
        try:
            response = self.client._make_request(document_url)
            return response.text
        except Exception as e:
            print(f"下载文档失败: {e}")
            return None
    
    def parse_10k_sections(self, document_content: str) -> Dict[str, str]:
        """
        解析10-K文档的主要章节
        
        Args:
            document_content: 文档HTML内容
            
        Returns:
            包含各章节内容的字典
        """
        soup = BeautifulSoup(document_content, 'html.parser')
        
        sections = {}
        
        # 定义10-K的主要章节
        section_patterns = {
            'Item 1': r'item\s*1[^\w].*?business',
            'Item 1A': r'item\s*1a[^\w].*?risk\s*factors',
            'Item 2': r'item\s*2[^\w].*?properties',
            'Item 3': r'item\s*3[^\w].*?legal\s*proceedings',
            'Item 7': r'item\s*7[^\w].*?management.*?discussion',
            'Item 8': r'item\s*8[^\w].*?financial\s*statements'
        }
        
        text_content = soup.get_text()
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
            if match:
                # 尝试提取该章节的内容
                start_pos = match.start()
                
                # 查找下一个章节的开始位置
                next_section_pos = len(text_content)
                for next_pattern in section_patterns.values():
                    next_match = re.search(next_pattern, text_content[start_pos + len(match.group()):], 
                                         re.IGNORECASE | re.DOTALL)
                    if next_match:
                        next_section_pos = min(next_section_pos, 
                                             start_pos + len(match.group()) + next_match.start())
                
                section_content = text_content[start_pos:next_section_pos]
                sections[section_name] = section_content[:10000]  # 限制长度
        
        return sections
    
    def get_financial_highlights(self, ticker: str, form_type: str = '10-Q') -> Dict:
        """
        获取财务亮点数据
        
        Args:
            ticker: 股票代码
            form_type: 文档类型（10-K或10-Q）
            
        Returns:
            包含财务亮点的字典
        """
        filings = self.get_10k_10q_filings(ticker, years=1)
        
        if filings.empty:
            return {}
        
        # 获取最新的指定类型文档
        latest_filing = filings[filings['form'] == form_type].iloc[0]
        
        # 获取文档列表
        documents = self.get_filing_documents(
            latest_filing['cik'],
            latest_filing['accessionNumber']
        )
        
        # 查找主要文档
        main_document = None
        for doc in documents.get('documents', []):
            if doc.get('document', '').endswith('.htm') or doc.get('document', '').endswith('.html'):
                main_document = doc
                break
        
        if not main_document:
            return {}
        
        # 下载并解析文档
        content = self.download_document_content(main_document['url'])
        if not content:
            return {}
        
        # 提取基本信息
        highlights = {
            'ticker': ticker,
            'form_type': form_type,
            'filing_date': latest_filing['filingDate'],
            'report_date': latest_filing['reportDate'],
            'accession_number': latest_filing['accessionNumber'],
            'document_url': main_document['url']
        }
        
        if form_type == '10-K':
            highlights['sections'] = self.parse_10k_sections(content)
        
        return highlights