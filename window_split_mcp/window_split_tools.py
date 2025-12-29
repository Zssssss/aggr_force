"""窗口分屏工具模块 - 提供跨平台窗口分屏功能

支持的功能：
1. 获取当前活动窗口列表
2. 将窗口移动到屏幕的指定位置和大小
3. 预设分屏布局（左右分屏、上下分屏、四分屏等）
4. 自动排列多个窗口
5. WSL环境下管理Windows原生窗口
"""

import subprocess
import platform
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class WindowInfo:
    """窗口信息数据类"""
    window_id: str
    title: str
    x: int
    y: int
    width: int
    height: int
    desktop: int = 0


class WindowSplitTool:
    """窗口分屏工具类 - 自动检测环境并选择合适的后端"""
    
    def __init__(self):
        """初始化窗口分屏工具"""
        self.system = platform.system()
        self.is_wsl = self._check_wsl()
        
        # 如果在WSL环境，使用Windows窗口管理器
        if self.is_wsl:
            try:
                from windows_window_manager import WindowsWindowManager
                self.backend = WindowsWindowManager()
                self.backend_type = "windows"
            except Exception as e:
                print(f"警告: 无法加载Windows窗口管理器: {e}")
                self.backend = None
                self.backend_type = "none"
        else:
            self.backend = None
            self.backend_type = "linux"
            self._check_dependencies()
    
    def _check_wsl(self) -> bool:
        """检查是否在WSL环境中"""
        if self.system != "Linux":
            return False
        try:
            with open("/proc/version", "r") as f:
                version_info = f.read().lower()
                return "microsoft" in version_info or "wsl" in version_info
        except:
            return False
    
    def _check_dependencies(self):
        """检查系统依赖"""
        if self.system == "Linux":
            # 检查是否有wmctrl
            try:
                subprocess.run(["wmctrl", "-v"], 
                             capture_output=True, 
                             check=True)
                self.has_wmctrl = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.has_wmctrl = False
            
            # 检查是否有xdotool
            try:
                subprocess.run(["xdotool", "--version"], 
                             capture_output=True, 
                             check=True)
                self.has_xdotool = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.has_xdotool = False
        else:
            self.has_wmctrl = False
            self.has_xdotool = False
    
    def get_screen_size(self) -> Dict[str, Any]:
        """
        获取屏幕尺寸
        
        Returns:
            包含屏幕宽度和高度的字典
        """
        # 如果是WSL环境且有Windows后端，使用Windows后端
        if self.is_wsl and self.backend:
            return self.backend.get_screen_size()
        
        try:
            if self.system == "Linux":
                # 使用xdpyinfo获取屏幕尺寸
                result = subprocess.run(
                    ["xdpyinfo"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # 解析输出
                for line in result.stdout.split('\n'):
                    if 'dimensions:' in line:
                        # 格式: dimensions:    1920x1080 pixels (508x285 millimeters)
                        match = re.search(r'(\d+)x(\d+) pixels', line)
                        if match:
                            width = int(match.group(1))
                            height = int(match.group(2))
                            return {
                                "success": True,
                                "width": width,
                                "height": height,
                                "method": "xdpyinfo"
                            }
            
            elif self.system == "Windows":
                # Windows使用ctypes获取屏幕尺寸
                import ctypes
                user32 = ctypes.windll.user32
                width = user32.GetSystemMetrics(0)
                height = user32.GetSystemMetrics(1)
                return {
                    "success": True,
                    "width": width,
                    "height": height,
                    "method": "ctypes"
                }
            
            elif self.system == "Darwin":
                # macOS使用system_profiler
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                # 简化处理，返回常见分辨率
                return {
                    "success": True,
                    "width": 1920,
                    "height": 1080,
                    "method": "system_profiler",
                    "note": "使用默认分辨率"
                }
            
            return {
                "success": False,
                "error": f"不支持的操作系统: {self.system}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_windows(self) -> Dict[str, Any]:
        """
        列出所有窗口
        
        Returns:
            包含窗口列表的字典
        """
        # 如果是WSL环境且有Windows后端，使用Windows后端
        if self.is_wsl and self.backend:
            return self.backend.list_windows()
        
        try:
            if self.system == "Linux":
                if not self.has_wmctrl:
                    return {
                        "success": False,
                        "error": "需要安装wmctrl: sudo apt install wmctrl"
                    }
                
                # 使用wmctrl列出窗口
                result = subprocess.run(
                    ["wmctrl", "-lG"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                windows = []
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    
                    # 格式: 0x03400006  0 1920 0    1920 1080 hostname Window Title
                    parts = line.split(None, 7)
                    if len(parts) >= 8:
                        window = WindowInfo(
                            window_id=parts[0],
                            desktop=int(parts[1]),
                            x=int(parts[2]),
                            y=int(parts[3]),
                            width=int(parts[4]),
                            height=int(parts[5]),
                            title=parts[7]
                        )
                        windows.append({
                            "id": window.window_id,
                            "title": window.title,
                            "x": window.x,
                            "y": window.y,
                            "width": window.width,
                            "height": window.height,
                            "desktop": window.desktop
                        })
                
                return {
                    "success": True,
                    "windows": windows,
                    "count": len(windows),
                    "method": "wmctrl"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"暂不支持 {self.system} 系统"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def move_window(self, window_id: str, x: int, y: int,
                   width: int, height: int) -> Dict[str, Any]:
        """
        移动和调整窗口大小
        
        Args:
            window_id: 窗口ID
            x: X坐标
            y: Y坐标
            width: 宽度
            height: 高度
            
        Returns:
            操作结果字典
        """
        # 如果是WSL环境且有Windows后端，使用Windows后端
        if self.is_wsl and self.backend:
            return self.backend.move_window(window_id, x, y, width, height)
        
        try:
            if self.system == "Linux":
                if not self.has_wmctrl:
                    return {
                        "success": False,
                        "error": "需要安装wmctrl: sudo apt install wmctrl"
                    }
                
                # 使用wmctrl移动窗口
                # 格式: wmctrl -i -r <window_id> -e 0,x,y,width,height
                result = subprocess.run(
                    ["wmctrl", "-i", "-r", window_id, "-e", 
                     f"0,{x},{y},{width},{height}"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                return {
                    "success": True,
                    "window_id": window_id,
                    "position": {"x": x, "y": y},
                    "size": {"width": width, "height": height},
                    "method": "wmctrl"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"暂不支持 {self.system} 系统"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def split_windows_horizontal(self, window_ids: List[str]) -> Dict[str, Any]:
        """
        水平分屏（左右分屏）
        
        Args:
            window_ids: 窗口ID列表（最多2个）
            
        Returns:
            操作结果字典
        """
        # 如果是WSL环境且有Windows后端，使用Windows后端
        if self.is_wsl and self.backend:
            return self.backend.split_windows_horizontal(window_ids)
        
        try:
            if len(window_ids) == 0:
                return {
                    "success": False,
                    "error": "至少需要提供一个窗口ID"
                }
            
            if len(window_ids) > 2:
                return {
                    "success": False,
                    "error": "水平分屏最多支持2个窗口"
                }
            
            # 获取屏幕尺寸
            screen = self.get_screen_size()
            if not screen.get("success"):
                return screen
            
            screen_width = screen["width"]
            screen_height = screen["height"]
            
            results = []
            
            if len(window_ids) == 1:
                # 单个窗口，占据左半屏
                result = self.move_window(
                    window_ids[0],
                    0, 0,
                    screen_width // 2, screen_height
                )
                results.append(result)
            else:
                # 两个窗口，左右分屏
                # 左窗口
                result1 = self.move_window(
                    window_ids[0],
                    0, 0,
                    screen_width // 2, screen_height
                )
                results.append(result1)
                
                # 右窗口
                result2 = self.move_window(
                    window_ids[1],
                    screen_width // 2, 0,
                    screen_width // 2, screen_height
                )
                results.append(result2)
            
            success = all(r.get("success") for r in results)
            
            return {
                "success": success,
                "layout": "horizontal",
                "screen_size": {"width": screen_width, "height": screen_height},
                "windows": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def split_windows_vertical(self, window_ids: List[str]) -> Dict[str, Any]:
        """
        垂直分屏（上下分屏）
        
        Args:
            window_ids: 窗口ID列表（最多2个）
            
        Returns:
            操作结果字典
        """
        # 如果是WSL环境且有Windows后端，使用Windows后端
        if self.is_wsl and self.backend:
            return self.backend.split_windows_vertical(window_ids)
        
        try:
            if len(window_ids) == 0:
                return {
                    "success": False,
                    "error": "至少需要提供一个窗口ID"
                }
            
            if len(window_ids) > 2:
                return {
                    "success": False,
                    "error": "垂直分屏最多支持2个窗口"
                }
            
            # 获取屏幕尺寸
            screen = self.get_screen_size()
            if not screen.get("success"):
                return screen
            
            screen_width = screen["width"]
            screen_height = screen["height"]
            
            results = []
            
            if len(window_ids) == 1:
                # 单个窗口，占据上半屏
                result = self.move_window(
                    window_ids[0],
                    0, 0,
                    screen_width, screen_height // 2
                )
                results.append(result)
            else:
                # 两个窗口，上下分屏
                # 上窗口
                result1 = self.move_window(
                    window_ids[0],
                    0, 0,
                    screen_width, screen_height // 2
                )
                results.append(result1)
                
                # 下窗口
                result2 = self.move_window(
                    window_ids[1],
                    0, screen_height // 2,
                    screen_width, screen_height // 2
                )
                results.append(result2)
            
            success = all(r.get("success") for r in results)
            
            return {
                "success": success,
                "layout": "vertical",
                "screen_size": {"width": screen_width, "height": screen_height},
                "windows": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def split_windows_grid(self, window_ids: List[str]) -> Dict[str, Any]:
        """
        网格分屏（四分屏）
        
        Args:
            window_ids: 窗口ID列表（最多4个）
            
        Returns:
            操作结果字典
        """
        # 如果是WSL环境且有Windows后端，使用Windows后端
        if self.is_wsl and self.backend:
            return self.backend.split_windows_grid(window_ids)
        
        try:
            if len(window_ids) == 0:
                return {
                    "success": False,
                    "error": "至少需要提供一个窗口ID"
                }
            
            if len(window_ids) > 4:
                return {
                    "success": False,
                    "error": "网格分屏最多支持4个窗口"
                }
            
            # 获取屏幕尺寸
            screen = self.get_screen_size()
            if not screen.get("success"):
                return screen
            
            screen_width = screen["width"]
            screen_height = screen["height"]
            
            half_width = screen_width // 2
            half_height = screen_height // 2
            
            # 定义四个位置
            positions = [
                (0, 0, half_width, half_height),  # 左上
                (half_width, 0, half_width, half_height),  # 右上
                (0, half_height, half_width, half_height),  # 左下
                (half_width, half_height, half_width, half_height),  # 右下
            ]
            
            results = []
            for i, window_id in enumerate(window_ids):
                x, y, w, h = positions[i]
                result = self.move_window(window_id, x, y, w, h)
                results.append(result)
            
            success = all(r.get("success") for r in results)
            
            return {
                "success": success,
                "layout": "grid",
                "screen_size": {"width": screen_width, "height": screen_height},
                "windows": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def maximize_window(self, window_id: str) -> Dict[str, Any]:
        """
        最大化窗口
        
        Args:
            window_id: 窗口ID
            
        Returns:
            操作结果字典
        """
        # 如果是WSL环境且有Windows后端，使用Windows后端
        if self.is_wsl and self.backend:
            return self.backend.maximize_window(window_id)
        
        try:
            if self.system == "Linux":
                if not self.has_wmctrl:
                    return {
                        "success": False,
                        "error": "需要安装wmctrl: sudo apt install wmctrl"
                    }
                
                # 使用wmctrl最大化窗口
                result = subprocess.run(
                    ["wmctrl", "-i", "-r", window_id, "-b", "add,maximized_vert,maximized_horz"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                return {
                    "success": True,
                    "window_id": window_id,
                    "action": "maximize",
                    "method": "wmctrl"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"暂不支持 {self.system} 系统"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_active_window(self) -> Dict[str, Any]:
        """
        获取当前活动窗口
        
        Returns:
            包含活动窗口信息的字典
        """
        # 如果是WSL环境且有Windows后端，使用Windows后端
        if self.is_wsl and self.backend:
            return self.backend.get_active_window()
        
        try:
            if self.system == "Linux":
                if not self.has_xdotool:
                    return {
                        "success": False,
                        "error": "需要安装xdotool: sudo apt install xdotool"
                    }
                
                # 使用xdotool获取活动窗口ID
                result = subprocess.run(
                    ["xdotool", "getactivewindow"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                window_id = result.stdout.strip()
                
                # 转换为wmctrl格式的ID
                window_id_hex = hex(int(window_id))
                
                # 获取窗口信息
                result = subprocess.run(
                    ["xdotool", "getwindowname", window_id],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                window_title = result.stdout.strip()
                
                return {
                    "success": True,
                    "window_id": window_id_hex,
                    "window_id_decimal": window_id,
                    "title": window_title,
                    "method": "xdotool"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"暂不支持 {self.system} 系统"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 便捷函数
def list_windows_simple() -> Dict[str, Any]:
    """简单的列出窗口函数"""
    tool = WindowSplitTool()
    return tool.list_windows()


def split_horizontal_simple(window_ids: List[str]) -> Dict[str, Any]:
    """简单的水平分屏函数"""
    tool = WindowSplitTool()
    return tool.split_windows_horizontal(window_ids)


def split_vertical_simple(window_ids: List[str]) -> Dict[str, Any]:
    """简单的垂直分屏函数"""
    tool = WindowSplitTool()
    return tool.split_windows_vertical(window_ids)


def split_grid_simple(window_ids: List[str]) -> Dict[str, Any]:
    """简单的网格分屏函数"""
    tool = WindowSplitTool()
    return tool.split_windows_grid(window_ids)


if __name__ == "__main__":
    # 测试代码
    tool = WindowSplitTool()
    
    print("=== 测试窗口分屏工具 ===\n")
    
    # 测试获取屏幕尺寸
    print("1. 获取屏幕尺寸:")
    screen = tool.get_screen_size()
    print(f"   结果: {screen}\n")
    
    # 测试列出窗口
    print("2. 列出所有窗口:")
    windows = tool.list_windows()
    if windows.get("success"):
        print(f"   找到 {windows['count']} 个窗口")
        for i, win in enumerate(windows['windows'][:3], 1):
            print(f"   {i}. {win['title'][:50]} (ID: {win['id']})")
    else:
        print(f"   错误: {windows.get('error')}")
    
    # 测试获取活动窗口
    print("\n3. 获取活动窗口:")
    active = tool.get_active_window()
    print(f"   结果: {active}")
