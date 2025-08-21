#!/usr/bin/env python3
"""
批量获取SEC公司财务数据脚本

该脚本可以批量获取多个公司的近五年财务数据，并进行基本分析。
符合SEC API调用规范，包括User-Agent设置和请求频率限制。
"""

import sys
import os
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.sec_client import SECClient
from src.xbrl_frames import XBRLFramesClient
from src.financial_analyzer import FinancialAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_fetch_log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 财务概念定义
FINANCIAL_CONCEPTS = {
    'income_statement': {
        'Revenues': '营收',
        'RevenueFromContractWithCustomerExcludingAssessedTax': '销售收入',
        'CostOfRevenue': '销售成本',
        'GrossProfit': '毛利润',
        'OperatingIncomeLoss': '营业利润',
        'NetIncomeLoss': '净利润',
        'EarningsPerShareBasic': '基本每股收益',
        'EarningsPerShareDiluted': '稀释每股收益',
        'DepreciationDepletionAndAmortization': '折旧摊销'
    },
    'balance_sheet': {
        'Assets': '总资产',
        'AssetsCurrent': '流动资产',
        'CashAndCashEquivalentsAtCarryingValue': '现金及现金等价物',
        'AccountsReceivableNetCurrent': '应收账款净额',
        'InventoryNet': '存货净额',
        'Liabilities': '总负债',
        'LiabilitiesCurrent': '流动负债',
        'AccountsPayableCurrent': '应付账款',
        'LongTermDebtNoncurrent': '长期债务',
        'StockholdersEquity': '股东权益',
        'CommonStockSharesIssued': '发行的普通股股数',
        'RetainedEarningsAccumulatedDeficit': '留存收益'
    },
    'cash_flow': {
        'NetCashProvidedByUsedInOperatingActivities': '经营活动现金流',
        'NetCashProvidedByUsedInInvestingActivities': '投资活动现金流',
        'NetCashProvidedByUsedInFinancingActivities': '筹资活动现金流',
        'PaymentsToAcquirePropertyPlantAndEquipment': '购买固定资产支出',
        'PaymentsOfDividends': '支付股息',
        'PaymentsForRepurchaseOfCommonStock': '回购股票支出'
    }
}

