#!/usr/bin/env python3
"""
SEC API 多公司数据测试

测试从SEC EDGAR API获取多个公司的真实数据
User-Agent: Ting Wang <tting.wang@gmail.com>
"""

import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, XBRLFramesClient, FinancialAnalyzer
import pandas as pd


def test_company_data(ticker):
    """测试单个公司的SEC数据获取"""
    
    print(f"\n{'='*60}")
    print(f"🔍 测试 {ticker} 的SEC API数据获取")
    print(f"{'='*60}")
    
    # 已知公司信息
    known_companies = {
        "AAPL": {"cik": "0000320193", "title": "Apple Inc."},
        "MSFT": {"cik": "0000789019", "title": "Microsoft Corporation"},
        "GOOGL": {"cik": "0001652044", "title": "Alphabet Inc."},
        "AMZN": {"cik": "0001018724", "title": "Amazon.com Inc."},
        "TSLA": {"cik": "0001318605", "title": "Tesla Inc."}
    }
    
    if ticker not in known_companies:
        print(f"❌ 未知的股票代码: {ticker}")
        return
    
    company_info = known_companies[ticker]
    user_agent = "Ting Wang tting.wang@gmail.com"
    
    print(f"🏢 公司: {company_info['title']}")
    print(f"📊 CIK: {company_info['cik']}")
    
    # 初始化客户端
    sec_client = SECClient(user_agent=user_agent)
    xbrl_client = XBRLFramesClient(sec_client)
    analyzer = FinancialAnalyzer()
    
    try:
        # 测试单个概念数据获取
        print(f"\n🔍 测试获取 {ticker} 的关键财务概念...")
        test_concepts = ['Assets', 'Revenues', 'NetIncomeLoss', 'StockholdersEquity']
        
        results = []
        for concept in test_concepts:
            try:
                print(f"  📋 获取 {concept} (2023年度)...")
                concept_data = xbrl_client.get_concept_data(concept, 'CY2023I')  # 2023年瞬时数据
                
                if not concept_data.empty:
                    # 查找目标公司数据
                    company_data = concept_data[concept_data['cik'] == int(company_info['cik'])]
                    if not company_data.empty:
                        row = company_data.iloc[0]
                        value = row['val']
                        formatted_value = analyzer.format_financial_number(value)
                        
                        results.append({
                            'concept': concept,
                            'value': value,
                            'formatted': formatted_value,
                            'date': row['end']
                        })
                        
                        print(f"    ✅ {concept}: {formatted_value}")
                    else:
                        print(f"    ⚠️  未找到 {ticker} 在2023年的 {concept} 数据")
                else:
                    print(f"    ❌ 2023年 {concept} 无数据")
                    
            except Exception as e:
                print(f"    ❌ 获取 {concept} 失败: {e}")
        
        # 显示结果汇总
        if results:
            print(f"\n📊 {ticker} 2023年关键财务数据汇总:")
            print("-" * 50)
            for result in results:
                print(f"  {result['concept']:20}: {result['formatted']}")
            print("-" * 50)
        else:
            print(f"\n❌ 未获取到 {ticker} 的任何财务数据")
        
        # 测试公司概念历史数据
        print(f"\n📈 测试获取 {ticker} 的历史数据...")
        try:
            historical_data = xbrl_client.get_company_concept_data(
                cik=company_info['cik'], 
                concept='Assets'
            )
            
            if historical_data and 'units' in historical_data:
                usd_data = historical_data['units'].get('USD', [])
                if usd_data:
                    print(f"  ✅ 获取到 {len(usd_data)} 期资产数据")
                    
                    # 显示最近3期数据
                    sorted_data = sorted(usd_data, key=lambda x: x.get('end', ''), reverse=True)
                    print(f"    最近3期总资产:")
                    for i, item in enumerate(sorted_data[:3]):
                        end_date = item.get('end', 'N/A')
                        value = item.get('val', 0)
                        form = item.get('form', 'N/A')
                        formatted_value = analyzer.format_financial_number(value)
                        print(f"      {i+1}. {end_date}: {formatted_value} ({form})")
                else:
                    print(f"  ❌ 未找到USD单位的历史数据")
            else:
                print(f"  ❌ 未获取到历史数据")
                
        except Exception as e:
            print(f"  ❌ 获取历史数据失败: {e}")
        
        return results
        
    except Exception as e:
        print(f"❌ 测试 {ticker} 时出错: {e}")
        return None


def main():
    """主函数"""
    print("🚀 SEC EDGAR API 多公司数据测试")
    print("📧 User-Agent: Ting Wang <tting.wang@gmail.com>")
    print("🌐 数据来源: SEC EDGAR 真实API")
    print("⏰ 注意: SEC API有频率限制，测试可能需要一些时间...")
    
    # 测试的公司列表
    test_companies = ['AAPL', 'MSFT', 'GOOGL']
    
    print(f"\n🎯 将测试以下公司: {', '.join(test_companies)}")
    
    all_results = {}
    
    for ticker in test_companies:
        try:
            results = test_company_data(ticker)
            if results:
                all_results[ticker] = results
        except KeyboardInterrupt:
            print(f"\n⚠️ 用户中断了测试")
            break
        except Exception as e:
            print(f"\n❌ 测试 {ticker} 时出现异常: {e}")
            continue
    
    # 显示测试总结
    print(f"\n{'='*60}")
    print("📊 SEC API 测试总结")
    print(f"{'='*60}")
    
    if all_results:
        print(f"✅ 成功测试的公司: {len(all_results)} 个")
        
        for ticker, results in all_results.items():
            print(f"\n🏢 {ticker}:")
            for result in results:
                print(f"  📈 {result['concept']}: {result['formatted']}")
        
        print(f"\n🎉 SEC EDGAR API 连接正常，数据获取成功！")
        print(f"📧 API调用使用的User-Agent: Ting Wang <tting.wang@gmail.com>")
        print(f"🔗 数据均来自SEC官方EDGAR数据库")
        
    else:
        print("❌ 未成功获取到任何公司数据")
        print("🔍 可能的原因:")
        print("  • 网络连接问题")
        print("  • SEC服务器暂时不可用")
        print("  • API频率限制")
        print("  • User-Agent配置问题")
    
    print(f"\n✅ 测试完成")


if __name__ == "__main__":
    main()