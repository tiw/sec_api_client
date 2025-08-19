#!/usr/bin/env python3
"""
示例脚本：演示如何通过程序获取SEC XBRL中PaymentsToAcquirePropertyPlantAndEquipment概念的定义和出处

User-Agent: Ting Wang <tting.wang@gmail.com>
"""

import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, XBRLFramesClient
import json


def get_concept_definition():
    """获取PaymentsToAcquirePropertyPlantAndEquipment概念的定义和出处"""
    
    print("🔍 获取SEC XBRL概念定义示例")
    print("="*50)
    
    # 初始化客户端
    user_agent = "Ting Wang tting.wang@gmail.com"
    sec_client = SECClient(user_agent=user_agent)
    xbrl_client = XBRLFramesClient(sec_client)
    
    # 要查询的概念
    concept = "PaymentsToAcquirePropertyPlantAndEquipment"
    taxonomy = "us-gaap"
    
    print(f"🏢 概念: {concept}")
    print(f"📚 分类标准: {taxonomy}")
    print(f"📧 User-Agent: {user_agent}")
    
    # 方法1: 通过companyconcept API获取概念定义信息
    print(f"\n📋 方法1: 通过companyconcept API获取概念定义")
    print("-" * 40)
    
    # 使用Apple公司CIK获取示例数据
    apple_cik = "0000320193"
    try:
        print(f"正在获取Apple公司{concept}概念数据...")
        concept_data = xbrl_client.get_company_concept_data(
            cik=apple_cik,
            concept=concept,
            taxonomy=taxonomy
        )
        
        if concept_data:
            print("✅ 成功获取概念数据")
            
            # 显示概念的基本信息
            print(f"\n📊 概念基本信息:")
            print(f"  标签 (tag): {concept_data.get('tag', 'N/A')}")
            print(f"  分类标准 (taxonomy): {concept_data.get('taxonomy', 'N/A')}")
            print(f"  单位 (units): {list(concept_data.get('units', {}).keys())}")
            
            # 显示概念的定义信息（如果有的话）
            if 'concept' in concept_data:
                print(f"\n📝 概念定义信息:")
                concept_info = concept_data['concept']
                print(f"  命名空间 (namespace): {concept_info.get('namespace', 'N/A')}")
                print(f"  标准标签 (standard label): {concept_info.get('label', 'N/A')}")
                
                # 显示参考信息
                if 'reference' in concept_info:
                    print(f"\n📖 参考信息:")
                    for ref in concept_info['reference']:
                        print(f"  条款: {ref.get('section', 'N/A')}")
                        print(f"  描述: {ref.get('description', 'N/A')}")
                        print(f"  类型: {ref.get('type', 'N/A')}")
                        print(f"  URI: {ref.get('uri', 'N/A')}")
                        print()
            
            # 显示部分数据点作为示例
            print(f"\n📈 数据示例 (最近5条):")
            units_data = concept_data.get('units', {})
            if units_data:
                # 查看USD单位的数据
                usd_data = units_data.get('USD', [])
                if usd_data:
                    for i, item in enumerate(usd_data[-5:]):  # 显示最近5条
                        print(f"  {i+1}. 金额: {item.get('val', 'N/A'):,}")
                        print(f"      期间: {item.get('start', 'N/A')} 至 {item.get('end', 'N/A')}")
                        print(f"      表单: {item.get('form', 'N/A')}")
                        print(f"      财年: FY{item.get('fy', 'N/A')}")
                        print(f"      财期: {item.get('fp', 'N/A')}")
                        print(f"      提交日期: {item.get('filed', 'N/A')}")
                        print()
                else:
                    print("  未找到USD单位数据")
            else:
                print("  未找到单位数据")
        else:
            print("❌ 获取概念数据失败")
            
    except Exception as e:
        print(f"❌ 获取概念数据时出错: {e}")
    
    # 方法2: 通过frames API获取概念信息
    print(f"\n📋 方法2: 通过frames API获取概念信息")
    print("-" * 40)
    
    try:
        # 获取最近一个财年的数据
        period = "CY2024"  # 2024财年
        unit = "USD"
        
        print(f"正在获取{period}期间的{concept}概念数据...")
        frame_data = xbrl_client.get_concept_data(
            concept=concept,
            period=period,
            unit=unit,
            taxonomy=taxonomy
        )
        
        if not frame_data.empty:
            print("✅ 成功获取框架数据")
            
            # 显示元数据
            print(f"\n📊 框架元数据:")
            print(f"  分类标准 (taxonomy): {frame_data.get('taxonomy', ['N/A'])[0] if 'taxonomy' in frame_data else 'N/A'}")
            print(f"  标签 (tag): {frame_data.get('tag', ['N/A'])[0] if 'tag' in frame_data else 'N/A'}")
            print(f"  单位 (uom): {frame_data.get('uom', ['N/A'])[0] if 'uom' in frame_data else 'N/A'}")
            print(f"  标签 (label): {frame_data.get('label', ['N/A'])[0] if 'label' in frame_data else 'N/A'}")
            print(f"  CCP: {frame_data.get('ccp', ['N/A'])[0] if 'ccp' in frame_data else 'N/A'}")
            
            # 显示前几条数据
            print(f"\n📈 数据示例:")
            print(frame_data[['cik', 'entityName', 'val', 'end']].head().to_string(index=False))
        else:
            print("❌ 未获取到框架数据")
            
    except Exception as e:
        print(f"❌ 获取框架数据时出错: {e}")
    
    # 方法3: 解释如何查找概念的官方定义
    print(f"\n📋 方法3: 查找概念的官方定义")
    print("-" * 40)
    print("要获取PaymentsToAcquirePropertyPlantAndEquipment的官方定义，可以通过以下途径:")
    print()
    print("1. 访问FASB XBRL分类标准网站:")
    print("   - 网址: https://fasb.org/xbrl")
    print("   - 搜索概念: PaymentsToAcquirePropertyPlantAndEquipment")
    print()
    print("2. 查看SEC EDGAR数据库中的官方文档:")
    print("   - 网址: https://www.sec.gov/edgar")
    print("   - 搜索包含该概念的公司文件")
    print()
    print("3. 查看US GAAP分类标准文档:")
    print("   - 概念定义: 用于购买、建造和资本化的厂房设备的现金支出")
    print("   - 通常出现在现金流量表的投资活动部分")
    print("   - 属于现金流量表项目，反映企业在固定资产方面的投资")
    print()
    print("4. 根据XBRL标准，该概念的详细信息包括:")
    print("   - 命名空间: http://fasb.org/us-gaap/2024")
    print("   - 类型: monetary")
    print("   - 期间类型: duration")
    print("   - 可用单位: USD等货币单位")
    
    print(f"\n✅ 概念定义查询完成!")


def main():
    """主函数"""
    try:
        get_concept_definition()
    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断了程序执行")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    main()