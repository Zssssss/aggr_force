#!/usr/bin/env python3
"""
Move to Monitor MCP Server
将Windows程序移动到指定显示器的MCP服务器
"""

import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from monitor_tools import list_monitors, find_window, move_to_monitor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
app = Server("move-to-monitor")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="list_monitors",
            description=(
                "列出所有显示器信息。返回每个显示器的编号、是否为主显示器、"
                "位置坐标、宽度和高度等信息。"
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="find_window",
            description=(
                "根据窗口标题查找窗口。支持部分匹配，返回窗口句柄和完整标题。"
                "例如：查找标题包含'Chrome'的窗口。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title_pattern": {
                        "type": "string",
                        "description": "窗口标题（支持部分匹配）"
                    }
                },
                "required": ["title_pattern"]
            }
        ),
        Tool(
            name="move_to_monitor",
            description=(
                "将指定窗口移动到目标显示器。根据窗口标题查找窗口，"
                "然后将其移动到指定编号的显示器上。可选择是否最大化窗口。"
                "显示器编号从1开始。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title_pattern": {
                        "type": "string",
                        "description": "窗口标题（支持部分匹配）"
                    },
                    "monitor_number": {
                        "type": "integer",
                        "description": "目标显示器编号（从1开始）",
                        "minimum": 1
                    },
                    "maximize": {
                        "type": "boolean",
                        "description": "是否最大化窗口（默认为false）",
                        "default": False
                    }
                },
                "required": ["title_pattern", "monitor_number"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    try:
        if name == "list_monitors":
            result = list_monitors()
            return [TextContent(type="text", text=result)]
        
        elif name == "find_window":
            title_pattern = arguments.get("title_pattern")
            if not title_pattern:
                return [TextContent(
                    type="text",
                    text='{"success": false, "error": "缺少参数: title_pattern"}'
                )]
            
            result = find_window(title_pattern)
            return [TextContent(type="text", text=result)]
        
        elif name == "move_to_monitor":
            title_pattern = arguments.get("title_pattern")
            monitor_number = arguments.get("monitor_number")
            maximize = arguments.get("maximize", False)
            
            if not title_pattern:
                return [TextContent(
                    type="text",
                    text='{"success": false, "error": "缺少参数: title_pattern"}'
                )]
            
            if not monitor_number:
                return [TextContent(
                    type="text",
                    text='{"success": false, "error": "缺少参数: monitor_number"}'
                )]
            
            result = move_to_monitor(title_pattern, monitor_number, maximize)
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(
                type="text",
                text=f'{{"success": false, "error": "未知工具: {name}"}}'
            )]
    
    except Exception as e:
        logger.error(f"工具调用失败: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f'{{"success": false, "error": "工具调用失败: {str(e)}"}}'
        )]


async def main():
    """主函数"""
    logger.info("启动 Move to Monitor MCP 服务器...")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
