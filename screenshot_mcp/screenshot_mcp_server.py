#!/usr/bin/env python3
"""Screenshot MCP Server - 提供截屏功能的MCP服务器，支持多显示器"""

import asyncio
import json
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

from screenshot_mcp.screenshot_tools import ScreenshotTool


# 创建MCP服务器实例
app = Server("screenshot-mcp-server")

# 全局截屏工具实例
screenshot_tool: Optional[ScreenshotTool] = None


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="take_screenshot",
            description="截取当前全屏并保存为PNG图片文件。支持Windows、Linux和macOS系统。在WSL环境下会自动调用Windows的截图功能。",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "自定义截图文件名（不含路径），如果不提供则自动生成时间戳文件名。例如: 'my_screenshot.png'",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "截图保存目录的绝对路径，如果不提供则保存到screenshot_mcp目录下",
                    },
                    "return_base64": {
                        "type": "boolean",
                        "description": "是否返回图片的base64编码数据，默认为false",
                        "default": False,
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="get_screenshot_info",
            description="获取最近一次截图的详细信息，包括文件路径、尺寸、格式等",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="list_monitors",
            description="列出所有显示器信息，包括显示器编号、是否为主显示器、位置坐标、宽度和高度等。支持多显示器环境。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="take_screenshot_monitor",
            description="截取指定显示器的屏幕并保存为PNG图片文件。可以选择截取特定的显示器，适用于多显示器环境。",
            inputSchema={
                "type": "object",
                "properties": {
                    "monitor_number": {
                        "type": "integer",
                        "description": "显示器编号（从1开始），可以通过list_monitors工具获取显示器列表",
                        "minimum": 1,
                    },
                    "filename": {
                        "type": "string",
                        "description": "自定义截图文件名（不含路径），如果不提供则自动生成时间戳文件名。例如: 'monitor1_screenshot.png'",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "截图保存目录的绝对路径，如果不提供则保存到screenshot_mcp目录下",
                    },
                    "return_base64": {
                        "type": "boolean",
                        "description": "是否返回图片的base64编码数据，默认为false",
                        "default": False,
                    }
                },
                "required": ["monitor_number"],
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """处理工具调用"""
    global screenshot_tool
    
    if name == "take_screenshot":
        # 获取参数
        filename = arguments.get("filename")
        output_dir = arguments.get("output_dir")
        return_base64 = arguments.get("return_base64", False)
        
        # 创建截屏工具实例
        screenshot_tool = ScreenshotTool(output_dir)
        
        # 执行截图
        if return_base64:
            result = screenshot_tool.take_screenshot_base64(filename)
        else:
            result = screenshot_tool.take_screenshot(filename)
        
        # 构建响应
        if result.get("success"):
            response_text = f"""✅ 截图成功！

📁 文件信息:
  - 文件名: {result['filename']}
  - 完整路径: {result['filepath']}
  - 文件格式: {result['format']}
  
📐 图片尺寸:
  - 宽度: {result['width']} 像素
  - 高度: {result['height']} 像素
  - 颜色模式: {result['mode']}
  
🔧 截图方法: {result.get('method', 'unknown')}
"""
            
            if return_base64:
                response_text += f"\n📦 数据大小: {result.get('size_bytes', 0)} 字节"
                response_text += f"\n🔐 Base64数据已生成（长度: {len(result.get('base64', ''))} 字符）"
            
            return [TextContent(type="text", text=response_text)]
        else:
            error_text = f"""❌ 截图失败！

错误信息: {result.get('error', '未知错误')}
操作系统: {result.get('system', '未知')}

💡 提示:
- 在WSL环境下，请确保Windows系统可以正常截图
- 在Linux环境下，可能需要安装 mss 库: pip install mss
- 或者安装 scrot 命令: sudo apt install scrot
- 确保有图形界面环境（DISPLAY环境变量已设置）
"""
            return [TextContent(type="text", text=error_text)]
    
    elif name == "get_screenshot_info":
        if screenshot_tool is None:
            return [TextContent(
                type="text",
                text="⚠️ 还没有进行过截图操作，请先使用 take_screenshot 工具进行截图。"
            )]
        
        # 获取最新的截图文件
        screenshots = list(screenshot_tool.output_dir.glob("screenshot_*.png"))
        if not screenshots:
            return [TextContent(
                type="text",
                text="⚠️ 未找到任何截图文件。"
            )]
        
        latest_screenshot = max(screenshots, key=lambda p: p.stat().st_mtime)
        
        try:
            from PIL import Image
            import datetime
            with Image.open(latest_screenshot) as img:
                info_text = f"""📸 最新截图信息:

📁 文件信息:
  - 文件名: {latest_screenshot.name}
  - 完整路径: {latest_screenshot.absolute()}
  - 文件大小: {latest_screenshot.stat().st_size} 字节
  - 文件格式: {img.format}
  
📐 图片尺寸:
  - 宽度: {img.size[0]} 像素
  - 高度: {img.size[1]} 像素
  - 颜色模式: {img.mode}
  
🕐 创建时间: {datetime.datetime.fromtimestamp(latest_screenshot.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
"""
                return [TextContent(type="text", text=info_text)]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ 读取截图信息失败: {str(e)}"
            )]
    
    elif name == "list_monitors":
        # 创建截屏工具实例（如果还没有）
        if screenshot_tool is None:
            screenshot_tool = ScreenshotTool()
        
        try:
            monitors = screenshot_tool.get_monitors_info()
            
            response_text = f"""🖥️ 显示器信息列表:

检测到 {len(monitors)} 个显示器:

"""
            for monitor in monitors:
                response_text += f"""📺 显示器 {monitor['MonitorNumber']}:
  - 是否为主显示器: {'是' if monitor['IsPrimary'] else '否'}
  - 位置: ({monitor['Left']}, {monitor['Top']})
  - 尺寸: {monitor['Width']} x {monitor['Height']} 像素
  - 边界: Left={monitor['Left']}, Top={monitor['Top']}, Right={monitor['Right']}, Bottom={monitor['Bottom']}

"""
            
            response_text += "💡 提示: 使用 take_screenshot_monitor 工具可以截取指定显示器的屏幕"
            
            return [TextContent(type="text", text=response_text)]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ 获取显示器信息失败: {str(e)}"
            )]
    
    elif name == "take_screenshot_monitor":
        # 获取参数
        monitor_number = arguments.get("monitor_number")
        filename = arguments.get("filename")
        output_dir = arguments.get("output_dir")
        return_base64 = arguments.get("return_base64", False)
        
        if monitor_number is None:
            return [TextContent(
                type="text",
                text="❌ 错误: 必须指定 monitor_number 参数"
            )]
        
        # 创建截屏工具实例
        screenshot_tool = ScreenshotTool(output_dir)
        
        # 执行截图
        if return_base64:
            result = screenshot_tool.take_screenshot_base64(filename, monitor_number)
        else:
            result = screenshot_tool.take_screenshot(filename, monitor_number)
        
        # 构建响应
        if result.get("success"):
            response_text = f"""✅ 截取显示器 {monitor_number} 成功！

📁 文件信息:
  - 文件名: {result['filename']}
  - 完整路径: {result['filepath']}
  - 文件格式: {result['format']}
  
📐 图片尺寸:
  - 宽度: {result['width']} 像素
  - 高度: {result['height']} 像素
  - 颜色模式: {result['mode']}
  
🖥️ 显示器编号: {result.get('monitor_number', 'N/A')}
🔧 截图方法: {result.get('method', 'unknown')}
"""
            
            if return_base64:
                response_text += f"\n📦 数据大小: {result.get('size_bytes', 0)} 字节"
                response_text += f"\n🔐 Base64数据已生成（长度: {len(result.get('base64', ''))} 字符）"
            
            return [TextContent(type="text", text=response_text)]
        else:
            error_text = f"""❌ 截取显示器 {monitor_number} 失败！

错误信息: {result.get('error', '未知错误')}
操作系统: {result.get('system', '未知')}

💡 提示:
- 请先使用 list_monitors 工具查看可用的显示器列表
- 确保指定的显示器编号有效
- 在WSL环境下，请确保Windows系统可以正常截图
- 在Linux环境下，可能需要安装 mss 库: pip install mss
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
                server_name="screenshot-mcp-server",
                server_version="2.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import datetime
    asyncio.run(main())
