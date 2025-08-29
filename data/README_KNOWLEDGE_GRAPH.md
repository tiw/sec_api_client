
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
