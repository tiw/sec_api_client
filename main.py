#!/usr/bin/env python3
"""
SEC EDGAR API客户端项目

一个功能完整的Python项目，用于访问美国证券交易委员会(SEC)的EDGAR数据库
获取公司的10-K、10-Q财务报告和XBRL结构化数据

主要功能:
- 🔍 公司信息搜索
- 📋 10-K/10-Q文档获取
- 💰 XBRL/Frames财务数据访问
- 📊 财务数据分析和比率计算
- 📈 趋势分析和同行对比
"""

import os


def show_project_info():
    """显示项目信息"""
    print("🚀 SEC EDGAR API 客户端")
    print("="*50)
    print("📁 项目结构:")
    print("  src/              - 源代码目录")
    print("    sec_client.py    - SEC API核心客户端")
    print("    document_retriever.py - 10-K/10-Q文档获取")
    print("    xbrl_frames.py   - XBRL/Frames数据访问")
    print("    financial_analyzer.py - 财务数据分析")
    print("  examples/         - 使用示例")
    print("  tests/           - 测试代码")
    print()
    
    print("📚 使用示例:")
    print("  python examples/basic_usage.py          - 基本使用示例")
    print("  python examples/xbrl_frames_demo.py     - XBRL数据演示")
    print("  python examples/financial_analysis_demo.py - 财务分析演示")
    print()
    
    print("⚡ 快速开始:")
    print("  1. 激活虚拟环境: source venv/bin/activate")
    print("  2. 安装依赖: pip install -r requirements.txt")
    print("  3. 运行示例: python examples/basic_usage.py")
    print()
    
    print("📖 重要提醒:")
    print("  - 使用API前请设置正确的User-Agent（包含您的邮箱）")
    print("  - SEC API有频率限制，每秒最多10次请求")
    print("  - 建议在业务时间外使用以避免影响SEC服务器")
    print()


def main():
    """主函数"""
    show_project_info()
    
    # 检查依赖是否已安装
    try:
        import requests
        import pandas
        import numpy
        from bs4 import BeautifulSoup
        print("✅ 所有依赖已正确安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 检查示例文件
    examples_dir = "examples"
    if os.path.exists(examples_dir):
        example_files = [f for f in os.listdir(examples_dir) if f.endswith('.py')]
        if example_files:
            print(f"\n🎯 可用的示例文件 ({len(example_files)} 个):")
            for i, filename in enumerate(example_files, 1):
                print(f"  {i}. {filename}")
    
    print("\n🎉 项目已就绪！请查看examples目录中的示例代码开始使用。")


if __name__ == "__main__":
    main()