#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j财务指标知识图谱完整设置脚本
包括数据导入、验证和基本查询功能
"""

import pandas as pd
from pathlib import Path
import json
import logging

# 尝试导入neo4j，如果没有安装则提供安装提示
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Neo4j驱动未安装，请运行: pip install neo4j")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialKnowledgeGraph:
    """财务指标知识图谱管理类"""
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        """初始化连接"""
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j驱动未安装，请运行: pip install neo4j")
        
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.data_dir = Path("/Users/tingwang/work/sec_api_client/data")
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # 测试连接
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Neo4j连接成功")
            return True
        except Exception as e:
            logger.error(f"Neo4j连接失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j连接已关闭")
    
    def execute_cypher(self, query, parameters=None):
        """执行Cypher查询"""
        if not self.driver:
            raise RuntimeError("数据库未连接")
        
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def clear_database(self):
        """清空数据库"""
        logger.info("清空数据库...")
        self.execute_cypher("MATCH (n) DETACH DELETE n")
        logger.info("数据库已清空")
    
    def setup_schema(self):
        """设置数据库模式（约束和索引）"""
        logger.info("设置数据库模式...")
        
        schema_queries = [
            # 创建约束
            "CREATE CONSTRAINT gaap_concept_id IF NOT EXISTS FOR (g:GAAPConcept) REQUIRE g.id IS UNIQUE",
            "CREATE CONSTRAINT metric_id IF NOT EXISTS FOR (m:FinancialMetric) REQUIRE g.id IS UNIQUE",
            "CREATE CONSTRAINT formula_id IF NOT EXISTS FOR (f:Formula) REQUIRE f.id IS UNIQUE",
            "CREATE CONSTRAINT view_id IF NOT EXISTS FOR (v:View) REQUIRE v.id IS UNIQUE",
            
            # 创建索引
            "CREATE INDEX gaap_concept_name IF NOT EXISTS FOR (g:GAAPConcept) ON (g.name)",
            "CREATE INDEX metric_name IF NOT EXISTS FOR (m:FinancialMetric) ON (m.name)",
            "CREATE INDEX metric_chinese_name IF NOT EXISTS FOR (m:FinancialMetric) ON (m.chinese_name)",
        ]
        
        for query in schema_queries:
            try:
                self.execute_cypher(query)
                logger.info(f"执行成功: {query.split(' ')[1]} {query.split(' ')[2]}")
            except Exception as e:
                logger.warning(f"执行失败: {query[:50]}... 错误: {e}")
    
    def load_gaap_concepts(self):
        """加载US-GAAP概念"""
        logger.info("加载US-GAAP概念...")
        
        mapping_file = self.data_dir / "gaap_metric_mapping.csv"
        if not mapping_file.exists():
            logger.error(f"映射文件不存在: {mapping_file}")
            return False
        
        mapping_df = pd.read_csv(mapping_file)
        gaap_concepts = mapping_df['us_gaap_concept'].dropna().unique()
        
        for concept in gaap_concepts:
            name = concept.replace('us-gaap:', '')
            self.execute_cypher("""
                MERGE (g:GAAPConcept {id: $id})
                SET g.name = $name,
                    g.namespace = 'us-gaap',
                    g.full_name = $id,
                    g.created_at = datetime()
            """, {'id': concept, 'name': name})
        
        logger.info(f"加载了 {len(gaap_concepts)} 个GAAP概念")
        return True
    
    def load_financial_metrics(self):
        """加载财务指标"""
        logger.info("加载财务指标...")
        
        # 加载主要指标
        main_file = self.data_dir / "1.metrics_nodes - 工作表1.csv"
        process_file = self.data_dir / "5.过程指标_nodes - 工作表1.csv"
        
        if not main_file.exists() or not process_file.exists():
            logger.error("指标文件不存在")
            return False
        
        main_df = pd.read_csv(main_file)
        process_df = pd.read_csv(process_file)
        
        # 处理主要指标
        for _, row in main_df.iterrows():
            self.execute_cypher("""
                MERGE (m:FinancialMetric {id: $id})
                SET m.metric_id = $metric_id,
                    m.name = $name,
                    m.chinese_name = $chinese_name,
                    m.metric_type = $metric_type,
                    m.source = 'main_metrics',
                    m.created_at = datetime()
            """, {
                'id': f"metric_{row[':ID']}",
                'metric_id': row[':ID'],
                'name': row['name'],
                'chinese_name': row['name_chinese'],
                'metric_type': row['metrics_type']
            })
        
        # 处理过程指标
        for _, row in process_df.iterrows():
            self.execute_cypher("""
                MERGE (m:FinancialMetric {id: $id})
                SET m.metric_id = $metric_id,
                    m.name = $name,
                    m.chinese_name = $chinese_name,
                    m.metric_type = $metric_type,
                    m.source = 'process_metrics',
                    m.created_at = datetime()
            """, {
                'id': f"metric_{row[':ID']}",
                'metric_id': row[':ID'],
                'name': row['name'],
                'chinese_name': row['name_chinese'],
                'metric_type': row['metrics_type']
            })
        
        total_metrics = len(main_df) + len(process_df)
        logger.info(f"加载了 {total_metrics} 个财务指标")
        return True
    
    def load_views_and_formulas(self):
        """加载视图和公式"""
        logger.info("加载视图和公式...")
        
        # 加载视图
        views_file = self.data_dir / "4.view_nodes - 工作表1.csv"
        if views_file.exists():
            views_df = pd.read_csv(views_file)
            for _, row in views_df.iterrows():
                self.execute_cypher("""
                    MERGE (v:View {id: $id})
                    SET v.name = $name,
                        v.level = $level,
                        v.parent_id = $parent_id,
                        v.created_at = datetime()
                """, {
                    'id': row[':ID'],
                    'name': row['view_name'],
                    'level': int(row['level']),
                    'parent_id': row['parent_id'] if pd.notna(row['parent_id']) else None
                })
            logger.info(f"加载了 {len(views_df)} 个视图")
        
        # 加载公式
        formulas_file = self.data_dir / "2.formula_nodes. - 工作表1.csv"
        if formulas_file.exists():
            formulas_df = pd.read_csv(formulas_file)
            for _, row in formulas_df.iterrows():
                self.execute_cypher("""
                    MERGE (f:Formula {id: $id})
                    SET f.expression = $expression,
                        f.chinese_description = $chinese_description,
                        f.created_at = datetime()
                """, {
                    'id': row[':ID'],
                    'expression': row['formula_expression'],
                    'chinese_description': row['formula_chinese']
                })
            logger.info(f"加载了 {len(formulas_df)} 个公式")
        
        return True
    
    def create_relationships(self):
        """创建关系"""
        logger.info("创建关系...")
        
        # 1. 指标到GAAP概念的映射关系
        mapping_file = self.data_dir / "gaap_metric_mapping.csv"
        if mapping_file.exists():
            mapping_df = pd.read_csv(mapping_file)
            for _, row in mapping_df.iterrows():
                confidence = 1.0 if row['mapping_status'] == 'mapped' else 0.7
                self.execute_cypher("""
                    MATCH (m:FinancialMetric {metric_id: $metric_id})
                    MATCH (g:GAAPConcept {id: $gaap_concept})
                    MERGE (m)-[r:MAPS_TO_GAAP]->(g)
                    SET r.mapping_status = $mapping_status,
                        r.confidence = $confidence,
                        r.created_at = datetime()
                """, {
                    'metric_id': row['metric_id'],
                    'gaap_concept': row['us_gaap_concept'],
                    'mapping_status': row['mapping_status'],
                    'confidence': confidence
                })
            logger.info(f"创建了 {len(mapping_df)} 个映射关系")
        
        # 2. 其他关系可以在这里添加
        return True
    
    def create_labels_and_categories(self):
        """创建标签和分类"""
        logger.info("创建标签和分类...")
        
        # 指标类型标签
        self.execute_cypher("""
            MATCH (m:FinancialMetric)
            WHERE m.metric_type = '基础指标'
            SET m:BasicMetric
        """)
        
        self.execute_cypher("""
            MATCH (m:FinancialMetric)
            WHERE m.metric_type = '计算指标'
            SET m:CalculatedMetric
        """)
        
        # GAAP概念分类
        categories = [
            ('Assets', 'AssetConcept'),
            ('Liabilit', 'LiabilityConcept'),
            ('Equity', 'EquityConcept'),
            ('Income', 'IncomeConcept'),
            ('Revenue', 'RevenueConcept'),
            ('Cash', 'CashConcept'),
            ('Debt', 'DebtConcept'),
            ('Earnings', 'EarningsConcept'),
            ('Dividend', 'DividendConcept'),
        ]
        
        for keyword, label in categories:
            count = self.execute_cypher(f"""
                MATCH (g:GAAPConcept)
                WHERE g.name CONTAINS '{keyword}'
                SET g:{label}
                RETURN count(g) as count
            """)[0]['count']
            if count > 0:
                logger.info(f"为 {count} 个概念添加了 {label} 标签")
        
        return True
    
    def create_statistics(self):
        """创建统计信息"""
        logger.info("创建统计信息...")
        
        stats_queries = [
            ("总指标数", "MATCH (m:FinancialMetric) RETURN count(m) as count"),
            ("GAAP概念数", "MATCH (g:GAAPConcept) RETURN count(g) as count"),
            ("映射关系数", "MATCH ()-[r:MAPS_TO_GAAP]->() RETURN count(r) as count"),
            ("基础指标数", "MATCH (m:BasicMetric) RETURN count(m) as count"),
            ("计算指标数", "MATCH (m:CalculatedMetric) RETURN count(m) as count"),
        ]
        
        stats = {}
        for name, query in stats_queries:
            result = self.execute_cypher(query)
            count = result[0]['count'] if result else 0
            stats[name] = count
            logger.info(f"{name}: {count}")
        
        # 保存统计信息到图中
        self.execute_cypher("""
            CREATE (s:Statistics {
                type: 'knowledge_graph_stats',
                total_metrics: $total_metrics,
                gaap_concepts: $gaap_concepts,
                mapping_relationships: $mapping_relationships,
                basic_metrics: $basic_metrics,
                calculated_metrics: $calculated_metrics,
                created_at: datetime()
            })
        """, {
            'total_metrics': stats['总指标数'],
            'gaap_concepts': stats['GAAP概念数'],
            'mapping_relationships': stats['映射关系数'],
            'basic_metrics': stats['基础指标数'],
            'calculated_metrics': stats['计算指标数']
        })
        
        return True
    
    def setup_full_knowledge_graph(self, clear_existing=False):
        """完整设置知识图谱"""
        logger.info("开始设置财务指标知识图谱...")
        
        if not self.connect():
            return False
        
        try:
            if clear_existing:
                self.clear_database()
            
            # 按顺序执行设置步骤
            steps = [
                ("设置数据库模式", self.setup_schema),
                ("加载GAAP概念", self.load_gaap_concepts),
                ("加载财务指标", self.load_financial_metrics),
                ("加载视图和公式", self.load_views_and_formulas),
                ("创建关系", self.create_relationships),
                ("创建标签和分类", self.create_labels_and_categories),
                ("创建统计信息", self.create_statistics),
            ]
            
            for step_name, step_func in steps:
                logger.info(f"执行步骤: {step_name}")
                if not step_func():
                    logger.error(f"步骤失败: {step_name}")
                    return False
            
            logger.info("知识图谱设置完成！")
            return True
            
        except Exception as e:
            logger.error(f"设置过程中出现错误: {e}")
            return False
        finally:
            self.close()
    
    def query_examples(self):
        """示例查询"""
        if not self.connect():
            return
        
        try:
            logger.info("执行示例查询...")
            
            # 1. 查询映射统计
            print("\n=== 映射统计 ===")
            result = self.execute_cypher("""
                MATCH (m:FinancialMetric)
                OPTIONAL MATCH (m)-[:MAPS_TO_GAAP]->(g:GAAPConcept)
                RETURN 
                    CASE WHEN g IS NULL THEN 'Unmapped' ELSE 'Mapped' END as status,
                    count(m) as count
                ORDER BY status
            """)
            for record in result:
                print(f"{record['status']}: {record['count']} 个指标")
            
            # 2. 查询资产相关的GAAP概念
            print("\n=== 资产相关的GAAP概念 ===")
            result = self.execute_cypher("""
                MATCH (g:GAAPConcept)
                WHERE g.name CONTAINS 'Asset'
                RETURN g.name, g.id
                LIMIT 10
            """)
            for record in result:
                print(f"• {record['g.name']} ({record['g.id']})")
            
            # 3. 查询映射到特定GAAP概念的指标
            print("\n=== 映射到现金相关GAAP概念的指标 ===")
            result = self.execute_cypher("""
                MATCH (m:FinancialMetric)-[:MAPS_TO_GAAP]->(g:GAAPConcept)
                WHERE g.name CONTAINS 'Cash'
                RETURN m.chinese_name, m.name, g.name
            """)
            for record in result:
                print(f"• {record['m.chinese_name']} ({record['m.name']}) -> {record['g.name']}")
            
        finally:
            self.close()

def main():
    """主函数"""
    if not NEO4J_AVAILABLE:
        print("错误: Neo4j驱动未安装")
        print("请运行: pip install neo4j")
        return
    
    # 配置参数 - 请根据您的Neo4j配置修改
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password"  # 请修改为您的密码
    
    print("财务指标知识图谱设置工具")
    print("=" * 50)
    
    # 创建知识图谱管理器
    kg = FinancialKnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    # 设置知识图谱
    success = kg.setup_full_knowledge_graph(clear_existing=True)
    
    if success:
        print("\n知识图谱设置成功！")
        print("执行示例查询...")
        kg.query_examples()
        
        print("\n可以使用以下Cypher查询来探索知识图谱:")
        print("1. 查看所有节点类型:")
        print("   MATCH (n) RETURN DISTINCT labels(n), count(n)")
        print("\n2. 查看映射关系:")
        print("   MATCH (m:FinancialMetric)-[r:MAPS_TO_GAAP]->(g:GAAPConcept) RETURN m.chinese_name, g.name LIMIT 10")
        print("\n3. 查看未映射的指标:")
        print("   MATCH (m:FinancialMetric) WHERE NOT (m)-[:MAPS_TO_GAAP]->() RETURN m.chinese_name")
    else:
        print("知识图谱设置失败，请检查日志信息")

if __name__ == "__main__":
    main()