// Neo4j财务指标知识图谱导入脚本
// 用于管理财务指标与US-GAAP概念的映射关系

// 1. 创建约束和索引
CREATE CONSTRAINT gaap_concept_id IF NOT EXISTS FOR (g:GAAPConcept) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT metric_id IF NOT EXISTS FOR (m:FinancialMetric) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT formula_id IF NOT EXISTS FOR (f:Formula) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT view_id IF NOT EXISTS FOR (v:View) REQUIRE v.id IS UNIQUE;

CREATE INDEX gaap_concept_name IF NOT EXISTS FOR (g:GAAPConcept) ON (g.name);
CREATE INDEX metric_name IF NOT EXISTS FOR (m:FinancialMetric) ON (m.name);
CREATE INDEX metric_chinese_name IF NOT EXISTS FOR (m:FinancialMetric) ON (m.chinese_name);

// 2. 导入US-GAAP概念节点
LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes.csv' AS row
WHERE row.type = 'GAAP_CONCEPT'
CREATE (g:GAAPConcept {
    id: row.id,
    name: row.name,
    namespace: row.namespace,
    full_name: row.id,
    created_at: datetime()
});

// 3. 导入财务指标节点
LOAD CSV WITH HEADERS FROM 'file:///neo4j_nodes.csv' AS row
WHERE row.type = 'FINANCIAL_METRIC'
CREATE (m:FinancialMetric {
    id: row.id,
    metric_id: replace(row.id, 'metric_', ''),
    name: row.name,
    chinese_name: row.chinese_name,
    metric_type: row.metric_type,
    source: row.source,
    created_at: datetime()
});

// 4. 导入视图节点
LOAD CSV WITH HEADERS FROM 'file:///4.view_nodes - 工作表1.csv' AS row
CREATE (v:View {
    id: row.`:ID`,
    name: row.view_name,
    level: toInteger(row.level),
    parent_id: row.parent_id,
    created_at: datetime()
});

// 5. 导入公式节点
LOAD CSV WITH HEADERS FROM 'file:///2.formula_nodes. - 工作表1.csv' AS row
CREATE (f:Formula {
    id: row.`:ID`,
    expression: row.formula_expression,
    chinese_description: row.formula_chinese,
    created_at: datetime()
});

// 6. 创建指标到GAAP概念的映射关系
LOAD CSV WITH HEADERS FROM 'file:///gaap_metric_mapping.csv' AS row
MATCH (m:FinancialMetric {metric_id: row.metric_id})
MATCH (g:GAAPConcept {id: row.us_gaap_concept})
CREATE (m)-[:MAPS_TO_GAAP {
    mapping_status: row.mapping_status,
    confidence: CASE row.mapping_status 
        WHEN 'mapped' THEN 1.0 
        WHEN 'fuzzy_mapped' THEN 0.7 
        ELSE 0.5 
    END,
    created_at: datetime()
}]->(g);

// 7. 创建指标到视图的关系
LOAD CSV WITH HEADERS FROM 'file:///1.metrics_nodes - 工作表1.csv' AS row
WHERE row.view_id IS NOT NULL AND row.view_id <> ''
MATCH (m:FinancialMetric {metric_id: row.`:ID`})
MATCH (v:View {id: row.view_id})
CREATE (m)-[:BELONGS_TO_VIEW]->(v);

// 8. 创建指标到公式的关系
LOAD CSV WITH HEADERS FROM 'file:///1.metrics_nodes - 工作表1.csv' AS row
WHERE row.formula_id IS NOT NULL AND row.formula_id <> ''
MATCH (m:FinancialMetric {metric_id: row.`:ID`})
MATCH (f:Formula {id: row.formula_id})
CREATE (m)-[:CALCULATED_BY]->(f);

// 9. 创建公式使用的基础指标关系
LOAD CSV WITH HEADERS FROM 'file:///3.formula_relationships - 工作表1.csv' AS row
MATCH (f:Formula {id: row.`:START_ID`})
MATCH (m:FinancialMetric {metric_id: row.`:END_ID`})
CREATE (f)-[:USES_METRIC]->(m);

// 10. 创建视图层级关系
LOAD CSV WITH HEADERS FROM 'file:///4.view_nodes - 工作表1.csv' AS row
WHERE row.parent_id IS NOT NULL AND row.parent_id <> ''
MATCH (child:View {id: row.`:ID`})
MATCH (parent:View {id: row.parent_id})
CREATE (child)-[:CHILD_OF]->(parent);

// 11. 为未映射的指标创建特殊标记
LOAD CSV WITH HEADERS FROM 'file:///unmapped_metrics.csv' AS row
MATCH (m:FinancialMetric {metric_id: row.metric_id})
SET m:UnmappedMetric, m.unmapped_reason = row.reason;

// 12. 创建指标分类标签
MATCH (m:FinancialMetric)
WHERE m.metric_type = '基础指标'
SET m:BasicMetric;

MATCH (m:FinancialMetric)
WHERE m.metric_type = '计算指标'
SET m:CalculatedMetric;

// 13. 创建GAAP概念分类
MATCH (g:GAAPConcept)
WHERE g.name CONTAINS 'Assets'
SET g:AssetConcept;

MATCH (g:GAAPConcept)
WHERE g.name CONTAINS 'Liabilit'
SET g:LiabilityConcept;

MATCH (g:GAAPConcept)
WHERE g.name CONTAINS 'Equity' OR g.name CONTAINS 'Stockholders'
SET g:EquityConcept;

MATCH (g:GAAPConcept)
WHERE g.name CONTAINS 'Revenue' OR g.name CONTAINS 'Income'
SET g:IncomeConcept;

MATCH (g:GAAPConcept)
WHERE g.name CONTAINS 'Cash'
SET g:CashConcept;

MATCH (g:GAAPConcept)
WHERE g.name CONTAINS 'Debt'
SET g:DebtConcept;

MATCH (g:GAAPConcept)
WHERE g.name CONTAINS 'Earnings' OR g.name CONTAINS 'EarningsPerShare'
SET g:EarningsConcept;

MATCH (g:GAAPConcept)
WHERE g.name CONTAINS 'Dividend'
SET g:DividendConcept;

// 14. 创建一些有用的查询视图统计
MATCH (m:FinancialMetric)-[:MAPS_TO_GAAP]->(g:GAAPConcept)
WITH count(m) as mapped_count
MATCH (m2:FinancialMetric)
WITH mapped_count, count(m2) as total_count
CREATE (:Statistics {
    type: 'mapping_stats',
    mapped_metrics: mapped_count,
    total_metrics: total_count,
    mapping_rate: toFloat(mapped_count) / toFloat(total_count),
    created_at: datetime()
});

// 显示导入结果统计
MATCH (m:FinancialMetric) RETURN 'FinancialMetric' as NodeType, count(m) as Count
UNION
MATCH (g:GAAPConcept) RETURN 'GAAPConcept' as NodeType, count(g) as Count
UNION
MATCH (f:Formula) RETURN 'Formula' as NodeType, count(f) as Count
UNION
MATCH (v:View) RETURN 'View' as NodeType, count(v) as Count
UNION
MATCH (m:FinancialMetric)-[:MAPS_TO_GAAP]->(g:GAAPConcept) 
RETURN 'MappedMetrics' as NodeType, count(DISTINCT m) as Count
UNION
MATCH (m:UnmappedMetric) 
RETURN 'UnmappedMetrics' as NodeType, count(m) as Count;