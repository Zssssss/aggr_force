#!/usr/bin/env python3
"""
Get Skills MCP Server - 基于Anthropic Skills概念的技能管理MCP服务器

这个MCP服务器提供技能加载、查询和管理功能。
支持从以下目录加载技能：
1. skills/custom - 用户自定义技能目录
2. vendor/anthropics-skills - Anthropic开源技能目录
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Any, Optional

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, Resource, ResourceTemplate
except ImportError:
    print("错误: 未找到MCP SDK。请安装: pip install mcp", file=sys.stderr)
    sys.exit(1)

from get_skills_mcp.skill_loader import SkillLoader, Skill

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
app = Server("get-skills-mcp-server")

# 全局技能加载器实例
skill_loader: Optional[SkillLoader] = None


@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    """列出所有可用的技能资源"""
    global skill_loader
    
    if skill_loader is None:
        skill_loader = SkillLoader()
        skill_loader.load_all_skills()
    
    resources = []
    for skill_name, skill in skill_loader.skills.items():
        resources.append(
            Resource(
                uri=f"skill://{skill_name}",
                name=skill_name,
                description=skill.description or f"Skill: {skill_name}",
                mimeType="text/plain"
            )
        )
    
    return resources


@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取指定技能的详细内容"""
    global skill_loader
    
    if skill_loader is None:
        skill_loader = SkillLoader()
        skill_loader.load_all_skills()
    
    # 解析URI: skill://skill_name
    if not uri.startswith("skill://"):
        raise ValueError(f"Invalid skill URI: {uri}")
    
    skill_name = uri[8:]  # 移除 "skill://" 前缀
    skill = skill_loader.get_skill(skill_name)
    
    if skill is None:
        raise ValueError(f"Skill not found: {skill_name}")
    
    # 返回技能的完整信息
    content = f"""# {skill.name}

## 描述
{skill.description}

## 指令
{skill.instructions}

## 元数据
- 来源: {skill.metadata.get('source', 'unknown')}
- 格式: {skill.metadata.get('format', 'unknown')}
- 文件路径: {skill.source_path}
"""
    return content


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="list_skills",
            description="列出所有已加载的技能，包括自定义技能和vendor技能",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "筛选技能来源：'custom'（自定义）、'vendor'（开源）或不指定（全部）",
                        "enum": ["custom", "vendor", "all"]
                    }
                }
            }
        ),
        Tool(
            name="get_skill",
            description="获取指定技能的详细信息，包括名称、描述、指令和元数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "技能名称"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="search_skills",
            description="根据关键词搜索技能，在技能名称和描述中查找匹配项",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="reload_skills",
            description="重新加载所有技能，用于在添加新技能后刷新技能列表",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_skill_instructions",
            description="获取指定技能的执行指令，可直接用于AI助手执行",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "技能名称"
                    }
                },
                "required": ["name"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    global skill_loader
    
    # 初始化技能加载器
    if skill_loader is None:
        skill_loader = SkillLoader()
        skill_loader.load_all_skills()
    
    try:
        if name == "list_skills":
            source = arguments.get("source", "all")
            
            if source == "all":
                skills = skill_loader.skills
            else:
                skills = skill_loader.get_skills_by_source(source)
            
            if not skills:
                return [TextContent(
                    type="text",
                    text=f"📋 未找到技能（来源: {source}）"
                )]
            
            # 按来源分组
            custom_skills = [s for s in skills.values() if s.metadata.get('source') == 'custom']
            vendor_skills = [s for s in skills.values() if s.metadata.get('source') == 'vendor']
            
            result = f"📋 技能列表（共 {len(skills)} 个）\n\n"
            
            if custom_skills:
                result += f"## 🎨 自定义技能 ({len(custom_skills)})\n"
                for skill in custom_skills:
                    result += f"- **{skill.name}**: {skill.description}\n"
                result += "\n"
            
            if vendor_skills:
                result += f"## 📦 Vendor技能 ({len(vendor_skills)})\n"
                for skill in vendor_skills:
                    result += f"- **{skill.name}**: {skill.description}\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_skill":
            skill_name = arguments.get("name")
            if not skill_name:
                return [TextContent(
                    type="text",
                    text="❌ 错误: 必须提供技能名称"
                )]
            
            skill = skill_loader.get_skill(skill_name)
            if skill is None:
                return [TextContent(
                    type="text",
                    text=f"❌ 未找到技能: {skill_name}\n\n💡 使用 list_skills 工具查看所有可用技能"
                )]
            
            result = f"""📖 技能详情

**名称**: {skill.name}

**描述**: {skill.description}

**指令**:
{skill.instructions}

**元数据**:
- 来源: {skill.metadata.get('source', 'unknown')}
- 格式: {skill.metadata.get('format', 'unknown')}
- 文件路径: {skill.source_path}
"""
            return [TextContent(type="text", text=result)]
        
        elif name == "search_skills":
            keyword = arguments.get("keyword", "").lower()
            if not keyword:
                return [TextContent(
                    type="text",
                    text="❌ 错误: 必须提供搜索关键词"
                )]
            
            # 搜索技能
            matched_skills = []
            for skill_name, skill in skill_loader.skills.items():
                if (keyword in skill_name.lower() or 
                    keyword in skill.description.lower() or
                    keyword in skill.instructions.lower()):
                    matched_skills.append(skill)
            
            if not matched_skills:
                return [TextContent(
                    type="text",
                    text=f"🔍 未找到包含关键词 '{keyword}' 的技能"
                )]
            
            result = f"🔍 搜索结果（关键词: '{keyword}'，共 {len(matched_skills)} 个）\n\n"
            for skill in matched_skills:
                result += f"- **{skill.name}** [{skill.metadata.get('source', 'unknown')}]\n"
                result += f"  {skill.description}\n\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "reload_skills":
            skill_loader.reload_skills()
            
            custom_count = len(skill_loader.get_skills_by_source('custom'))
            vendor_count = len(skill_loader.get_skills_by_source('vendor'))
            
            result = f"""🔄 技能重新加载完成

- 自定义技能: {custom_count} 个
- Vendor技能: {vendor_count} 个
- 总计: {len(skill_loader.skills)} 个

💡 使用 list_skills 工具查看所有技能
"""
            return [TextContent(type="text", text=result)]
        
        elif name == "get_skill_instructions":
            skill_name = arguments.get("name")
            if not skill_name:
                return [TextContent(
                    type="text",
                    text="❌ 错误: 必须提供技能名称"
                )]
            
            skill = skill_loader.get_skill(skill_name)
            if skill is None:
                return [TextContent(
                    type="text",
                    text=f"❌ 未找到技能: {skill_name}"
                )]
            
            result = f"""📝 技能指令: {skill.name}

{skill.instructions}
"""
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ 未知的工具: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"❌ 工具执行错误: {str(e)}"
        )]


async def main():
    """主函数"""
    logger.info("Starting Get Skills MCP Server...")
    
    # 初始化技能加载器
    global skill_loader
    skill_loader = SkillLoader()
    skill_loader.load_all_skills()
    
    logger.info(f"Loaded {len(skill_loader.skills)} skills")
    
    # 使用stdio传输运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="get-skills-mcp-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
