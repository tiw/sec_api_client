#!/usr/bin/env python3
"""
企业价值报告Web页面生成器演示脚本

展示如何使用generate_enterprise_value_web.py生成企业价值报告Web页面
"""

import subprocess
import sys
import os
import webbrowser
from pathlib import Path

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*80}")
    print(f"📊 {description}")
    print(f"{'='*80}")
    print(f"🔧 命令: {command}")
    print(f"{'.'*80}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(f"错误输出:\n{result.stderr}")
    
    return result.returncode == 0

def main():
    """主函数"""
    print("🚀 企业价值报告Web页面生成器演示")
    print("=" * 80)
    print("基于企业价值报告结构，从数据库读取财务指标数据，生成现代化的HTML报告页面")
    
    # 测试案例列表
    test_cases = [
        {
            "company": "AAPL",
            "year": 2024,
            "description": "生成Apple 2024年企业价值报告"
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    generated_files = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试 {i}/{total_tests}: {test_case['description']}")
        
        # 构建命令
        command = f"python generate_enterprise_value_web.py --company {test_case['company']} --year {test_case['year']}"
        
        # 运行测试
        if run_command(command, test_case['description']):
            successful_tests += 1
            output_file = f"{test_case['company']}_{test_case['year']}_enterprise_value_report.html"
            generated_files.append(output_file)
            print("✅ 测试成功")
        else:
            print("❌ 测试失败")
    
    # 显示总结
    print(f"\n📈 测试总结")
    print(f"{'='*80}")
    print(f"✅ 成功: {successful_tests}/{total_tests}")
    print(f"📊 成功率: {successful_tests/total_tests*100:.1f}%")
    
    # 功能说明
    print(f"\n💡 企业价值报告Web生成器功能特点:")
    print(f"{'='*80}")
    print("🎯 结构化展示: 按照企业价值分析框架组织指标")
    print("📊 实时数据: 从数据库动态获取最新财务数据")
    print("🎨 现代设计: 响应式设计，支持移动端访问")
    print("📱 交互功能: 支持打印和数据导出")
    print("🔍 智能格式化: 根据指标类型自动格式化数值显示")
    
    print(f"\n📋 指标分组结构:")
    print(f"{'='*80}")
    print("1. 净利润水平 - 净利润率、所得税、税前利润、税率")
    print("2. 现金流水平 - 净利润、折旧摊销")
    print("3. 股东价值 - 每股指标、流通股数、增长率等")
    print("4. 营收水平 - 营业利润、营业利润率、营收")
    print("5. 资本分配效率 - 留存收益、股息、资本支出")
    print("6. 资本回报率 - ROE、ROTC等")
    print("7. 资本结构健康度 - 资产负债、流动性指标")
    print("8. 关键计算指标 - EPS、比率、现金流等")
    
    print(f"\n📋 使用方法:")
    print(f"{'='*80}")
    print("# 生成指定公司的企业价值报告")
    print('python generate_enterprise_value_web.py --company AAPL --year 2024')
    print()
    print("# 指定输出文件名")
    print('python generate_enterprise_value_web.py --company MSFT --year 2024 --output my_report.html')
    print()
    print("# 查看帮助信息")
    print('python generate_enterprise_value_web.py --help')
    
    print(f"\n🔗 Web页面特性:")
    print(f"{'='*80}")
    print("📱 响应式设计: 自适应桌面和移动设备")
    print("🎨 现代化UI: 渐变背景、毛玻璃效果、动画过渡")
    print("📊 数据可视化: 清晰的指标展示和分组")
    print("🖨️ 打印支持: 一键打印报告")
    print("📤 导出功能: 支持CSV格式数据导出")
    print("🔍 交互体验: 悬停效果、点击反馈")
    
    print(f"\n📁 生成的文件:")
    print(f"{'='*80}")
    for file_path in generated_files:
        if Path(file_path).exists():
            file_size = Path(file_path).stat().st_size / 1024
            print(f"✅ {file_path} ({file_size:.1f} KB)")
            
            # 询问是否在浏览器中打开
            if successful_tests > 0:
                try:
                    user_input = input(f"\n是否在浏览器中打开 {file_path}? (y/n): ").strip().lower()
                    if user_input in ['y', 'yes', '是']:
                        file_url = f"file://{Path(file_path).absolute()}"
                        webbrowser.open(file_url)
                        print(f"🌐 已在浏览器中打开: {file_url}")
                except KeyboardInterrupt:
                    print("\n操作取消")
                except Exception as e:
                    print(f"打开浏览器失败: {e}")
        else:
            print(f"❌ {file_path} (文件未找到)")
    
    print(f"\n💼 业务价值:")
    print(f"{'='*80}")
    print("📈 投资分析: 全面的企业价值评估框架")
    print("📊 财务健康: 多维度财务指标监控")
    print("🔍 决策支持: 结构化数据呈现，支持快速决策")
    print("📱 便携访问: Web格式便于分享和查看")
    print("🎯 专业呈现: 适合投资报告和分析展示")
    
    print(f"\n✅ 演示完成!")
    
    return 0 if successful_tests == total_tests else 1

if __name__ == "__main__":
    exit(main())