#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
US-GAAP概念下载和解释使用示例

演示如何使用脚本下载US-GAAP概念并获取详细解释

作者: Ting Wang <tting.wang@gmail.com>
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"命令: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 命令执行成功")
            if result.stdout:
                print("输出:")
                print(result.stdout)
        else:
            print("❌ 命令执行失败")
            if result.stderr:
                print("错误:")
                print(result.stderr)
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")

def main():
    """主演示函数"""
    print("US-GAAP概念下载和解释工具演示")
    print("该演示将展示如何下载和解释US-GAAP财务概念")
    
    # 1. 下载基本概念列表
    run_command(
        "python download_gaap_concepts.py --concepts-only --output basic_concepts.csv",
        "下载基本US-GAAP概念列表"
    )
    
    time.sleep(2)
    
    # 2. 下载特定分类的概念（带定义）
    run_command(
        "python download_gaap_concepts.py --category assets --with-definitions --output assets_concepts.csv",
        "下载资产类概念（包含定义）"
    )
    
    time.sleep(2)
    
    # 3. 解释单个概念
    run_command(
        "python gaap_concept_explainer.py --single-concept NetIncomeLoss",
        "详细解释单个概念：NetIncomeLoss（净利润）"
    )
    
    time.sleep(2)
    
    # 4. 批量解释多个概念
    concepts = [
        "Assets", "Liabilities", "StockholdersEquity", 
        "RevenueFromContractWithCustomerExcludingAssessedTax", "NetIncomeLoss"
    ]
    concepts_str = " ".join(concepts)
    
    run_command(
        f"python gaap_concept_explainer.py --concepts {concepts_str} --output batch_explanations.json",
        "批量解释多个核心财务概念"
    )
    
    time.sleep(2)
    
    # 5. 解释估值分析相关概念
    run_command(
        "python gaap_concept_explainer.py --valuation-concepts --output valuation_analysis.csv",
        "解释所有估值分析相关概念"
    )
    
    time.sleep(2)
    
    # 6. 创建完整概念词典
    run_command(
        "python download_gaap_concepts.py --create-dictionary",
        "创建完整的US-GAAP概念词典"
    )
    
    print("\n" + "="*60)
    print("🎉 演示完成！")
    print("="*60)
    
    # 显示生成的文件
    output_files = [
        "basic_concepts.csv",
        "assets_concepts.csv", 
        "batch_explanations.json",
        "valuation_analysis.csv",
        "gaap_dictionary/"
    ]
    
    print("\n📁 生成的文件:")
    for file_path in output_files:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                print(f"  ✅ {file_path} ({size:,} bytes)")
            else:
                print(f"  ✅ {file_path}/ (目录)")
        else:
            print(f"  ❌ {file_path} (未生成)")
    
    print("\n📖 使用说明:")
    print("1. basic_concepts.csv - 基本概念列表，可用Excel打开")
    print("2. assets_concepts.csv - 资产类概念详细信息")  
    print("3. batch_explanations.json - 批量解释结果（JSON格式）")
    print("4. valuation_analysis.csv - 估值分析相关概念")
    print("5. gaap_dictionary/ - 完整概念词典目录")
    
    print("\n🔧 高级用法:")
    print("• 解释特定概念: python gaap_concept_explainer.py --single-concept <概念名>")
    print("• 按分类下载: python download_gaap_concepts.py --category <分类名>")
    print("• 从文件批量解释: python gaap_concept_explainer.py --concepts-file concepts.txt")
    
    print("\n💡 提示:")
    print("• 所有工具都支持 --help 参数查看详细帮助")
    print("• 可以修改 --user-agent 参数设置您的联系信息")
    print("• 大批量操作会自动控制请求频率以遵守SEC API限制")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")