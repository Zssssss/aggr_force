"""
Mouse Move MCP Tools - 集成截屏、图像分析和鼠标移动功能
"""

import os
import sys
import subprocess
import base64
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
import json

# 导入鼠标位置工具
sys.path.append(str(Path(__file__).parent.parent / "get_mouse_position_mcp"))
from mouse_position_tools import get_mouse_position


class MouseMoveTools:
    """集成截屏、图像分析和鼠标移动的工具类"""
    
    def __init__(self):
        self.screenshot_dir = Path.home() / "screenshot_mcp"
        self.screenshot_dir.mkdir(exist_ok=True)
        self.last_screenshot_path = None
        self.last_screenshot_base64 = None
    
    def get_current_mouse_position(self) -> Dict[str, Any]:
        """
        获取当前鼠标位置
        
        Returns:
            包含鼠标坐标的字典
        """
        try:
            result = get_mouse_position()
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"获取鼠标位置异常: {str(e)}"
            }
    
    def move_mouse_to_position(self, x: int, y: int) -> Dict[str, Any]:
        """
        移动鼠标到指定位置
        
        Args:
            x: 目标X坐标
            y: 目标Y坐标
            
        Returns:
            移动结果
        """
        try:
            # 检测操作系统
            if sys.platform.startswith('linux'):
                # Linux系统使用xdotool
                result = subprocess.run(
                    ['xdotool', 'mousemove', str(x), str(y)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "x": x,
                        "y": y,
                        "message": f"鼠标已移动到位置 ({x}, {y})"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"移动鼠标失败: {result.stderr}"
                    }
            
            elif sys.platform == 'darwin':
                # macOS系统使用AppleScript
                script = f'''
                tell application "System Events"
                    set mousePosition to {{{x}, {y}}}
                end tell
                '''
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "x": x,
                        "y": y,
                        "message": f"鼠标已移动到位置 ({x}, {y})"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"移动鼠标失败: {result.stderr}"
                    }
            
            elif sys.platform == 'win32':
                # Windows系统使用PowerShell
                ps_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x}, {y})
                '''
                result = subprocess.run(
                    ['powershell', '-Command', ps_script],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "x": x,
                        "y": y,
                        "message": f"鼠标已移动到位置 ({x}, {y})"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"移动鼠标失败: {result.stderr}"
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"不支持的操作系统: {sys.platform}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "移动鼠标超时"
            }
        except FileNotFoundError as e:
            return {
                "success": False,
                "error": f"未找到必要的系统工具: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"移动鼠标异常: {str(e)}"
            }
    
    def calculate_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        计算两点之间的距离
        
        Args:
            x1, y1: 第一个点的坐标
            x2, y2: 第二个点的坐标
            
        Returns:
            两点之间的欧几里得距离
        """
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


# 创建全局工具实例
_tools_instance = MouseMoveTools()


def get_mouse_position_tool() -> Dict[str, Any]:
    """获取当前鼠标位置的MCP工具函数"""
    return _tools_instance.get_current_mouse_position()


def move_mouse_tool(x: int, y: int) -> Dict[str, Any]:
    """移动鼠标到指定位置的MCP工具函数"""
    return _tools_instance.move_mouse_to_position(x, y)


def calculate_distance_tool(x1: int, y1: int, x2: int, y2: int) -> Dict[str, Any]:
    """计算两点之间距离的MCP工具函数"""
    distance = _tools_instance.calculate_distance(x1, y1, x2, y2)
    return {
        "success": True,
        "distance": distance,
        "point1": {"x": x1, "y": y1},
        "point2": {"x": x2, "y": y2},
        "message": f"两点之间的距离: {distance:.2f}px"
    }
