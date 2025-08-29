#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GAAP概念知识图谱演示脚本
展示如何使用生成的GAAP概念数据，无需Neo4j依赖
"""

import json
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GAAPConceptAnalyzer:
    """GAAP概念分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.data_dir = Path("/Users/tingwang/work/sec_api_client/data")
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        # 加载增强概念数据
        concepts_file = self.data_dir / "enhanced_gaap_concepts.json"
        if concepts_file.exists():
            with open(concepts_file, 'r', encoding='utf-8') as f:
                self.concepts = json.load(f)
            logger.info(f"加载了 {len(self.concepts)} 个GAAP概念")
        else:
            self.concepts = []
            logger.warning("GAAP概念文件不存在")
        
        # 加载映射数据
        mapping_file = self.data_dir / "gaap_metric_mapping.csv"
        if mapping_file.exists():
            self.mapping_df = pd.read_csv(mapping_file)
            logger.info(f"加载了 {len(self.mapping_df)} 个映射关系")
        else:
            self.mapping_df = pd.DataFrame()
            logger.warning("映射文件不存在")
    
    def analyze_concept_categories(self):
        """分析概念类别分布"""
        if not self.concepts:
            return
        
        print("\n📊 GAAP概念类别分布分析")
        print("=" * 60)
        
        # 统计类别
        categories = {}
        for concept in self.concepts:
            category = concept.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        # 显示统计结果
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(self.concepts) * 100
            print(f"{category.ljust(20)}: {count:2d} 个概念 ({percentage:5.1f}%)")
        
        print(f"\n总计: {len(self.concepts)} 个概念")
    
    def analyze_valuation_concepts(self):
        """分析估值相关概念"""
        if not self.concepts:
            return
        
        print("\n💰 估值分析相关概念")
        print("=" * 60)
        
        valuation_concepts = []
        for concept in self.concepts:
            valuation_context = concept.get('valuation_context', {})
            if isinstance(valuation_context, str):
                # 处理字符串格式的valuation_context
                try:
                    valuation_context = eval(valuation_context)
                except:
                    valuation_context = {}
            
            if valuation_context.get('valuation_relevance') == 'high':
                valuation_concepts.append(concept)
        
        if valuation_concepts:
            print(f"发现 {len(valuation_concepts)} 个估值相关概念:\n")
            
            # 按分析类别分组
            by_category = {}
            for concept in valuation_concepts:
                valuation_context = concept.get('valuation_context', {})
                if isinstance(valuation_context, str):
                    try:
                        valuation_context = eval(valuation_context)
                    except:
                        valuation_context = {}
                
                category = valuation_context.get('analysis_category', '未分类')
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(concept)
            
            for category, concepts in by_category.items():
                print(f"🔍 {category}")
                for concept in concepts:
                    chinese_name = concept.get('chinese_name', '')
                    concept_name = concept.get('concept', '')
                    role = ''
                    
                    valuation_context = concept.get('valuation_context', {})
                    if isinstance(valuation_context, str):
                        try:
                            valuation_context = eval(valuation_context)
                        except:
                            valuation_context = {}
                    
                    calc_role = valuation_context.get('calculation_role', '')
                    if calc_role:
                        role = f" - {calc_role}"
                    
                    display_name = f"{chinese_name} ({concept_name})" if chinese_name else concept_name
                    print(f"  • {display_name}{role}")
                print()
        else:
            print("未找到估值相关概念")
    
    def find_concepts_with_chinese(self):
        """查找有中文翻译的概念"""
        if not self.concepts:
            return
        
        print("\n🇨🇳 有中文翻译的GAAP概念")
        print("=" * 60)
        
        chinese_concepts = []
        for concept in self.concepts:
            if concept.get('chinese_name') and concept.get('chinese_definition'):
                chinese_concepts.append(concept)
        
        print(f"发现 {len(chinese_concepts)} 个有完整中文翻译的概念:\n")
        
        for concept in chinese_concepts[:10]:  # 显示前10个
            print(f"📝 {concept['concept']}")
            print(f"   中文名称: {concept['chinese_name']}")
            print(f"   中文定义: {concept['chinese_definition'][:80]}...")
            print()
        
        if len(chinese_concepts) > 10:
            print(f"... 还有 {len(chinese_concepts) - 10} 个概念")
    
    def search_concept(self, keyword: str):
        """搜索概念"""
        if not self.concepts:
            return
        
        print(f"\n🔍 搜索包含 '{keyword}' 的概念")
        print("=" * 60)
        
        results = []
        keyword_lower = keyword.lower()
        
        for concept in self.concepts:
            # 在概念名称、中文名称、中文定义中搜索
            if (keyword_lower in concept.get('concept', '').lower() or
                keyword_lower in concept.get('chinese_name', '').lower() or
                keyword_lower in concept.get('chinese_definition', '').lower()):
                results.append(concept)
        
        if results:
            print(f"找到 {len(results)} 个相关概念:\n")
            for concept in results:
                chinese_name = concept.get('chinese_name', '')
                chinese_def = concept.get('chinese_definition', '')
                
                print(f"📌 {concept['concept']}")
                if chinese_name:
                    print(f"   中文名称: {chinese_name}")
                if chinese_def:
                    print(f"   中文定义: {chinese_def}")
                print(f"   类别: {concept.get('category', 'unknown')}")
                print(f"   数据类型: {concept.get('data_type', 'unknown')}")
                print()
        else:
            print("未找到相关概念")
    
    def generate_neo4j_cypher_examples(self):
        """生成Neo4j Cypher查询示例"""
        print("\n🔧 Neo4j Cypher查询示例")
        print("=" * 60)
        
        cypher_examples = [
            {
                "描述": "查询所有GAAP概念",
                "查询": "MATCH (g:GAAPConcept) RETURN g.name, g.chinese_name, g.category LIMIT 10"
            },
            {
                "描述": "查询估值相关概念",
                "查询": "MATCH (g:GAAPConcept) WHERE g.valuation_relevance = 'high' RETURN g"
            },
            {
                "描述": "按类别统计概念数量",
                "查询": "MATCH (g:GAAPConcept) RETURN g.category, count(*) as count ORDER BY count DESC"
            },
            {
                "描述": "查询资产类概念",
                "查询": "MATCH (g:GAAPConcept) WHERE g.category = 'assets' RETURN g.name, g.chinese_name"
            },
            {
                "描述": "查询有中文定义的概念",
                "查询": "MATCH (g:GAAPConcept) WHERE g.chinese_definition <> '' RETURN g.name, g.chinese_name, g.chinese_definition"
            },
            {
                "描述": "查询每股相关指标",
                "查询": "MATCH (g:GAAPConcept) WHERE g.data_type = 'monetary_per_share' RETURN g"
            }
        ]
        
        for example in cypher_examples:
            print(f"💡 {example['描述']}")
            print(f"```cypher")
            print(f"{example['查询']}")
            print(f"```\n")
    
    def export_summary_report(self):
        """导出概要报告"""
        if not self.concepts:
            return
        
        # 统计信息
        total_concepts = len(self.concepts)
        chinese_concepts = len([c for c in self.concepts if c.get('chinese_name')])
        valuation_concepts = len([c for c in self.concepts if 'high' in str(c.get('valuation_context', {}))])
        
        # 类别统计
        categories = {}
        for concept in self.concepts:
            category = concept.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        # 生成报告
        report = f"""
# GAAP概念知识图谱分析报告

## 概览统计
- 总概念数: {total_concepts} 个
- 有中文翻译: {chinese_concepts} 个 ({chinese_concepts/total_concepts*100:.1f}%)
- 估值相关: {valuation_concepts} 个 ({valuation_concepts/total_concepts*100:.1f}%)

## 类别分布
"""
        
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_concepts * 100
            report += f"- {category}: {count} 个 ({percentage:.1f}%)\n"
        
        report += f"""

## 数据文件
- enhanced_gaap_concepts.json: 增强概念数据
- enhanced_gaap_concepts.csv: 概念数据CSV格式  
- gaap_metric_mapping.csv: 概念与指标映射
- *.csv: Neo4j导入用节点和关系文件

## 下一步
1. 安装并启动Neo4j数据库
2. 运行 neo4j_knowledge_graph.py 导入数据
3. 使用Cypher查询分析概念关系
4. 扩展概念库添加更多US-GAAP概念
"""
        
        # 保存报告
        report_file = self.data_dir / "gaap_concepts_analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📋 分析报告已保存到: {report_file}")

def main():
    """主函数"""
    print("🚀 GAAP概念知识图谱分析器")
    print("=" * 60)
    
    analyzer = GAAPConceptAnalyzer()
    
    # 执行各种分析
    analyzer.analyze_concept_categories()
    analyzer.analyze_valuation_concepts()
    analyzer.find_concepts_with_chinese()
    
    # 演示搜索功能
    analyzer.search_concept("cash")
    analyzer.search_concept("股东权益")
    
    # 生成Cypher示例
    analyzer.generate_neo4j_cypher_examples()
    
    # 导出报告
    analyzer.export_summary_report()
    
    print("\n✅ 分析完成！")

if __name__ == "__main__":
    main()