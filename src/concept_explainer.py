#!/usr/bin/env python3
"""
SEC XBRL财务概念口径解释CLI工具

根据财务指标名称和公司CIK获取其详细定义和口径解释
User-Agent: Ting Wang <tting.wang@gmail.com>
"""

import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, XBRLFramesClient
import argparse


class ConceptExplainer:
    """财务概念解释器"""
    
    # 常见概念的中文名称映射
    CONCEPT_CHINESE_NAMES = {
        'PaymentsToAcquirePropertyPlantAndEquipment': '购建固定资产支出',
        'CommercialPaper': '商业票据',
        'LongTermDebtCurrent': '一年内到期的长期债务',
        'LongTermDebtNoncurrent': '长期债务',
        'MarketableSecuritiesCurrent': '流动有价证券',
        'Cash': '现金',
        'CashAndCashEquivalentsAtCarryingValue': '现金及现金等价物',
        'AccountsReceivableNetCurrent': '应收账款净额',
        'InventoryNet': '存货净额',
        'Assets': '总资产',
        'AssetsCurrent': '流动资产',
        'AssetsNoncurrent': '非流动资产',
        'Liabilities': '总负债',
        'LiabilitiesCurrent': '流动负债',
        'LiabilitiesNoncurrent': '非流动负债',
        'AccountsPayableCurrent': '应付账款',
        'StockholdersEquity': '股东权益',
        'RetainedEarningsAccumulatedDeficit': '留存收益',
        'Revenues': '营收',
        'RevenueFromContractWithCustomerExcludingAssessedTax': '客户合同收入',
        'CostOfRevenue': '销售成本',
        'GrossProfit': '毛利润',
        'OperatingExpenses': '营业费用',
        'OperatingIncomeLoss': '营业利润',
        'NetIncomeLoss': '净利润',
        'EarningsPerShareBasic': '基本每股收益',
        'EarningsPerShareDiluted': '稀释每股收益',
        'NetCashProvidedByUsedInOperatingActivities': '经营活动现金流',
        'NetCashProvidedByUsedInInvestingActivities': '投资活动现金流',
        'NetCashProvidedByUsedInFinancingActivities': '融资活动现金流',
        'DepreciationDepletionAndAmortization': '折旧摊销',
        'ShareBasedCompensation': '股权激励费用',
        'PaymentsOfDividends': '支付股息',
        'PaymentsForRepurchaseOfCommonStock': '回购股票支出'
    }
    
    # 常见概念的定义映射
    CONCEPT_DEFINITIONS = {
        'PaymentsToAcquirePropertyPlantAndEquipment': '企业为购买、建造和资本化厂房设备而发生的现金支出，通常出现在现金流量表的投资活动部分',
        'CommercialPaper': '企业发行的无抵押短期债务工具，通常用于筹集应收账款和库存资金',
        'LongTermDebtCurrent': '一年内到期的长期债务，属于流动负债',
        'LongTermDebtNoncurrent': '长期债务中到期日超过一年的部分，属于非流动负债',
        'MarketableSecuritiesCurrent': '可在短期内变现的有价证券，属于流动资产',
        'Cash': '企业的现金及现金等价物',
        'CashAndCashEquivalentsAtCarryingValue': '包括现金、银行活期存款以及其他可以随时用于支付的货币资金',
        'AccountsReceivableNetCurrent': '企业因销售商品或提供劳务等经营活动应收取的款项净额',
        'InventoryNet': '企业在日常活动中持有以备出售的产成品或商品、处在生产过程中的在产品等净额',
        'Assets': '企业拥有或控制的能以货币计量的经济资源',
        'AssetsCurrent': '预计在一年内或超过一年的一个营业周期内变现或耗用的资产',
        'AssetsNoncurrent': '不能在一年内或超过一年的一个营业周期内变现或耗用的资产',
        'Liabilities': '企业由于过去的交易或事项而承担的现时义务',
        'LiabilitiesCurrent': '预计在一年内或超过一年的一个营业周期内偿还的债务',
        'LiabilitiesNoncurrent': '偿还期在一年以上或超过一年的一个营业周期以上的债务',
        'AccountsPayableCurrent': '企业因购买材料、商品或接受劳务供应等经营活动应支付的款项',
        'StockholdersEquity': '企业资产扣除负债后由所有者享有的剩余权益',
        'RetainedEarningsAccumulatedDeficit': '企业历年实现的净利润弥补亏损、提取盈余公积和向投资者分配利润后留存在企业的、历年结存的利润',
        'Revenues': '企业在日常活动中形成的、会导致所有者权益增加的、与所有者投入资本无关的经济利益的总流入',
        'RevenueFromContractWithCustomerExcludingAssessedTax': '企业与客户签订合同后，因履行合同义务而应收取的对价总额，不包括代第三方收取的税款',
        'CostOfRevenue': '企业为生产产品、提供劳务等发生的可归属于产品成本、劳务成本等的费用',
        'GrossProfit': '营业收入与营业成本之间的差额',
        'OperatingExpenses': '企业为组织和管理企业生产经营所发生的费用',
        'OperatingIncomeLoss': '企业通过其主要经营活动所取得的利润或发生的亏损',
        'NetIncomeLoss': '企业在一定会计期间的经营成果',
        'EarningsPerShareBasic': '企业当期实现的净利润与发行在外普通股加权平均数的比值',
        'EarningsPerShareDiluted': '在假设当期期初或发行日转换为普通股的潜在普通股全部转换为普通股的基础上计算的每股收益',
        'NetCashProvidedByUsedInOperatingActivities': '企业通过其主要经营活动产生的现金流入和流出的净额',
        'NetCashProvidedByUsedInInvestingActivities': '企业长期资产投资活动产生的现金流入和流出的净额',
        'NetCashProvidedByUsedInFinancingActivities': '企业筹资活动产生的现金流入和流出的净额',
        'DepreciationDepletionAndAmortization': '企业对固定资产、油气资产和无形资产计提的折旧、摊销和折耗',
        'ShareBasedCompensation': '企业为获取职工和其他方提供服务而授予权益工具或承担以权益工具为基础确定的负债的交易',
        'PaymentsOfDividends': '企业向股东分配利润而支付的现金',
        'PaymentsForRepurchaseOfCommonStock': '企业为回购普通股而支付的现金'
    }
    
    # 常见概念的英文解释
    CONCEPT_ENGLISH_EXPLANATIONS = {
        'PaymentsToAcquirePropertyPlantAndEquipment': 'Cash payments for purchases, construction, and capitalization of property, plant, and equipment. This item is usually found in the investing activities section of the cash flow statement.',
        'CommercialPaper': 'Unsecured short-term debt instrument issued by a corporation, typically for financing accounts receivable and inventories. It is usually issued at a discount reflecting prevailing market interest rates.',
        'LongTermDebtCurrent': 'Long-term debt that is due within one year, classified as current liabilities.',
        'LongTermDebtNoncurrent': 'Long-term debt with maturity dates beyond one year, classified as non-current liabilities.',
        'MarketableSecuritiesCurrent': 'Securities that can be converted to cash quickly, classified as current assets.',
        'Cash': 'Cash and cash equivalents of the entity.',
        'CashAndCashEquivalentsAtCarryingValue': 'Cash and cash equivalents including cash, demand deposits, and other readily available funds.',
        'AccountsReceivableNetCurrent': 'The net amount of accounts receivable, which represents amounts billed to customers for goods or services rendered but not yet collected.',
        'InventoryNet': 'The net carrying amount of inventories held for sale or use in the ordinary course of business.',
        'Assets': 'Resources controlled by the entity as a result of past events and from which future economic benefits are expected to flow to the entity.',
        'AssetsCurrent': 'Assets that are expected to be realized or consumed within one year or the normal operating cycle.',
        'AssetsNoncurrent': 'Assets that are not expected to be realized or consumed within one year or the normal operating cycle.',
        'Liabilities': 'Present obligations of the entity arising from past events, the settlement of which is expected to result in an outflow of resources.',
        'LiabilitiesCurrent': 'Obligations that are expected to be settled within one year or the normal operating cycle.',
        'LiabilitiesNoncurrent': 'Obligations that are not expected to be settled within one year or the normal operating cycle.',
        'AccountsPayableCurrent': 'Obligations to pay for goods or services that have been acquired in the ordinary course of business.',
        'StockholdersEquity': 'The residual interest in the assets of the entity after deducting liabilities.',
        'RetainedEarningsAccumulatedDeficit': 'The cumulative amount of net income, dividends, and other adjustments since the entity\'s inception.',
        'Revenues': 'Inflows or other enhancements of assets or settlements of liabilities that result in increases in equity.',
        'RevenueFromContractWithCustomerExcludingAssessedTax': 'Revenue from contracts with customers excluding any assessed taxes.',
        'CostOfRevenue': 'The cost of goods or services sold during the reporting period.',
        'GrossProfit': 'The difference between revenue and cost of revenue.',
        'OperatingExpenses': 'Expenses incurred in the normal conduct of business operations.',
        'OperatingIncomeLoss': 'The profit or loss generated from the entity\'s main business activities.',
        'NetIncomeLoss': 'The overall profit or loss for the reporting period.',
        'EarningsPerShareBasic': 'Net income allocated to each outstanding common share.',
        'EarningsPerShareDiluted': 'Net income allocated to each share assuming all convertible securities are exercised.',
        'NetCashProvidedByUsedInOperatingActivities': 'Net cash inflows or outflows from the entity\'s main business operations.',
        'NetCashProvidedByUsedInInvestingActivities': 'Net cash inflows or outflows from investments in long-term assets.',
        'NetCashProvidedByUsedInFinancingActivities': 'Net cash inflows or outflows from financing activities such as issuing debt or equity.',
        'DepreciationDepletionAndAmortization': 'Systematic allocation of the cost of tangible and intangible assets over their useful lives.',
        'ShareBasedCompensation': 'Compensation cost resulting from equity-based payment transactions.',
        'PaymentsOfDividends': 'Cash payments made to shareholders as a distribution of profits.',
        'PaymentsForRepurchaseOfCommonStock': 'Cash payments for the repurchase of the entity\'s common stock.'
    }

    def __init__(self, user_agent: str = None):
        """
        初始化概念解释器
        
        Args:
            user_agent: 用户代理字符串
        """
        if not user_agent:
            user_agent = "Ting Wang tting.wang@gmail.com"
            
        self.sec_client = SECClient(user_agent=user_agent)
        self.xbrl_client = XBRLFramesClient(self.sec_client)
    
    def explain_concept(self, concept: str, cik: str, taxonomy: str = 'us-gaap'):
        """
        解释财务概念的口径
        
        Args:
            concept: 财务概念名称
            cik: 公司CIK号码
            taxonomy: 分类标准，默认为us-gaap
        """
        print(f"🔍 财务概念口径解释工具")
        print("="*60)
        print(f"概念名称: {concept}")
        print(f"公司CIK: {cik}")
        print(f"分类标准: {taxonomy}")
        print()
        
        try:
            # 获取公司概念数据
            print("正在获取概念数据...")
            concept_data = self.xbrl_client.get_company_concept_data(
                cik=cik,
                concept=concept,
                taxonomy=taxonomy
            )
            
            if not concept_data:
                print("❌ 未找到相关概念数据")
                return
            
            print("✅ 成功获取概念数据")
            print()
            
            # 显示概念基本信息
            self._display_concept_info(concept_data)
            
            # 显示概念定义
            self._display_concept_definition(concept_data)
            
            # 显示数据示例
            self._display_data_examples(concept_data)
            
            # 显示参考信息
            self._display_references(concept_data)
            
        except Exception as e:
            print(f"❌ 获取概念信息时出错: {e}")
    
    def _display_concept_info(self, concept_data: dict):
        """显示概念基本信息"""
        print("📊 概念基本信息")
        print("-" * 30)
        print(f"  标签 (tag): {concept_data.get('tag', 'N/A')}")
        print(f"  分类标准 (taxonomy): {concept_data.get('taxonomy', 'N/A')}")
        print(f"  单位类型: {list(concept_data.get('units', {}).keys())}")
        print()
    
    def _display_concept_definition(self, concept_data: dict):
        """显示概念定义"""
        print("📝 概念定义")
        print("-" * 30)
        
        concept_tag = concept_data.get('tag', '')
        
        # 显示中文名称
        chinese_name = self.CONCEPT_CHINESE_NAMES.get(concept_tag, '未找到中文名称')
        print(f"  中文名称: {chinese_name}")
        
        # 显示官方英文标签和描述
        label = concept_data.get('label', 'N/A')
        if label != 'N/A':
            print(f"  官方标签: {label}")
        
        description = concept_data.get('description', 'N/A')
        if description != 'N/A':
            print(f"  官方描述: {description}")
        
        # 如果没有官方描述，则显示我们自定义的英文解释
        if description == 'N/A':
            english_explanation = self.CONCEPT_ENGLISH_EXPLANATIONS.get(concept_tag, '未找到英文解释')
            print(f"  英文解释: {english_explanation}")
        
        # 从concept字段获取定义信息
        if 'concept' in concept_data:
            concept_info = concept_data['concept']
            
            # 显示概念的详细定义（如果可用）
            if 'namespace' in concept_info:
                print(f"  命名空间: {concept_info['namespace']}")
            
            if 'type' in concept_info:
                print(f"  数据类型: {concept_info['type']}")
                
            if 'periodType' in concept_info:
                print(f"  期间类型: {concept_info['periodType']}")
        else:
            # 如果没有详细的concept信息，提供通用定义
            definition = self.CONCEPT_DEFINITIONS.get(concept_tag, '未找到标准定义')
            print(f"  通用定义: {definition}")
        
        print()
    
    def _display_data_examples(self, concept_data: dict):
        """显示数据示例"""
        print("📈 数据示例")
        print("-" * 30)
        
        units_data = concept_data.get('units', {})
        if not units_data:
            print("  未找到数据")
            print()
            return
        
        # 显示USD单位的数据示例
        usd_data = units_data.get('USD', [])
        if usd_data:
            print("  USD单位数据 (最近3条):")
            for i, item in enumerate(usd_data[-3:]):  # 显示最近3条
                value = item.get('val', 'N/A')
                if isinstance(value, (int, float)):
                    value_str = f"{value:,.2f}" if '.' in str(value) else f"{value:,}"
                else:
                    value_str = str(value)
                    
                print(f"    {i+1}. 金额: {value_str}")
                print(f"       期间: {item.get('start', 'N/A')} 至 {item.get('end', 'N/A')}")
                print(f"       表单: {item.get('form', 'N/A')}")
                print(f"       财年: FY{item.get('fy', 'N/A')}")
                print(f"       提交日期: {item.get('filed', 'N/A')}")
                print()
        else:
            print("  未找到USD单位数据")
            print()
    
    def _display_references(self, concept_data: dict):
        """显示参考信息"""
        print("📖 参考信息")
        print("-" * 30)
        
        if 'concept' in concept_data and 'reference' in concept_data['concept']:
            references = concept_data['concept']['reference']
            for i, ref in enumerate(references[:3]):  # 显示前3个参考
                print(f"  参考 {i+1}:")
                if 'section' in ref:
                    print(f"    条款: {ref['section']}")
                if 'description' in ref:
                    print(f"    描述: {ref['description']}")
                if 'type' in ref:
                    print(f"    类型: {ref['type']}")
                if 'uri' in ref:
                    print(f"    链接: {ref['uri']}")
                print()
        else:
            # 提供通用参考信息
            print("  通用参考:")
            print("    - FASB Accounting Standards Codification")
            print("    - US GAAP Financial Reporting Taxonomy")
            print("    - SEC EDGAR Database")
            print("    - https://fasb.org/xbrl")
            print("    - https://www.sec.gov/edgar")
            print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SEC XBRL财务概念口径解释工具')
    parser.add_argument('concept', help='财务概念名称 (如: PaymentsToAcquirePropertyPlantAndEquipment)')
    parser.add_argument('cik', help='公司CIK号码 (如: 0000320193)')
    parser.add_argument('--taxonomy', default='us-gaap', help='分类标准 (默认: us-gaap)')
    parser.add_argument('--user-agent', default='Ting Wang tting.wang@gmail.com', 
                       help='User-Agent字符串 (默认: Ting Wang tting.wang@gmail.com)')
    
    args = parser.parse_args()
    
    try:
        explainer = ConceptExplainer(user_agent=args.user_agent)
        explainer.explain_concept(
            concept=args.concept,
            cik=args.cik,
            taxonomy=args.taxonomy
        )
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了程序执行")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    main()