#!/usr/bin/env python3
"""Window Split MCP Server - 提供窗口分屏功能的MCP服务器

这个MCP服务器提供以下功能：
1. 列出所有窗口
2. 获取屏幕尺寸
3. 获取活动窗口
4. 移动和调整窗口大小
5. 水平分屏（左右分屏）
6. 垂直分屏（上下分屏）
7. 网格分屏（四分屏）
8. 最大化窗口
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Optional

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from window_split_mcp.window_split_tools import WindowSplitTool


# 创建MCP服务器实例
app = Server("window-split-mcp-server")

# 全局工具实例
window_tool: Optional[WindowSplitTool] = None


def get_tool() -> WindowSplitTool:
    """获取或创建工具实例"""
    global window_tool
    if window_tool is None:
        window_tool = WindowSplitTool()
    return window_tool


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="list_windows",
            description="列出所有打开的窗口，包括窗口ID、标题、位置和大小信息。支持Linux系统（需要wmctrl）。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_screen_size",
            description="获取当前屏幕的尺寸（宽度和高度）。支持Linux、Windows和macOS系统。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_active_window",
            description="获取当前活动（焦点）窗口的信息，包括窗口ID和标题。支持Linux系统（需要xdotool）。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="move_window",
            description="移动窗口到指定位置并调整大小。支持Linux系统（需要wmctrl）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_id": {
                        "type": "string",
                        "description": "窗口ID（可以从list_windows获取）",
                    },
                    "x": {
                        "type": "integer",
                        "description": "窗口左上角的X坐标（像素）",
                    },
                    "y": {
                        "type": "integer",
                        "description": "窗口左上角的Y坐标（像素）",
                    },
                    "width": {
                        "type": "integer",
                        "description": "窗口宽度（像素）",
                    },
                    "height": {
                        "type": "integer",
                        "description": "窗口高度（像素）",
                    },
                },
                "required": ["window_id", "x", "y", "width", "height"],
            },
        ),
        Tool(
            name="split_horizontal",
            description="水平分屏（左右分屏）。将1-2个窗口排列在屏幕左右两侧。如果只提供1个窗口，它将占据左半屏。",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "窗口ID列表（最多2个），第一个窗口在左侧，第二个在右侧",
                        "minItems": 1,
                        "maxItems": 2,
                    },
                },
                "required": ["window_ids"],
            },
        ),
        Tool(
            name="split_vertical",
            description="垂直分屏（上下分屏）。将1-2个窗口排列在屏幕上下两侧。如果只提供1个窗口，它将占据上半屏。",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "窗口ID列表（最多2个），第一个窗口在上方，第二个在下方",
                        "minItems": 1,
                        "maxItems": 2,
                    },
                },
                "required": ["window_ids"],
            },
        ),
        Tool(
            name="split_grid",
            description="网格分屏（四分屏）。将1-4个窗口排列成2x2网格。窗口按顺序排列：左上、右上、左下、右下。",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "窗口ID列表（最多4个），按左上、右上、左下、右下的顺序排列",
                        "minItems": 1,
                        "maxItems": 4,
                    },
                },
                "required": ["window_ids"],
            },
        ),
        Tool(
            name="maximize_window",
            description="最大化指定窗口，使其占据整个屏幕。支持Linux系统（需要wmctrl）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "window_id": {
                        "type": "string",
                        "description": "要最大化的窗口ID",
                    },
                },
                "required": ["window_id"],
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    tool = get_tool()
    
    try:
        if name == "list_windows":
            result = tool.list_windows()
            return [TextContent(type="text", text=format_list_windows_result(result))]
        
        elif name == "get_screen_size":
            result = tool.get_screen_size()
            return [TextContent(type="text", text=format_screen_size_result(result))]
        
        elif name == "get_active_window":
            result = tool.get_active_window()
            return [TextContent(type="text", text=format_active_window_result(result))]
        
        elif name == "move_window":
            window_id = arguments.get("window_id")
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            
            result = tool.move_window(window_id, x, y, width, height)
            return [TextContent(type="text", text=format_move_window_result(result))]
        
        elif name == "split_horizontal":
            window_ids = arguments.get("window_ids", [])
            result = tool.split_windows_horizontal(window_ids)
            return [TextContent(type="text", text=format_split_result(result, "水平分屏"))]
        
        elif name == "split_vertical":
            window_ids = arguments.get("window_ids", [])
            result = tool.split_windows_vertical(window_ids)
            return [TextContent(type="text", text=format_split_result(result, "垂直分屏"))]
        
        elif name == "split_grid":
            window_ids = arguments.get("window_ids", [])
            result = tool.split_windows_grid(window_ids)
            return [TextContent(type="text", text=format_split_result(result, "网格分屏"))]
        
        elif name == "maximize_window":
            window_id = arguments.get("window_id")
            result = tool.maximize_window(window_id)
            return [TextContent(type="text", text=format_maximize_result(result))]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ 未知的工具: {name}"
            )]
    
    except Exception as e:
        import traceback
        return [TextContent(
            type="text",
            text=f"❌ 工具调用异常: {str(e)}\n\n{traceback.format_exc()}"
        )]


def format_list_windows_result(result: dict) -> str:
    """格式化窗口列表结果"""
    if not result.get("success"):
        return f"""❌ 获取窗口列表失败

