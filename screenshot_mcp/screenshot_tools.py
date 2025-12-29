"""截屏工具模块 - 提供跨平台截屏功能，支持多显示器"""

import datetime
import os
import sys
import platform
import subprocess
import base64
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image


class ScreenshotTool:
    """截屏工具类"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化截屏工具
        
        Args:
            output_dir: 截图保存目录，默认为当前模块所在目录
        """
        # 获取当前模块的绝对路径
        module_dir = Path(__file__).resolve().parent
        
        if output_dir is None:
            self.output_dir = module_dir
        else:
            self.output_dir = Path(output_dir).resolve()
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # PowerShell脚本路径（使用绝对路径）
        self.ps_script_path = module_dir / "take_screenshot.ps1"
        
        # 检查系统环境
        self.system = platform.system()
        self.is_wsl = self._check_wsl()
    
    def _check_wsl(self) -> bool:
        """检查是否在WSL环境"""
        if self.system == "Linux":
            try:
                with open("/proc/version", "r") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        return True
            except:
                pass
        return False
    
    def _run_powershell(self, script: str) -> str:
        """
        执行PowerShell脚本
        
        Args:
            script: PowerShell脚本内容
            
        Returns:
            脚本执行结果
        """
        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", script],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                try:
                    error_msg = result.stderr.decode('gbk', errors='ignore').strip()
                except:
                    error_msg = result.stderr.decode('utf-8', errors='ignore').strip()
                raise RuntimeError(f"PowerShell执行失败: {error_msg}")
            
            # 尝试使用GBK解码，失败则使用UTF-8
            try:
                output = result.stdout.decode('gbk', errors='ignore').strip()
            except:
                output = result.stdout.decode('utf-8', errors='ignore').strip()
            
            return output
        except subprocess.TimeoutExpired:
            raise RuntimeError("PowerShell执行超时")
        except Exception as e:
            raise RuntimeError(f"执行PowerShell时出错: {str(e)}")
    
    def get_monitors_info(self) -> List[Dict[str, Any]]:
        """
        获取所有显示器信息
        
        Returns:
            显示器信息列表，每个显示器包含：
            - MonitorNumber: 显示器编号（从1开始）
            - IsPrimary: 是否为主显示器
            - Left: 左边界坐标
            - Top: 上边界坐标
            - Width: 宽度
            - Height: 高度
            - Right: 右边界坐标
            - Bottom: 下边界坐标
        """
        # 只在WSL或Windows环境下支持PowerShell方式
        if not (self.is_wsl or self.system == "Windows"):
            # 对于Linux/macOS，使用mss库获取显示器信息
            try:
                import mss
                with mss.mss() as sct:
                    monitors = []
                    for i, monitor in enumerate(sct.monitors[1:], 1):  # 跳过第一个（所有显示器的组合）
                        monitors.append({
                            "MonitorNumber": i,
                            "IsPrimary": i == 1,  # 假设第一个是主显示器
                            "Left": monitor["left"],
                            "Top": monitor["top"],
                            "Width": monitor["width"],
                            "Height": monitor["height"],
                            "Right": monitor["left"] + monitor["width"],
                            "Bottom": monitor["top"] + monitor["height"]
                        })
                    return monitors
            except Exception as e:
                raise RuntimeError(f"获取显示器信息失败: {e}")
        
        # WSL/Windows环境使用PowerShell
        script = """
Add-Type -AssemblyName System.Windows.Forms
$monitors = [System.Windows.Forms.Screen]::AllScreens
$result = @()
$index = 1
foreach ($monitor in $monitors) {
    $info = @{
        MonitorNumber = $index
        IsPrimary = $monitor.Primary
        Left = $monitor.Bounds.Left
        Top = $monitor.Bounds.Top
        Width = $monitor.Bounds.Width
        Height = $monitor.Bounds.Height
        Right = $monitor.Bounds.Right
        Bottom = $monitor.Bounds.Bottom
    }
    $result += $info
    $index++
}
$result | ConvertTo-Json
"""
        try:
            output = self._run_powershell(script)
            monitors = json.loads(output)
            
            # 确保返回的是列表
            if isinstance(monitors, dict):
                monitors = [monitors]
            
            return monitors
        except json.JSONDecodeError as e:
            raise RuntimeError(f"解析显示器信息失败: {str(e)}")
    
    def take_screenshot(self, filename: Optional[str] = None, monitor_number: Optional[int] = None) -> Dict[str, Any]:
        """
        截取屏幕
        
        Args:
            filename: 自定义文件名（不含路径），如果为None则自动生成时间戳文件名
            monitor_number: 显示器编号（从1开始），如果为None则截取所有显示器
            
        Returns:
            包含截图信息的字典，包括文件路径、尺寸等信息
        """
        # 生成文件名
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if monitor_number:
                filename = f"screenshot_monitor{monitor_number}_{timestamp}.png"
            else:
                filename = f"screenshot_{timestamp}.png"
        
        # 确保文件名以.png结尾
        if not filename.endswith('.png'):
            filename += '.png'
            
        filepath = self.output_dir / filename
        
        try:
            # 如果指定了显示器编号，使用专门的方法
            if monitor_number is not None:
                result = self._take_screenshot_monitor(filepath, monitor_number)
            else:
                result = self._take_screenshot_all(filepath)
            
            # 获取图片信息
            if filepath.exists():
                with Image.open(filepath) as img:
                    result.update({
                        "filename": filename,
                        "filepath": str(filepath.absolute()),
                        "format": img.format,
                        "size": img.size,
                        "width": img.size[0],
                        "height": img.size[1],
                        "mode": img.mode,
                        "success": True,
                        "monitor_number": monitor_number
                    })
                return result
            else:
                raise RuntimeError("截图文件未生成")
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "system": platform.system()
            }
    
    def _take_screenshot_all(self, filepath: Path) -> Dict[str, Any]:
        """
        截取所有显示器（全屏）
        """
        # 检查是否在WSL环境
        if self.is_wsl:
            if not self.ps_script_path.exists():
                raise RuntimeError(f"找不到PowerShell脚本: {self.ps_script_path}")
            
            # 在当前目录执行PowerShell脚本
            script_dir = self.ps_script_path.parent
            result = subprocess.run(
                ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(self.ps_script_path)],
                capture_output=True,
                text=True,
                cwd=str(script_dir)
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"PowerShell截图失败: {result.stderr}")
            
            # 查找当前目录中生成的截图文件
            screenshots = list(script_dir.glob("screenshot_*.png"))
            if not screenshots:
                raise RuntimeError("PowerShell脚本执行成功但未找到截图文件")
            
            # 获取最新的截图文件
            latest_screenshot = max(screenshots, key=lambda p: p.stat().st_mtime)
            
            # 移动到目标位置
            import shutil
            shutil.move(str(latest_screenshot), str(filepath))
            
            return {"method": "powershell_wsl"}
        
        # 原生Linux环境：使用mss库
        elif self.system == "Linux":
            try:
                import mss
                with mss.mss() as sct:
                    sct.shot(output=str(filepath))
                return {"method": "mss"}
            except Exception as e:
                raise RuntimeError(f"Linux截图失败: {e}. 提示: 需要X服务器或安装scrot")
        
        # Windows原生环境
        elif self.system == "Windows":
            try:
                import mss
                with mss.mss() as sct:
                    sct.shot(output=str(filepath))
                return {"method": "mss"}
            except ImportError:
                raise RuntimeError("需要安装mss库: pip install mss")
        
        # macOS环境
        elif self.system == "Darwin":
            try:
                subprocess.run(
                    ["screencapture", "-x", str(filepath)],
                    check=True,
                    capture_output=True
                )
                return {"method": "screencapture"}
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"macOS截图失败: {e}")
        
        else:
            raise RuntimeError(f"不支持的操作系统: {self.system}")
    
    def _take_screenshot_monitor(self, filepath: Path, monitor_number: int) -> Dict[str, Any]:
        """
        截取指定显示器
        
        Args:
            filepath: 保存路径
            monitor_number: 显示器编号（从1开始）
        """
        # 获取显示器信息
        monitors = self.get_monitors_info()
        
        if monitor_number < 1 or monitor_number > len(monitors):
            raise RuntimeError(f"显示器编号 {monitor_number} 无效，当前有 {len(monitors)} 个显示器")
        
        monitor_info = monitors[monitor_number - 1]
        
        # WSL或Windows环境使用PowerShell
        if self.is_wsl or self.system == "Windows":
            script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$monitors = [System.Windows.Forms.Screen]::AllScreens
