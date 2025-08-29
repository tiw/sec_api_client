#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US-GAAP概念批量解释器

基于SEC XBRL taxonomy和实际公司数据，提供US-GAAP财务概念的详细解释
包括概念定义、数据类型、使用示例和会计准则上下文

功能特点：
1. 从SEC官方taxonomy获取概念标准定义
2. 分析实际公司使用该概念的数据模式
3. 提供中英文对照解释
4. 支持批量处理和导出
5. 包含估值分析相关的概念映射

作者: Ting Wang <tting.wang@gmail.com>
"""

import sys
import os
import pandas as pd
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import argparse

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from src import SECClient, XBRLFramesClient, ConceptExplainer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedGAAPExplainer:
    """增强版US-GAAP概念解释器"""
    
    def __init__(self, user_agent: str = "Ting Wang tting.wang@gmail.com"):
        """初始化解释器"""
        self.user_agent = user_agent
        self.sec_client = SECClient(user_agent=user_agent)
        self.xbrl_client = XBRLFramesClient(self.sec_client)
        self.concept_explainer = ConceptExplainer(user_agent=user_agent)
        
        # 示例公司CIK列表（用于获取概念使用示例）
        self.sample_companies = {
            "0000320193": "Apple Inc.",
            "0001318605": "Tesla, Inc.",
            "0000789019": "Microsoft Corporation",
            "0001652044": "Alphabet Inc.",
            "0001018724": "Amazon.com, Inc.",
            "0000051143": "International Business Machines Corporation",
            "0000066740": "General Electric Company",
            "0000019617": "JPMorgan Chase & Co."
        }
        
        # 估值分析相关概念分组
        self.valuation_concepts = {
            '估值水平': {
                '市盈率分子': ['EarningsPerShareBasic', 'EarningsPerShareDiluted'],
                '股息率': ['CommonStockDividendsPerShareDeclared', 'PaymentsOfDividends', 'Dividends'],
                '市现率': ['NetCashProvidedByUsedInOperatingActivities', 'DepreciationDepletionAndAmortization']
            },
            '企业价值': {
                '股东价值': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'NetIncomeLoss', 'PaymentsOfDividends'],
                '营收水平': ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'OperatingIncomeLoss'],
                '现金流水平': ['NetCashProvidedByUsedInOperatingActivities', 'DepreciationDepletionAndAmortization'],
                '净利润水平': ['NetIncomeLoss', 'IncomeTaxExpenseBenefit'],
                '资本结构': ['Assets', 'Liabilities', 'StockholdersEquity', 'LongTermDebtNoncurrent'],
                '资本回报率': ['NetIncomeLoss', 'StockholdersEquity', 'Assets']
            }
        }
    
    def get_concept_taxonomy_info(self, concept: str, taxonomy: str = 'us-gaap') -> Dict[str, Any]:
        """
        从SEC taxonomy获取概念的官方信息
        
        Args:
            concept: 概念名称
            taxonomy: 分类标准
            
        Returns:
            概念的taxonomy信息
        """
        try:
            # 构建taxonomy URL
            taxonomy_url = f"https://xbrl.sec.gov/dei/2023/dei-2023.xsd"
            if taxonomy == 'us-gaap':
                taxonomy_url = f"https://xbrl.fasb.org/us-gaap/2023/elts/us-gaap-2023.xsd"
            
            # 注意：实际实现中需要解析XSD文件，这里提供基本框架
            # 由于XSD解析比较复杂，我们主要依赖从实际数据中推断
            
            return {
                'taxonomy': taxonomy,
                'concept': concept,
                'standard_label': concept,
                'documentation': '',
                'data_type': 'unknown',
                'period_type': 'unknown',
                'balance': 'unknown'
            }
            
        except Exception as e:
            logger.warning(f"获取taxonomy信息失败: {e}")
            return {}
    
    def analyze_concept_usage(self, concept: str, taxonomy: str = 'us-gaap', 
                            sample_size: int = 3) -> Dict[str, Any]:
        """
        分析概念在实际公司中的使用情况
        
        Args:
            concept: 概念名称
            taxonomy: 分类标准
            sample_size: 分析的公司样本数量
            
        Returns:
            概念使用分析结果
        """
        usage_analysis = {
            'concept': concept,
            'taxonomy': taxonomy,
            'companies_using': [],
            'common_units': set(),
            'value_ranges': {},
            'filing_forms': set(),
            'reporting_patterns': {}
        }
        
        companies_analyzed = 0
        for cik, company_name in self.sample_companies.items():
            if companies_analyzed >= sample_size:
                break
                
            try:
                logger.info(f"分析 {company_name} 使用概念 {concept} 的情况...")
                
                concept_data = self.xbrl_client.get_company_concept_data(
                    cik=cik, concept=concept, taxonomy=taxonomy
                )
                
                if concept_data and 'units' in concept_data:
                    # 记录使用该概念的公司
                    company_info = {
                        'cik': cik,
                        'name': company_name,
                        'units_used': list(concept_data['units'].keys()),
                        'total_filings': len(concept_data.get('units', {}).get('USD', []) if 'USD' in concept_data.get('units', {}) else [])
                    }
                    usage_analysis['companies_using'].append(company_info)
                    
                    # 收集单位信息
                    usage_analysis['common_units'].update(concept_data['units'].keys())
                    
                    # 分析数值范围（以USD为例）
                    if 'USD' in concept_data['units']:
                        usd_data = concept_data['units']['USD']
                        values = [item.get('val', 0) for item in usd_data if isinstance(item.get('val'), (int, float))]
                        if values:
                            usage_analysis['value_ranges'][company_name] = {
                                'min': min(values),
                                'max': max(values),
                                'count': len(values)
                            }
                    
                    # 收集报告表格信息
                    for unit_data in concept_data['units'].values():
                        for item in unit_data:
                            if 'form' in item:
                                usage_analysis['filing_forms'].add(item['form'])
                    
                    companies_analyzed += 1
                elif concept_data is None:
                    logger.info(f"  → {company_name} 未使用概念 {concept}")
                
                time.sleep(0.1)  # 控制请求频率
                
            except Exception as e:
                logger.warning(f"  → 分析公司 {company_name} 失败: {e}")
                continue
        
        # 转换集合为列表以便JSON序列化
        usage_analysis['common_units'] = list(usage_analysis['common_units'])
        usage_analysis['filing_forms'] = list(usage_analysis['filing_forms'])
        
        return usage_analysis
    
    def get_comprehensive_explanation(self, concept: str, taxonomy: str = 'us-gaap') -> Dict[str, Any]:
        """
        获取概念的综合解释
        
        Args:
            concept: 概念名称
            taxonomy: 分类标准
            
        Returns:
            综合解释信息
        """
        logger.info(f"生成概念 {concept} 的综合解释...")
        
        explanation = {
            'concept': concept,
            'taxonomy': taxonomy,
            'timestamp': datetime.now().isoformat(),
            'basic_info': {},
            'taxonomy_info': {},
            'usage_analysis': {},
            'valuation_context': {},
            'chinese_info': {},
            'examples': []
        }
        
        try:
            # 1. 基本信息
            explanation['basic_info'] = {
                'concept_name': concept,
                'standard_name': concept,
                'category': self._categorize_concept(concept),
                'data_type': self._infer_data_type_from_name(concept)
            }
            
            # 2. 从内置知识库获取中文信息
            # 扩展的中文翻译
            additional_chinese_names = {
                'AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedLossBeforeTax': '可供出售债务证券累计未实现损失（税前）',
                'AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedGainBeforeTax': '可供出售债务证券累计未实现收益（税前）',
                'MarketableSecuritiesCurrent': '流动有价证券',
                'MarketableSecuritiesNoncurrent': '非流动有价证券',
                'TradingSecurities': '交易性证券',
                'HeldToMaturitySecurities': '持有至到期证券',
                'AccumulatedOtherComprehensiveIncomeLossNetOfTax': '其他综合收益累计额（税后净额）'
            }
            
            additional_chinese_definitions = {
                'AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedLossBeforeTax': '企业持有的可供出售债务证券因市场价格变动产生的累计未实现损失，未考虑所得税影响。这些损失计入其他综合收益，当证券出售时才会转入损益表。',
                'AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedGainBeforeTax': '企业持有的可供出售债务证券因市场价格变动产生的累计未实现收益，未考虑所得税影响。',
                'MarketableSecuritiesCurrent': '企业持有的可在短期内变现的有价证券，包括股票、债券等金融工具，属于流动资产。',
                'MarketableSecuritiesNoncurrent': '企业持有的计划长期持有的有价证券，不打算在一年内出售，属于非流动资产。',
                'TradingSecurities': '企业为了短期买卖获利而持有的证券，公允价值变动直接计入当期损益。',
                'HeldToMaturitySecurities': '企业有明确意图和能力持有至到期的债务证券，以摊余成本计量。',
                'AccumulatedOtherComprehensiveIncomeLossNetOfTax': '企业其他综合收益的累计金额，已扣除相关所得税影响。'
            }
            
            chinese_name = (self.concept_explainer.CONCEPT_CHINESE_NAMES.get(concept, '') or 
                          additional_chinese_names.get(concept, ''))
            chinese_definition = (self.concept_explainer.CONCEPT_DEFINITIONS.get(concept, '') or 
                                additional_chinese_definitions.get(concept, ''))
            
            explanation['chinese_info'] = {
                'chinese_name': chinese_name,
                'chinese_definition': chinese_definition,
                'english_explanation': self.concept_explainer.CONCEPT_ENGLISH_EXPLANATIONS.get(concept, '')
            }
            
            # 3. Taxonomy信息
            explanation['taxonomy_info'] = self.get_concept_taxonomy_info(concept, taxonomy)
            
            # 4. 使用情况分析
            explanation['usage_analysis'] = self.analyze_concept_usage(concept, taxonomy)
            
            # 5. 估值分析上下文
            explanation['valuation_context'] = self._get_valuation_context(concept)
            
            # 6. 获取具体数据示例
            explanation['examples'] = self._get_concept_examples(concept, taxonomy)
            
        except Exception as e:
            logger.error(f"生成综合解释失败: {e}")
            explanation['error'] = str(e)
        
        return explanation
    
    def _categorize_concept(self, concept: str) -> str:
        """概念分类"""
        concept_lower = concept.lower()
        
        # 证券投资相关
        if any(keyword in concept_lower for keyword in ['securities', 'marketablesecurities', 'availableforsale', 'heldtomaturity', 'trading']):
            return 'securities'
        # 资产类
        elif any(keyword in concept_lower for keyword in ['assets', 'cash', 'receivable', 'inventory', 'property', 'equipment']):
            return 'assets'
        # 负债类  
        elif any(keyword in concept_lower for keyword in ['liabilities', 'debt', 'payable', 'accrued']):
            return 'liabilities'
        # 权益类
        elif any(keyword in concept_lower for keyword in ['equity', 'stock', 'capital', 'retained']):
            return 'equity'
        # 收入类
        elif any(keyword in concept_lower for keyword in ['revenue', 'sales', 'income']) and 'expense' not in concept_lower:
            return 'revenue'
        # 费用类
        elif any(keyword in concept_lower for keyword in ['expense', 'cost', 'depreciation', 'amortization', 'loss']) and 'income' not in concept_lower:
            return 'expenses'
        # 现金流类
        elif 'cashflow' in concept_lower or ('cash' in concept_lower and 'activities' in concept_lower):
            return 'cash_flow'
        # 每股数据
        elif 'pershare' in concept_lower or ('earnings' in concept_lower and 'share' in concept_lower):
            return 'per_share'
        # 其他综合收益相关
        elif any(keyword in concept_lower for keyword in ['comprehensive', 'unrealized', 'accumulated']):
            return 'other_comprehensive_income'
        else:
            return 'other'
    
    def _infer_data_type_from_name(self, concept: str) -> str:
        """从概念名称推断数据类型"""
        concept_lower = concept.lower()
        
        if 'pershare' in concept_lower:
            return 'monetary_per_share'
        elif 'shares' in concept_lower and any(kw in concept_lower for kw in ['outstanding', 'issued', 'authorized']):
            return 'shares_count'
        elif any(keyword in concept_lower for keyword in ['percentage', 'rate', 'ratio']):
            return 'percentage'
        elif any(keyword in concept_lower for keyword in ['assets', 'liabilities', 'revenue', 'income', 'cash', 'securities', 'debt', 'equity', 'expense', 'cost', 'gain', 'loss']):
            return 'monetary'
        elif 'date' in concept_lower or 'period' in concept_lower:
            return 'date'
        elif 'text' in concept_lower or 'description' in concept_lower:
            return 'text'
        else:
            return 'unknown'
    
    def _get_valuation_context(self, concept: str) -> Dict[str, Any]:
        """获取估值分析上下文"""
        context = {
            'valuation_relevance': 'none',
            'analysis_category': '',
            'related_concepts': [],
            'calculation_role': ''
        }
        
        # 检查是否与估值分析相关
        for analysis_type, categories in self.valuation_concepts.items():
            for category, concepts in categories.items():
                if concept in concepts:
                    context['valuation_relevance'] = 'high'
                    context['analysis_category'] = f"{analysis_type} - {category}"
                    context['related_concepts'] = [c for c in concepts if c != concept]
                    
                    # 根据估值分析规范添加说明
                    if analysis_type == '估值水平':
                        if '市盈率' in category:
                            context['calculation_role'] = '市盈率分子，用于估值水平判断的核心指标'
                        elif '股息率' in category:
                            context['calculation_role'] = '股息率计算，以国债收益率为判断基准的辅助指标'
                        elif '市现率' in category:
                            context['calculation_role'] = '市现率计算，作为利润操控辅助判断指标'
                    
                    break
        
        return context
    
    def _get_concept_examples(self, concept: str, taxonomy: str, limit: int = 3) -> List[Dict]:
        """获取概念使用示例"""
        examples = []
        
        try:
            # 使用Apple作为示例
            apple_cik = "0000320193"
            concept_data = self.xbrl_client.get_company_concept_data(
                cik=apple_cik, concept=concept, taxonomy=taxonomy
            )
            
            if concept_data and 'units' in concept_data:
                # 获取最近的几个数据点
                for unit, unit_data in concept_data['units'].items():
                    if len(examples) >= limit:
                        break
                    
                    # 按日期排序，获取最新数据
                    sorted_data = sorted(unit_data, key=lambda x: x.get('end', ''), reverse=True)
                    
                    for item in sorted_data[:2]:  # 每个单位取2个最新示例
                        if len(examples) >= limit:
                            break
                        
                        example = {
                            'company': 'Apple Inc.',
                            'cik': apple_cik,
                            'value': item.get('val'),
                            'unit': unit,
                            'end_date': item.get('end'),
                            'start_date': item.get('start'),
                            'form': item.get('form'),
                            'filed': item.get('filed'),
                            'formatted_value': self._format_value(item.get('val'), unit)
                        }
                        examples.append(example)
        
        except Exception as e:
            logger.warning(f"获取概念示例失败: {e}")
        
        return examples
    
    def _format_value(self, value: Any, unit: str) -> str:
        """格式化数值显示"""
        if value is None:
            return 'N/A'
        
        try:
            if unit == 'USD' and isinstance(value, (int, float)):
                if abs(value) >= 1e9:
                    return f"${value/1e9:.2f}B"
                elif abs(value) >= 1e6:
                    return f"${value/1e6:.2f}M"
                elif abs(value) >= 1e3:
                    return f"${value/1e3:.2f}K"
                else:
                    return f"${value:,.2f}"
            elif unit == 'shares' and isinstance(value, (int, float)):
                if abs(value) >= 1e9:
                    return f"{value/1e9:.2f}B shares"
                elif abs(value) >= 1e6:
                    return f"{value/1e6:.2f}M shares"
                else:
                    return f"{value:,.0f} shares"
            elif 'USD/shares' in unit and isinstance(value, (int, float)):
                return f"${value:.2f} per share"
            else:
                return str(value)
        except:
            return str(value)
    
    def batch_explain_concepts(self, concepts: List[str], 
                              taxonomy: str = 'us-gaap',
                              output_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        批量解释概念
        
        Args:
            concepts: 概念列表
            taxonomy: 分类标准
            output_file: 输出文件路径
            
        Returns:
            概念解释列表
        """
        logger.info(f"开始批量解释 {len(concepts)} 个概念...")
        
        explanations = []
        total = len(concepts)
        
        for i, concept in enumerate(concepts, 1):
            logger.info(f"处理概念 {i}/{total}: {concept}")
            
            try:
                explanation = self.get_comprehensive_explanation(concept, taxonomy)
                explanations.append(explanation)
                
                # 控制请求频率
                if i % 5 == 0:
                    logger.info(f"已处理 {i} 个概念，暂停1秒...")
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"处理概念 {concept} 失败: {e}")
                # 添加错误记录
                explanations.append({
                    'concept': concept,
                    'taxonomy': taxonomy,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # 保存结果
        if output_file:
            output_path = Path(output_file)
            
            if output_path.suffix.lower() == '.json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(explanations, f, ensure_ascii=False, indent=2)
            elif output_path.suffix.lower() == '.csv':
                # 转换为表格格式
                df_data = []
                for exp in explanations:
                    row = {
                        'concept': exp.get('concept', ''),
                        'taxonomy': exp.get('taxonomy', ''),
                        'chinese_name': exp.get('chinese_info', {}).get('chinese_name', ''),
                        'chinese_definition': exp.get('chinese_info', {}).get('chinese_definition', ''),
                        'category': exp.get('basic_info', {}).get('category', ''),
                        'data_type': exp.get('basic_info', {}).get('data_type', ''),
                        'valuation_relevance': exp.get('valuation_context', {}).get('valuation_relevance', ''),
                        'analysis_category': exp.get('valuation_context', {}).get('analysis_category', ''),
                        'companies_using_count': len(exp.get('usage_analysis', {}).get('companies_using', [])),
                        'common_units': ', '.join(exp.get('usage_analysis', {}).get('common_units', [])),
                        'error': exp.get('error', '')
                    }
                    df_data.append(row)
                
                df = pd.DataFrame(df_data)
                df.to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"结果已保存到: {output_path}")
        
        return explanations

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='US-GAAP概念批量解释器')
    
    parser.add_argument('--concepts', nargs='+', 
                       help='要解释的概念列表')
    parser.add_argument('--concepts-file', 
                       help='包含概念列表的文件路径（每行一个概念）')
    parser.add_argument('--taxonomy', default='us-gaap',
                       help='分类标准 (默认: us-gaap)')
    parser.add_argument('--output', '-o',
                       help='输出文件路径 (支持 .json, .csv)')
    parser.add_argument('--single-concept',
                       help='解释单个概念并显示详细信息')
    parser.add_argument('--valuation-concepts', action='store_true',
                       help='解释所有估值分析相关概念')
    parser.add_argument('--user-agent',
                       default="Ting Wang tting.wang@gmail.com",
                       help='用户代理字符串')
    
    args = parser.parse_args()
    
    try:
        # 初始化解释器
        explainer = EnhancedGAAPExplainer(user_agent=args.user_agent)
        
        if args.single_concept:
            # 单个概念详细解释
            explanation = explainer.get_comprehensive_explanation(args.single_concept, args.taxonomy)
            
            print(f"\n📊 概念详细解释: {args.single_concept}")
            print("=" * 60)
            
            # 基本信息
            basic_info = explanation.get('basic_info', {})
            category = basic_info.get('category', 'N/A')
            data_type = basic_info.get('data_type', 'N/A')
            
            # 添加分类说明
            category_descriptions = {
                'securities': '证券投资',
                'assets': '资产',
                'liabilities': '负债',
                'equity': '权益',
                'revenue': '收入',
                'expenses': '费用',
                'cash_flow': '现金流',
                'per_share': '每股数据',
                'other_comprehensive_income': '其他综合收益',
                'other': '其他'
            }
            
            category_desc = category_descriptions.get(category, category)
            print(f"分类: {category_desc} ({category})")
            print(f"数据类型: {data_type}")
            
            # 中文信息
            chinese_info = explanation.get('chinese_info', {})
            if chinese_info.get('chinese_name'):
                print(f"中文名称: {chinese_info['chinese_name']}")
            if chinese_info.get('chinese_definition'):
                print(f"中文定义: {chinese_info['chinese_definition']}")
            
            # 估值分析上下文
            valuation = explanation.get('valuation_context', {})
            if valuation.get('valuation_relevance') != 'none':
                print(f"估值分析相关性: {valuation.get('analysis_category', 'N/A')}")
                print(f"计算作用: {valuation.get('calculation_role', 'N/A')}")
            
            # 使用情况
            usage = explanation.get('usage_analysis', {})
            companies_using = usage.get('companies_using', [])
            if companies_using:
                print(f"使用该概念的公司数: {len(companies_using)}")
                print(f"常见单位: {', '.join(usage.get('common_units', []))}")
            
            # 示例
            examples = explanation.get('examples', [])
            if examples:
                print(f"\n数据示例:")
                for example in examples[:3]:
                    print(f"  {example['company']}: {example['formatted_value']} ({example['end_date']})")
            
            # 保存详细结果
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(explanation, f, ensure_ascii=False, indent=2)
                print(f"\n详细结果已保存到: {args.output}")
        
        elif args.valuation_concepts:
            # 解释所有估值分析相关概念
            all_valuation_concepts = []
            for analysis_type, categories in explainer.valuation_concepts.items():
                for category, concepts in categories.items():
                    all_valuation_concepts.extend(concepts)
            
            # 去重
            unique_concepts = list(set(all_valuation_concepts))
            
            print(f"解释 {len(unique_concepts)} 个估值分析相关概念...")
            explainer.batch_explain_concepts(
                concepts=unique_concepts,
                taxonomy=args.taxonomy,
                output_file=args.output or 'valuation_concepts_explained.json'
            )
        
        else:
            # 批量解释
            concepts_to_explain = []
            
            if args.concepts:
                concepts_to_explain.extend(args.concepts)
            
            if args.concepts_file:
                with open(args.concepts_file, 'r', encoding='utf-8') as f:
                    file_concepts = [line.strip() for line in f if line.strip()]
                    concepts_to_explain.extend(file_concepts)
            
            if not concepts_to_explain:
                print("请提供要解释的概念列表")
                return
            
            explainer.batch_explain_concepts(
                concepts=concepts_to_explain,
                taxonomy=args.taxonomy,
                output_file=args.output
            )
    
    except KeyboardInterrupt:
        print("\n⚠️  用户中断处理")
    except Exception as e:
        logger.error(f"处理失败: {e}")
        raise

if __name__ == "__main__":
    main()