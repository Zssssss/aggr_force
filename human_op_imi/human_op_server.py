"""
人类操作模拟 MCP 服务器入口
负责注册工具并运行 MCP 服务器。
"""

import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from .human_op_tools import HumanOpTools


def create_server() -> Server:
    """
    创建并配置 MCP 服务器。
    
    Returns:
        Server: MCP 服务器实例
    """
    # 创建人类操作模拟工具
    human_op_tools = HumanOpTools()
    
    # 创建 MCP 服务器
    server = Server("human-op-simulator")
    
    # 注册工具
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="mouse_click",
                description="模拟鼠标点击操作",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "鼠标点击的 X 坐标"},
                        "y": {"type": "integer", "description": "鼠标点击的 Y 坐标"},
                        "button": {
                            "type": "string", 
                            "description": "点击的鼠标按钮 (left/right/middle)",
                            "enum": ["left", "right", "middle"],
                            "default": "left"
                        },
                        "double_click": {"type": "boolean", "description": "是否为双击", "default": False}
                    },
                    "required": ["x", "y"],
                },
            ),
            Tool(
                name="mouse_move",
                description="模拟鼠标移动操作",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "目标 X 坐标"},
                        "y": {"type": "integer", "description": "目标 Y 坐标"},
                        "duration": {"type": "number", "description": "移动持续时间 (秒)", "default": 0.5}
                    },
                    "required": ["x", "y"],
                },
            ),
            Tool(
                name="keyboard_type",
                description="模拟键盘输入操作",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "要输入的文本"},
                        "speed": {"type": "number", "description": "按键间隔时间 (秒)", "default": 0.1}
                    },
                    "required": ["text"],
                },
            ),
            Tool(
                name="keyboard_press",
                description="模拟键盘按键操作",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "要按下的键 (如: Enter, Ctrl, Alt, Shift)"},
                        "modifier": {"type": "string", "description": "修饰键 (如: Ctrl, Alt, Shift)"}
                    },
                    "required": ["key"],
                },
            ),
            Tool(
                name="clipboard_copy",
                description="模拟复制到剪贴板操作",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "要复制的内容"}
                    },
                    "required": ["content"],
                },
            ),
            Tool(
                name="clipboard_paste",
                description="模拟从剪贴板粘贴操作",
                inputSchema={},
            ),
            Tool(
                name="window_switch",
                description="模拟窗口切换操作",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "window_title": {"type": "string", "description": "目标窗口标题"}
                    },
                    "required": ["window_title"],
                },
            ),
            Tool(
                name="get_simulation_state",
                description="获取当前模拟环境状态",
                inputSchema={},
            ),
            Tool(
                name="screenshot",
                description="模拟全局截图操作",
                inputSchema={},
            ),
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "mouse_click":
            result = await human_op_tools.mouse_click_tool(
                x=arguments["x"],
                y=arguments["y"],
                button=arguments.get("button", "left"),
                double_click=arguments.get("double_click", False)
            )
        elif name == "mouse_move":
            result = await human_op_tools.mouse_move_tool(
                x=arguments["x"],
                y=arguments["y"],
                duration=arguments.get("duration", 0.5)
            )
        elif name == "keyboard_type":
            result = await human_op_tools.keyboard_type_tool(
                text=arguments["text"],
                speed=arguments.get("speed", 0.1)
            )
        elif name == "keyboard_press":
            result = await human_op_tools.keyboard_press_tool(
                key=arguments["key"],
                modifier=arguments.get("modifier")
            )
        elif name == "clipboard_copy":
            result = await human_op_tools.clipboard_copy_tool(
                content=arguments["content"]
            )
        elif name == "clipboard_paste":
            result = await human_op_tools.clipboard_paste_tool()
        elif name == "window_switch":
            result = await human_op_tools.window_switch_tool(
                window_title=arguments["window_title"]
            )
        elif name == "get_simulation_state":
            result = await human_op_tools.get_simulation_state_tool()
        elif name == "screenshot":
            result = await human_op_tools.screenshot_tool()
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