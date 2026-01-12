# Get Skills MCP Server

基于 [Anthropic Skills](https://github.com/anthropics/skills) 概念的技能管理 MCP 服务器。

## 概述

Get Skills MCP 是一个用于加载、管理和查询技能的 MCP 服务器。它支持从多个来源加载技能：

- **skills/custom** - 用户自定义技能目录
- **vendor/anthropics-skills** - Anthropic 开源技能目录

## 功能特性

### 🔧 工具 (Tools)

1. **list_skills** - 列出所有已加载的技能
   - 支持按来源筛选（custom/vendor/all）
   - 显示技能名称和描述

2. **get_skill** - 获取指定技能的详细信息
   - 包含完整的指令内容
   - 显示元数据和来源信息

3. **search_skills** - 根据关键词搜索技能
   - 在技能名称、描述和指令中搜索
   - 返回匹配的技能列表

4. **reload_skills** - 重新加载所有技能
   - 用于添加新技能后刷新
   - 显示加载统计信息

5. **get_skill_instructions** - 获取技能执行指令
   - 返回纯指令内容
   - 可直接用于 AI 助手执行

### 📚 资源 (Resources)

- 每个技能都作为资源暴露
- URI 格式: `skill://skill_name`
- 支持通过 MCP 资源协议访问

## 安装

### 1. 安装依赖

```bash
cd get_skills_mcp
pip install -r requirements.txt
```

### 2. 配置技能目录

#### 自定义技能目录

在 `skills/custom/` 目录下添加你的技能文件：

```bash
skills/custom/
├── my_skill.md
├── another_skill.json
└── ...
```

#### Anthropic Skills（可选）

如果要使用 Anthropic 的开源技能，需要添加 git submodule：

```bash
# 在项目根目录执行
git submodule add https://github.com/anthropics/skills.git vendor/anthropics-skills
git submodule update --init --recursive
```

## 技能文件格式

### Markdown 格式 (.md)

```markdown
# 技能名称

这是技能的描述

## 指令

这里是具体的执行指令...
```

### JSON 格式 (.json)

```json
{
  "name": "skill_name",
  "description": "技能描述",
  "instructions": "执行指令...",
  "metadata": {
    "author": "作者",
    "version": "1.0.0"
  }
}
```

### 纯文本格式 (.txt)

纯文本内容将作为指令加载，文件名作为技能名称。

## 配置 MCP 客户端

在你的 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "get-skills": {
      "command": "python3",
      "args": [
        "/path/to/aggr_force/get_skills_mcp/get_skills_mcp_server.py"
      ]
    }
  }
}
```

## 使用示例

### 列出所有技能

```python
# 使用 MCP 工具
mcp_get_skills_list_skills(source="all")
```

### 获取特定技能

```python
# 获取技能详情
mcp_get_skills_get_skill(name="my_skill")

# 只获取指令
mcp_get_skills_get_skill_instructions(name="my_skill")
```

### 搜索技能

```python
# 搜索包含关键词的技能
mcp_get_skills_search_skills(keyword="python")
```

### 重新加载技能

```python
# 添加新技能后重新加载
mcp_get_skills_reload_skills()
```

## 目录结构

```
get_skills_mcp/
├── __init__.py              # 包初始化
├── skill_loader.py          # 技能加载器核心模块
├── get_skills_mcp_server.py # MCP 服务器主文件
├── requirements.txt         # Python 依赖
└── README.md               # 本文档

skills/
└── custom/                 # 自定义技能目录
    └── skill.md           # 示例技能文件

vendor/
└── anthropics-skills/     # Anthropic 开源技能（需要手动添加）
```

## 技能来源优先级

当技能名称冲突时，系统会自动添加来源前缀：
- 自定义技能优先使用原名称
- Vendor 技能如有冲突会添加 `vendor_` 前缀

## 开发

### 扩展技能加载器

可以通过继承 `SkillLoader` 类来支持更多格式：

```python
from get_skills_mcp.skill_loader import SkillLoader

class CustomSkillLoader(SkillLoader):
    def _load_skill_from_file(self, file_path, source):
        # 自定义加载逻辑
        pass
```

### 添加新工具

在 [`get_skills_mcp_server.py`](get_skills_mcp/get_skills_mcp_server.py) 中添加新的工具定义和处理逻辑。

## 日志

服务器日志输出到 stderr，可以通过 MCP 客户端查看：

```
2026-01-12 11:30:00 - INFO - SkillLoader initialized
2026-01-12 11:30:00 - INFO - Loading custom skills from: /path/to/skills/custom
2026-01-12 11:30:00 - INFO - Loaded skill: my_skill from /path/to/skills/custom/my_skill.md
2026-01-12 11:30:00 - INFO - Total skills loaded: 5
```

## 故障排除

### 技能未加载

1. 检查技能文件格式是否正确
2. 查看服务器日志中的错误信息
3. 确认目录路径配置正确

### 找不到 vendor 技能

1. 确认已添加 git submodule
2. 执行 `git submodule update --init --recursive`
3. 检查 `vendor/anthropics-skills` 目录是否存在

## 相关链接

- [Anthropic Skills](https://github.com/anthropics/skills)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 许可证

本项目遵循 MIT 许可证。
