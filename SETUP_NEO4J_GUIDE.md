# Neo4j知识图谱设置指南

## 快速开始

### 1. 设置环境变量

复制`.env.example`为`.env`文件：
```bash
cp .env.example .env
```

编辑`.env`文件，补充缺少的变量：
```bash
# 您现有的.env文件已有NEO4J_PASS，请添加：
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
# NEO4J_PASS=（您已有）
```

### 2. 启动Neo4j数据库

#### 方案A: 使用Docker (推荐)

如果您有Docker：
```bash
# 使用您.env文件中的密码启动Neo4j
docker run -d --name neo4j-gaap \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/您的密码 \
  -v neo4j_gaap_data:/data \
  neo4j:latest
```

#### 方案B: Neo4j Desktop

1. 下载并安装Neo4j Desktop: https://neo4j.com/download/
2. 创建新数据库，设置密码与`.env`文件中的`NEO4J_PASS`一致
3. 启动数据库

### 3. 测试连接

```bash
python test_neo4j_connection.py
```

如果看到"✅ Neo4j连接成功!"则说明配置正确。

### 4. 导入GAAP概念到知识图谱

```bash
# 生成数据文件（如果还没有）
python gaap_to_knowledge_graph.py

# 导入到Neo4j
python neo4j_knowledge_graph.py
```

### 5. 访问Neo4j浏览器

打开浏览器访问: http://localhost:7474
- 用户名: neo4j
- 密码: 您的密码

## 故障排除

### 常见错误及解决方案

1. **Authentication failure**
   - 检查密码是否正确
   - 确保Neo4j已启动

2. **Connection refused**
   - 确保Neo4j服务已启动
   - 检查端口7687是否被占用

3. **环境变量未找到**
   - 确保`.env`文件存在且格式正确
   - 重新运行测试脚本

## 查询示例

连接成功后，可以在Neo4j浏览器中运行这些查询：

```cypher
// 查看所有GAAP概念
MATCH (g:GAAPConcept) RETURN g LIMIT 10

// 查看有中文翻译的概念
MATCH (g:GAAPConcept) 
WHERE g.chinese_name <> '' 
RETURN g.name, g.chinese_name LIMIT 10

// 按类别统计概念
MATCH (g:GAAPConcept) 
RETURN g.category, count(*) as count 
ORDER BY count DESC
```