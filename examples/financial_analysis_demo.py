#!/usr/bin/env python3
"""
财务数据分析示例

演示如何使用财务分析工具进行深度数据分析
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, XBRLFramesClient, FinancialAnalyzer


def financial_analysis_demo():
    """财务分析演示"""
    
    # 初始化
    user_agent = "财务分析示例 analysis@example.com"
    sec_client = SECClient(user_agent=user_agent)
    xbrl_client = XBRLFramesClient(sec_client)
    analyzer = FinancialAnalyzer()
    
    print("📊 财务数据分析演示")
    print("=" * 50)
    
    # 分析目标公司
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    print(f"\n🎯 分析目标公司: {', '.join(tickers)}")
    print("-" * 30)
    
    companies_data = {}
    
    # 获取各公司数据
    for ticker in tickers:
        try:
            print(f"\n📈 获取 {ticker} 的财务数据...")
            
            # 获取年度财务指标
            annual_data = xbrl_client.get_financial_metrics(ticker, period_type='annual', years=3)
            
            if not annual_data.empty:
                companies_data[ticker] = annual_data
                print(f"  获取到 {len(annual_data)} 条年度数据")
                
                # 显示最新数据概况
                latest_revenues = annual_data[annual_data['concept'] == 'Revenues']
                if not latest_revenues.empty:
                    latest_revenue = latest_revenues.iloc[0]
                    formatted_revenue = analyzer.format_financial_number(latest_revenue['value'])
                    print(f"  最新年度营收: {formatted_revenue} ({latest_revenue['end_date'].strftime('%Y-%m-%d')})")
            else:
                print(f"  未获取到 {ticker} 的数据")
                
        except Exception as e:
            print(f"  获取 {ticker} 数据时出错: {e}")
    
    if not companies_data:
        print("未获取到任何公司数据，演示结束")
        return
    
    # 1. 财务比率分析
    print(f"\n1️⃣  财务比率分析")
    print("-" * 30)
    
    for ticker, data in companies_data.items():
        print(f"\n🏢 {ticker} 财务比率:")
        
        try:
            ratios = analyzer.calculate_financial_ratios(data)
            
            if not ratios.empty:
                latest_ratios = ratios.iloc[0]
                
                ratios_to_show = [
                    ('current_ratio', '流动比率', ''),
                    ('debt_to_assets', '资产负债率', '%'),
                    ('equity_ratio', '股东权益比率', '%'),
                    ('net_profit_margin', '净利润率', '%'),
                    ('roa', '总资产收益率', '%'),
                    ('roe', '股东权益收益率', '%')
                ]
                
                for ratio_key, ratio_name, unit in ratios_to_show:
                    if ratio_key in latest_ratios and not pd.isna(latest_ratios[ratio_key]):
                        value = latest_ratios[ratio_key]
                        if unit == '%':
                            print(f"  {ratio_name}: {value:.2%}")
                        else:
                            print(f"  {ratio_name}: {value:.2f}")
            else:
                print("  无法计算财务比率")
                
        except Exception as e:
            print(f"  计算财务比率时出错: {e}")
    
    # 2. 增长率分析
    print(f"\n2️⃣  增长率分析")
    print("-" * 30)
    
    for ticker, data in companies_data.items():
        print(f"\n📈 {ticker} 增长率分析:")
        
        try:
            # 营收增长率
            revenue_growth = analyzer.calculate_growth_rates(data, 'Revenues', periods=3)
            if not revenue_growth.empty:
                print("  营收增长率:")
                for _, row in revenue_growth.iterrows():
                    current_period = row['current_period'].strftime('%Y-%m-%d')
                    previous_period = row['previous_period'].strftime('%Y-%m-%d')
                    growth_rate = row['growth_rate_pct']
                    direction = "📈" if growth_rate > 0 else "📉"
                    print(f"    {previous_period} → {current_period}: {direction} {growth_rate:+.1f}%")
            
            # 净利润增长率
            profit_growth = analyzer.calculate_growth_rates(data, 'NetIncomeLoss', periods=2)
            if not profit_growth.empty:
                print("  净利润增长率:")
                for _, row in profit_growth.iterrows():
                    current_period = row['current_period'].strftime('%Y-%m-%d')
                    previous_period = row['previous_period'].strftime('%Y-%m-%d')
                    growth_rate = row['growth_rate_pct']
                    direction = "📈" if growth_rate > 0 else "📉"
                    print(f"    {previous_period} → {current_period}: {direction} {growth_rate:+.1f}%")
                    
        except Exception as e:
            print(f"  计算增长率时出错: {e}")
    
    # 3. 趋势分析
    print(f"\n3️⃣  趋势分析")
    print("-" * 30)
    
    for ticker, data in companies_data.items():
        print(f"\n📊 {ticker} 趋势分析:")
        
        try:
            trends = analyzer.trend_analysis(data, ['Revenues', 'NetIncomeLoss', 'Assets'])
            
            for concept, trend_info in trends.items():
                concept_names = {
                    'Revenues': '营收',
                    'NetIncomeLoss': '净利润',
                    'Assets': '总资产'
                }
                
                concept_name = concept_names.get(concept, concept)
                print(f"\n  📈 {concept_name}:")
                
                print(f"    数据点数: {trend_info['data_points']}")
                print(f"    最新值: {analyzer.format_financial_number(trend_info['latest_value'])}")
                print(f"    平均值: {analyzer.format_financial_number(trend_info['mean'])}")
                
                if 'overall_change_pct' in trend_info:
                    change = trend_info['overall_change_pct']
                    direction = "📈" if change > 0 else "📉"
                    print(f"    总体变化: {direction} {change:+.1f}%")
                
                if 'trend_direction' in trend_info:
                    direction_map = {
                        'increasing': '📈 上升趋势',
                        'decreasing': '📉 下降趋势',
                        'mixed': '📊 震荡趋势'
                    }
                    trend_desc = direction_map.get(trend_info['trend_direction'], '未知趋势')
                    print(f"    近期趋势: {trend_desc}")
                
                if 'coefficient_of_variation' in trend_info:
                    cv = trend_info['coefficient_of_variation']
                    stability = "稳定" if cv < 20 else "波动较大" if cv < 50 else "高度波动"
                    print(f"    波动性: {cv:.1f}% ({stability})")
                    
        except Exception as e:
            print(f"  趋势分析时出错: {e}")
    
    # 4. 同行对比
    print(f"\n4️⃣  同行对比分析")
    print("-" * 30)
    
    try:
        # 营收对比
        revenue_comparison = analyzer.peer_comparison(companies_data, 'Revenues')
        if not revenue_comparison.empty:
            print("\n💰 营收对比 (最新期间):")
            for _, row in revenue_comparison.iterrows():
                ticker = row['ticker']
                value = row['value']
                rank = int(row['rank'])
                vs_avg = row['vs_average_pct']
                
                rank_emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}️⃣"
                avg_emoji = "📈" if vs_avg > 0 else "📉"
                
                print(f"  {rank_emoji} {ticker}: {analyzer.format_financial_number(value)} "
                      f"({avg_emoji} {vs_avg:+.1f}% vs 平均)")
        
        # 净利润对比
        profit_comparison = analyzer.peer_comparison(companies_data, 'NetIncomeLoss')
        if not profit_comparison.empty:
            print(f"\n💎 净利润对比 (最新期间):")
            for _, row in profit_comparison.iterrows():
                ticker = row['ticker']
                value = row['value']
                rank = int(row['rank'])
                vs_avg = row['vs_average_pct']
                
                rank_emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}️⃣"
                avg_emoji = "📈" if vs_avg > 0 else "📉"
                
                print(f"  {rank_emoji} {ticker}: {analyzer.format_financial_number(value)} "
                      f"({avg_emoji} {vs_avg:+.1f}% vs 平均)")
                      
    except Exception as e:
        print(f"同行对比分析时出错: {e}")
    
    # 5. 季节性分析（如果有季度数据）
    print(f"\n5️⃣  季节性分析")
    print("-" * 30)
    
    for ticker, data in companies_data.items():
        print(f"\n🗓️ {ticker} 季节性分析:")
        
        try:
            # 尝试获取季度数据进行季节性分析
            quarterly_data = xbrl_client.get_financial_metrics(ticker, period_type='quarterly', years=2)
            
            if not quarterly_data.empty:
                seasonal_revenues = analyzer.seasonal_analysis(quarterly_data, 'Revenues')
                
                if seasonal_revenues:
                    print("  营收季节性特征:")
                    
                    if 'best_quarter' in seasonal_revenues:
                        best_q = seasonal_revenues['best_quarter']
                        worst_q = seasonal_revenues['worst_quarter']
                        variation = seasonal_revenues.get('quarterly_variation_pct', 0)
                        
                        print(f"    最佳季度: {best_q}")
                        print(f"    最差季度: {worst_q}")
                        print(f"    季度间差异: {variation:.1f}%")
                    
                    if 'quarterly_statistics' in seasonal_revenues:
                        print("    各季度平均表现:")
                        for quarter, stats in seasonal_revenues['quarterly_statistics'].items():
                            if quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
                                avg_value = stats.get('mean', 0)
                                count = stats.get('count', 0)
                                print(f"      {quarter}: {analyzer.format_financial_number(avg_value)} "
                                      f"(基于{count}期数据)")
                else:
                    print("  无足够季度数据进行季节性分析")
            else:
                print("  未获取到季度数据")
                
        except Exception as e:
            print(f"  季节性分析时出错: {e}")
    
    print(f"\n✅ 财务数据分析演示完成!")


if __name__ == "__main__":
    import pandas as pd  # 需要导入pandas
    financial_analysis_demo()