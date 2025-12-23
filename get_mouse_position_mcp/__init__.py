"""Mouse Position MCP Server - 获取鼠标位置的 MCP 服务器

这个包提供了一个 MCP 服务器,用于获取当前鼠标在屏幕上的坐标位置。
支持 Windows、Linux、macOS 和 WSL 环境。
"""

from .mouse_position_tools import MousePositionTool, get_mouse_position_simple

__version__ = "1.0.0"
__all__ = ["MousePositionTool", "get_mouse_position_simple"]
