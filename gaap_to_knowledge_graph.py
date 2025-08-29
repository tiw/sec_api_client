#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GAAP概念知识图谱集成器
将GAAP概念解释器的数据集成到Neo4j知识图谱中
"""

import sys
import os
import json
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入项目模块
sys.path.insert(0, os.path.dirname(__file__))
from gaap_concept_explainer import EnhancedGAAPExplainer
from src.concept_explainer import ConceptExplainer

# 尝试导入neo4j，提供备选方案
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️  Neo4j驱动未安装，请运行: pip install neo4j")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GAAPKnowledgeGraphIntegrator:
    """GAAP概念知识图谱集成器"""
    
    def __init__(self, neo4j_uri=None, neo4j_user=None, neo4j_password=None):
        """初始化集成器"""
        self.gaap_explainer = EnhancedGAAPExplainer()
        self.concept_explainer = ConceptExplainer()
        
        # 从环境变量获取Neo4j连接参数
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASS")
        self.driver = None
        
        # 数据目录
        self.data_dir = Path("/Users/tingwang/work/sec_api_client/data")
        self.data_dir.mkdir(exist_ok=True)
        
    def connect_neo4j(self):
        """连接Neo4j数据库"""
        if not NEO4J_AVAILABLE:
            logger.warning("Neo4j不可用，将仅生成数据文件")
            return False
        
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
            )
            # 测试连接
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Neo4j连接成功")
            return True
        except Exception as e:
            logger.warning(f"Neo4j连接失败: {e}")
            return False
    
    def extract_gaap_concepts_from_explainer(self) -> List[Dict[str, Any]]:
        """从概念解释器提取GAAP概念"""
        logger.info("从概念解释器提取GAAP概念...")
        
        gaap_concepts = []
        
        # 从内置字典提取概念
        concept_names = set()
        concept_names.update(self.concept_explainer.CONCEPT_CHINESE_NAMES.keys())
        concept_names.update(self.concept_explainer.CONCEPT_DEFINITIONS.keys())
        concept_names.update(self.concept_explainer.CONCEPT_ENGLISH_EXPLANATIONS.keys())
        
        # 添加估值分析相关概念
        for analysis_type, categories in self.gaap_explainer.valuation_concepts.items():
            for category, concepts in categories.items():
                concept_names.update(concepts)
        
        # 构建概念信息
        for concept in concept_names:
            gaap_concept = {
                'concept': concept,
                'us_gaap_concept': f'us-gaap:{concept}',
                'chinese_name': self.concept_explainer.CONCEPT_CHINESE_NAMES.get(concept, ''),
                'chinese_definition': self.concept_explainer.CONCEPT_DEFINITIONS.get(concept, ''),
                'english_explanation': self.concept_explainer.CONCEPT_ENGLISH_EXPLANATIONS.get(concept, ''),
                'category': self.gaap_explainer._categorize_concept(concept),
                'data_type': self.gaap_explainer._infer_data_type_from_name(concept),
                'valuation_context': self.gaap_explainer._get_valuation_context(concept)
            }
            gaap_concepts.append(gaap_concept)
        
        logger.info(f"提取了 {len(gaap_concepts)} 个GAAP概念")
        return gaap_concepts
    
    def generate_sample_data_files(self):
        """生成示例数据文件以支持知识图谱构建"""
        logger.info("生成示例数据文件...")
        
        # 1. 生成gaap_metric_mapping.csv
        gaap_concepts = self.extract_gaap_concepts_from_explainer()
        
        mapping_data = []
        for i, concept_info in enumerate(gaap_concepts):
            mapping_data.append({
                'metric_id': f'metric_{i+1:03d}',
                'metric_name': concept_info['concept'],
                'us_gaap_concept': concept_info['us_gaap_concept'],
                'mapping_status': 'mapped',
                'confidence': 0.9,
                'mapping_method': 'concept_explainer'
            })
        
        mapping_df = pd.DataFrame(mapping_data)
        mapping_df.to_csv(self.data_dir / "gaap_metric_mapping.csv", index=False)
        logger.info(f"生成映射文件: {len(mapping_data)} 条记录")
        
        # 2. 生成metrics_nodes文件
        metrics_data = []
        for i, concept_info in enumerate(gaap_concepts):
            metrics_data.append({
                ':ID': f'metric_{i+1:03d}',
                'name': concept_info['concept'],
                'name_chinese': concept_info['chinese_name'],
                'metrics_type': '基础指标' if concept_info['category'] in ['assets', 'liabilities', 'equity'] else '计算指标',
                'formula_id': f'formula_{i+1:03d}' if concept_info['category'] == 'calculated' else '',
                'view_id': f'view_{concept_info["category"]}'
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        metrics_df.to_csv(self.data_dir / "1.metrics_nodes.csv", index=False)
        
        # 3. 生成视图结构
        categories = set(concept['category'] for concept in gaap_concepts)
        view_data = []
        for i, category in enumerate(categories):
            view_data.append({
                ':ID': f'view_{category}',
                'view_name': category.title().replace('_', ' '),
                'level': 1,
                'parent_id': 'root_view'
            })
        
        # 添加根视图
        view_data.append({
            ':ID': 'root_view',
            'view_name': 'Financial Concepts',
            'level': 0,
            'parent_id': None
        })
        
        views_df = pd.DataFrame(view_data)
        views_df.to_csv(self.data_dir / "4.view_nodes.csv", index=False)
        
        # 4. 生成简单的公式文件
        formula_data = [{
            ':ID': f'formula_{i+1:03d}',
            'formula_expression': f'{concept["concept"]} = Base Calculation',
            'formula_chinese': f'{concept["chinese_name"]}计算公式'
        } for i, concept in enumerate(gaap_concepts) if concept['category'] == 'calculated']
        
        formulas_df = pd.DataFrame(formula_data)
        formulas_df.to_csv(self.data_dir / "2.formula_nodes.csv", index=False)
        
        # 5. 生成空的关系文件
        empty_rel_df = pd.DataFrame(columns=[':START_ID', ':END_ID', ':TYPE'])
        empty_rel_df.to_csv(self.data_dir / "3.formula_relationships.csv", index=False)
        
        # 6. 生成空的过程指标文件
        empty_process_df = pd.DataFrame(columns=[':ID', 'name', 'name_chinese', 'metrics_type', 'view_id'])
        empty_process_df.to_csv(self.data_dir / "5.process_metrics_nodes.csv", index=False)
        
        logger.info("示例数据文件生成完成")
    
    def create_gaap_concepts_in_neo4j(self):
        """在Neo4j中创建GAAP概念"""
        if not self.driver:
            logger.warning("Neo4j未连接，跳过数据库操作")
            return
        
        logger.info("在Neo4j中创建GAAP概念...")
        
        gaap_concepts = self.extract_gaap_concepts_from_explainer()
        
        with self.driver.session() as session:
            # 创建约束
            try:
                session.run("CREATE CONSTRAINT gaap_concept_id IF NOT EXISTS FOR (g:GAAPConcept) REQUIRE g.id IS UNIQUE")
            except:
                pass
            
            # 导入概念
            for concept_info in gaap_concepts:
                session.run("""
                    MERGE (g:GAAPConcept {id: $id})
                    SET g.name = $name,
                        g.chinese_name = $chinese_name,
                        g.chinese_definition = $chinese_definition,
                        g.english_explanation = $english_explanation,
                        g.category = $category,
                        g.data_type = $data_type,
                        g.namespace = 'us-gaap',
                        g.valuation_relevance = $valuation_relevance,
                        g.created_at = datetime()
                """, {
                    'id': concept_info['us_gaap_concept'],
                    'name': concept_info['concept'],
                    'chinese_name': concept_info['chinese_name'],
                    'chinese_definition': concept_info['chinese_definition'],
                    'english_explanation': concept_info['english_explanation'],
                    'category': concept_info['category'],
                    'data_type': concept_info['data_type'],
                    'valuation_relevance': concept_info['valuation_context'].get('valuation_relevance', 'none')
                })
        
        logger.info(f"在Neo4j中创建了 {len(gaap_concepts)} 个GAAP概念")
    
    def export_enhanced_concepts(self, output_file: str = None):
        """导出增强的概念信息"""
        if not output_file:
            output_file = self.data_dir / "enhanced_gaap_concepts.json"
        
        logger.info("导出增强的概念信息...")
        
        gaap_concepts = self.extract_gaap_concepts_from_explainer()
        
        # 保存为JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(gaap_concepts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"增强概念信息已保存到: {output_file}")
        
        # 同时保存为CSV供分析使用
        concepts_df = pd.DataFrame(gaap_concepts)
        csv_file = str(output_file).replace('.json', '.csv')
        concepts_df.to_csv(csv_file, index=False, encoding='utf-8')
        
        return gaap_concepts
    
    def full_integration(self):
        """完整集成流程"""
        logger.info("开始GAAP概念知识图谱完整集成...")
        
        try:
            # 1. 生成数据文件
            self.generate_sample_data_files()
            
            # 2. 导出增强概念信息
            self.export_enhanced_concepts()
            
            # 3. 尝试连接Neo4j并创建概念
            if self.connect_neo4j():
                self.create_gaap_concepts_in_neo4j()
                logger.info("✅ Neo4j集成完成")
            else:
                logger.info("⚠️  Neo4j不可用，但数据文件已生成")
            
            # 4. 生成使用说明
            self.generate_usage_instructions()
            
            logger.info("🎉 GAAP概念知识图谱集成完成！")
            
        except Exception as e:
            logger.error(f"集成过程失败: {e}")
            raise
        finally:
            if self.driver:
                self.driver.close()
    
    def generate_usage_instructions(self):
        """生成使用说明"""
        instructions = """
