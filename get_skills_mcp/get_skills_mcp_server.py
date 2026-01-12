#!/usr/bin/env python3
"""Get Skills MCP Server

按用户给定的最小规范暴露 skills：

- Skills 根目录：`./skills`
- 每个 skill 为 `skills/<skill_name>/SKILL.md`
- list 只扫描 `skills/` 的一级子目录且必须存在 `SKILL.md`

同时兼容 vendor/anthropics-skills：
- `vendor/anthropics-skills/skills/<skill_name>/SKILL.md`
- 同样只扫描一级子目录

对外能力：
- Tools:
  - list_skills(source=custom|vendor|all)
  - get_skill(name)
  - get_skill_instructions(name)  # 与 get_skill 等价，返回 SKILL.md 原文
  - search_skills(keyword)
  - reload_skills()
- Resources:
  - `skill://{name}` -> 对应 `SKILL.md` 原文

说明：这里不解析 frontmatter、不做“文档/规范类”内容聚合；仅按目录存在 `SKILL.md` 判定是否为 skill。
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Optional

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, TextContent, Tool
except ImportError:
    print("错误: 未找到 MCP SDK。请安装: pip install mcp", file=sys.stderr)
    sys.exit(1)

from get_skills_mcp.skill_loader import SkillLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

app = Server("get-skills-mcp-server")

skill_loader: Optional[SkillLoader] = None


def _ensure_loader() -> SkillLoader:
    global skill_loader
    if skill_loader is None:
        skill_loader = SkillLoader()
        skill_loader.load_all_skills()
    return skill_loader


def _parse_skill_uri(uri: str) -> str:
    if not uri.startswith("skill://"):
        raise ValueError(f"Invalid skill URI: {uri}")
    name = uri[len("skill://") :].strip()
    if not name:
        raise ValueError(f"Invalid skill URI (missing name): {uri}")
    return name


@app.list_resources()
async def handle_list_resources() -> list[Resource]:
    loader = _ensure_loader()

    resources: list[Resource] = []
    for key in loader.list_skills():
        resources.append(
            Resource(
                uri=f"skill://{key}",
                name=key,
                description=f"Skill folder '{key}' (read SKILL.md)",
                mimeType="text/plain",
            )
        )

    return resources


@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    loader = _ensure_loader()

    skill_key = _parse_skill_uri(uri)
    skill = loader.get_skill(skill_key)
    if skill is None:
        raise ValueError(f"Skill not found: {skill_key}")

    return skill.read_text()


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_skills",
            description="列出所有 skills/<name>/SKILL.md（以及 vendor/anthropics-skills/skills/<name>/SKILL.md）",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "筛选来源：custom（./skills）/vendor（vendor/anthropics-skills/skills）/all（默认）",
                        "enum": ["custom", "vendor", "all"],
                    }
                },
            },
        ),
        Tool(
            name="get_skill",
            description="读取 skill 的 SKILL.md 原文",
            inputSchema={
                "type": "object",
                "properties": {"name": {"type": "string", "description": "skill key"}},
                "required": ["name"],
            },
        ),
        Tool(
            name="get_skill_instructions",
            description="读取 skill 的 SKILL.md 原文（与 get_skill 等价）",
            inputSchema={
                "type": "object",
                "properties": {"name": {"type": "string", "description": "skill key"}},
                "required": ["name"],
            },
        ),
        Tool(
            name="search_skills",
            description="在 skill key 与 SKILL.md 原文中搜索关键词",
            inputSchema={
                "type": "object",
                "properties": {"keyword": {"type": "string", "description": "搜索关键词"}},
                "required": ["keyword"],
            },
        ),
        Tool(
            name="reload_skills",
            description="重新扫描 skills 目录",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="debug_paths",
            description="调试：显示MCP服务器的实际路径配置和加载的skills详情",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    loader = _ensure_loader()

    try:
        if name == "list_skills":
            source = (arguments.get("source") or "all").strip()
            if source not in {"custom", "vendor", "all"}:
                source = "all"

            if source == "all":
                skills = loader.skills
            else:
                skills = loader.get_skills_by_source(source)

            keys = sorted(skills.keys())
            return [
                TextContent(
                    type="text",
                    text="\n".join([f"count={len(keys)} source={source}"] + keys),
                )
            ]

        if name == "get_skill" or name == "get_skill_instructions":
            skill_key = (arguments.get("name") or "").strip()
            if not skill_key:
                return [TextContent(type="text", text="错误: 必须提供 name")]
            skill = loader.get_skill(skill_key)
            if skill is None:
                return [TextContent(type="text", text=f"Skill not found: {skill_key}")]
            return [TextContent(type="text", text=skill.read_text())]

        if name == "search_skills":
            keyword = (arguments.get("keyword") or "").strip().lower()
            if not keyword:
                return [TextContent(type="text", text="错误: 必须提供 keyword")]

            hits: list[str] = []
            for key, sk in loader.skills.items():
                if keyword in key.lower():
                    hits.append(key)
                    continue
                try:
                    if keyword in sk.read_text().lower():
                        hits.append(key)
                except Exception:
                    # 读取失败不阻断搜索
                    continue

            hits = sorted(set(hits))
            return [
                TextContent(
                    type="text",
                    text="\n".join([f"count={len(hits)} keyword={keyword}"] + hits),
                )
            ]

        if name == "reload_skills":
            loader.reload_skills()
            custom_count = len(loader.get_skills_by_source("custom"))
            vendor_count = len(loader.get_skills_by_source("vendor"))
            total = len(loader.skills)
            return [
                TextContent(
                    type="text",
                    text=(
                        "reloaded\n"
                        f"custom={custom_count}\n"
                        f"vendor={vendor_count}\n"
                        f"total={total}"
                    ),
                )
            ]

        if name == "debug_paths":
            custom_skills = loader.get_skills_by_source("custom")
            vendor_skills = loader.get_skills_by_source("vendor")
            
            lines = [
                f"Base dir: {loader.base_dir}",
                f"Custom root: {loader.custom_skills_root}",
                f"Vendor root: {loader.vendor_skills_root}",
                f"",
                f"Custom skills ({len(custom_skills)}):",
            ]
            for key, skill in sorted(custom_skills.items()):
                lines.append(f"  {key} -> {skill.skill_md_path}")
            
            lines.append(f"")
            lines.append(f"Vendor skills ({len(vendor_skills)}):")
            for key, skill in sorted(vendor_skills.items()):
                lines.append(f"  {key} -> {skill.skill_md_path}")
            
            return [TextContent(type="text", text="\n".join(lines))]

        return [TextContent(type="text", text=f"未知工具: {name}")]

    except Exception as e:
        logger.error("Tool execution error: %s", e, exc_info=True)
        return [TextContent(type="text", text=f"工具执行错误: {str(e)}")]


async def main() -> None:
    logger.info("Starting Get Skills MCP Server...")

    global skill_loader
    skill_loader = SkillLoader()
    skill_loader.load_all_skills()

    logger.info("Loaded %s skills", len(skill_loader.skills))
    logger.info("Base dir: %s", skill_loader.base_dir)
    logger.info("Custom root: %s", skill_loader.custom_skills_root)
    logger.info("Vendor root: %s", skill_loader.vendor_skills_root)
    logger.info("Custom skills: %s", len(skill_loader.get_skills_by_source("custom")))
    logger.info("Vendor skills: %s", len(skill_loader.get_skills_by_source("vendor")))

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="get-skills-mcp-server",
                server_version="1.2.0",
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
        logger.error("Server error: %s", e, exc_info=True)
        sys.exit(1)
