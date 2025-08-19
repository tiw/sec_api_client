#!/usr/bin/env python3
"""
Concept Explainer CLI工具使用示例

演示如何使用CLI工具获取财务概念的口径解释
User-Agent: Ting Wang <tting.wang@gmail.com>
"""

import subprocess
import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_example():
    """运行示例命令"""
    print("🎯 Concept Explainer CLI工具使用示例")
    print("="*50)
    
    # 示例1: PaymentsToAcquirePropertyPlantAndEquipment
    print("\n📝 示例1: 获取PaymentsToAcquirePropertyPlantAndEquipment概念解释")
    print("命令: python -m src.concept_explainer PaymentsToAcquirePropertyPlantAndEquipment 0000320193")
    print("-" * 60)
    
    try:
        result = subprocess.run([
            'python', '-m', 'src.concept_explainer', 
            'PaymentsToAcquirePropertyPlantAndEquipment', 
            '0000320193'
        ], cwd='/Users/tingwang/work/sec_api_client', capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ 命令执行失败:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("⚠️ 命令执行超时")
    except Exception as e:
        print(f"❌ 执行出错: {e}")
    
    # 示例2: CommercialPaper
    print("\n📝 示例2: 获取CommercialPaper概念解释")
    print("命令: python -m src.concept_explainer CommercialPaper 0000320193")
    print("-" * 60)
    
    try:
        result = subprocess.run([
            'python', '-m', 'src.concept_explainer', 
            'CommercialPaper', 
            '0000320193'
        ], cwd='/Users/tingwang/work/sec_api_client', capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ 命令执行失败:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("⚠️ 命令执行超时")
    except Exception as e:
        print(f"❌ 执行出错: {e}")
    
    # 示例3: LongTermDebtNoncurrent
    print("\n📝 示例3: 获取LongTermDebtNoncurrent概念解释")
    print("命令: python -m src.concept_explainer LongTermDebtNoncurrent 0000320193")
    print("-" * 60)
    
    try:
        result = subprocess.run([
            'python', '-m', 'src.concept_explainer', 
            'LongTermDebtNoncurrent', 
            '0000320193'
        ], cwd='/Users/tingwang/work/sec_api_client', capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ 命令执行失败:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("⚠️ 命令执行超时")
    except Exception as e:
        print(f"❌ 执行出错: {e}")
    
    print("\n✅ 示例演示完成!")


def main():
    """主函数"""
    try:
        run_example()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了程序执行")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    main()