class BatchSECDataFetcher:
    """批量获取SEC数据的类"""
    
    def __init__(self, user_agent: str):
        """
        初始化批量获取器
        
        Args:
            user_agent: 用户代理字符串，必须符合SEC要求
        """
        self.sec_client = SECClient(user_agent=user_agent)
        self.xbrl_client = XBRLFramesClient(self.sec_client)
        self.analyzer = FinancialAnalyzer()
        self.companies_data = {}
        self.error_log = []
        
    def get_company_info(self, cik: str) -> Optional[Dict]:
        """
        获取公司基本信息
        
        Args:
            cik: 公司CIK号码
            
        Returns:
            公司信息字典或None
        """
        try:
            logger.info(f"获取公司 {cik} 基本信息")
            submissions = self.sec_client.get_company_submissions(cik)
            company_info = {
                'cik': cik,
                'name': submissions.get('name', 'Unknown'),
                'ticker': submissions.get('tickers', ['Unknown'])[0] if submissions.get('tickers') else 'Unknown'
            }
            logger.info(f"公司信息: {company_info}")
            return company_info
        except Exception as e:
            error_msg = f"获取公司 {cik} 信息失败: {str(e)}"
            logger.error(error_msg)
            self.error_log.append({
                'type': 'company_info_error',
                'cik': cik,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return None
    
    def get_company_financial_data(self, cik: str, years: int = 5) -> Dict:
        """
        获取公司财务数据
        
        Args:
            cik: 公司CIK号码
            years: 获取年数，默认5年
            
        Returns:
            财务数据字典
        """
        financial_data = {}
        current_year = datetime.now().year
        
        logger.info(f"开始获取公司 {cik} 近 {years} 年财务数据")
        
        for category, concepts in FINANCIAL_CONCEPTS.items():
            logger.info(f"处理 {category} 数据")
            category_data = {}
            
            for concept, chinese_name in concepts.items():
                try:
                    logger.info(f"  获取概念 {concept} ({chinese_name})")
                    concept_data = self.xbrl_client.get_company_concept_data(
                        cik=cik,
                        concept=concept
                    )
                    
                    if concept_data and 'units' in concept_data:
                        # 确定单位
                        unit_key = 'USD'
                        if concept in ['EarningsPerShareBasic', 'EarningsPerShareDiluted']:
                            unit_key = 'USD/shares'
                        elif concept in ['WeightedAverageNumberOfSharesOutstandingBasic', 
                                       'WeightedAverageNumberOfDilutedSharesOutstanding', 
                                       'CommonStockSharesIssued']:
                            unit_key = 'shares'
                        
                        unit_data = concept_data['units'].get(unit_key, [])
                        
                        # 尝试查找其他可能的单位
                        if not unit_data:
                            for possible_unit in concept_data['units'].keys():
                                if concept in ['EarningsPerShareBasic', 'EarningsPerShareDiluted']:
                                    if 'shares' in possible_unit.lower() or 'per' in possible_unit.lower():
                                        unit_data = concept_data['units'][possible_unit]
                                        unit_key = possible_unit
                                        break
                                elif concept in ['CommonStockSharesIssued']:
                                    if 'shares' in possible_unit.lower():
                                        unit_data = concept_data['units'][possible_unit]
                                        unit_key = possible_unit
                                        break
                        
                        if unit_data:
                            # 筛选近N年的数据
                            recent_data = []
                            for item in unit_data:
                                end_date = item.get('end', '')
                                if end_date:
                                    try:
                                        end_year = datetime.fromisoformat(end_date.replace('Z', '')).year
                                        if current_year - end_year < years:
                                            recent_data.append(item)
                                    except ValueError:
                                        pass  # 日期格式不正确
                            
                            category_data[concept] = {
                                'chinese_name': chinese_name,
                                'unit': unit_key,
                                'data': recent_data
                            }
                        else:
                            logger.warning(f"    未找到 {concept} 的 {unit_key} 单位数据")
                            self.error_log.append({
                                'type': 'missing_unit_data',
                                'cik': cik,
                                'concept': concept,
                                'unit': unit_key,
                                'timestamp': datetime.now().isoformat()
                            })
                    else:
                        logger.warning(f"    未找到 {concept} 的数据")
                        self.error_log.append({
                            'type': 'missing_concept_data',
                            'cik': cik,
                            'concept': concept,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    error_msg = f"获取概念 {concept} 失败: {str(e)}"
                    logger.error(error_msg)
                    self.error_log.append({
                        'type': 'concept_fetch_error',
                        'cik': cik,
                        'concept': concept,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            
            financial_data[category] = category_data
        
        return financial_data
    
    def calculate_metrics(self, financial_data: Dict) -> List[Dict]:
        """
        计算财务指标
        
        Args:
            financial_data: 财务数据
            
        Returns:
            计算的指标列表
        """
        metrics = []
        
        # 获取最新年度的数据用于计算
        latest_year_data = {}
        for category, concepts in financial_data.items():
            for concept, data in concepts.items():
                if data.get('data'):
                    # 获取最新的年度数据
                    annual_data = [item for item in data['data'] if item.get('fp') == 'FY']
                    if annual_data:
                        latest = max(annual_data, key=lambda x: x.get('end', ''))
                        latest_year_data[concept] = {
                            'value': latest.get('val', 0),
                            'end': latest.get('end', ''),
                            'fy': latest.get('fy', '')
                        }
        
        # 计算基本财务指标
        try:
            # EBITDA = OperatingIncomeLoss + DepreciationDepletionAndAmortization
            if 'OperatingIncomeLoss' in latest_year_data and 'DepreciationDepletionAndAmortization' in latest_year_data:
                ebitda = latest_year_data['OperatingIncomeLoss']['value'] + latest_year_data['DepreciationDepletionAndAmortization']['value']
                metrics.append({
                    'metric_name': 'EBITDA',
                    'formula': 'OperatingIncomeLoss + DepreciationDepletionAndAmortization',
                    'value': ebitda,
                    'year': latest_year_data['OperatingIncomeLoss']['fy']
                })
            
            # 净利润率
            if 'NetIncomeLoss' in latest_year_data and 'RevenueFromContractWithCustomerExcludingAssessedTax' in latest_year_data:
                net_margin = latest_year_data['NetIncomeLoss']['value'] / latest_year_data['RevenueFromContractWithCustomerExcludingAssessedTax']['value']
                metrics.append({
                    'metric_name': '净利润率',
                    'formula': 'NetIncomeLoss / RevenueFromContractWithCustomerExcludingAssessedTax',
                    'value': net_margin,
                    'year': latest_year_data['NetIncomeLoss']['fy']
                })
                
        except Exception as e:
            logger.error(f"计算财务指标时出错: {str(e)}")
            self.error_log.append({
                'type': 'metric_calculation_error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        
        return metrics
    
    def save_company_data(self, company_info: Dict, financial_data: Dict, metrics: List[Dict]):
        """
        保存公司数据到文件
        
        Args:
            company_info: 公司信息
            financial_data: 财务数据
            metrics: 计算的指标
        """
        cik = company_info['cik']
        ticker = company_info['ticker']
        company_name = company_info['name']
        
        # 创建公司目录
        company_dir = f"batch_data/{ticker}_{cik}"
        os.makedirs(company_dir, exist_ok=True)
        
        # 保存公司信息
        with open(f"{company_dir}/company_info.json", 'w', encoding='utf-8') as f:
            json.dump(company_info, f, ensure_ascii=False, indent=2)
        
        # 保存原始财务数据
        all_data_rows = []
        for category, concepts in financial_data.items():
            for concept, data in concepts.items():
                for item in data.get('data', []):
                    row = {
                        'concept': concept,
                        'category': category,
                        'chinese_name': data['chinese_name'],
                        'unit': data['unit'],
                        'value': item.get('val', ''),
                        'end_date': item.get('end', ''),
                        'start_date': item.get('start', ''),
                        'form': item.get('form', ''),
                        'fiscal_year': item.get('fy', ''),
                        'fiscal_period': item.get('fp', '')
                    }
                    all_data_rows.append(row)
        
        if all_data_rows:
            df = pd.DataFrame(all_data_rows)
            df.to_csv(f"{company_dir}/financial_data.csv", index=False, encoding='utf-8')
            
            # 按类别保存
            for category in FINANCIAL_CONCEPTS.keys():
                category_df = df[df['category'] == category]
                if not category_df.empty:
                    category_df.to_csv(f"{company_dir}/{category}.csv", index=False, encoding='utf-8')
        
        # 保存计算的指标
        if metrics:
            metrics_df = pd.DataFrame(metrics)
            metrics_df.to_csv(f"{company_dir}/calculated_metrics.csv", index=False, encoding='utf-8')
        
        logger.info(f"公司 {ticker} ({cik}) 数据已保存到 {company_dir}")
    
    def fetch_companies_data(self, cik_list: List[str]):
        """
        批量获取公司数据
        
        Args:
            cik_list: 公司CIK号码列表
        """
        logger.info(f"开始批量获取 {len(cik_list)} 家公司数据")
        
        for i, cik in enumerate(cik_list):
            logger.info(f"处理第 {i+1}/{len(cik_list)} 家公司: {cik}")
            
            try:
                # 获取公司信息
                company_info = self.get_company_info(cik)
                if not company_info:
                    continue
                
                # 获取财务数据
                financial_data = self.get_company_financial_data(cik)
                
                # 计算指标
                metrics = self.calculate_metrics(financial_data)
                
                # 保存数据
                self.save_company_data(company_info, financial_data, metrics)
                
                # 存储到内存中
                self.companies_data[cik] = {
                    'info': company_info,
                    'financial_data': financial_data,
                    'metrics': metrics
                }
                
                logger.info(f"公司 {cik} 数据处理完成")
                
                # 避免请求过于频繁
                if i < len(cik_list) - 1:  # 不是最后一个
                    time.sleep(0.2)  # 等待200ms
                    
            except Exception as e:
                error_msg = f"处理公司 {cik} 时发生错误: {str(e)}"
                logger.error(error_msg)
                self.error_log.append({
                    'type': 'company_processing_error',
                    'cik': cik,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # 保存错误日志
        if self.error_log:
            with open('batch_fetch_errors.json', 'w', encoding='utf-8') as f:
                json.dump(self.error_log, f, ensure_ascii=False, indent=2)
        
        logger.info("批量数据获取完成")
    
    def generate_analysis_report(self) -> str:
        """
        生成分析报告
        
        Returns:
            分析报告内容
        """
        report = []
        report.append("# 批量数据获取分析报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 总体统计
        total_companies = len(self.companies_data)
        report.append(f"## 总体统计")
        report.append(f"- 处理公司总数: {total_companies}")
        report.append(f"- 错误记录数: {len(self.error_log)}")
        report.append("")
        
        # 错误分析
        if self.error_log:
            report.append("## 错误分析")
            
            # 按错误类型统计
            error_types = {}
            for error in self.error_log:
                error_type = error.get('type', 'unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            report.append("### 错误类型统计")
            for error_type, count in error_types.items():
                report.append(f"- {error_type}: {count}")
            report.append("")
            
            # 详细错误记录
            report.append("### 详细错误记录")
            for i, error in enumerate(self.error_log, 1):
                report.append(f"{i}. 类型: {error.get('type', 'unknown')}")
                report.append(f"   时间: {error.get('timestamp', 'unknown')}")
                if 'cik' in error:
                    report.append(f"   公司: {error['cik']}")
                if 'concept' in error:
                    report.append(f"   概念: {error['concept']}")
                if 'error' in error:
                    report.append(f"   错误: {error['error']}")
                report.append("")
        
        # 数据完整性分析
        report.append("## 数据完整性分析")
        for cik, data in self.companies_data.items():
            ticker = data['info'].get('ticker', 'Unknown')
            name = data['info'].get('name', 'Unknown')
            report.append(f"### {ticker} ({cik}) - {name}")
            
            # 统计各类别数据完整性
            for category, concepts in FINANCIAL_CONCEPTS.items():
                available_concepts = len(data['financial_data'].get(category, {}))
                total_concepts = len(concepts)
                report.append(f"  {category}: {available_concepts}/{total_concepts}")
            
            # 指标计算情况
            metrics_count = len(data.get('metrics', []))
            report.append(f"  计算指标数: {metrics_count}")
            report.append("")
        
        return "\n".join(report)

def main():
    """主函数"""
    # SEC要求的User-Agent
    USER_AGENT = "Batch SEC Data Fetcher (your-email@example.com)"
    
    # 要获取数据的公司CIK列表（示例）
    CIK_LIST = [
        "0000320193",  # Apple Inc.
        "0000789019",  # Microsoft Corp
        "0001652044",  # Alphabet Inc.
        "0001018724",  # Amazon.com Inc
        "0001045810"   # NVIDIA Corp
    ]
    
    # 创建批量获取器
    fetcher = BatchSECDataFetcher(USER_AGENT)
    
    # 获取数据
    fetcher.fetch_companies_data(CIK_LIST)
    
    # 生成分析报告
    report = fetcher.generate_analysis_report()
    
    # 保存报告
    with open('batch_fetch_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("批量数据获取完成，分析报告已生成: batch_fetch_analysis_report.md")
    print("错误日志已保存: batch_fetch_errors.json")

if __name__ == "__main__":
    main()