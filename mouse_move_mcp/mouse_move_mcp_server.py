#!/usr/bin/env python3
"""
Mouse Move MCP Server - 集成截屏、图像分析和鼠标移动的MCP服务器

这个MCP服务器提供鼠标位置获取和移动功能。
截屏和图像读取功能应该通过调用已有的screenshot MCP工具来实现。
图像分析（找到鼠标位置和目标位置）由调用此MCP的AI助手完成。
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

# 添加MCP SDK路径
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("错误: 未找到MCP SDK。请安装: pip install mcp", file=sys.stderr)
    sys.exit(1)

# 导入工具函数
from mouse_move_tools import (
    get_mouse_position_tool,
    move_mouse_tool,
    calculate_distance_tool
)


# 创建MCP服务器实例
server = Server("mouse-move-mcp")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    列出所有可用的工具
    """
    return [
        Tool(
            name="get_mouse_position",
            description="获取当前鼠标在屏幕上的位置坐标",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="move_mouse",
            description="移动鼠标到屏幕上的指定位置",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "目标位置的X坐标（像素）"
                    },
                    "y": {
                        "type": "integer",
                        "description": "目标位置的Y坐标（像素）"
                    }
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="calculate_distance",
            description="计算两个屏幕坐标点之间的欧几里得距离",
            inputSchema={
                "type": "object",
                "properties": {
                    "x1": {
                        "type": "integer",
                        "description": "第一个点的X坐标"
                    },
                    "y1": {
                        "type": "integer",
                        "description": "第一个点的Y坐标"
                    },
                    "x2": {
                        "type": "integer",
                        "description": "第二个点的X坐标"
                    },
                    "y2": {
                        "type": "integer",
                        "description": "第二个点的Y坐标"
                    }
                },
                "required": ["x1", "y1", "x2", "y2"]
            }
        ),
        Tool(
            name="move_to_target_with_verification",
            description="""智能移动鼠标到目标位置并验证。
            
这是一个高级工具，用于自动化鼠标移动流程：
1. AI助手首先调用screenshot MCP工具截取屏幕
2. AI助手读取截屏图片（使用screenshot MCP的read_screenshot工具）
3. AI助手分析图片，找到当前鼠标位置和目标文本位置
4. AI助手调用此工具，提供目标坐标
5. 此工具会循环执行：获取当前位置→计算距离→移动鼠标→验证，直到到达目标

使用流程示例：
- 步骤1: 调用 mcp-screenshot.capture_screen() 截屏
- 步骤2: 调用 mcp-screenshot.read_screenshot() 读取图片
- 步骤3: AI分析图片，确定目标位置坐标
- 步骤4: 调用此工具 move_to_target_with_verification(target_x, target_y)
- 步骤5: 如果未到达，重复步骤1-4""",
            inputSchema={
                "type": "object",
                "properties": {
                    "target_x": {
                        "type": "integer",
                        "description": "目标位置的X坐标（像素）"
                    },
                    "target_y": {
                        "type": "integer",
                        "description": "目标位置的Y坐标（像素）"
                    },
                    "tolerance": {
                        "type": "integer",
                        "description": "允许的误差范围（像素），默认为10",
                        "default": 10
                    }
                },
                "required": ["target_x", "target_y"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    处理工具调用请求
    """
    try:
        if name == "get_mouse_position":
            result = get_mouse_position_tool()
            
            return [
                TextContent(
                    type="text",
                    text=f"鼠标位置:\n{format_result(result)}"
                )
            ]
        
        elif name == "move_mouse":
            x = arguments.get("x")
            y = arguments.get("y")
            
            if x is None or y is None:
                return [
                    TextContent(
                        type="text",
                        text="错误: 必须提供x和y坐标"
                    )
                ]
            
            result = move_mouse_tool(int(x), int(y))
            
            return [
                TextContent(
                    type="text",
                    text=f"移动鼠标结果:\n{format_result(result)}"
                )
            ]
        
        elif name == "calculate_distance":
            x1 = arguments.get("x1")
            y1 = arguments.get("y1")
            x2 = arguments.get("x2")
            y2 = arguments.get("y2")
            
            if None in [x1, y1, x2, y2]:
                return [
                    TextContent(
                        type="text",
                        text="错误: 必须提供x1, y1, x2, y2四个坐标"
                    )
                ]
            
            result = calculate_distance_tool(int(x1), int(y1), int(x2), int(y2))
            
            return [
                TextContent(
                    type="text",
                    text=f"距离计算结果:\n{format_result(result)}"
                )
            ]
        
        elif name == "move_to_target_with_verification":
            target_x = arguments.get("target_x")
            target_y = arguments.get("target_y")
            tolerance = arguments.get("tolerance", 10)
            
            if target_x is None or target_y is None:
                return [
                    TextContent(
                        type="text",
                        text="错误: 必须提供target_x和target_y坐标"
                    )
                ]
            
            # 获取当前鼠标位置
            current_pos = get_mouse_position_tool()
            if not current_pos.get("success"):
                return [
                    TextContent(
                        type="text",
                        text=f"错误: 无法获取当前鼠标位置\n{format_result(current_pos)}"
                    )
                ]
            
            current_x = current_pos.get("x")
            current_y = current_pos.get("y")
            
            # 计算距离
            distance_result = calculate_distance_tool(
                current_x, current_y,
                int(target_x), int(target_y)
            )
            distance = distance_result.get("distance")
            
            # 检查是否已在目标位置
            if distance <= tolerance:
                return [
                    TextContent(
                        type="text",
                        text=f"鼠标已在目标位置附近\n当前位置: ({current_x}, {current_y})\n目标位置: ({target_x}, {target_y})\n距离: {distance:.2f}px (容差: {tolerance}px)"
                    )
                ]
            
            # 移动鼠标
            move_result = move_mouse_tool(int(target_x), int(target_y))
            
            if not move_result.get("success"):
                return [
                    TextContent(
                        type="text",
                        text=f"移动鼠标失败:\n{format_result(move_result)}"
                    )
                ]
            
            # 验证移动后的位置
            new_pos = get_mouse_position_tool()
            if new_pos.get("success"):
                new_x = new_pos.get("x")
                new_y = new_pos.get("y")
                new_distance = calculate_distance_tool(
                    new_x, new_y,
                    int(target_x), int(target_y)
                ).get("distance")
                
                success = new_distance <= tolerance
                
                return [
                    TextContent(
                        type="text",
                        text=f"""移动鼠标并验证结果:
状态: {'成功' if success else '需要继续调整'}
原始位置: ({current_x}, {current_y})
目标位置: ({target_x}, {target_y})
当前位置: ({new_x}, {new_y})
原始距离: {distance:.2f}px
当前距离: {new_distance:.2f}px
容差范围: {tolerance}px

{'鼠标已到达目标位置' if success else '建议: 重新截屏并再次调用此工具以继续调整位置'}"""
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"鼠标已移动，但无法验证新位置:\n{format_result(move_result)}"
                    )
                ]
        
        else:
            return [
                TextContent(
                    type="text",
                    text=f"错误: 未知的工具名称: {name}"
                )
            ]
    
    except Exception as e:
        import traceback
        return [
            TextContent(
                type="text",
                text=f"工具调用异常: {str(e)}\n{traceback.format_exc()}"
            )
        ]


def format_result(result: dict) -> str:
    """
    格式化结果字典为可读的字符串
    """
    import json
    return json.dumps(result, ensure_ascii=False, indent=2)


async def main():
    """
    主函数：启动MCP服务器
    """
    # 使用stdio传输运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mouse-move-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
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
