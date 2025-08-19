"""
SEC EDGAR API客户端核心模块

提供访问SEC EDGAR数据库的基础功能，包括：
- 公司搜索
- 文档获取（10-K, 10-Q等）
- XBRL/Frames数据访问
"""

import requests
import time
import json
from typing import Dict, List, Optional, Union
from datetime import datetime, date
import pandas as pd
from urllib.parse import urljoin


class SECClient:
    """SEC EDGAR API客户端主类"""
    
    BASE_URL = "https://data.sec.gov/api/"
    COMPANY_SEARCH_URL = "https://data.sec.gov/api/xbrl/companyconcept/"
    FRAMES_URL = "https://data.sec.gov/api/xbrl/frames/"
    SUBMISSIONS_URL = "https://data.sec.gov/submissions/"
    
    def __init__(self, user_agent: str = None):
        """
        初始化SEC客户端
        
        Args:
            user_agent: 用户代理字符串，SEC要求必须提供有效的联系方式
        """
        if not user_agent:
            raise ValueError("必须提供user_agent，格式建议: '您的姓名 您的邮箱'")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        })
        
        # API调用频率限制（每秒最多10次请求）
        self.rate_limit_delay = 0.1
        self.last_request_time = 0
    
    def _rate_limit(self):
        """实现API调用频率限制"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict = None) -> requests.Response:
        """
        发起API请求
        
        Args:
            url: 请求URL
            params: 请求参数
            
        Returns:
            requests.Response对象
            
        Raises:
            requests.exceptions.HTTPError: HTTP错误
        """
        self._rate_limit()
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {url}")
            print(f"错误信息: {str(e)}")
            raise
    
    def get_company_tickers(self) -> Dict:
        """
        获取所有公司的ticker列表
        
        Returns:
            包含公司ticker信息的字典
        """
        # 尝试从ticker.txt文件获取数据
        ticker_url = "https://www.sec.gov/include/ticker.txt"
        
        try:
            response = self._make_request(ticker_url)
            ticker_text = response.text
            
            # 解析ticker.txt格式: ticker\tcik\n
            companies = {}
            for i, line in enumerate(ticker_text.strip().split('\n')):
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        ticker = parts[0].upper()
                        cik = parts[1]
                        companies[str(i)] = {
                            "cik_str": int(cik),
                            "ticker": ticker,
                            "title": f"{ticker} Corp"  # 简化的公司名称
                        }
            
            if companies:
                return companies
                
        except Exception as e:
            print(f"从ticker.txt获取数据失败: {e}")
        
        # 如果获取失败，返回常用公司的默认数据
        print("使用默认的公司ticker数据")
        return {
            "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."},
            "1": {"cik_str": 789019, "ticker": "MSFT", "title": "MICROSOFT CORP"},
            "2": {"cik_str": 1652044, "ticker": "GOOGL", "title": "Alphabet Inc."},
            "3": {"cik_str": 1018724, "ticker": "AMZN", "title": "AMAZON COM INC"},
            "4": {"cik_str": 1045810, "ticker": "NVDA", "title": "NVIDIA CORP"},
            "5": {"cik_str": 1318605, "ticker": "TSLA", "title": "TESLA INC"},
            "6": {"cik_str": 1326801, "ticker": "META", "title": "META PLATFORMS INC"},
            "7": {"cik_str": 1067983, "ticker": "BRK-B", "title": "BERKSHIRE HATHAWAY INC"},
            "8": {"cik_str": 886982, "ticker": "WMT", "title": "WALMART INC"},
            "9": {"cik_str": 200406, "ticker": "JNJ", "title": "JOHNSON & JOHNSON"}
        }
    
    def search_company_by_ticker(self, ticker: str) -> Optional[Dict]:
        """
        根据股票代码搜索公司信息
        
        Args:
            ticker: 股票代码（如：AAPL, MSFT）
            
        Returns:
            公司信息字典，如果未找到返回None
        """
        companies = self.get_company_tickers()
        
        for company_id, company_info in companies.items():
            if company_info.get('ticker', '').upper() == ticker.upper():
                return {
                    'cik': str(company_info['cik_str']).zfill(10),
                    'ticker': company_info['ticker'],
                    'title': company_info['title']
                }
        
        return None
    
    def get_company_submissions(self, cik: str) -> Dict:
        """
        获取公司的所有提交文档
        
        Args:
            cik: 公司的CIK号码（10位数字字符串）
            
        Returns:
            包含公司提交文档的字典
        """
        # 确保CIK是10位数字
        cik = str(cik).zfill(10)
        url = f"{self.SUBMISSIONS_URL}CIK{cik}.json"
        
        response = self._make_request(url)
        return response.json()
    
    def get_recent_filings(self, cik: str, form_types: List[str] = None, 
                          limit: int = 10) -> pd.DataFrame:
        """
        获取公司最近的文档提交
        
        Args:
            cik: 公司CIK号码
            form_types: 文档类型列表（如：['10-K', '10-Q']）
            limit: 返回结果数量限制
            
        Returns:
            包含文档信息的DataFrame
        """
        submissions = self.get_company_submissions(cik)
        
        # 提取recent filings数据
        recent = submissions.get('filings', {}).get('recent', {})
        
        if not recent:
            return pd.DataFrame()
        
        # 创建DataFrame
        df = pd.DataFrame({
            'accessionNumber': recent.get('accessionNumber', []),
            'filingDate': recent.get('filingDate', []),
            'reportDate': recent.get('reportDate', []),
            'form': recent.get('form', []),
            'fileNumber': recent.get('fileNumber', []),
            'filmNumber': recent.get('filmNumber', []),
            'items': recent.get('items', []),
            'size': recent.get('size', []),
            'isXBRL': recent.get('isXBRL', []),
            'isInlineXBRL': recent.get('isInlineXBRL', []),
            'primaryDocument': recent.get('primaryDocument', []),
            'primaryDocDescription': recent.get('primaryDocDescription', [])
        })
        
        # 过滤文档类型
        if form_types:
            df = df[df['form'].isin(form_types)]
        
        # 转换日期格式
        df['filingDate'] = pd.to_datetime(df['filingDate'])
        df['reportDate'] = pd.to_datetime(df['reportDate'])
        
        # 按文档提交日期降序排列
        df = df.sort_values('filingDate', ascending=False)
        
        return df.head(limit)