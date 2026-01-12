# Get Skills MCP - 使用示例

## 示例 1: 列出所有技能

```python
# 列出所有技能
mcp_get_skills_list_skills(source="all")
```

**输出**:
```
📋 技能列表（共 66 个）

## 🎨 自定义技能 (3)
- **code_review**: 代码审查技能
- **api_design**: RESTful API 设计技能 - 帮助设计符合最佳实践的 REST API
- **skill**: Skill from skill.md

## 📦 Vendor技能 (63)
- **README**: Skill from README.md
- **agent-skills-spec**: Agent Skills Spec
- **html2pptx**: HTML to PowerPoint Guide
...
```

## 示例 2: 获取特定技能

```python
# 获取代码审查技能
mcp_get_skills_get_skill(name="code_review")
```

**输出**:
```
📖 技能详情

**名称**: code_review

**描述**: 代码审查技能

**指令**:
这是一个帮助进行代码审查的技能，提供系统化的代码质量评估方法。

## 指令

作为代码审查专家，请按照以下步骤对代码进行全面审查：

### 1. 代码风格和格式
- 检查代码是否遵循项目的编码规范
...

**元数据**:
- 来源: custom
- 格式: markdown
- 文件路径: /home/zsss/zsss_useful_tools/aggr_force/skills/custom/code_review.md
```

## 示例 3: 搜索技能

```python
# 搜索包含 "api" 的技能
mcp_get_skills_search_skills(keyword="api")
```

**输出**:
```
🔍 搜索结果（关键词: 'api'，共 1 个）

- **api_design** [custom]
  RESTful API 设计技能 - 帮助设计符合最佳实践的 REST API
```

## 示例 4: 获取技能指令

```python
# 只获取指令内容，不含元数据
mcp_get_skills_get_skill_instructions(name="api_design")
```

**输出**:
```
📝 技能指令: api_design

作为 API 设计专家，请按照以下原则设计 RESTful API：

## 1. 资源命名
- 使用名词而非动词表示资源
- 使用复数形式（如 /users 而非 /user）
...
```

## 示例 5: 按来源筛选

```python
# 只列出自定义技能
mcp_get_skills_list_skills(source="custom")
```

**输出**:
```
📋 技能列表（共 3 个）

## 🎨 自定义技能 (3)
- **code_review**: 代码审查技能
- **api_design**: RESTful API 设计技能 - 帮助设计符合最佳实践的 REST API
- **skill**: Skill from skill.md
```

```python
# 只列出 vendor 技能
mcp_get_skills_list_skills(source="vendor")
```

## 示例 6: 重新加载技能

```python
# 添加新技能后重新加载
mcp_get_skills_reload_skills()
```

**输出**:
```
🔄 技能重新加载完成

- 自定义技能: 3 个
- Vendor技能: 63 个
- 总计: 66 个

💡 使用 list_skills 工具查看所有技能
```

## 示例 7: 实际应用 - 代码审查

**步骤 1**: 获取代码审查技能指令
```python
mcp_get_skills_get_skill_instructions(name="code_review")
```

**步骤 2**: 应用技能审查代码
```
请使用上述代码审查技能，审查以下 Python 代码：

[粘贴你的代码]
```

**AI 将按照技能指令进行系统化的代码审查**

## 示例 8: 实际应用 - API 设计

**步骤 1**: 获取 API 设计技能
```python
mcp_get_skills_get_skill(name="api_design")
```

**步骤 2**: 应用技能设计 API
```
我需要为一个博客系统设计 RESTful API，包括文章、评论和用户管理。
请使用 api_design 技能帮我设计。
```

**AI 将按照技能指令提供专业的 API 设计方案**

## 示例 9: 通过资源协议访问

技能也可以作为 MCP 资源访问：

```
# 访问技能资源
skill://code_review
skill://api_design
```

这在某些 MCP 客户端中可以直接读取技能内容。

## 示例 10: 创建自定义技能

**创建 Markdown 技能**:

文件: `skills/custom/database_design.md`

```markdown
# 数据库设计

这是一个数据库设计技能，帮助设计高效的数据库架构

## 指令

作为数据库设计专家，请按照以下步骤设计数据库：

1. 需求分析
   - 理解业务需求
   - 识别实体和关系

2. 概念设计
   - 创建 ER 图
   - 定义实体属性

3. 逻辑设计
   - 规范化（1NF, 2NF, 3NF）
   - 定义主键和外键

4. 物理设计
   - 选择数据类型
   - 创建索引
   - 考虑性能优化

5. 安全性
   - 访问控制
   - 数据加密
   - 备份策略
```

**创建 JSON 技能**:

文件: `skills/custom/security_audit.json`

```json
{
  "name": "security_audit",
  "description": "安全审计技能 - 系统化的安全检查方法",
  "instructions": "作为安全专家，请进行以下安全审计：\n\n1. 认证和授权\n2. 输入验证\n3. 数据加密\n4. 日志和监控\n5. 依赖项安全\n6. 配置安全\n7. 网络安全",
  "metadata": {
    "author": "Security Team",
    "version": "1.0.0",
    "tags": ["security", "audit", "best-practices"]
  }
}
```

**重新加载技能**:
```python
mcp_get_skills_reload_skills()
```

现在新技能就可以使用了！

## 工作流示例

### 完整的代码开发工作流

1. **设计 API**
   ```python
   mcp_get_skills_get_skill_instructions(name="api_design")
   # 使用技能设计 API
   ```

2. **编写代码**
   ```
   # 根据 API 设计编写代码
   ```

3. **代码审查**
   ```python
   mcp_get_skills_get_skill_instructions(name="code_review")
   # 使用技能审查代码
   ```

4. **安全审计**
   ```python
   mcp_get_skills_get_skill_instructions(name="security_audit")
   # 使用技能进行安全检查
   ```

5. **数据库设计**
   ```python
   mcp_get_skills_get_skill_instructions(name="database_design")
   # 使用技能设计数据库
   ```

## 技巧和最佳实践

### 1. 技能组合使用

将多个技能组合使用可以获得更好的效果：

```
请使用 api_design 技能设计 API，
然后使用 code_review 技能审查生成的代码，
最后使用 security_audit 技能检查安全问题。
```

### 2. 技能定制

根据项目需求创建专门的技能：

- 项目特定的编码规范
- 团队的最佳实践
- 领域特定的知识

### 3. 技能版本管理

在 JSON 格式中使用版本号：

```json
{
  "metadata": {
    "version": "1.0.0"
  }
}
```

### 4. 技能文档化

在 Markdown 技能中提供详细的说明和示例。

### 5. 技能搜索

使用搜索功能快速找到需要的技能：

```python
mcp_get_skills_search_skills(keyword="design")
mcp_get_skills_search_skills(keyword="security")
mcp_get_skills_search_skills(keyword="review")
```

## 常见问题

**Q: 如何知道有哪些可用的技能？**

A: 使用 `list_skills` 工具列出所有技能。

**Q: 技能文件放在哪里？**

A: 自定义技能放在 `skills/custom/` 目录，vendor 技能在 `vendor/anthropics-skills/`。

**Q: 如何更新技能？**

A: 修改技能文件后，使用 `reload_skills` 工具重新加载。

**Q: 支持哪些文件格式？**

A: 支持 Markdown (.md)、JSON (.json) 和纯文本 (.txt)。

**Q: 如何处理技能名称冲突？**

A: 系统会自动添加来源前缀（如 `vendor_skill_name`）。

## 相关文档

- [README.md](README.md) - 完整文档
- [QUICKSTART.md](QUICKSTART.md) - 快速入门
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结
