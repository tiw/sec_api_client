#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US-GAAP 财务概念下载和解释工具

功能：
1. 下载完整的US-GAAP分类标准列表
2. 获取每个概念的详细定义和解释
3. 支持按分类筛选和导出
4. 生成中英文对照的概念词典

使用方法：
    python download_gaap_concepts.py --output gaap_concepts.csv
    python download_gaap_concepts.py --concepts-only  # 仅下载概念列表
    python download_gaap_concepts.py --with-definitions  # 包含详细定义
    python download_gaap_concepts.py --category assets  # 按分类筛选

作者: Ting Wang <tting.wang@gmail.com>
"""

import sys
import os
import requests
import pandas as pd
import json
import time
from pathlib import Path
import argparse
from typing import Dict, List, Optional, Any
import logging

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from src import SECClient, ConceptExplainer

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class USGAAPDownloader:
    """US-GAAP概念下载器"""
    
    def __init__(self, user_agent: str = "Ting Wang tting.wang@gmail.com"):
        """初始化下载器"""
        self.user_agent = user_agent
        self.sec_client = SECClient(user_agent=user_agent)
        self.concept_explainer = ConceptExplainer(user_agent=user_agent)
        
        # US-GAAP分类标准URL
        self.taxonomy_urls = {
            'us-gaap': 'https://xbrl.fasb.org/us-gaap/2023/entire/us-gaap-2023.zip',
            'dei': 'https://xbrl.sec.gov/dei/2023/dei-2023.xsd',
            'invest': 'https://xbrl.sec.gov/invest/2023/invest-2023.xsd'
        }
        
        # SEC XBRL概念列表API
        self.frames_api_base = "https://data.sec.gov/api/xbrl/frames"
        
        # 概念分类映射
        self.concept_categories = {
            'assets': ['Assets', 'Cash', 'Receivable', 'Inventory', 'Investment', 'Property'],
            'liabilities': ['Liabilities', 'Debt', 'Payable', 'Accrued', 'Deferred'],
            'equity': ['Equity', 'Stock', 'Capital', 'Earnings', 'Dividend'],
            'revenue': ['Revenue', 'Sales', 'Income', 'Gain'],
            'expenses': ['Expense', 'Cost', 'Loss', 'Depreciation', 'Amortization'],
            'cash_flow': ['CashFlow', 'Operating', 'Investing', 'Financing'],
            'per_share': ['PerShare', 'EarningsPerShare', 'BookValue'],
            'ratios': ['Ratio', 'Percentage', 'Rate']
        }
    
    def get_available_concepts(self, taxonomy: str = 'us-gaap') -> List[str]:
        """
        获取可用的财务概念列表
        
        Args:
            taxonomy: 分类标准，默认为us-gaap
            
        Returns:
            概念名称列表
        """
        logger.info(f"获取 {taxonomy} 分类标准下的概念列表...")
        
        # 方法1: 从frames API获取
        concepts = self._get_concepts_from_frames_api(taxonomy)
        
        if not concepts:
            # 方法2: 从预定义列表获取
            concepts = self._get_predefined_concepts()
        
        logger.info(f"获取到 {len(concepts)} 个概念")
        return concepts
    
    def _get_concepts_from_frames_api(self, taxonomy: str) -> List[str]:
        """从frames API获取概念列表"""
        try:
            # 尝试获取一些常见概念的数据来推断可用概念
            test_concepts = [
                'Assets', 'Liabilities', 'StockholdersEquity', 'Revenues', 'NetIncomeLoss',
                'CashAndCashEquivalentsAtCarryingValue', 'AccountsReceivableNetCurrent',
                'InventoryNet', 'PropertyPlantAndEquipmentNet', 'LongTermDebtNoncurrent',
                'AccountsPayableCurrent', 'OperatingIncomeLoss', 'EarningsPerShareBasic',
                'NetCashProvidedByUsedInOperatingActivities'
            ]
            
            available_concepts = []
            
            for concept in test_concepts:
                try:
                    url = f"{self.frames_api_base}/{taxonomy}/{concept}/USD/CY2023Q4I.json"
                    response = self.sec_client._make_request(url)
                    if response and response.status_code == 200:
                        available_concepts.append(concept)
                    time.sleep(0.1)  # 控制请求频率
                except:
                    continue
            
            return available_concepts
            
        except Exception as e:
            logger.warning(f"从frames API获取概念列表失败: {e}")
            return []
    
    def _get_predefined_concepts(self) -> List[str]:
        """获取预定义的常见财务概念"""
        return [
            # 资产类
            'Assets', 'AssetsCurrent', 'AssetsNoncurrent',
            'CashAndCashEquivalentsAtCarryingValue', 'Cash',
            'MarketableSecuritiesCurrent', 'MarketableSecuritiesNoncurrent',
            'AccountsReceivableNetCurrent', 'InventoryNet',
            'PropertyPlantAndEquipmentNet', 'PropertyPlantAndEquipmentGross',
            'AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment',
            'Goodwill', 'IntangibleAssetsNetExcludingGoodwill',
            'DeferredTaxAssetsNet', 'OtherAssetsNoncurrent',
            
            # 负债类
            'Liabilities', 'LiabilitiesCurrent', 'LiabilitiesNoncurrent',
            'AccountsPayableCurrent', 'AccruedLiabilitiesCurrent',
            'ShortTermBorrowings', 'LongTermDebtCurrent',
            'LongTermDebtNoncurrent', 'LongTermDebt',
            'CommercialPaper', 'DeferredRevenue',
            'DeferredTaxLiabilitiesNet', 'OtherLiabilitiesNoncurrent',
            
            # 权益类
            'StockholdersEquity', 'CommonStockSharesOutstanding',
            'CommonStockSharesIssued', 'CommonStockValue',
            'AdditionalPaidInCapital', 'RetainedEarningsAccumulatedDeficit',
            'AccumulatedOtherComprehensiveIncomeLossNetOfTax',
            'TreasuryStockValue', 'TreasuryStockShares',
            
            # 收入和费用
            'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
            'SalesRevenueNet', 'CostOfRevenue', 'CostOfGoodsAndServicesSold',
            'GrossProfit', 'OperatingExpenses', 'SellingGeneralAndAdministrativeExpense',
            'ResearchAndDevelopmentExpense', 'DepreciationDepletionAndAmortization',
            'OperatingIncomeLoss', 'NonoperatingIncomeExpense',
            'InterestExpense', 'InterestIncome',
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
            'IncomeTaxExpenseBenefit', 'NetIncomeLoss',
            
            # 每股数据
            'EarningsPerShareBasic', 'EarningsPerShareDiluted',
            'WeightedAverageNumberOfSharesOutstandingBasic',
            'WeightedAverageNumberOfDilutedSharesOutstanding',
            'CommonStockDividendsPerShareDeclared',
            
            # 现金流
            'NetCashProvidedByUsedInOperatingActivities',
            'NetCashProvidedByUsedInInvestingActivities',
            'NetCashProvidedByUsedInFinancingActivities',
            'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',
            'PaymentsToAcquirePropertyPlantAndEquipment',
            'PaymentsForRepurchaseOfCommonStock',
            'PaymentsOfDividends', 'Dividends',
            
            # 其他重要概念
            'ShareBasedCompensation', 'EmployeeServiceShareBasedCompensationNonvestedAwardsTotalCompensationCostNotYetRecognized',
            'RepaymentsOfLongTermDebt', 'ProceedsFromIssuanceOfLongTermDebt',
            'BusinessCombinationAcquisitionRelatedCosts',
            'RestructuringCharges', 'AssetImpairmentCharges',
        ]
    
    def get_concept_definition(self, concept: str, taxonomy: str = 'us-gaap') -> Dict[str, Any]:
        """
        获取概念的详细定义
        
        Args:
            concept: 概念名称
            taxonomy: 分类标准
            
        Returns:
            包含概念定义的字典
        """
        try:
            # 使用Apple的CIK获取概念数据示例
            apple_cik = "0000320193"
            concept_data = self.concept_explainer.xbrl_client.get_company_concept_data(
                cik=apple_cik,
                concept=concept,
                taxonomy=taxonomy
            )
            
            if not concept_data:
                return self._get_basic_concept_info(concept, taxonomy)
            
            # 提取概念信息
            concept_info = {
                'concept': concept,
                'taxonomy': taxonomy,
                'label': concept_data.get('label', concept),
                'description': concept_data.get('description', ''),
                'chinese_name': self.concept_explainer.CONCEPT_CHINESE_NAMES.get(concept, ''),
                'chinese_definition': self.concept_explainer.CONCEPT_DEFINITIONS.get(concept, ''),
                'english_explanation': self.concept_explainer.CONCEPT_ENGLISH_EXPLANATIONS.get(concept, ''),
                'units': list(concept_data.get('units', {}).keys()) if concept_data.get('units') else [],
                'data_type': self._infer_data_type(concept_data),
                'category': self._categorize_concept(concept)
            }
            
            return concept_info
            
        except Exception as e:
            logger.warning(f"获取概念 {concept} 定义失败: {e}")
            return self._get_basic_concept_info(concept, taxonomy)
    
    def _get_basic_concept_info(self, concept: str, taxonomy: str) -> Dict[str, Any]:
        """获取基本概念信息"""
        return {
            'concept': concept,
            'taxonomy': taxonomy,
            'label': concept,
            'description': '',
            'chinese_name': self.concept_explainer.CONCEPT_CHINESE_NAMES.get(concept, ''),
            'chinese_definition': self.concept_explainer.CONCEPT_DEFINITIONS.get(concept, ''),
            'english_explanation': self.concept_explainer.CONCEPT_ENGLISH_EXPLANATIONS.get(concept, ''),
            'units': [],
            'data_type': self._infer_data_type_from_name(concept),
            'category': self._categorize_concept(concept)
        }
    
    def _infer_data_type(self, concept_data: Dict) -> str:
        """从概念数据推断数据类型"""
        units = concept_data.get('units', {})
        if 'USD' in units or 'USD/shares' in units:
            return 'monetary' if 'USD' in units else 'per_share'
        elif 'shares' in units:
            return 'shares'
        elif 'pure' in units:
            return 'ratio'
        else:
            return 'unknown'
    
    def _infer_data_type_from_name(self, concept: str) -> str:
        """从概念名称推断数据类型"""
        concept_lower = concept.lower()
        if 'pershare' in concept_lower or 'earnings' in concept_lower and 'share' in concept_lower:
            return 'per_share'
        elif 'shares' in concept_lower:
            return 'shares'
        elif 'percentage' in concept_lower or 'rate' in concept_lower or 'ratio' in concept_lower:
            return 'ratio'
        else:
            return 'monetary'
    
    def _categorize_concept(self, concept: str) -> str:
        """将概念分类"""
        concept_lower = concept.lower()
        
        for category, keywords in self.concept_categories.items():
            for keyword in keywords:
                if keyword.lower() in concept_lower:
                    return category
        
        return 'other'
    
    def download_concepts(self, 
                         taxonomy: str = 'us-gaap',
                         with_definitions: bool = False,
                         category_filter: Optional[str] = None,
                         output_file: Optional[str] = None) -> pd.DataFrame:
        """
        下载US-GAAP概念数据
        
        Args:
            taxonomy: 分类标准
            with_definitions: 是否包含详细定义
            category_filter: 分类筛选器
            output_file: 输出文件路径
            
        Returns:
            包含概念数据的DataFrame
        """
        logger.info(f"开始下载 {taxonomy} 概念数据...")
        
        # 获取概念列表
        concepts = self.get_available_concepts(taxonomy)
        
        # 按分类筛选
        if category_filter:
            concepts = [c for c in concepts if self._categorize_concept(c) == category_filter]
            logger.info(f"按分类 '{category_filter}' 筛选后剩余 {len(concepts)} 个概念")
        
        # 收集概念数据
        concepts_data = []
        total = len(concepts)
        
        for i, concept in enumerate(concepts, 1):
            logger.info(f"处理概念 {i}/{total}: {concept}")
            
            if with_definitions:
                concept_info = self.get_concept_definition(concept, taxonomy)
            else:
                concept_info = self._get_basic_concept_info(concept, taxonomy)
            
            concepts_data.append(concept_info)
            
            # 控制请求频率
            if with_definitions and i % 10 == 0:
                logger.info(f"已处理 {i} 个概念，暂停2秒...")
                time.sleep(2)
        
        # 创建DataFrame
        df = pd.DataFrame(concepts_data)
        
        # 保存到文件
        if output_file:
            output_path = Path(output_file)
            if output_path.suffix.lower() == '.csv':
                df.to_csv(output_path, index=False, encoding='utf-8')
            elif output_path.suffix.lower() == '.json':
                df.to_json(output_path, orient='records', ensure_ascii=False, indent=2)
            elif output_path.suffix.lower() == '.xlsx':
                df.to_excel(output_path, index=False)
            
            logger.info(f"数据已保存到: {output_path}")
        
        return df
    
    def create_concept_dictionary(self, output_dir: str = "gaap_dictionary"):
        """创建完整的概念词典"""
        logger.info("创建US-GAAP概念词典...")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 下载完整概念数据
        full_df = self.download_concepts(
            taxonomy='us-gaap',
            with_definitions=True,
            output_file=output_path / "us_gaap_concepts_full.csv"
        )
        
        # 按分类保存
        for category in self.concept_categories.keys():
            category_df = full_df[full_df['category'] == category]
            if not category_df.empty:
                category_file = output_path / f"us_gaap_{category}_concepts.csv"
                category_df.to_csv(category_file, index=False, encoding='utf-8')
                logger.info(f"保存分类 '{category}': {len(category_df)} 个概念")
        
        # 创建摘要统计
        summary = {
            'total_concepts': len(full_df),
            'categories': full_df['category'].value_counts().to_dict(),
            'data_types': full_df['data_type'].value_counts().to_dict(),
            'with_chinese_names': len(full_df[full_df['chinese_name'] != '']),
            'with_definitions': len(full_df[full_df['chinese_definition'] != ''])
        }
        
        with open(output_path / "summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"概念词典已创建完成，保存在: {output_path}")
        logger.info(f"总概念数: {summary['total_concepts']}")
        
        return full_df

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='US-GAAP财务概念下载工具')
    
    parser.add_argument('--taxonomy', default='us-gaap', 
                       help='分类标准 (默认: us-gaap)')
    parser.add_argument('--output', '-o', 
                       help='输出文件路径 (支持 .csv, .json, .xlsx)')
    parser.add_argument('--concepts-only', action='store_true',
                       help='仅下载概念列表，不包含详细定义')
    parser.add_argument('--with-definitions', action='store_true',
                       help='包含详细定义和解释')
    parser.add_argument('--category', 
                       choices=['assets', 'liabilities', 'equity', 'revenue', 
                               'expenses', 'cash_flow', 'per_share', 'ratios'],
                       help='按分类筛选概念')
    parser.add_argument('--create-dictionary', action='store_true',
                       help='创建完整的概念词典')
    parser.add_argument('--user-agent', 
                       default="Ting Wang tting.wang@gmail.com",
                       help='用户代理字符串')
    
    args = parser.parse_args()
    
    try:
        # 初始化下载器
        downloader = USGAAPDownloader(user_agent=args.user_agent)
        
        if args.create_dictionary:
            # 创建完整词典
            downloader.create_concept_dictionary()
        else:
            # 下载指定概念
            with_definitions = args.with_definitions and not args.concepts_only
            
            df = downloader.download_concepts(
                taxonomy=args.taxonomy,
                with_definitions=with_definitions,
                category_filter=args.category,
                output_file=args.output
            )
            
            print(f"\n✅ 成功下载 {len(df)} 个概念")
            
            if not args.output:
                # 显示前几行数据
                print("\n概念预览:")
                print(df.head()[['concept', 'category', 'chinese_name']].to_string())
    
    except KeyboardInterrupt:
        print("\n⚠️  用户中断下载")
    except Exception as e:
        logger.error(f"下载失败: {e}")
        raise

if __name__ == "__main__":
    main()