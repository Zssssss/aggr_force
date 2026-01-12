# Get Skills MCP - 快速入门

## 快速开始

### 1. 安装依赖

```bash
cd get_skills_mcp
pip install -r requirements.txt
```

### 2. 测试服务器

```bash
# 直接运行服务器（用于测试）
python3 get_skills_mcp_server.py
```

### 3. 配置到 MCP 客户端

在你的 MCP 客户端配置文件中添加（例如 Claude Desktop 的配置）：

**Linux/Mac**: `~/.config/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "get-skills": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/get_skills_mcp/get_skills_mcp_server.py"
      ]
    }
  }
}
```

### 4. 添加自定义技能

在 `skills/custom/` 目录下创建技能文件：

**示例 1: Markdown 格式**

创建 `skills/custom/code_review.md`:

```markdown
# 代码审查

这是一个代码审查技能，帮助审查代码质量

## 指令

请按照以下步骤进行代码审查：

1. 检查代码风格和格式
2. 查找潜在的 bug 和安全问题
3. 评估代码可读性和可维护性
4. 提供改进建议
5. 给出总体评分
```

**示例 2: JSON 格式**

创建 `skills/custom/api_design.json`:

```json
{
  "name": "api_design",
  "description": "RESTful API 设计技能",
  "instructions": "设计 RESTful API 时请遵循以下原则：\n1. 使用名词表示资源\n2. 使用 HTTP 方法表示操作\n3. 使用合适的状态码\n4. 提供清晰的错误信息\n5. 支持版本控制",
  "metadata": {
    "author": "Your Name",
    "version": "1.0.0",
    "tags": ["api", "design", "rest"]
  }
}
```

### 5. 使用技能

在 MCP 客户端中使用工具：

```
# 列出所有技能
使用 mcp-get-skills.list_skills 工具

# 获取特定技能
使用 mcp-get-skills.get_skill 工具，参数 name="code_review"

# 搜索技能
使用 mcp-get-skills.search_skills 工具，参数 keyword="api"

# 重新加载技能
使用 mcp-get-skills.reload_skills 工具
```

## 技能文件格式说明

### Markdown (.md)

- 第一个 `#` 标题会被用作描述
- 其余内容作为指令
- 文件名作为技能名称

### JSON (.json)

必需字段：
- `name`: 技能名称
- `description`: 技能描述
- `instructions`: 执行指令

可选字段：
- `metadata`: 元数据对象

### 纯文本 (.txt)

- 整个文件内容作为指令
- 文件名作为技能名称
- 自动生成描述

## 使用 Anthropic Skills

Anthropic 的开源技能已经在 `vendor/anthropics-skills` 目录中。

查看可用的技能：

```bash
ls -la vendor/anthropics-skills/
```

这些技能会自动加载，并标记为 `vendor` 来源。

## 故障排除

### 问题：技能未加载

**解决方案**：
1. 检查文件格式是否正确
2. 查看服务器日志（stderr）
3. 使用 `reload_skills` 工具重新加载

### 问题：找不到 vendor 技能

**解决方案**：
```bash
cd /home/zsss/zsss_useful_tools/aggr_force
git submodule update --init --recursive
```

### 问题：MCP 客户端连接失败

**解决方案**：
1. 确认 Python 路径正确
2. 确认服务器文件路径正确
3. 检查是否安装了 mcp 依赖
4. 重启 MCP 客户端

## 高级用法

### 按来源筛选技能

```python
# 只列出自定义技能
mcp_get_skills_list_skills(source="custom")

# 只列出 vendor 技能
mcp_get_skills_list_skills(source="vendor")
```

### 获取纯指令内容

```python
# 获取技能的执行指令（不含元数据）
mcp_get_skills_get_skill_instructions(name="code_review")
```

### 通过资源协议访问

技能也可以作为 MCP 资源访问：

```
skill://code_review
skill://api_design
```

## 下一步

- 创建更多自定义技能
- 探索 Anthropic 的开源技能库
- 将技能集成到你的工作流中
- 与其他 MCP 服务器组合使用

## 相关文档

- [README.md](README.md) - 完整文档
- [Anthropic Skills](https://github.com/anthropics/skills) - 开源技能库
