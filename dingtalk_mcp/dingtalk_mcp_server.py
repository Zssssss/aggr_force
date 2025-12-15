"""
钉钉文档 MCP 服务器入口

负责加载配置、创建客户端、注册工具并运行 MCP 服务器。
"""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from .config import load_config
from .dingtalk_client import DingTalkClient
from .mcp_tools import MCPTools


def create_server() -> Server:
    """
    创建并配置 MCP 服务器。
    
    Returns:
        Server: MCP 服务器实例
    """
    # 加载配置
    config = load_config()
    
    # 创建钉钉客户端
    client = DingTalkClient(config)
    
    # 创建 MCP 工具
    mcp_tools = MCPTools(client)
    
    # 创建 MCP 服务器
    server = Server("dingtalk-docs")
    
    # 注册工具
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="create_doc",
                description="创建钉钉文档",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "文档标题"},
                        "content": {"type": "string", "description": "文档初始内容（可选）"},
                        "space_id": {"type": "string", "description": "空间 ID（可选）"},
                        "folder_id": {"type": "string", "description": "文件夹 ID（可选）"},
                    },
                    "required": ["title"],
                },
            ),
            Tool(
                name="get_doc",
                description="获取文档内容",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "文档 ID"},
                        "format": {
                            "type": "string",
                            "description": "返回格式（text/markdown/html，默认为 text）",
                            "enum": ["text", "markdown", "html"],
                            "default": "text",
                        },
                    },
                    "required": ["document_id"],
                },
            ),
            Tool(
                name="update_doc",
                description="更新文档内容",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "文档 ID"},
                        "content": {"type": "string", "description": "更新内容"},
                        "mode": {
                            "type": "string",
                            "description": "更新模式（overwrite/append，默认为 overwrite）",
                            "enum": ["overwrite", "append"],
                            "default": "overwrite",
                        },
                        "comment": {"type": "string", "description": "更新备注（可选）"},
                    },
                    "required": ["document_id", "content"],
                },
            ),
            Tool(
                name="list_docs",
                description="列出可访问文档",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "space_id": {"type": "string", "description": "空间 ID（可选）"},
                        "folder_id": {"type": "string", "description": "文件夹 ID（可选）"},
                        "keyword": {"type": "string", "description": "搜索关键词（可选）"},
                        "page": {
                            "type": "integer",
                            "description": "页码（从 1 开始，默认为 1）",
                            "minimum": 1,
                            "default": 1,
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "每页数量（默认为 20）",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                        },
                        "sort_by": {
                            "type": "string",
                            "description": "排序字段（create_time/update_time/title，默认为 update_time）",
                            "enum": ["create_time", "update_time", "title"],
                            "default": "update_time",
                        },
                        "sort_order": {
                            "type": "string",
                            "description": "排序顺序（asc/desc，默认为 desc）",
                            "enum": ["asc", "desc"],
                            "default": "desc",
                        },
                    },
                },
            ),
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "create_doc":
            result = await mcp_tools.create_doc_tool(
                title=arguments["title"],
                content=arguments.get("content"),
                space_id=arguments.get("space_id"),
                folder_id=arguments.get("folder_id"),
            )
        elif name == "get_doc":
            result = await mcp_tools.get_doc_tool(
                document_id=arguments["document_id"],
                format=arguments.get("format", "text"),
            )
        elif name == "update_doc":
            result = await mcp_tools.update_doc_tool(
                document_id=arguments["document_id"],
                content=arguments["content"],
                mode=arguments.get("mode", "overwrite"),
                comment=arguments.get("comment"),
            )
        elif name == "list_docs":
            result = await mcp_tools.list_docs_tool(
                space_id=arguments.get("space_id"),
                folder_id=arguments.get("folder_id"),
                keyword=arguments.get("keyword"),
                page=arguments.get("page", 1),
                page_size=arguments.get("page_size", 20),
                sort_by=arguments.get("sort_by", "update_time"),
                sort_order=arguments.get("sort_order", "desc"),
            )
        else:
            raise ValueError(f"未知工具: {name}")
        
        # 将结果转换为 TextContent
        import json
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    
    return server


async def main():
    """
    MCP 服务器主函数。
    """
    # 从 stdin/stdout 读取
    import sys
    
    server = create_server()
    
    # 运行服务器
    await server.run(
        read_stream=sys.stdin.buffer,
        write_stream=sys.stdout.buffer,
    )


if __name__ == "__main__":
    asyncio.run(main())