# GAAP概念知识图谱使用说明

## 生成的文件

1. **data/gaap_metric_mapping.csv** - GAAP概念与指标映射
2. **data/enhanced_gaap_concepts.json** - 增强的概念信息
3. **data/enhanced_gaap_concepts.csv** - 概念信息CSV格式
4. **data/*.csv** - Neo4j导入所需的节点和关系文件

## 使用Neo4j知识图谱

### 1. 启动Neo4j
```bash
# 使用Docker启动Neo4j
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### 2. 导入数据
```python
from neo4j_knowledge_graph import FinancialMetricsKnowledgeGraph

kg = FinancialMetricsKnowledgeGraph()
kg.full_import()
```

### 3. 查询示例
```cypher
// 查找所有证券投资相关概念
MATCH (g:GAAPConcept) WHERE g.category = 'securities' RETURN g

// 查找有中文定义的概念
MATCH (g:GAAPConcept) WHERE g.chinese_name <> '' RETURN g.name, g.chinese_name

// 查找估值分析相关概念
MATCH (g:GAAPConcept) WHERE g.valuation_relevance <> 'none' RETURN g
```

## 扩展概念

要添加新的GAAP概念，请更新：
1. `src/concept_explainer.py` 中的字典
2. `gaap_concept_explainer.py` 中的扩展字典
3. 重新运行集成器
"""
        
        with open(self.data_dir / "README_KNOWLEDGE_GRAPH.md", 'w', encoding='utf-8') as f:
            f.write(instructions)

def main():
    """主函数"""
    print("🚀 启动GAAP概念知识图谱集成器...")
    
    integrator = GAAPKnowledgeGraphIntegrator()
    integrator.full_integration()

if __name__ == "__main__":
    main()