#!/usr/bin/env python3
"""Mouse Position MCP Server - 提供鼠标位置获取功能的MCP服务器"""

import asyncio
import sys
from typing import Any, Optional
from pathlib import Path

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from get_mouse_position_mcp.mouse_position_tools import MousePositionTool


# 创建MCP服务器实例
app = Server("mouse-position-mcp-server")

# 全局鼠标位置工具实例
mouse_tool: Optional[MousePositionTool] = None


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="get_mouse_position",
            description="获取当前鼠标的屏幕坐标位置。支持Windows、Linux、macOS系统。在WSL环境下会自动调用Windows的鼠标位置获取功能。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """处理工具调用"""
    global mouse_tool
    
    if name == "get_mouse_position":
        # 创建鼠标位置工具实例
        if mouse_tool is None:
            mouse_tool = MousePositionTool()
        
        # 获取鼠标位置
        result = mouse_tool.get_mouse_position()
        
        # 构建响应
        if result.get("success"):
            response_text = f"""🖱️ 鼠标位置获取成功！

📍 当前坐标:
  - X坐标: {result['x']} 像素
  - Y坐标: {result['y']} 像素
  
🔧 获取方法: {result.get('method', 'unknown')}
💻 操作系统: {result.get('system', 'unknown')}
"""
            return [TextContent(type="text", text=response_text)]
        else:
            error_text = f"""❌ 鼠标位置获取失败！

错误信息: {result.get('error', '未知错误')}
操作系统: {result.get('system', '未知')}

💡 提示:
- 在WSL环境下，会自动使用Windows的鼠标位置获取功能
- 在Linux环境下，可能需要安装以下工具之一:
  * pip install pyautogui
  * pip install pynput
  * sudo apt install xdotool
- 在Windows环境下，可能需要安装:
  * pip install pyautogui
  * pip install pynput
  * pip install pywin32
- 在macOS环境下，可能需要安装:
  * pip install pyautogui
  * pip install pynput
  * pip install pyobjc-framework-Quartz
"""
            return [TextContent(type="text", text=error_text)]
    
    else:
        return [TextContent(
            type="text",
            text=f"❌ 未知的工具: {name}"
        )]


async def main():
    """主函数"""
    # 使用stdio传输运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mouse-position-mcp-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
