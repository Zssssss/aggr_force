"""Window Split MCP - 窗口分屏管理工具

这个MCP服务器提供窗口分屏和管理功能，支持：
- 列出所有窗口
- 获取屏幕尺寸
- 移动和调整窗口
- 多种分屏布局（水平、垂直、网格）
- 窗口最大化

主要支持Linux系统（需要wmctrl和xdotool）
"""

__version__ = "1.0.0"
__author__ = "Window Split MCP Team"

from .window_split_tools import (
    WindowSplitTool,
    WindowInfo,
    list_windows_simple,
    split_horizontal_simple,
    split_vertical_simple,
    split_grid_simple,
)

__all__ = [
    "WindowSplitTool",
    "WindowInfo",
    "list_windows_simple",
    "split_horizontal_simple",
    "split_vertical_simple",
    "split_grid_simple",
]