错误信息: {result.get('error', '未知错误')}

💡 提示:
- 在Linux系统上需要安装wmctrl: sudo apt install wmctrl
- 确保在图形界面环境中运行
"""
    
    windows = result.get("windows", [])
    count = result.get("count", 0)
    
    if count == 0:
        return "📋 当前没有打开的窗口"
    
    text = f"""✅ 成功获取窗口列表

📊 统计信息:
  - 窗口总数: {count}
  - 检测方法: {result.get('method', 'unknown')}

📋 窗口列表:
"""
    
    for i, win in enumerate(windows, 1):
        text += f"""
{i}. {win['title'][:60]}
   ID: {win['id']}
   位置: ({win['x']}, {win['y']})
   大小: {win['width']} x {win['height']}"""
        # desktop字段可能不存在（例如在Windows后端）
        if 'desktop' in win:
            text += f"""
   桌面: {win['desktop']}"""
        text += "\n"
    
    return text


def format_screen_size_result(result: dict) -> str:
    """格式化屏幕尺寸结果"""
    if not result.get("success"):
        return f"""❌ 获取屏幕尺寸失败

错误信息: {result.get('error', '未知错误')}
"""
    
    return f"""✅ 屏幕尺寸信息

📐 尺寸:
  - 宽度: {result['width']} 像素
  - 高度: {result['height']} 像素
  - 检测方法: {result.get('method', 'unknown')}
"""


def format_active_window_result(result: dict) -> str:
    """格式化活动窗口结果"""
    if not result.get("success"):
        return f"""❌ 获取活动窗口失败

错误信息: {result.get('error', '未知错误')}

💡 提示:
- 在Linux系统上需要安装xdotool: sudo apt install xdotool
"""
    
    return f"""✅ 活动窗口信息

🪟 窗口详情:
  - 标题: {result['title']}
  - ID (十六进制): {result['window_id']}
  - ID (十进制): {result['window_id_decimal']}
  - 检测方法: {result.get('method', 'unknown')}
"""


def format_move_window_result(result: dict) -> str:
    """格式化移动窗口结果"""
    if not result.get("success"):
        return f"""❌ 移动窗口失败

错误信息: {result.get('error', '未知错误')}
"""
    
    pos = result.get('position', {})
    size = result.get('size', {})
    
    return f"""✅ 窗口移动成功

🪟 窗口信息:
  - 窗口ID: {result['window_id']}
  - 新位置: ({pos.get('x')}, {pos.get('y')})
  - 新大小: {size.get('width')} x {size.get('height')}
  - 操作方法: {result.get('method', 'unknown')}
"""


def format_split_result(result: dict, layout_name: str) -> str:
    """格式化分屏结果"""
    if not result.get("success"):
        return f"""❌ {layout_name}失败

错误信息: {result.get('error', '未知错误')}
"""
    
    screen_size = result.get('screen_size', {})
    windows = result.get('windows', [])
    
    text = f"""✅ {layout_name}成功

📐 屏幕尺寸: {screen_size.get('width')} x {screen_size.get('height')}
📊 布局类型: {result.get('layout', 'unknown')}
🪟 处理窗口数: {len(windows)}

窗口详情:
"""
    
    for i, win in enumerate(windows, 1):
        if win.get('success'):
            pos = win.get('position', {})
            size = win.get('size', {})
            text += f"""
{i}. 窗口ID: {win['window_id']}
   位置: ({pos.get('x')}, {pos.get('y')})
   大小: {size.get('width')} x {size.get('height')}
   状态: ✅ 成功
"""
        else:
            text += f"""
{i}. 窗口ID: {win.get('window_id', 'unknown')}
   状态: ❌ 失败
   错误: {win.get('error', '未知错误')}
"""
    
    return text


def format_maximize_result(result: dict) -> str:
    """格式化最大化窗口结果"""
    if not result.get("success"):
        return f"""❌ 最大化窗口失败

错误信息: {result.get('error', '未知错误')}
"""
    
    return f"""✅ 窗口最大化成功

🪟 窗口信息:
  - 窗口ID: {result['window_id']}
  - 操作: {result['action']}
  - 方法: {result.get('method', 'unknown')}
"""


async def main():
    """主函数"""
    # 使用stdio传输运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="window-split-mcp-server",
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
        print("\n服务器已停止", file=sys.stderr)
    except Exception as e:
        print(f"服务器错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
