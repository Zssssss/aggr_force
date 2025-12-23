"""
打开钉钉 MCP 工具包
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "MCP 工具：打开钉钉应用"

from .open_dingtalk_tools import open_dingtalk, check_dingtalk_installed

__all__ = [
    "open_dingtalk",
    "check_dingtalk_installed",
]
