"""
财务数据分析和处理工具

提供财务数据的分析、计算和可视化功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import warnings


class FinancialAnalyzer:
    """财务数据分析器"""
    
    def __init__(self):
        """初始化分析器"""
        pass
    
    def calculate_financial_ratios(self, financial_data: pd.DataFrame) -> pd.DataFrame:
        """
        计算常用财务比率
        
        Args:
            financial_data: 包含财务数据的DataFrame，需包含concept和value列
            
        Returns:
            包含财务比率的DataFrame
        """
        # 按期间分组数据
        periods = financial_data['end_date'].unique()
        ratio_results = []
        
        for period in periods:
            period_data = financial_data[financial_data['end_date'] == period]
            
            # 创建概念-值映射
            concept_values = {}
            for _, row in period_data.iterrows():
                concept_values[row['concept']] = row['value']
            
            ratios = {
                'period': period,
                'ticker': period_data['ticker'].iloc[0] if not period_data.empty else None
            }
            
            # 流动比率 = 流动资产 / 流动负债
            if 'AssetsCurrent' in concept_values and 'LiabilitiesCurrent' in concept_values:
                current_assets = concept_values['AssetsCurrent']
                current_liabilities = concept_values['LiabilitiesCurrent']
                if current_liabilities != 0:
                    ratios['current_ratio'] = current_assets / current_liabilities
            
            # 资产负债率 = 总负债 / 总资产
            if 'Liabilities' in concept_values and 'Assets' in concept_values:
                total_liabilities = concept_values['Liabilities']
                total_assets = concept_values['Assets']
                if total_assets != 0:
                    ratios['debt_to_assets'] = total_liabilities / total_assets
            
            # 股东权益比率 = 股东权益 / 总资产
            if 'StockholdersEquity' in concept_values and 'Assets' in concept_values:
                stockholders_equity = concept_values['StockholdersEquity']
                total_assets = concept_values['Assets']
                if total_assets != 0:
                    ratios['equity_ratio'] = stockholders_equity / total_assets
            
            # 净利润率 = 净利润 / 营业收入
            if 'NetIncomeLoss' in concept_values and 'Revenues' in concept_values:
                net_income = concept_values['NetIncomeLoss']
                revenues = concept_values['Revenues']
                if revenues != 0:
                    ratios['net_profit_margin'] = net_income / revenues
            
            # 总资产收益率 (ROA) = 净利润 / 总资产
            if 'NetIncomeLoss' in concept_values and 'Assets' in concept_values:
                net_income = concept_values['NetIncomeLoss']
                total_assets = concept_values['Assets']
                if total_assets != 0:
                    ratios['roa'] = net_income / total_assets
            
            # 股东权益收益率 (ROE) = 净利润 / 股东权益
            if 'NetIncomeLoss' in concept_values and 'StockholdersEquity' in concept_values:
                net_income = concept_values['NetIncomeLoss']
                stockholders_equity = concept_values['StockholdersEquity']
                if stockholders_equity != 0:
                    ratios['roe'] = net_income / stockholders_equity
            
            ratio_results.append(ratios)
        
        if not ratio_results:
            return pd.DataFrame()
        
        ratios_df = pd.DataFrame(ratio_results)
        ratios_df['period'] = pd.to_datetime(ratios_df['period'])
        return ratios_df.sort_values('period', ascending=False)
    
    def calculate_growth_rates(self, financial_data: pd.DataFrame, 
                             concept: str, periods: int = 4) -> pd.DataFrame:
        """
        计算增长率
        
        Args:
            financial_data: 财务数据DataFrame
            concept: 要计算增长率的财务概念
            periods: 计算期数
            
        Returns:
            包含增长率的DataFrame
        """
        concept_data = financial_data[financial_data['concept'] == concept].copy()
        
        if concept_data.empty:
            return pd.DataFrame()
        
        # 按日期排序
        concept_data = concept_data.sort_values('end_date')
        
        growth_rates = []
        
        for i in range(1, min(len(concept_data), periods + 1)):
            current_row = concept_data.iloc[-i]
            previous_row = concept_data.iloc[-i-1]
            
            current_value = current_row['value']
            previous_value = previous_row['value']
            
            if previous_value != 0 and not pd.isna(current_value) and not pd.isna(previous_value):
                growth_rate = ((current_value - previous_value) / abs(previous_value)) * 100
                
                growth_rates.append({
                    'ticker': current_row['ticker'],
                    'concept': concept,
                    'current_period': current_row['end_date'],
                    'previous_period': previous_row['end_date'],
                    'current_value': current_value,
                    'previous_value': previous_value,
                    'growth_rate_pct': growth_rate
                })
        
        return pd.DataFrame(growth_rates)
    
    def trend_analysis(self, financial_data: pd.DataFrame, 
                      concepts: List[str]) -> Dict[str, Dict]:
        """
        趋势分析
        
        Args:
            financial_data: 财务数据DataFrame
            concepts: 要分析的财务概念列表
            
        Returns:
            包含趋势分析结果的字典
        """
        trends = {}
        
        for concept in concepts:
            concept_data = financial_data[financial_data['concept'] == concept].copy()
            
            if len(concept_data) < 2:
                continue
            
            concept_data = concept_data.sort_values('end_date')
            
            # 计算基本统计信息
            values = concept_data['value'].dropna()
            
            if len(values) < 2:
                continue
            
            trend_info = {
                'concept': concept,
                'data_points': len(values),
                'latest_value': float(values.iloc[-1]),
                'earliest_value': float(values.iloc[0]),
                'mean': float(values.mean()),
                'std': float(values.std()),
                'min': float(values.min()),
                'max': float(values.max()),
                'median': float(values.median())
            }
            
            # 计算整体趋势
            if trend_info['earliest_value'] != 0:
                overall_change = ((trend_info['latest_value'] - trend_info['earliest_value']) / 
                                abs(trend_info['earliest_value'])) * 100
                trend_info['overall_change_pct'] = overall_change
            
            # 计算变异系数（相对标准差）
            if trend_info['mean'] != 0:
                trend_info['coefficient_of_variation'] = (trend_info['std'] / abs(trend_info['mean'])) * 100
            
            # 判断趋势方向
            if len(values) >= 3:
                recent_values = values.iloc[-3:]
                if recent_values.is_monotonic_increasing:
                    trend_info['trend_direction'] = 'increasing'
                elif recent_values.is_monotonic_decreasing:
                    trend_info['trend_direction'] = 'decreasing'
                else:
                    trend_info['trend_direction'] = 'mixed'
            
            trends[concept] = trend_info
        
        return trends
    
    def peer_comparison(self, companies_data: Dict[str, pd.DataFrame], 
                       concept: str, period: Optional[str] = None) -> pd.DataFrame:
        """
        同行业公司对比
        
        Args:
            companies_data: 公司数据字典，键为ticker，值为财务数据DataFrame
            concept: 对比的财务概念
            period: 特定期间，None表示使用最新数据
            
        Returns:
            对比结果DataFrame
        """
        comparison_data = []
        
        for ticker, data in companies_data.items():
            concept_data = data[data['concept'] == concept].copy()
            
            if concept_data.empty:
                continue
            
            if period:
                # 使用特定期间的数据
                period_data = concept_data[concept_data['end_date'] == period]
                if period_data.empty:
                    continue
                latest_data = period_data.iloc[0]
            else:
                # 使用最新数据
                concept_data = concept_data.sort_values('end_date', ascending=False)
                latest_data = concept_data.iloc[0]
            
            comparison_data.append({
                'ticker': ticker,
                'concept': concept,
                'value': latest_data['value'],
                'period': latest_data['end_date'],
                'fiscal_year': latest_data.get('fiscal_year'),
                'fiscal_period': latest_data.get('fiscal_period')
            })
        
        if not comparison_data:
            return pd.DataFrame()
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # 添加排名
        comparison_df['rank'] = comparison_df['value'].rank(ascending=False)
        
        # 添加相对于平均值的比较
        mean_value = comparison_df['value'].mean()
        comparison_df['vs_average_pct'] = ((comparison_df['value'] - mean_value) / abs(mean_value)) * 100
        
        # 添加相对于最大值的比较
        max_value = comparison_df['value'].max()
        comparison_df['vs_max_pct'] = (comparison_df['value'] / max_value) * 100
        
        return comparison_df.sort_values('rank')
    
    def seasonal_analysis(self, financial_data: pd.DataFrame, 
                         concept: str) -> Dict:
        """
        季节性分析（基于季度数据）
        
        Args:
            financial_data: 财务数据DataFrame
            concept: 财务概念
            
        Returns:
            季节性分析结果字典
        """
        concept_data = financial_data[
            (financial_data['concept'] == concept) & 
            (financial_data['fiscal_period'].notna())
        ].copy()
        
        if concept_data.empty:
            return {}
        
        # 按季度分组
        quarterly_stats = concept_data.groupby('fiscal_period')['value'].agg([
            'mean', 'std', 'count', 'min', 'max'
        ]).to_dict('index')
        
        # 计算季度间差异
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        seasonal_info = {
            'concept': concept,
            'quarterly_statistics': quarterly_stats,
            'total_quarters_analyzed': len(concept_data),
        }
        
        # 找出表现最好和最差的季度
        if quarterly_stats:
            avg_values = {q: stats['mean'] for q, stats in quarterly_stats.items() if q in quarters}
            if avg_values:
                best_quarter = max(avg_values.keys(), key=lambda k: avg_values[k])
                worst_quarter = min(avg_values.keys(), key=lambda k: avg_values[k])
                
                seasonal_info['best_quarter'] = best_quarter
                seasonal_info['worst_quarter'] = worst_quarter
                seasonal_info['quarterly_variation_pct'] = (
                    (avg_values[best_quarter] - avg_values[worst_quarter]) / 
                    abs(avg_values[worst_quarter]) * 100
                )
        
        return seasonal_info
    
    @staticmethod
    def format_financial_number(value: Union[int, float], 
                              unit: str = 'USD', scale: str = 'auto') -> str:
        """
        格式化财务数字
        
        Args:
            value: 数值
            unit: 单位
            scale: 缩放比例 ('auto', 'thousands', 'millions', 'billions')
            
        Returns:
            格式化后的字符串
        """
        if pd.isna(value):
            return 'N/A'
        
        if scale == 'auto':
            if abs(value) >= 1e9:
                scale = 'billions'
            elif abs(value) >= 1e6:
                scale = 'millions'
            elif abs(value) >= 1e3:
                scale = 'thousands'
            else:
                scale = 'units'
        
        if scale == 'billions':
            scaled_value = value / 1e9
            suffix = 'B'
        elif scale == 'millions':
            scaled_value = value / 1e6
            suffix = 'M'
        elif scale == 'thousands':
            scaled_value = value / 1e3
            suffix = 'K'
        else:
            scaled_value = value
            suffix = ''
        
        formatted = f"{scaled_value:,.2f}{suffix}"
        
        if unit and unit != 'USD':
            formatted = f"{formatted} {unit}"
        
        return formatted