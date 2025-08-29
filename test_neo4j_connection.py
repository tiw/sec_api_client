#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j 连接测试和设置助手
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_env_file():
    """检查.env文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env文件不存在")
        print("\n请创建.env文件，内容如下:")
        print("NEO4J_URI=bolt://localhost:7687")
        print("NEO4J_USER=neo4j")
        print("NEO4J_PASS=your_password")
        return False
    
    print("✅ .env文件存在")
    
    # 检查必要的环境变量
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASS']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 对密码进行脱敏显示
            display_value = value if var != 'NEO4J_PASS' else '*' * len(value)
            print(f"✅ {var} = {display_value}")
        else:
            print(f"❌ {var} = 未设置")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  缺少环境变量: {', '.join(missing_vars)}")
        return False
    
    return True

def test_neo4j_connection():
    """测试Neo4j连接"""
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("❌ neo4j库未安装，请运行: pip install neo4j")
        return False
    
    # 获取连接参数
    uri = os.getenv('NEO4J_URI')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASS')
    
    if not all([uri, user, password]):
        print("❌ 连接参数不完整")
        return False
    
    print(f"\n🔗 尝试连接到 {uri}...")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # 测试连接
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                print("✅ Neo4j连接成功!")
                
                # 获取数据库信息
                db_info = session.run("CALL dbms.components()").data()
                for component in db_info:
                    if component.get('name') == 'Neo4j Kernel':
                        version = component.get('versions', ['未知'])[0]
                        print(f"📊 Neo4j版本: {version}")
                        break
                
                driver.close()
                return True
            else:
                print("❌ 连接测试失败")
                driver.close()
                return False
                
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        
        # 提供常见错误的解决方案
        error_str = str(e).lower()
        if 'unauthorized' in error_str or 'authentication' in error_str:
            print("\n💡 可能的解决方案:")
            print("1. 检查用户名和密码是否正确")
            print("2. 确保Neo4j数据库已启动")
            print("3. 如果是新安装，可能需要重置密码")
        elif 'connection refused' in error_str:
            print("\n💡 可能的解决方案:")
            print("1. 确保Neo4j数据库已启动")
            print("2. 检查端口7687是否可用")
            print("3. 如果使用Docker，确保端口映射正确")
        
        return False

def provide_setup_instructions():
    """提供设置说明"""
    print("\n📋 Neo4j设置说明")
    print("=" * 50)
    
    instructions = """
1. 安装Neo4j (选择一种方式):

   方式A - 使用Docker (推荐):
   docker run -d --name neo4j-gaap \\
     -p 7474:7474 -p 7687:7687 \\
     -e NEO4J_AUTH=neo4j/your_password \\
     neo4j:latest

   方式B - 下载Neo4j Desktop:
   https://neo4j.com/download/

2. 创建.env文件:
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASS=your_password

3. 安装依赖:
   pip install python-dotenv neo4j

4. 测试连接:
   python test_neo4j_connection.py
"""
    print(instructions)

def main():
    """主函数"""
    print("🧪 Neo4j连接测试工具")
    print("=" * 50)
    
    # 检查.env文件
    if not check_env_file():
        provide_setup_instructions()
        return
    
    # 测试连接
    if test_neo4j_connection():
        print("\n🎉 一切就绪！现在可以运行知识图谱导入:")
        print("python neo4j_knowledge_graph.py")
    else:
        provide_setup_instructions()

if __name__ == "__main__":
    main()