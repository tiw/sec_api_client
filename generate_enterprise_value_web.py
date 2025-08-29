#!/usr/bin/env python3
"""
企业价值报告Web页面生成器

基于企业价值报告结构，从数据库读取财务指标数据，生成现代化的HTML报告页面。
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.database.manager import get_default_sqlite_manager
from src.database.utils import DatabaseUtils

class EnterpriseValueWebGenerator:
    """企业价值报告Web页面生成器"""
    
    def __init__(self, db_manager=None):
        """初始化生成器"""
        self.db_manager = db_manager or get_default_sqlite_manager()
        self.db_utils = DatabaseUtils(self.db_manager)
        
        # 定义指标分组结构（基于数据库中实际存在的指标）
        self.metric_groups = {
            "净利润水平": {
                "metrics": [
                    ("净利润", "NetIncomeLoss", "currency"),
                    ("所得税", "IncomeTaxExpenseBenefit", "currency"),
                    ("税前利润", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "currency"),
                    ("研发费用", "ResearchAndDevelopmentExpense", "currency")
                ]
            },
            "现金流水平": {
                "metrics": [
                    ("净利润", "NetIncomeLoss", "currency"),
                    ("折旧摊销", "DepreciationDepletionAndAmortization", "currency"),
                    ("折旧", "Depreciation", "currency")
                ]
            },
            "股东价值": {
                "metrics": [
                    ("基本每股收益", "EarningsPerShareBasic", "currency_per_share"),
                    ("稀释每股收益", "EarningsPerShareDiluted", "currency_per_share"),
                    ("基本加权平均股数", "WeightedAverageNumberOfSharesOutstandingBasic", "shares"),
                    ("稀释加权平均股数", "WeightedAverageNumberOfDilutedSharesOutstanding", "shares"),
                    ("股东权益", "StockholdersEquity", "currency"),
                    ("留存收益", "RetainedEarningsAccumulatedDeficit", "currency")
                ]
            },
            "营收和成本": {
                "metrics": [
                    ("商品和服务成本", "CostOfGoodsAndServicesSold", "currency"),
                    ("库存净额", "InventoryNet", "currency")
                ]
            },
            "资产结构": {
                "metrics": [
                    ("总资产", "Assets", "currency"),
                    ("流动资产", "AssetsCurrent", "currency"),
                    ("非流动资产", "AssetsNoncurrent", "currency"),
                    ("固定资产净额", "PropertyPlantAndEquipmentNet", "currency"),
                    ("固定资产总额", "PropertyPlantAndEquipmentGross", "currency")
                ]
            },
            "负债结构": {
                "metrics": [
                    ("总负债", "Liabilities", "currency"),
                    ("流动负债", "LiabilitiesCurrent", "currency"),
                    ("非流动负债", "LiabilitiesNoncurrent", "currency"),
                    ("长期债务", "LongTermDebt", "currency"),
                    ("长期债务(非流动)", "LongTermDebtNoncurrent", "currency"),
                    ("流动部分长期债务", "LongTermDebtCurrent", "currency")
                ]
            },
            "股东权益": {
                "metrics": [
                    ("股东权益总计", "StockholdersEquity", "currency"),
                    ("普通股(含溢价)", "CommonStocksIncludingAdditionalPaidInCapital", "currency"),
                    ("留存收益", "RetainedEarningsAccumulatedDeficit", "currency"),
                    ("累计其他综合损益", "AccumulatedOtherComprehensiveIncomeLossNetOfTax", "currency")
                ]
            }
        }
        
        # 计算指标（这些需要基于现有数据计算）
        self.calculated_metrics = [
            ("Basic EPS (基本每股收益)", "EarningsPerShareBasic", "currency_per_share"),
            ("Diluted EPS (稀释每股收益)", "EarningsPerShareDiluted", "currency_per_share"),
            ("Current Ratio (流动比率)", "CALCULATED_CurrentRatio", "ratio"),
            ("Debt-to-Asset Ratio (资产负债率)", "CALCULATED_DebtToAssetRatio", "percentage"),
            ("ROE (净资产收益率)", "CALCULATED_ReturnOnEquity", "percentage"),
            ("Gross Margin (毛利率)", "CALCULATED_GrossMargin", "percentage"),
            ("Tax Rate (实际税率)", "CALCULATED_EffectiveTaxRate", "percentage"),
            ("每股净资产", "CALCULATED_BookValuePerShare", "currency_per_share")
        ]
    
    def get_metric_data(self, company_ticker: str, fiscal_year: int, metric_name: str) -> Optional[Dict]:
        """从数据库获取指标数据或计算指标"""
        try:
            # 检查是否是计算指标
            if metric_name.startswith('CALCULATED_'):
                return self._calculate_metric(company_ticker, fiscal_year, metric_name)
            
            # 从数据库获取原始指标
            results = self.db_utils.query_reports(
                company_identifier=company_ticker,
                metric_names=[metric_name],
                fiscal_years=[fiscal_year]
            )
            
            if results:
                return results[0]
            return None
        except Exception as e:
            print(f"获取指标 {metric_name} 数据失败: {e}")
            return None
    
    def _calculate_metric(self, company_ticker: str, fiscal_year: int, metric_name: str) -> Optional[Dict]:
        """计算派生指标"""
        try:
            if metric_name == 'CALCULATED_CurrentRatio':
                # 流动比率 = 流动资产 / 流动负债
                current_assets = self.get_metric_data(company_ticker, fiscal_year, 'AssetsCurrent')
                current_liabilities = self.get_metric_data(company_ticker, fiscal_year, 'LiabilitiesCurrent')
                
                if current_assets and current_liabilities and current_liabilities['value'] != 0:
                    ratio = current_assets['value'] / current_liabilities['value']
                    return {
                        'value': ratio,
                        'formatted_value': f"{ratio:.2f}",
                        'metric_name': 'Current Ratio',
                        'unit': 'ratio'
                    }
            
            elif metric_name == 'CALCULATED_DebtToAssetRatio':
                # 资产负债率 = 总负债 / 总资产
                total_liabilities = self.get_metric_data(company_ticker, fiscal_year, 'Liabilities')
                total_assets = self.get_metric_data(company_ticker, fiscal_year, 'Assets')
                
                if total_liabilities and total_assets and total_assets['value'] != 0:
                    ratio = (total_liabilities['value'] / total_assets['value']) * 100
                    return {
                        'value': ratio,
                        'formatted_value': f"{ratio:.1f}%",
                        'metric_name': 'Debt-to-Asset Ratio',
                        'unit': 'percentage'
                    }
            
            elif metric_name == 'CALCULATED_ReturnOnEquity':
                # ROE = 净利润 / 股东权益
                net_income = self.get_metric_data(company_ticker, fiscal_year, 'NetIncomeLoss')
                shareholders_equity = self.get_metric_data(company_ticker, fiscal_year, 'StockholdersEquity')
                
                if net_income and shareholders_equity and shareholders_equity['value'] != 0:
                    roe = (net_income['value'] / shareholders_equity['value']) * 100
                    return {
                        'value': roe,
                        'formatted_value': f"{roe:.1f}%",
                        'metric_name': 'Return on Equity',
                        'unit': 'percentage'
                    }
            
            elif metric_name == 'CALCULATED_GrossMargin':
                # 毛利率 = (营收 - 成本) / 营收
                # 这里我们用净利润作为近似，因为没有营收数据
                net_income = self.get_metric_data(company_ticker, fiscal_year, 'NetIncomeLoss')
                cost_of_goods = self.get_metric_data(company_ticker, fiscal_year, 'CostOfGoodsAndServicesSold')
                
                if net_income and cost_of_goods:
                    # 估算营收 = 净利润 + 成本 (简化计算)
                    estimated_revenue = net_income['value'] + cost_of_goods['value']
                    if estimated_revenue != 0:
                        gross_margin = ((estimated_revenue - cost_of_goods['value']) / estimated_revenue) * 100
                        return {
                            'value': gross_margin,
                            'formatted_value': f"{gross_margin:.1f}%",
                            'metric_name': 'Gross Margin (估算)',
                            'unit': 'percentage'
                        }
            
            elif metric_name == 'CALCULATED_EffectiveTaxRate':
                # 实际税率 = 所得税 / 税前利润
                tax_expense = self.get_metric_data(company_ticker, fiscal_year, 'IncomeTaxExpenseBenefit')
                pretax_income = self.get_metric_data(company_ticker, fiscal_year, 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest')
                
                if tax_expense and pretax_income and pretax_income['value'] != 0:
                    tax_rate = (tax_expense['value'] / pretax_income['value']) * 100
                    return {
                        'value': tax_rate,
                        'formatted_value': f"{tax_rate:.1f}%",
                        'metric_name': 'Effective Tax Rate',
                        'unit': 'percentage'
                    }
            
            elif metric_name == 'CALCULATED_BookValuePerShare':
                # 每股净资产 = 股东权益 / 基本股数
                shareholders_equity = self.get_metric_data(company_ticker, fiscal_year, 'StockholdersEquity')
                shares_basic = self.get_metric_data(company_ticker, fiscal_year, 'WeightedAverageNumberOfSharesOutstandingBasic')
                
                if shareholders_equity and shares_basic and shares_basic['value'] != 0:
                    book_value_per_share = shareholders_equity['value'] / shares_basic['value']
                    return {
                        'value': book_value_per_share,
                        'formatted_value': f"${book_value_per_share:.2f}",
                        'metric_name': 'Book Value per Share',
                        'unit': 'currency_per_share'
                    }
            
            return None
            
        except Exception as e:
            print(f"计算指标 {metric_name} 失败: {e}")
            return None
    
    def format_value(self, value: float, format_type: str) -> str:
        """格式化数值显示"""
        if value is None:
            return "无数据"
        
        try:
            if format_type == "currency":
                if abs(value) >= 1e9:
                    return f"${value/1e9:.2f}B"
                elif abs(value) >= 1e6:
                    return f"${value/1e6:.2f}M"
                else:
                    return f"${value:,.2f}"
            
            elif format_type == "currency_per_share":
                return f"${value:.2f}"
            
            elif format_type == "percentage":
                return f"{value:.1f}%"
            
            elif format_type == "ratio":
                return f"{value:.2f}"
            
            elif format_type == "shares":
                if abs(value) >= 1e9:
                    return f"{value/1e9:.2f}B"
                elif abs(value) >= 1e6:
                    return f"{value/1e6:.2f}M"
                else:
                    return f"{value:,.0f}"
            
            else:
                return str(value)
                
        except (ValueError, TypeError):
            return "无数据"
    
    def generate_html_content(self, company_ticker: str, fiscal_year: int) -> str:
        """生成HTML内容"""
        # 获取公司信息
        company_info = self.db_utils.get_company_by_ticker(company_ticker)
        company_name = company_info.name if company_info else company_ticker
        
        # HTML头部和样式
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} ({company_ticker}) - {fiscal_year}年企业价值报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .header h1 {{ color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }}
        .header .subtitle {{ color: #7f8c8d; font-size: 1.2em; margin-bottom: 20px; }}
        
        .meta-info {{ display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; }}
        .meta-item {{
            background: #f8f9fa;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            color: #495057;
        }}
        
        .section-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            margin-bottom: 25px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .section-card:hover {{ transform: translateY(-2px); }}
        
        .section-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            font-size: 1.4em;
            font-weight: 600;
        }}
        
        .section-content {{ padding: 25px 30px; }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .metric-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }}
        
        .metric-item:hover {{ background: #e9ecef; transform: translateX(5px); }}
        
        .metric-name {{ font-weight: 600; color: #2c3e50; flex: 1; }}
        
        .metric-value {{
            font-weight: 700;
            color: #27ae60;
            font-size: 1.1em;
            text-align: right;
        }}
        
        .metric-value.no-data {{ color: #e74c3c; font-style: italic; }}
        
        .calculated-metrics {{ background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); }}
        .calculated-metrics .section-header {{ background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); }}
        
        .export-section {{
            text-align: center;
            margin-top: 30px;
            padding: 25px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .export-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            margin: 0 10px;
            transition: all 0.3s ease;
        }}
        
        .export-btn:hover {{ transform: translateY(-2px); }}
        
        .timestamp {{ margin-top: 20px; color: #7f8c8d; font-size: 0.9em; }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            .header h1 {{ font-size: 2em; }}
            .meta-info {{ flex-direction: column; align-items: center; }}
            .metric-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{company_name}</h1>
            <div class="subtitle">{fiscal_year}年企业价值分析报告</div>
            <div class="meta-info">
                <div class="meta-item">股票代码: {company_ticker}</div>
                <div class="meta-item">财年: {fiscal_year}</div>
                <div class="meta-item">数据来源: SEC EDGAR</div>
            </div>
        </div>
"""
        
        # 生成各个指标分组的HTML
        for group_name, group_data in self.metric_groups.items():
            html_content += f"""
        <div class="section-card">
            <div class="section-header">{group_name}</div>
            <div class="section-content">
                <div class="metric-grid">
"""
            
            for metric_display_name, metric_name, format_type in group_data.get("metrics", []):
                metric_data = self.get_metric_data(company_ticker, fiscal_year, metric_name)
                
                if metric_data:
                    formatted_value = self.format_value(metric_data.get('value'), format_type)
                    value_class = ""
                else:
                    formatted_value = "无数据"
                    value_class = "no-data"
                
                html_content += f"""
                    <div class="metric-item">
                        <span class="metric-name">{metric_display_name}</span>
                        <span class="metric-value {value_class}">{formatted_value}</span>
                    </div>
"""
            
            html_content += """
                </div>
            </div>
        </div>
"""
        
        # 计算指标部分
        html_content += """
        <div class="section-card calculated-metrics">
            <div class="section-header">关键计算指标</div>
            <div class="section-content">
                <div class="metric-grid">
"""
        
        for metric_display_name, metric_name, format_type in self.calculated_metrics:
            metric_data = self.get_metric_data(company_ticker, fiscal_year, metric_name)
            
            if metric_data:
                formatted_value = self.format_value(metric_data.get('value'), format_type)
                value_class = ""
            else:
                formatted_value = "无数据"
                value_class = "no-data"
            
            html_content += f"""
                <div class="metric-item">
                    <span class="metric-name">{metric_display_name}</span>
                    <span class="metric-value {value_class}">{formatted_value}</span>
                </div>
"""
        
        # 结尾部分
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        html_content += f"""
                </div>
            </div>
        </div>
        
        <div class="export-section">
            <h3>报告操作</h3>
            <button class="export-btn" onclick="window.print()">🖨️ 打印报告</button>
            <button class="export-btn" onclick="exportData()">📊 导出数据</button>
            <div class="timestamp">报告生成时间: {current_time}</div>
        </div>
    </div>
    
    <script>
        function exportData() {{
            const data = [];
            document.querySelectorAll('.metric-item').forEach(item => {{
                data.push({{
                    name: item.querySelector('.metric-name').textContent,
                    value: item.querySelector('.metric-value').textContent
                }});
            }});
            
            const csv = 'Name,Value\\n' + data.map(row => `"${{row.name}}","${{row.value}}"`).join('\\n');
            const blob = new Blob([csv], {{type: 'text/csv'}});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '{company_ticker}_{fiscal_year}_report.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
"""
        
        return html_content
    
    def generate_web_page(self, company_ticker: str, fiscal_year: int, output_path: str = None) -> str:
        """生成完整的Web页面文件"""
        if output_path is None:
            output_path = f"{company_ticker}_{fiscal_year}_enterprise_value_report.html"
        
        html_content = self.generate_html_content(company_ticker, fiscal_year)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 企业价值报告Web页面已生成: {output_path}")
        return output_path
    
    def close(self):
        """关闭数据库连接"""
        if self.db_manager:
            self.db_manager.close()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="企业价值报告Web页面生成器")
    parser.add_argument('--company', '-c', required=True, help='公司股票代码 (如: AAPL)')
    parser.add_argument('--year', '-y', type=int, required=True, help='财政年度 (如: 2024)')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    try:
        generator = EnterpriseValueWebGenerator()
        
        print(f"🚀 开始生成 {args.company} {args.year}年企业价值报告Web页面...")
        
        output_file = generator.generate_web_page(
            company_ticker=args.company,
            fiscal_year=args.year,
            output_path=args.output
        )
        
        print(f"📊 报告概述:")
        print(f"   公司: {args.company}")
        print(f"   年份: {args.year}")
        print(f"   输出: {output_file}")
        print(f"\n💡 使用方法:")
        print(f"   在浏览器中打开: {output_file}")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return 1
    
    finally:
        if 'generator' in locals():
            generator.close()
    
    return 0

if __name__ == "__main__":
    exit(main())