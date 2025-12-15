"""
人类操作模拟 MCP 模块
模拟人类对电脑的各种操作动作
"""

from .human_op_server import create_server
from .human_op_tools import HumanOpTools

__all__ = ["create_server", "HumanOpTools"]