$monitor = $monitors[{monitor_number - 1}]

$bounds = $monitor.Bounds
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

$graphics.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bounds.Size)

$bitmap.Save("{str(filepath).replace(chr(92), chr(92)*2)}", [System.Drawing.Imaging.ImageFormat]::Png)

$graphics.Dispose()
$bitmap.Dispose()

Write-Output "success"
"""
            try:
                output = self._run_powershell(script)
                if "success" in output:
                    return {"method": "powershell_monitor"}
                else:
                    raise RuntimeError(f"截取显示器失败: {output}")
            except Exception as e:
                raise RuntimeError(f"PowerShell截取显示器失败: {str(e)}")
        
        # Linux/macOS使用mss库
        else:
            try:
                import mss
                with mss.mss() as sct:
                    # mss的monitors列表：[0]是所有显示器，[1]开始是各个显示器
                    monitor = sct.monitors[monitor_number]
                    screenshot = sct.grab(monitor)
                    mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filepath))
                return {"method": "mss_monitor"}
            except Exception as e:
                raise RuntimeError(f"截取显示器失败: {e}")
    
    def take_screenshot_base64(self, filename: Optional[str] = None, monitor_number: Optional[int] = None) -> Dict[str, Any]:
        """
        截取屏幕并返回base64编码的图片数据
        
        Args:
            filename: 自定义文件名（不含路径），如果为None则自动生成时间戳文件名
            monitor_number: 显示器编号（从1开始），如果为None则截取所有显示器
            
        Returns:
            包含截图信息和base64数据的字典
        """
        result = self.take_screenshot(filename, monitor_number)
        
        if result.get("success"):
            filepath = result["filepath"]
            with open(filepath, "rb") as f:
                image_data = f.read()
                result["base64"] = base64.b64encode(image_data).decode("utf-8")
                result["size_bytes"] = len(image_data)
        
        return result


def take_screenshot_simple(output_dir: Optional[str] = None, 
                          filename: Optional[str] = None,
                          monitor_number: Optional[int] = None) -> Dict[str, Any]:
    """
    简单的截屏函数接口
    
    Args:
        output_dir: 截图保存目录
        filename: 自定义文件名
        monitor_number: 显示器编号（从1开始），如果为None则截取所有显示器
        
    Returns:
        包含截图信息的字典
    """
    tool = ScreenshotTool(output_dir)
    return tool.take_screenshot(filename, monitor_number)


def get_monitors_info_simple() -> List[Dict[str, Any]]:
    """
    获取显示器信息的简单接口
    
    Returns:
        显示器信息列表
    """
    tool = ScreenshotTool()
    return tool.get_monitors_info()


if __name__ == "__main__":
    # 测试代码
    print("=== 测试获取显示器信息 ===")
    try:
        monitors = get_monitors_info_simple()
        print(f"检测到 {len(monitors)} 个显示器:")
        for monitor in monitors:
            print(f"  显示器 {monitor['MonitorNumber']}: {monitor['Width']}x{monitor['Height']}", end="")
            if monitor['IsPrimary']:
                print(" (主显示器)", end="")
            print()
    except Exception as e:
        print(f"获取显示器信息失败: {e}")
    
    print("\n=== 测试截取全屏 ===")
    result = take_screenshot_simple()
    if result.get("success"):
        print(f"截图成功!")
        print(f"文件路径: {result['filepath']}")
        print(f"图片尺寸: {result['width']} x {result['height']}")
        print(f"图片格式: {result['format']}")
    else:
        print(f"截图失败: {result.get('error')}")
    
    print("\n=== 测试截取第一个显示器 ===")
    result = take_screenshot_simple(monitor_number=1)
    if result.get("success"):
        print(f"截图成功!")
        print(f"文件路径: {result['filepath']}")
        print(f"图片尺寸: {result['width']} x {result['height']}")
    else:
        print(f"截图失败: {result.get('error')}")
