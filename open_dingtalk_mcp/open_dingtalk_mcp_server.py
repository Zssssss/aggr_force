#!/usr/bin/env python3
"""
打开钉钉 MCP 服务器
提供打开钉钉应用的 MCP 工具
"""

import asyncio
import logging
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from open_dingtalk_tools import open_dingtalk, check_dingtalk_installed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建服务器实例
server = Server("open-dingtalk-mcp")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    列出所有可用的工具
    """
    return [
        types.Tool(
            name="open_dingtalk",
            description="打开钉钉应用。支持 Windows、Linux (WSL) 和 macOS 系统。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="check_dingtalk_installed",
            description="检查钉钉应用是否已安装，并返回可能的安装路径。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    处理工具调用请求
    """
    try:
        if name == "open_dingtalk":
            logger.info("执行打开钉钉操作")
            result = open_dingtalk()
            
            if result["success"]:
                message = f"✅ {result['message']}\n"
                message += f"平台: {result['platform']}\n"
                if 'method' in result:
                    message += f"使用方法: {result['method']}"
            else:
                message = f"❌ {result['message']}\n"
                message += f"平台: {result['platform']}\n"
                if 'error' in result:
                    message += f"错误信息: {result['error']}"
            
            return [
                types.TextContent(
                    type="text",
                    text=message
                )
            ]
            
        elif name == "check_dingtalk_installed":
            logger.info("检查钉钉安装状态")
            result = check_dingtalk_installed()
            
            if result["installed"]:
                message = f"✅ {result['message']}\n"
                message += f"平台: {result['platform']}\n"
                if result['paths']:
                    message += f"安装路径:\n"
                    for path in result['paths']:
                        message += f"  - {path}\n"
            else:
                message = f"❌ {result['message']}\n"
                message += f"平台: {result['platform']}\n"
                if 'error' in result:
                    message += f"错误信息: {result['error']}"
            
            return [
                types.TextContent(
                    type="text",
                    text=message
                )
            ]
            
        else:
            raise ValueError(f"未知的工具: {name}")
            
    except Exception as e:
        logger.error(f"执行工具 {name} 时发生错误: {str(e)}")
        return [
            types.TextContent(
                type="text",
                text=f"❌ 执行工具时发生错误: {str(e)}"
            )
        ]


async def main():
    """
    主函数：启动 MCP 服务器
    """
    logger.info("启动打开钉钉 MCP 服务器...")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="open-dingtalk-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器运行时发生错误: {str(e)}")
        raise
