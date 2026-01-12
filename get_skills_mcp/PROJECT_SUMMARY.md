# Get Skills MCP - 项目总结

## 项目概述

Get Skills MCP 是一个基于 [Anthropic Skills](https://github.com/anthropics/skills) 概念的技能管理 MCP 服务器。它提供了一个统一的接口来加载、管理和查询技能，支持从多个来源加载技能文件。

## 实现完成情况

### ✅ 已完成的功能

1. **核心模块**
   - [`skill_loader.py`](skill_loader.py) - 技能加载器核心模块
     - 支持从多个目录加载技能
     - 支持 Markdown (.md)、JSON (.json) 和纯文本 (.txt) 格式
     - 自动处理技能名称冲突
     - 提供技能查询和搜索功能

2. **MCP 服务器**
   - [`get_skills_mcp_server.py`](get_skills_mcp_server.py) - MCP 服务器主文件
     - 实现了 5 个工具 (Tools)
     - 实现了资源协议 (Resources)
     - 完整的错误处理和日志记录

3. **工具列表**
   - `list_skills` - 列出所有技能（支持按来源筛选）
   - `get_skill` - 获取技能详细信息
   - `search_skills` - 搜索技能
   - `reload_skills` - 重新加载技能
   - `get_skill_instructions` - 获取技能执行指令

4. **资源支持**
   - 每个技能都作为 MCP 资源暴露
   - URI 格式: `skill://skill_name`
   - 支持通过资源协议读取技能内容

5. **技能目录结构**
   - `skills/custom/` - 自定义技能目录
   - `vendor/anthropics-skills/` - Anthropic 开源技能目录（已配置为 git submodule）

6. **文档**
   - [`README.md`](README.md) - 完整的项目文档
   - [`QUICKSTART.md`](QUICKSTART.md) - 快速入门指南
   - 本文档 - 项目总结

7. **测试**
   - [`test_skills.py`](test_skills.py) - 功能测试脚本
   - 测试结果：✅ 所有测试通过
   - 成功加载 66 个技能（3 个自定义 + 63 个 vendor）

8. **示例技能**
   - [`skills/custom/code_review.md`](../skills/custom/code_review.md) - 代码审查技能（Markdown 格式）
   - [`skills/custom/api_design.json`](../skills/custom/api_design.json) - API 设计技能（JSON 格式）

## 技术架构

```
get_skills_mcp/
├── __init__.py                 # 包初始化
├── skill_loader.py             # 技能加载器（核心逻辑）
├── get_skills_mcp_server.py    # MCP 服务器（MCP 协议实现）
├── requirements.txt            # Python 依赖
├── test_skills.py              # 测试脚本
├── README.md                   # 完整文档
├── QUICKSTART.md               # 快速入门
└── PROJECT_SUMMARY.md          # 本文档

skills/
└── custom/                     # 自定义技能目录
    ├── skill.md               # 占位符
    ├── code_review.md         # 代码审查技能
    └── api_design.json        # API 设计技能

vendor/
└── anthropics-skills/         # Anthropic 开源技能（git submodule）
```

## 核心设计

### 1. 技能加载器 (SkillLoader)

**职责**：
- 从文件系统加载技能
- 解析不同格式的技能文件
- 管理技能缓存
- 提供查询接口

**关键特性**：
- 支持多种文件格式（MD/JSON/TXT）
- 自动处理名称冲突
- 按来源分组管理
- 支持热重载

### 2. MCP 服务器

**职责**：
- 实现 MCP 协议
- 暴露工具和资源
- 处理客户端请求
- 错误处理和日志

**关键特性**：
- 标准 MCP 协议实现
- 完整的工具集
- 资源协议支持
- 详细的日志记录

### 3. 技能格式

**Markdown (.md)**：
```markdown
# 技能标题（作为描述）

其余内容作为指令...
```

**JSON (.json)**：
```json
{
  "name": "skill_name",
  "description": "描述",
  "instructions": "指令",
  "metadata": {}
}
```

**纯文本 (.txt)**：
- 整个文件内容作为指令
- 文件名作为技能名称

## 使用方式

### 1. 配置 MCP 客户端

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

### 2. 使用工具

```python
# 列出所有技能
mcp_get_skills_list_skills(source="all")

# 获取特定技能
mcp_get_skills_get_skill(name="code_review")

# 搜索技能
mcp_get_skills_search_skills(keyword="api")

# 重新加载
mcp_get_skills_reload_skills()
```

### 3. 添加自定义技能

在 `skills/custom/` 目录下创建 `.md` 或 `.json` 文件即可。

## 测试结果

```
✅ 所有测试通过！

加载统计：
- 自定义技能: 3 个
- Vendor技能: 63 个
- 总计: 66 个技能

测试项目：
✓ SkillLoader 初始化
✓ 技能加载
✓ 技能查询
✓ 格式解析
✓ 对象转换
```

## 特色功能

1. **多来源支持**
   - 自定义技能和开源技能分离管理
   - 自动标记来源
   - 支持按来源筛选

2. **多格式支持**
   - Markdown - 适合文档化的技能
   - JSON - 适合结构化的技能
   - 纯文本 - 适合简单的技能

3. **名称冲突处理**
   - 自动检测重名
   - 添加来源前缀
   - 保持原始技能可用

4. **资源协议**
   - 技能作为 MCP 资源暴露
   - 支持 URI 访问
   - 与工具互补

5. **热重载**
   - 支持运行时重新加载
   - 无需重启服务器
   - 方便开发和测试

## 扩展性

### 添加新格式支持

在 [`skill_loader.py`](skill_loader.py) 中扩展 `_load_skill_from_file` 方法：

```python
def _load_skill_from_file(self, file_path: Path, source: str):
    if file_path.suffix.lower() == '.yaml':
        return self._load_skill_from_yaml(file_path, source)
    # ...
```

### 添加新工具

在 [`get_skills_mcp_server.py`](get_skills_mcp_server.py) 中添加工具定义和处理逻辑。

### 自定义加载逻辑

继承 `SkillLoader` 类并重写相关方法。

## 与 Anthropic Skills 的关系

本项目基于 Anthropic Skills 的概念，但做了以下扩展：

1. **MCP 协议集成** - 通过 MCP 协议暴露技能
2. **多格式支持** - 支持 MD/JSON/TXT 多种格式
3. **自定义技能** - 支持用户自定义技能目录
4. **工具化** - 提供丰富的工具集进行技能管理
5. **资源化** - 技能作为 MCP 资源可被访问

## 后续改进方向

1. **技能验证** - 添加技能格式验证
2. **技能模板** - 提供技能创建模板
3. **技能分类** - 支持技能分类和标签
4. **技能依赖** - 支持技能间依赖关系
5. **技能版本** - 支持技能版本管理
6. **性能优化** - 缓存优化和懒加载
7. **Web UI** - 提供 Web 界面管理技能

## 相关链接

- [Anthropic Skills](https://github.com/anthropics/skills)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [项目 README](README.md)
- [快速入门](QUICKSTART.md)

## 许可证

MIT License

---

**创建日期**: 2026-01-12  
**版本**: 1.0.0  
**状态**: ✅ 完成并测试通过
