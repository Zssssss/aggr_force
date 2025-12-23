"""鼠标位置获取工具模块 - 提供跨平台鼠标位置获取功能
"""

import platform
import subprocess
from typing import Dict, Any, Optional


class MousePositionTool:
    """鼠标位置获取工具类"""
    
    def __init__(self):
        """初始化鼠标位置工具"""
        self.system = platform.system()
        self.is_wsl = self._check_wsl()
    
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
    
    def get_mouse_position(self) -> Dict[str, Any]:
        """
        获取当前鼠标位置
        
        Returns:
            包含鼠标位置信息的字典，包括x、y坐标等信息
        """
        try:
            if self.is_wsl:
                # WSL环境：使用PowerShell获取鼠标位置
                return self._get_position_wsl()
            elif self.system == "Linux":
                # 原生Linux环境：使用xdotool或Python库
                return self._get_position_linux()
            elif self.system == "Windows":
                # Windows环境：使用Python库
                return self._get_position_windows()
            elif self.system == "Darwin":
                # macOS环境：使用Python库
                return self._get_position_macos()
            else:
                return {
                    "success": False,
                    "error": f"不支持的操作系统: {self.system}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "system": self.system
            }
    
    def _get_position_wsl(self) -> Dict[str, Any]:
        """在WSL环境中使用PowerShell获取鼠标位置"""
        ps_command = """
Add-Type -AssemblyName System.Windows.Forms
$pos = [System.Windows.Forms.Cursor]::Position
Write-Output "$($pos.X),$($pos.Y)"
"""
        
        result = subprocess.run(
            ["powershell.exe", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"PowerShell执行失败: {result.stderr}")
        
        output = result.stdout.strip()
        x, y = map(int, output.split(','))
        
        return {
            "success": True,
            "x": x,
            "y": y,
            "method": "powershell_wsl",
            "system": "WSL"
        }
    
    def _get_position_linux(self) -> Dict[str, Any]:
        """在原生Linux环境中获取鼠标位置"""
        # 方法1: 尝试使用PyAutoGUI
        try:
            import pyautogui
            x, y = pyautogui.position()
            return {
                "success": True,
                "x": x,
                "y": y,
                "method": "pyautogui",
                "system": "Linux"
            }
        except ImportError:
            pass
        
        # 方法2: 尝试使用xdotool命令
        try:
            result = subprocess.run(
                ["xdotool", "getmouselocation", "--shell"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout
                x = None
                y = None
                for line in output.split('\n'):
                    if line.startswith('X='):
                        x = int(line.split('=')[1])
                    elif line.startswith('Y='):
                        y = int(line.split('=')[1])
                
                if x is not None and y is not None:
                    return {
                        "success": True,
                        "x": x,
                        "y": y,
                        "method": "xdotool",
                        "system": "Linux"
                    }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # 方法3: 尝试使用pynput
        try:
            from pynput import mouse
            controller = mouse.Controller()
            x, y = controller.position
            return {
                "success": True,
                "x": x,
                "y": y,
                "method": "pynput",
                "system": "Linux"
            }
        except ImportError:
            pass
        
        raise RuntimeError(
            "无法获取鼠标位置。请安装以下工具之一:\n"
            "- pip install pyautogui\n"
            "- pip install pynput\n"
            "- sudo apt install xdotool"
        )
    
    def _get_position_windows(self) -> Dict[str, Any]:
        """在Windows环境中获取鼠标位置"""
        # 方法1: 尝试使用PyAutoGUI
        try:
            import pyautogui
            x, y = pyautogui.position()
            return {
                "success": True,
                "x": x,
                "y": y,
                "method": "pyautogui",
                "system": "Windows"
            }
        except ImportError:
            pass
        
        # 方法2: 尝试使用pynput
        try:
            from pynput import mouse
            controller = mouse.Controller()
            x, y = controller.position
            return {
                "success": True,
                "x": x,
                "y": y,
                "method": "pynput",
                "system": "Windows"
            }
        except ImportError:
            pass
        
        # 方法3: 使用win32api
        try:
            import win32api
            x, y = win32api.GetCursorPos()
            return {
                "success": True,
                "x": x,
                "y": y,
                "method": "win32api",
                "system": "Windows"
            }
        except ImportError:
            pass
        
        raise RuntimeError(
            "无法获取鼠标位置。请安装以下库之一:\n"
            "- pip install pyautogui\n"
            "- pip install pynput\n"
            "- pip install pywin32"
        )
    
    def _get_position_macos(self) -> Dict[str, Any]:
        """在macOS环境中获取鼠标位置"""
        # 方法1: 尝试使用PyAutoGUI
        try:
            import pyautogui
            x, y = pyautogui.position()
            return {
                "success": True,
                "x": x,
                "y": y,
                "method": "pyautogui",
                "system": "macOS"
            }
        except ImportError:
            pass
        
        # 方法2: 尝试使用pynput
        try:
            from pynput import mouse
            controller = mouse.Controller()
            x, y = controller.position
            return {
                "success": True,
                "x": x,
                "y": y,
                "method": "pynput",
                "system": "macOS"
            }
        except ImportError:
            pass
        
        # 方法3: 使用Quartz (PyObjC)
        try:
            from Quartz import CGEventGetLocation, CGEventCreate
            from Quartz.CoreGraphics import kCGEventMouseMoved
            
            event = CGEventCreate(None)
            location = CGEventGetLocation(event)
            x, y = int(location.x), int(location.y)
            
            return {
                "success": True,
                "x": x,
                "y": y,
                "method": "quartz",
                "system": "macOS"
            }
        except ImportError:
            pass
        
        raise RuntimeError(
            "无法获取鼠标位置。请安装以下库之一:\n"
            "- pip install pyautogui\n"
            "- pip install pynput\n"
            "- pip install pyobjc-framework-Quartz"
        )


def get_mouse_position_simple() -> Dict[str, Any]:
    """
    简单的鼠标位置获取函数接口
    
    Returns:
        包含鼠标位置信息的字典
    """
    tool = MousePositionTool()
    return tool.get_mouse_position()


if __name__ == "__main__":
    # 测试代码
    result = get_mouse_position_simple()
    if result.get("success"):
        print(f"鼠标位置获取成功!")
        print(f"X坐标: {result['x']}")
        print(f"Y坐标: {result['y']}")
        print(f"获取方法: {result['method']}")
        print(f"操作系统: {result['system']}")
    else:
        print(f"鼠标位置获取失败: {result.get('error')}")
