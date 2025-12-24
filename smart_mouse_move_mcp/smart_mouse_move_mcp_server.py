#!/usr/bin/env python3
"""
智能鼠标移动 MCP 服务器

封装完整的工作流程：
1. 截取屏幕
2. 读取图片供AI分析
3. AI识别目标位置
4. 移动鼠标到目标位置
5. 验证是否到达
6. 如未到达，重复上述步骤
"""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl

from smart_mouse_move_tools import SmartMouseMoveTools

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("smart-mouse-move-mcp")

# 创建MCP服务器实例
app = Server("smart-mouse-move")

# 创建工具实例
tools = SmartMouseMoveTools()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="smart_move_to_target",
            description=(
                "智能移动鼠标到目标位置的完整工作流。"
                "此工具会：1) 截取当前屏幕，2) 返回截图供AI分析，"
                "3) AI需要分析图片找到目标位置并调用execute_move_to_coordinates。"
                "这是工作流的第一步。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "target_description": {
                        "type": "string",
                        "description": "目标位置的描述，例如：'屏幕右上角的关闭按钮'、'搜索框'等"
                    },
                    "max_attempts": {
                        "type": "integer",
                        "description": "最大尝试次数（可选，默认5次）",
                        "default": 5
                    },
                    "tolerance": {
                        "type": "integer",
                        "description": "位置容差，单位像素（可选，默认10）",
                        "default": 10
                    }
                },
                "required": ["target_description"]
            }
        ),
        Tool(
            name="execute_move_to_coordinates",
            description=(
                "执行移动鼠标到指定坐标并验证。"
                "这是在AI分析截图并确定目标坐标后调用的工具。"
                "会移动鼠标并验证是否到达目标位置。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "target_x": {
                        "type": "integer",
                        "description": "目标X坐标"
                    },
                    "target_y": {
                        "type": "integer",
                        "description": "目标Y坐标"
                    },
                    "tolerance": {
                        "type": "integer",
                        "description": "位置容差，单位像素（可选，默认10）",
                        "default": 10
                    },
                    "verify": {
                        "type": "boolean",
                        "description": "是否验证移动结果（可选，默认true）",
                        "default": True
                    }
                },
                "required": ["target_x", "target_y"]
            }
        ),
        Tool(
            name="verify_position_with_screenshot",
            description=(
                "截图并验证当前鼠标位置是否到达预期位置。"
                "如果未到达，返回新的截图供AI重新分析。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "expected_x": {
                        "type": "integer",
                        "description": "期望的X坐标"
                    },
                    "expected_y": {
                        "type": "integer",
                        "description": "期望的Y坐标"
                    },
                    "tolerance": {
                        "type": "integer",
                        "description": "位置容差，单位像素（可选，默认10）",
                        "default": 10
                    }
                },
                "required": ["expected_x", "expected_y"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """处理工具调用"""
    try:
        if name == "smart_move_to_target":
            # 开始智能移动工作流
            target_description = arguments.get("target_description")
            max_attempts = arguments.get("max_attempts")
            tolerance = arguments.get("tolerance")
            
            result = tools.smart_move_to_target(
                target_description=target_description,
                max_attempts=max_attempts,
                tolerance=tolerance
            )
            
            if not result.get("success"):
                return [
                    TextContent(
                        type="text",
                        text=f"错误: {result.get('error')}\n步骤: {result.get('step')}"
                    )
                ]
            
            # 返回截图和当前状态
            response_parts = [
                TextContent(
                    type="text",
                    text=(
                        f"✅ 截图已准备好\n\n"
                        f"目标描述: {result['target_description']}\n"
                        f"当前鼠标位置: ({result['current_mouse_position']['x']}, "
                        f"{result['current_mouse_position']['y']})\n"
                        f"截图路径: {result['screenshot_path']}\n\n"
                        f"📋 下一步操作:\n"
                        f"{result['instructions']}\n\n"
                        f"请分析下方的截图，找到'{target_description}'的坐标位置。"
                    )
                )
            ]
            
            # 添加截图
            if result.get("screenshot_base64"):
                response_parts.append(
                    ImageContent(
                        type="image",
                        data=result["screenshot_base64"],
                        mimeType="image/png"
                    )
                )
            
            return response_parts
        
        elif name == "execute_move_to_coordinates":
            # 执行移动到坐标
            target_x = arguments.get("target_x")
            target_y = arguments.get("target_y")
            tolerance = arguments.get("tolerance")
            verify = arguments.get("verify", True)
            
            result = tools.execute_move_to_coordinates(
                target_x=target_x,
                target_y=target_y,
                tolerance=tolerance,
                verify=verify
            )
            
            if not result.get("success"):
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"❌ {result.get('message', '移动失败')}\n\n"
                            f"错误: {result.get('error', '未知错误')}\n\n"
                            f"建议: {result.get('suggestion', '请重试')}"
                        )
                    )
                ]
            
            # 成功移动
            text_response = f"✅ {result['message']}\n\n"
            text_response += f"移动前位置: ({result['before_position']['x']}, {result['before_position']['y']})\n"
            text_response += f"移动后位置: ({result['after_position']['x']}, {result['after_position']['y']})\n"
            text_response += f"目标位置: ({result['target_position']['x']}, {result['target_position']['y']})\n"
            text_response += f"距离目标: {result['distance_to_target']} 像素\n"
            text_response += f"容差范围: {result['tolerance']} 像素"
            
            return [TextContent(type="text", text=text_response)]
        
        elif name == "verify_position_with_screenshot":
            # 验证位置并截图
            expected_x = arguments.get("expected_x")
            expected_y = arguments.get("expected_y")
            tolerance = arguments.get("tolerance")
            
            result = tools.verify_position_with_screenshot(
                expected_x=expected_x,
                expected_y=expected_y,
                tolerance=tolerance
            )
            
            if not result.get("success"):
                return [
                    TextContent(
                        type="text",
                        text=f"错误: {result.get('error')}"
                    )
                ]
            
            # 构建响应
            status_icon = "✅" if result["reached_target"] else "❌"
            text_response = f"{status_icon} {result['message']}\n\n"
            text_response += f"当前位置: ({result['current_position']['x']}, {result['current_position']['y']})\n"
            text_response += f"期望位置: ({result['expected_position']['x']}, {result['expected_position']['y']})\n"
            text_response += f"距离: {result['distance']} 像素\n"
            text_response += f"容差: {result['tolerance']} 像素\n"
            text_response += f"截图路径: {result['screenshot_path']}"
            
            response_parts = [TextContent(type="text", text=text_response)]
            
            # 添加截图
            if result.get("screenshot_base64"):
                response_parts.append(
                    ImageContent(
                        type="image",
                        data=result["screenshot_base64"],
                        mimeType="image/png"
                    )
                )
            
            return response_parts
        
        else:
            return [
                TextContent(
                    type="text",
                    text=f"未知工具: {name}"
                )
            ]
    
    except Exception as e:
        logger.error(f"工具调用错误: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"工具执行出错: {str(e)}"
            )
        ]


async def main():
    """主函数"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("智能鼠标移动 MCP 服务器已启动")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
