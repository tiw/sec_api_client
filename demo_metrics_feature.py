#!/usr/bin/env python3
"""
演示sec_report_fetcher_db.py的--metrics功能

展示如何使用--metrics参数获取指定的SEC财务指标
"""

import subprocess
import sys
import time

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*80}")
    print(f"📊 {description}")
    print(f"{'='*80}")
    print(f"🔧 命令: {command}")
    print(f"{'.'*80}")
    
    # 运行命令
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # 显示输出
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(f"错误输出:\n{result.stderr}")
    
    # 等待一下，避免API频率限制
    time.sleep(2)
    
    return result.returncode == 0

def main():
    """主函数"""
    print("🚀 sec_report_fetcher_db.py --metrics 功能演示")
    print("=" * 80)
    print("新增的--metrics参数允许您指定具体的指标名称，而不需要获取整个报告部分的所有指标")
    
    user_agent = "SEC Metrics Demo <demo@example.com>"
    base_command = f'python sec_report_fetcher_db.py --company AAPL --report 10-K --year 2024 --user-agent "{user_agent}"'
    
    # 测试案例列表
    test_cases = [
        {
            "description": "获取营业收入和净利润",
            "metrics": ["RevenueFromContractWithCustomerExcludingAssessedTax", "NetIncomeLoss"],
            "expected": "USD格式的大数值（B为十亿）"
        },
        {
            "description": "获取每股收益指标",
            "metrics": ["EarningsPerShareBasic", "EarningsPerShareDiluted"],
            "expected": "USD/shares格式的每股数值"
        },
        {
            "description": "获取股票数量指标",
            "metrics": ["WeightedAverageNumberOfSharesOutstandingBasic", "WeightedAverageNumberOfDilutedSharesOutstanding"],
            "expected": "shares格式的股票数量"
        },
        {
            "description": "获取资产和负债信息",
            "metrics": ["Assets", "Liabilities", "StockholdersEquity"],
            "expected": "USD格式的资产负债表项目"
        },
        {
            "description": "获取现金流相关指标",
            "metrics": ["NetCashProvidedByUsedInOperatingActivities"],
            "expected": "USD格式的现金流数据"
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}/{total_tests}: {test_case['description']}")
        print(f"💡 预期结果: {test_case['expected']}")
        
        # 构建命令
        metrics_str = " ".join(f'"{metric}"' for metric in test_case['metrics'])
        command = f"{base_command} --metrics {metrics_str}"
        
        # 运行测试
        if run_command(command, test_case['description']):
            successful_tests += 1
            print("✅ 测试成功")
        else:
            print("❌ 测试失败")
    
    # 显示总结
    print(f"\n📈 测试总结")
    print(f"{'='*80}")
    print(f"✅ 成功: {successful_tests}/{total_tests}")
    print(f"📊 成功率: {successful_tests/total_tests*100:.1f}%")
    
    # 功能说明
    print(f"\n💡 --metrics 功能特点:")
    print(f"{'='*80}")
    print("🎯 精确获取: 只获取指定的指标，而不是整个报告部分")
    print("🚀 高效查询: 减少不必要的API调用和数据处理")  
    print("🔧 灵活使用: 支持多个指标名称，用空格分隔")
    print("📊 智能识别: 自动识别不同单位类型（USD、USD/shares、shares等）")
    print("💾 格式化显示: 根据单位类型智能格式化数值")
    
    print(f"\n📋 使用方法:")
    print(f"{'='*80}")
    print("# 获取单个指标")
    print('python sec_report_fetcher_db.py --company AAPL --report 10-K --year 2024 --metrics "NetIncomeLoss"')
    print()
    print("# 获取多个指标")  
    print('python sec_report_fetcher_db.py --company AAPL --report 10-K --year 2024 --metrics "EarningsPerShareBasic" "NetIncomeLoss" "Assets"')
    print()
    print("# 获取复杂指标名称（使用引号）")
    print('python sec_report_fetcher_db.py --company AAPL --report 10-K --year 2024 --metrics "RevenueFromContractWithCustomerExcludingAssessedTax"')
    
    print(f"\n🔗 与现有功能的对比:")
    print(f"{'='*80}")
    print("📄 --section 方式: 获取整个报告部分的所有指标（可能数百个）")
    print("🎯 --metrics 方式: 只获取指定的指标（精确控制）")
    print("💡 建议: 当您知道确切需要哪些指标时，使用--metrics更高效")
    
    print(f"\n✅ 演示完成!")

if __name__ == "__main__":
    main()