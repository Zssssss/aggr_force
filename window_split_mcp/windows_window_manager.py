"""Windows窗口分屏工具模块 - WSL环境专用
通过PowerShell管理Windows原生窗口
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class WindowsWindowManager:
    """Windows窗口管理类 - 通过PowerShell在WSL中管理Windows窗口"""
    
    def __init__(self):
        """初始化Windows窗口管理器"""
        self.module_dir = Path(__file__).resolve().parent
        self.ps_module = self.module_dir / "WindowManager.psm1"
        
        if not self.ps_module.exists():
            raise FileNotFoundError(f"找不到PowerShell模块: {self.ps_module}")
        
        # 读取PowerShell模块内容
        with open(self.ps_module, 'r', encoding='utf-8') as f:
            self.ps_module_content = f.read()
    
    def _run_powershell(self, command: str) -> Dict[str, Any]:
        """
        运行PowerShell命令
        
        Args:
            command: PowerShell命令
            
        Returns:
            命令执行结果
        """
        try:
            # 构建完整的PowerShell命令，直接包含模块内容
            full_command = f"""
{self.ps_module_content}

{command}
"""
            
            # 在WSL中调用PowerShell，使用UTF-8编码
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", full_command],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',  # 忽略编码错误
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"PowerShell执行失败: {result.stderr}"
                }
            
            return {
                "success": True,
                "output": result.stdout.strip()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "PowerShell命令超时"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_screen_size(self) -> Dict[str, Any]:
        """
        获取屏幕尺寸
        
        Returns:
            包含屏幕宽度和高度的字典
        """
        command = "Get-ScreenSize | ConvertTo-Json"
        result = self._run_powershell(command)
        
        if not result.get("success"):
            return result
        
        try:
            data = json.loads(result["output"])
            return {
                "success": True,
                "width": data["Width"],
                "height": data["Height"],
                "method": "powershell_wsl"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"解析屏幕尺寸失败: {e}"
            }
    
    def list_windows(self) -> Dict[str, Any]:
        """
        列出所有Windows窗口
        
        Returns:
            包含窗口列表的字典
        """
        command = "Get-AllWindows | ConvertTo-Json"
        result = self._run_powershell(command)
        
        if not result.get("success"):
            return result
        
        try:
            output = result["output"]
            if not output or output == "":
                return {
                    "success": True,
                    "windows": [],
                    "count": 0,
                    "method": "powershell_wsl"
                }
            
            data = json.loads(output)
            
            # 处理单个窗口的情况（PowerShell返回对象而非数组）
            if isinstance(data, dict):
                data = [data]
            
            windows = []
            for win in data:
                windows.append({
                    "id": str(win["Handle"]),
                    "title": win["Title"],
                    "x": win["X"],
                    "y": win["Y"],
                    "width": win["Width"],
                    "height": win["Height"]
                })
            
            return {
                "success": True,
                "windows": windows,
                "count": len(windows),
                "method": "powershell_wsl"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"解析窗口列表失败: {e}, 输出: {result.get('output', '')[:200]}"
            }
    
    def get_active_window(self) -> Dict[str, Any]:
        """
        获取当前活动窗口
        
        Returns:
            包含活动窗口信息的字典
        """
        command = "Get-ActiveWindow | ConvertTo-Json"
        result = self._run_powershell(command)
        
        if not result.get("success"):
            return result
        
        try:
            output = result["output"]
            if not output or output == "null":
                return {
                    "success": False,
                    "error": "没有活动窗口"
                }
            
            data = json.loads(output)
            
            return {
                "success": True,
                "window_id": str(data["Handle"]),
                "title": data["Title"],
                "x": data["X"],
                "y": data["Y"],
                "width": data["Width"],
                "height": data["Height"],
                "method": "powershell_wsl"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"解析活动窗口失败: {e}"
            }
    
    def move_window(self, window_id: str, x: int, y: int, 
                   width: int, height: int) -> Dict[str, Any]:
        """
        移动和调整窗口大小
        
        Args:
            window_id: 窗口ID（Handle）
            x: X坐标
            y: Y坐标
            width: 宽度
            height: 高度
            
        Returns:
            操作结果字典
        """
        command = f"Move-WindowToPosition -Handle {window_id} -X {x} -Y {y} -Width {width} -Height {height}"
        result = self._run_powershell(command)
        
        if not result.get("success"):
            return result
        
        # PowerShell返回True/False
        success = result["output"].strip().lower() == "true"
        
        if success:
            return {
                "success": True,
                "window_id": window_id,
                "position": {"x": x, "y": y},
                "size": {"width": width, "height": height},
                "method": "powershell_wsl"
            }
        else:
            return {
                "success": False,
                "error": "移动窗口失败"
            }
    
    def maximize_window(self, window_id: str) -> Dict[str, Any]:
        """
        最大化窗口
        
        Args:
            window_id: 窗口ID
            
        Returns:
            操作结果字典
        """
        command = f"Maximize-WindowByHandle -Handle {window_id}"
        result = self._run_powershell(command)
        
        if not result.get("success"):
            return result
        
        success = result["output"].strip().lower() == "true"
        
        if success:
            return {
                "success": True,
                "window_id": window_id,
                "action": "maximize",
                "method": "powershell_wsl"
            }
        else:
            return {
                "success": False,
                "error": "最大化窗口失败"
            }
    
    def split_windows_horizontal(self, window_ids: List[str]) -> Dict[str, Any]:
        """
        水平分屏（左右分屏）
        
        Args:
            window_ids: 窗口ID列表（最多2个）
            
        Returns:
            操作结果字典
        """
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
            result1 = self.move_window(
                window_ids[0],
                0, 0,
                screen_width // 2, screen_height
            )
            results.append(result1)
            
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
    
    def split_windows_vertical(self, window_ids: List[str]) -> Dict[str, Any]:
        """
        垂直分屏（上下分屏）
        
        Args:
            window_ids: 窗口ID列表（最多2个）
            
        Returns:
            操作结果字典
        """
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
            result1 = self.move_window(
                window_ids[0],
                0, 0,
                screen_width, screen_height // 2
            )
            results.append(result1)
            
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
    
    def split_windows_grid(self, window_ids: List[str]) -> Dict[str, Any]:
        """
        网格分屏（四分屏）
        
        Args:
            window_ids: 窗口ID列表（最多4个）
            
        Returns:
            操作结果字典
        """
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


if __name__ == "__main__":
    # 测试代码
    manager = WindowsWindowManager()
    
    print("=== 测试Windows窗口管理工具 ===\n")
    
    # 测试获取屏幕尺寸
    print("1. 获取屏幕尺寸:")
    screen = manager.get_screen_size()
    print(f"   结果: {screen}\n")
    
    # 测试列出窗口
    print("2. 列出所有窗口:")
    windows = manager.list_windows()
    if windows.get("success"):
        print(f"   找到 {windows['count']} 个窗口")
        for i, win in enumerate(windows['windows'][:3], 1):
            print(f"   {i}. {win['title'][:50]} (ID: {win['id']})")
    else:
        print(f"   错误: {windows.get('error')}")
    
    # 测试获取活动窗口
    print("\n3. 获取活动窗口:")
    active = manager.get_active_window()
    print(f"   结果: {active}")
