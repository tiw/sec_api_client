"""
SEC XBRL/Frames API数据获取模块

基于SEC XBRL/Frames API获取结构化财务数据
支持年度、季度和瞬时数据查询
"""

import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime, date
import re
from .sec_client import SECClient


class XBRLFramesClient:
    """XBRL/Frames数据客户端"""
    
    # 常用的US-GAAP标准财务指标
    COMMON_CONCEPTS = {
        # 资产负债表项目
        'Assets': 'Assets',  # 总资产
        'AssetsCurrent': 'AssetsCurrent',  # 流动资产
        'AssetsNoncurrent': 'AssetsNoncurrent',  # 非流动资产
        'CashAndCashEquivalentsAtCarryingValue': 'CashAndCashEquivalentsAtCarryingValue',  # 现金及现金等价物
        'AccountsReceivableNetCurrent': 'AccountsReceivableNetCurrent',  # 应收账款净额
        'InventoryNet': 'InventoryNet',  # 存货净额
        
        'Liabilities': 'Liabilities',  # 总负债
        'LiabilitiesCurrent': 'LiabilitiesCurrent',  # 流动负债
        'LiabilitiesNoncurrent': 'LiabilitiesNoncurrent',  # 非流动负债
        'AccountsPayableCurrent': 'AccountsPayableCurrent',  # 应付账款
        'LongTermDebtNoncurrent': 'LongTermDebtNoncurrent',  # 长期债务
        
        'StockholdersEquity': 'StockholdersEquity',  # 股东权益
        'RetainedEarningsAccumulatedDeficit': 'RetainedEarningsAccumulatedDeficit',  # 留存收益
        
        # 损益表项目
        'Revenues': 'Revenues',  # 营收
        'RevenueFromContractWithCustomerExcludingAssessedTax': 'RevenueFromContractWithCustomerExcludingAssessedTax',  # 销售收入
        'CostOfRevenue': 'CostOfRevenue',  # 销售成本
        'GrossProfit': 'GrossProfit',  # 毛利润
        'OperatingExpenses': 'OperatingExpenses',  # 营业费用
        'OperatingIncomeLoss': 'OperatingIncomeLoss',  # 营业利润
        'NetIncomeLoss': 'NetIncomeLoss',  # 净利润
        'EarningsPerShareBasic': 'EarningsPerShareBasic',  # 基本每股收益
        'EarningsPerShareDiluted': 'EarningsPerShareDiluted',  # 稀释每股收益
        
        # 现金流量表项目
        'NetCashProvidedByUsedInOperatingActivities': 'NetCashProvidedByUsedInOperatingActivities',  # 经营活动现金流
        'NetCashProvidedByUsedInInvestingActivities': 'NetCashProvidedByUsedInInvestingActivities',  # 投资活动现金流
        'NetCashProvidedByUsedInFinancingActivities': 'NetCashProvidedByUsedInFinancingActivities'   # 筹资活动现金流
    }
    
    def __init__(self, sec_client: SECClient):
        """
        初始化XBRL客户端
        
        Args:
            sec_client: SEC客户端实例
        """
        self.client = sec_client
    
    def _build_frames_url(self, taxonomy: str, tag: str, unit: str, period: str) -> str:
        """
        构建XBRL/Frames API URL
        
        Args:
            taxonomy: 分类标准（如：us-gaap）
            tag: 财务概念标签
            unit: 单位（如：USD）
            period: 时期（如：CY2023Q1I）
            
        Returns:
            完整的API URL
        """
        return f"{self.client.FRAMES_URL}{taxonomy}/{tag}/{unit}/{period}.json"
    
    def get_concept_data(self, concept: str, period: str, 
                        unit: str = 'USD', taxonomy: str = 'us-gaap') -> pd.DataFrame:
        """
        获取特定财务概念的数据
        
        Args:
            concept: 财务概念（如：Assets, Revenues等）
            period: 时期（如：CY2023Q1, CY2023Q1I）
            unit: 单位，默认USD
            taxonomy: 分类标准，默认us-gaap
            
        Returns:
            包含财务数据的DataFrame
        """
        url = self._build_frames_url(taxonomy, concept, unit, period)
        
        try:
            response = self.client._make_request(url)
            frame_data = response.json()
            
            # 解析JSON数据为DataFrame
            df = pd.json_normalize(
                frame_data.get('data', [])
            )
            
            if df.empty:
                return df
            
            # 添加元数据
            meta_fields = ['taxonomy', 'tag', 'ccp', 'uom', 'label', 'description']
            for field in meta_fields:
                if field in frame_data:
                    df[field] = frame_data[field]
            
            # 数据类型转换
            if 'val' in df.columns:
                df['val'] = pd.to_numeric(df['val'], errors='coerce')
            
            if 'end' in df.columns:
                df['end'] = pd.to_datetime(df['end'], errors='coerce')
            
            if 'start' in df.columns:
                df['start'] = pd.to_datetime(df['start'], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"获取概念数据失败 ({concept}, {period}): {e}")
            return pd.DataFrame()
    
    def get_company_concept_data(self, cik: str, concept: str, 
                               taxonomy: str = 'us-gaap') -> Dict:
        """
        获取特定公司某个财务概念的历史数据
        
        Args:
            cik: 公司CIK号码
            concept: 财务概念
            taxonomy: 分类标准
            
        Returns:
            包含历史数据的字典
        """
        cik = str(cik).zfill(10)
        url = f"{self.client.COMPANY_SEARCH_URL}CIK{cik}/{taxonomy}/{concept}.json"
        
        try:
            response = self.client._make_request(url)
            return response.json()
        except Exception as e:
            print(f"获取公司概念数据失败 ({cik}, {concept}): {e}")
            return {}
    
    def get_financial_metrics(self, ticker: str, period_type: str = 'annual', 
                            years: int = 3) -> pd.DataFrame:
        """
        获取公司的主要财务指标
        
        Args:
            ticker: 股票代码
            period_type: 期间类型（'annual', 'quarterly', 'instant'）
            years: 获取年数
            
        Returns:
            包含财务指标的DataFrame
        """
        # 获取公司信息
        company_info = self.client.search_company_by_ticker(ticker)
        if not company_info:
            raise ValueError(f"未找到股票代码 {ticker} 对应的公司")
        
        cik = company_info['cik']
        results = []
        
        # 选择关键指标
        key_concepts = [
            'Assets', 'Liabilities', 'StockholdersEquity',
            'Revenues', 'NetIncomeLoss', 'OperatingIncomeLoss'
        ]
        
        for concept in key_concepts:
            if concept not in self.COMMON_CONCEPTS:
                continue
                
            concept_tag = self.COMMON_CONCEPTS[concept]
            company_data = self.get_company_concept_data(cik, concept_tag)
            
            if not company_data:
                continue
            
            # 提取USD数据
            units_data = company_data.get('units', {}).get('USD', [])
            if not units_data:
                continue
            
            for item in units_data:
                # 过滤期间类型
                if period_type == 'annual' and 'Q' in item.get('frame', ''):
                    continue
                elif period_type == 'quarterly' and 'Q' not in item.get('frame', ''):
                    continue
                
                results.append({
                    'ticker': ticker,
                    'cik': cik,
                    'concept': concept,
                    'concept_tag': concept_tag,
                    'value': item.get('val'),
                    'start_date': item.get('start'),
                    'end_date': item.get('end'),
                    'frame': item.get('frame'),
                    'fiscal_year': item.get('fy'),
                    'fiscal_period': item.get('fp'),
                    'form': item.get('form'),
                    'filed_date': item.get('filed')
                })
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # 数据类型转换
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
        df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
        df['filed_date'] = pd.to_datetime(df['filed_date'], errors='coerce')
        
        # 按日期排序
        df = df.sort_values('end_date', ascending=False)
        
        return df
    
    def build_period_string(self, year: int, quarter: Optional[int] = None, 
                           instant: bool = False) -> str:
        """
        构建期间字符串
        
        Args:
            year: 年份
            quarter: 季度（1-4），None表示年度数据
            instant: 是否为瞬时数据
            
        Returns:
            期间字符串（如：CY2023, CY2023Q1, CY2023Q1I）
        """
        period = f"CY{year}"
        
        if quarter:
            if not 1 <= quarter <= 4:
                raise ValueError("季度必须在1-4之间")
            period += f"Q{quarter}"
        
        if instant:
            period += "I"
        
        return period
    
    def get_quarterly_comparison(self, concept: str, year: int, 
                               unit: str = 'USD') -> pd.DataFrame:
        """
        获取某年四个季度的数据对比
        
        Args:
            concept: 财务概念
            year: 年份
            unit: 单位
            
        Returns:
            包含四个季度数据的DataFrame
        """
        quarterly_data = []
        
        for quarter in range(1, 5):
            period = self.build_period_string(year, quarter, instant=True)
            df = self.get_concept_data(concept, period, unit)
            
            if not df.empty:
                df['quarter'] = quarter
                df['year'] = year
                quarterly_data.append(df)
        
        if not quarterly_data:
            return pd.DataFrame()
        
        result_df = pd.concat(quarterly_data, ignore_index=True)
        return result_df.sort_values(['quarter', 'cik'])