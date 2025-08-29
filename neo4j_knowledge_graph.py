#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j财务指标知识图谱管理系统
用于导入和管理财务指标与US-GAAP概念的映射关系
"""

from neo4j import GraphDatabase
import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict, Any
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialMetricsKnowledgeGraph:
    """财务指标知识图谱管理类"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """
        初始化Neo4j连接
        
        Args:
            uri: Neo4j数据库URI
            user: 用户名
            password: 密码
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.data_dir = Path("/Users/tingwang/work/sec_api_client/data")
        
    def close(self):
        """关闭数据库连接"""
        self.driver.close()
        
    def execute_cypher(self, query: str, parameters: dict = None) -> List[Dict[str, Any]]:
        """
        执行Cypher查询
        
        Args:
            query: Cypher查询语句
            parameters: 查询参数
            
        Returns:
            查询结果列表
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def clear_database(self):
        """清空数据库"""
        logger.info("清空数据库...")
        self.execute_cypher("MATCH (n) DETACH DELETE n")
        
    def create_constraints_and_indexes(self):
        """创建约束和索引"""
        logger.info("创建约束和索引...")
        
        constraints_and_indexes = [
            "CREATE CONSTRAINT gaap_concept_id IF NOT EXISTS FOR (g:GAAPConcept) REQUIRE g.id IS UNIQUE",
            "CREATE CONSTRAINT metric_id IF NOT EXISTS FOR (m:FinancialMetric) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT formula_id IF NOT EXISTS FOR (f:Formula) REQUIRE f.id IS UNIQUE",
            "CREATE CONSTRAINT view_id IF NOT EXISTS FOR (v:View) REQUIRE v.id IS UNIQUE",
            "CREATE INDEX gaap_concept_name IF NOT EXISTS FOR (g:GAAPConcept) ON (g.name)",
            "CREATE INDEX metric_name IF NOT EXISTS FOR (m:FinancialMetric) ON (m.name)",
            "CREATE INDEX metric_chinese_name IF NOT EXISTS FOR (m:FinancialMetric) ON (m.chinese_name)"
        ]
        
        for query in constraints_and_indexes:
            try:
                self.execute_cypher(query)
                logger.info(f"执行成功: {query[:50]}...")
            except Exception as e:
                logger.warning(f"执行失败: {query[:50]}... - {e}")
    
    def import_gaap_concepts(self):
        """导入US-GAAP概念"""
        logger.info("导入US-GAAP概念...")
        
        # 读取映射文件中的GAAP概念
        mapping_df = pd.read_csv(self.data_dir / "gaap_metric_mapping.csv")
        gaap_concepts = mapping_df['us_gaap_concept'].unique()
        
        for concept in gaap_concepts:
            if pd.notna(concept):
                name = concept.replace('us-gaap:', '')
                self.execute_cypher("""
                    MERGE (g:GAAPConcept {id: $id})
                    SET g.name = $name,
                        g.namespace = 'us-gaap',
                        g.full_name = $id,
                        g.created_at = datetime()
                """, {'id': concept, 'name': name})
        
        logger.info(f"导入了 {len(gaap_concepts)} 个GAAP概念")
    
    def import_financial_metrics(self):
        """导入财务指标"""
        logger.info("导入财务指标...")
        
        # 导入主要指标 - 使用不带中文的文件名
        main_file = self.data_dir / "1.metrics_nodes.csv"
        process_file = self.data_dir / "5.process_metrics_nodes.csv"  # 假设重命名后的文件名
        
        # 如果新文件不存在，尝试使用原文件名
        if not main_file.exists():
            main_file = self.data_dir / "1.metrics_nodes - 工作表1.csv"
        if not process_file.exists():
            process_file = self.data_dir / "5.过程指标_nodes - 工作表1.csv"
        
        if not main_file.exists():
            logger.error(f"主要指标文件不存在: {main_file}")
            return False
        
        all_metrics = []
        
        # 处理主要指标
        try:
            metrics_df = pd.read_csv(main_file)
            for _, row in metrics_df.iterrows():
                all_metrics.append({
                    'id': f"metric_{row[':ID']}",
                    'metric_id': row[':ID'],
                    'name': row['name'],
                    'chinese_name': row['name_chinese'],
                    'metric_type': row['metrics_type'],
                    'source': 'main_metrics',
                    'formula_id': row.get('formula_id', ''),
                    'view_id': row.get('view_id', '')
                })
            logger.info(f"加载了 {len(metrics_df)} 个主要指标")
        except Exception as e:
            logger.error(f"加载主要指标失败: {e}")
        
        # 处理过程指标（如果文件存在且不为空）
        if process_file.exists():
            try:
                process_df = pd.read_csv(process_file)
                if not process_df.empty:
                    for _, row in process_df.iterrows():
                        all_metrics.append({
                            'id': f"metric_{row[':ID']}",
                            'metric_id': row[':ID'],
                            'name': row['name'],
                            'chinese_name': row['name_chinese'],
                            'metric_type': row['metrics_type'],
                            'source': 'process_metrics',
                            'formula_id': '',
                            'view_id': row.get('view_id', '')
                        })
                    logger.info(f"加载了 {len(process_df)} 个过程指标")
                else:
                    logger.info("过程指标文件为空，跳过")
            except Exception as e:
                logger.warning(f"加载过程指标失败: {e}")
        else:
            logger.info("过程指标文件不存在，跳过")
        
        # 批量导入指标
        for metric in all_metrics:
            self.execute_cypher("""
                MERGE (m:FinancialMetric {id: $id})
                SET m.metric_id = $metric_id,
                    m.name = $name,
                    m.chinese_name = $chinese_name,
                    m.metric_type = $metric_type,
                    m.source = $source,
                    m.created_at = datetime()
            """, metric)
        
        logger.info(f"导入了 {len(all_metrics)} 个财务指标")
    
    def import_views(self):
        """导入视图结构"""
        logger.info("导入视图结构...")
        
        # 使用不带中文的文件名
        views_file = self.data_dir / "4.view_nodes.csv"
        
        # 如果新文件不存在，尝试使用原文件名
        if not views_file.exists():
            views_file = self.data_dir / "4.view_nodes - 工作表1.csv"
        
        if not views_file.exists():
            logger.warning("视图文件不存在，跳过视图导入")
            return
        
        try:
            views_df = pd.read_csv(views_file)
            
            if views_df.empty:
                logger.info("视图数据为空，跳过视图导入")
                return
            
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
            
            logger.info(f"导入了 {len(views_df)} 个视图")
            
        except Exception as e:
            logger.error(f"导入视图失败: {e}")
    
    def import_formulas(self):
        """导入公式"""
        logger.info("导入公式...")
        
        formulas_df = pd.read_csv(self.data_dir / "2.formula_nodes. - 工作表1.csv")
        
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
    def import_formulas(self):
        """导入公式"""
        logger.info("导入公式...")
        
        # 使用不带中文的文件名
        formulas_file = self.data_dir / "2.formula_nodes.csv"
        
        # 如果新文件不存在，尝试使用原文件名
        if not formulas_file.exists():
            formulas_file = self.data_dir / "2.formula_nodes. - 工作表1.csv"
        
        if not formulas_file.exists():
            logger.info("公式文件不存在，跳过公式导入")
            return
        
        try:
            # 检查文件是否为空
            if formulas_file.stat().st_size <= 1:  # 空文件或只有换行符
                logger.info("公式文件为空，跳过公式导入")
                return
            
            formulas_df = pd.read_csv(formulas_file)
            
            # 检查DataFrame是否为空
            if formulas_df.empty:
                logger.info("公式数据为空，跳过公式导入")
                return
            
            # 检查必要的列是否存在
            required_columns = [':ID', 'formula_expression', 'formula_chinese']
            missing_columns = [col for col in required_columns if col not in formulas_df.columns]
            
            if missing_columns:
                logger.warning(f"公式文件缺少必要的列: {missing_columns}，跳过公式导入")
                return
            
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
            
            logger.info(f"导入了 {len(formulas_df)} 个公式")
            
        except pd.errors.EmptyDataError:
            logger.info("公式文件为空，跳过公式导入")
        except Exception as e:
            logger.error(f"导入公式失败: {e}")
    
    def create_relationships(self):
        """创建关系"""
        logger.info("创建关系...")
        
        # 1. 创建指标到GAAP概念的映射关系
        mapping_df = pd.read_csv(self.data_dir / "gaap_metric_mapping.csv")
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
        
        # 2. 创建指标到视图的关系
        main_file = self.data_dir / "1.metrics_nodes.csv"
        if not main_file.exists():
            main_file = self.data_dir / "1.metrics_nodes - 工作表1.csv"
        
        if main_file.exists():
            try:
                metrics_df = pd.read_csv(main_file)
                for _, row in metrics_df.iterrows():
                    if pd.notna(row.get('view_id', '')):
                        self.execute_cypher("""
                            MATCH (m:FinancialMetric {metric_id: $metric_id})
                            MATCH (v:View {id: $view_id})
                            MERGE (m)-[:BELONGS_TO_VIEW]->(v)
                        """, {
                            'metric_id': row[':ID'],
                            'view_id': row['view_id']
                        })
            except Exception as e:
                logger.warning(f"创建指标到视图关系失败: {e}")
        
        # 3. 创建指标到公式的关系
        if main_file.exists():
            try:
                metrics_df = pd.read_csv(main_file)
                for _, row in metrics_df.iterrows():
                    if pd.notna(row.get('formula_id', '')):
                        self.execute_cypher("""
                            MATCH (m:FinancialMetric {metric_id: $metric_id})
                            MATCH (f:Formula {id: $formula_id})
                            MERGE (m)-[:CALCULATED_BY]->(f)
                        """, {
                            'metric_id': row[':ID'],
                            'formula_id': row['formula_id']
                        })
            except Exception as e:
                logger.warning(f"创建指标到公式关系失败: {e}")
        
        # 4. 创建公式使用的基础指标关系
        formula_rel_file = self.data_dir / "3.formula_relationships.csv"
        if not formula_rel_file.exists():
            formula_rel_file = self.data_dir / "3.formula_relationships - 工作表1.csv"
        
        if formula_rel_file.exists():
            try:
                # 检查文件是否为空
                if formula_rel_file.stat().st_size > 1:
                    formula_rel_df = pd.read_csv(formula_rel_file)
                    if not formula_rel_df.empty and ':START_ID' in formula_rel_df.columns and ':END_ID' in formula_rel_df.columns:
                        for _, row in formula_rel_df.iterrows():
                            self.execute_cypher("""
                                MATCH (f:Formula {id: $formula_id})
                                MATCH (m:FinancialMetric {metric_id: $metric_id})
                                MERGE (f)-[:USES_METRIC]->(m)
                            """, {
                                'formula_id': row[':START_ID'],
                                'metric_id': row[':END_ID']
                            })
                    else:
                        logger.info("公式关系文件为空或缺少必要列，跳过")
                else:
                    logger.info("公式关系文件为空，跳过")
            except Exception as e:
                logger.warning(f"创建公式关系失败: {e}")
        
        # 5. 创建视图层级关系
        views_file = self.data_dir / "4.view_nodes.csv"
        if not views_file.exists():
            views_file = self.data_dir / "4.view_nodes - 工作表1.csv"
        
        if views_file.exists():
            try:
                views_df = pd.read_csv(views_file)
                for _, row in views_df.iterrows():
                    if pd.notna(row.get('parent_id')):
                        self.execute_cypher("""
                            MATCH (child:View {id: $child_id})
                            MATCH (parent:View {id: $parent_id})
                            MERGE (child)-[:CHILD_OF]->(parent)
                        """, {
                            'child_id': row[':ID'],
                            'parent_id': row['parent_id']
                        })
            except Exception as e:
                logger.warning(f"创建视图层级关系失败: {e}")
        
        logger.info("关系创建完成")
    
    def mark_unmapped_metrics(self):
        """标记未映射的指标"""
        logger.info("标记未映射的指标...")
        
        unmapped_df = pd.read_csv(self.data_dir / "unmapped_metrics.csv")
        for _, row in unmapped_df.iterrows():
            self.execute_cypher("""
                MATCH (m:FinancialMetric {metric_id: $metric_id})
                SET m:UnmappedMetric, m.unmapped_reason = $reason
            """, {
                'metric_id': row['metric_id'],
                'reason': row['reason']
            })
        
        logger.info(f"标记了 {len(unmapped_df)} 个未映射指标")
    
    def create_semantic_labels(self):
        """创建语义标签"""
        logger.info("创建语义标签...")
        
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
        
        # GAAP概念分类标签
        concept_categories = [
            ('Assets', 'AssetConcept'),
            ('Liabilit', 'LiabilityConcept'),
            ('Equity', 'EquityConcept'),
            ('Stockholders', 'EquityConcept'),
            ('Revenue', 'IncomeConcept'),
            ('Income', 'IncomeConcept'),
            ('Cash', 'CashConcept'),
            ('Debt', 'DebtConcept'),
            ('Earnings', 'EarningsConcept'),
            ('Dividend', 'DividendConcept')
        ]
        
        for keyword, label in concept_categories:
            self.execute_cypher(f"""
                MATCH (g:GAAPConcept)
                WHERE g.name CONTAINS '{keyword}'
                SET g:{label}
            """)
        
        logger.info("语义标签创建完成")
    
    def create_statistics(self):
        """创建统计信息"""
        logger.info("创建统计信息...")
        
        # 获取统计数据
        stats = {}
        
        # 总指标数
        result = self.execute_cypher("MATCH (m:FinancialMetric) RETURN count(m) as count")
        stats['total_metrics'] = result[0]['count']
        
        # 映射指标数
        result = self.execute_cypher("""
            MATCH (m:FinancialMetric)-[:MAPS_TO_GAAP]->(g:GAAPConcept) 
            RETURN count(DISTINCT m) as count
        """)
        stats['mapped_metrics'] = result[0]['count']
        
        # 未映射指标数
        result = self.execute_cypher("MATCH (m:UnmappedMetric) RETURN count(m) as count")
        stats['unmapped_metrics'] = result[0]['count']
        
        # GAAP概念数
        result = self.execute_cypher("MATCH (g:GAAPConcept) RETURN count(g) as count")
        stats['gaap_concepts'] = result[0]['count']
        
        # 计算映射率
        stats['mapping_rate'] = stats['mapped_metrics'] / stats['total_metrics'] if stats['total_metrics'] > 0 else 0
        
        # 创建统计节点
        self.execute_cypher("""
            CREATE (:Statistics {
                type: 'mapping_stats',
                total_metrics: $total_metrics,
                mapped_metrics: $mapped_metrics,
                unmapped_metrics: $unmapped_metrics,
                gaap_concepts: $gaap_concepts,
                mapping_rate: $mapping_rate,
                created_at: datetime()
            })
        """, stats)
        
        logger.info(f"统计信息: 总指标 {stats['total_metrics']}, "
                   f"已映射 {stats['mapped_metrics']}, "
                   f"未映射 {stats['unmapped_metrics']}, "
                   f"映射率 {stats['mapping_rate']:.1%}")
    
    def full_import(self):
        """完整导入流程"""
        logger.info("开始完整导入流程...")
        
        try:
            # 清空数据库（可选）
            # self.clear_database()
            
            # 创建约束和索引
            self.create_constraints_and_indexes()
            
            # 导入节点
            self.import_gaap_concepts()
            self.import_financial_metrics()
            self.import_views()
            self.import_formulas()
            
            # 创建关系
            self.create_relationships()
            
            # 标记未映射指标
            self.mark_unmapped_metrics()
            
            # 创建语义标签
            self.create_semantic_labels()
            
            # 创建统计信息
            self.create_statistics()
            
            logger.info("导入完成！")
            
        except Exception as e:
            logger.error(f"导入过程中出现错误: {e}")
            raise
    
    def query_mapping_status(self):
        """查询映射状态"""
        logger.info("查询映射状态...")
        
        result = self.execute_cypher("""
            MATCH (m:FinancialMetric) 
            OPTIONAL MATCH (m)-[r:MAPS_TO_GAAP]->(g:GAAPConcept)
            RETURN 
                CASE WHEN g IS NULL THEN 'Unmapped' ELSE 'Mapped' END as Status,
                count(m) as Count
            ORDER BY Status
        """)
        
        for record in result:
            logger.info(f"{record['Status']}: {record['Count']} 个指标")
        
        return result
    
    def query_unmapped_metrics(self):
        """查询未映射指标"""
        result = self.execute_cypher("""
            MATCH (m:UnmappedMetric)
            RETURN m.metric_id as metric_id, 
                   m.name as name, 
                   m.chinese_name as chinese_name,
                   m.metric_type as metric_type,
                   m.unmapped_reason as reason
            ORDER BY m.metric_type, m.name
        """)
        
        return result

def main():
    """主函数"""
    # 从环境变量获取Neo4j连接参数
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASS")
    
    if not NEO4J_PASSWORD:
        logger.error("未找到NEO4J_PASS环境变量，请检查.env文件")
        print("\n⚠️  请创建.env文件并设置NEO4J_PASS变量")
        print("示例:")
        print("NEO4J_URI=bolt://localhost:7687")
        print("NEO4J_USER=neo4j")
        print("NEO4J_PASS=your_password")
        return
    
    # 创建知识图谱管理器
    kg = FinancialMetricsKnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # 执行完整导入
        kg.full_import()
        
        # 查询映射状态
        kg.query_mapping_status()
        
        # 查询未映射指标
        unmapped = kg.query_unmapped_metrics()
        print(f"\n未映射的指标 ({len(unmapped)} 个):")
        for metric in unmapped:
            print(f"• {metric['metric_id']} ({metric['chinese_name']}) - {metric['metric_type']}")
            
    finally:
        kg.close()

if __name__ == "__main__":
    main()