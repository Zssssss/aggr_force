"""截屏工具模块 - 提供跨平台截屏功能
直接使用screen_op目录下已验证的截图代码
"""

import datetime
import os
import sys
import platform
import subprocess
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image


class ScreenshotTool:
    """截屏工具类"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化截屏工具
        
        Args:
            output_dir: 截图保存目录，默认为当前模块所在目录
        """
        if output_dir is None:
            self.output_dir = Path(__file__).parent
        else:
            self.output_dir = Path(output_dir)
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # screen_op目录路径
        self.screen_op_dir = Path(__file__).parent.parent / "screen_op"
        
    def take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        截取当前全屏 - 直接调用screen_op中的截图功能
        
        Args:
            filename: 自定义文件名（不含路径），如果为None则自动生成时间戳文件名
            
        Returns:
            包含截图信息的字典，包括文件路径、尺寸等信息
        """
        # 生成文件名
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # 确保文件名以.png结尾
        if not filename.endswith('.png'):
            filename += '.png'
            
        filepath = self.output_dir / filename
        
        try:
            # 直接使用screen_op中的截图方法
            result = self._take_screenshot_from_screen_op(filepath)
            
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
                        "success": True
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
    
    def _take_screenshot_from_screen_op(self, filepath: Path) -> Dict[str, Any]:
        """
        使用screen_op目录中的截图方法
        参考: screen_op/take_screenshot.py 和 take_screenshot.ps1
        """
        system = platform.system()
        
        # 检查是否在WSL环境
        is_wsl = False
        if system == "Linux":
            try:
                with open("/proc/version", "r") as f:
                    version_info = f.read().lower()
                    if "microsoft" in version_info or "wsl" in version_info:
                        is_wsl = True
            except:
                pass
        
        # WSL环境：使用PowerShell脚本
        if is_wsl:
            ps_script = self.screen_op_dir / "take_screenshot.ps1"
            if not ps_script.exists():
                raise RuntimeError(f"找不到PowerShell脚本: {ps_script}")
            
            # 转换WSL路径到Windows路径
            wsl_output_dir = str(self.output_dir.absolute())
            
            # 在screen_op目录执行PowerShell脚本
            result = subprocess.run(
                ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)],
                capture_output=True,
                text=True,
                cwd=str(self.screen_op_dir)
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"PowerShell截图失败: {result.stderr}")
            
            # 查找screen_op目录中生成的截图文件
            screenshots = list(self.screen_op_dir.glob("screenshot_*.png"))
            if not screenshots:
                raise RuntimeError("PowerShell脚本执行成功但未找到截图文件")
            
            # 获取最新的截图文件
            latest_screenshot = max(screenshots, key=lambda p: p.stat().st_mtime)
            
            # 移动到目标位置
            import shutil
            shutil.move(str(latest_screenshot), str(filepath))
            
            return {"method": "powershell_wsl"}
        
        # 原生Linux环境：使用mss库（参考screen_op/take_screenshot.py）
        elif system == "Linux":
            try:
                import mss
                with mss.mss() as sct:
                    sct.shot(output=str(filepath))
                return {"method": "mss"}
            except Exception as e:
                raise RuntimeError(f"Linux截图失败: {e}. 提示: 需要X服务器或安装scrot")
        
        # Windows原生环境
        elif system == "Windows":
            try:
                import mss
                with mss.mss() as sct:
                    sct.shot(output=str(filepath))
                return {"method": "mss"}
            except ImportError:
                raise RuntimeError("需要安装mss库: pip install mss")
        
        # macOS环境
        elif system == "Darwin":
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
            raise RuntimeError(f"不支持的操作系统: {system}")
    
    def take_screenshot_base64(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        截取当前全屏并返回base64编码的图片数据
        
        Args:
            filename: 自定义文件名（不含路径），如果为None则自动生成时间戳文件名
            
        Returns:
            包含截图信息和base64数据的字典
        """
        result = self.take_screenshot(filename)
        
        if result.get("success"):
            filepath = result["filepath"]
            with open(filepath, "rb") as f:
                image_data = f.read()
                result["base64"] = base64.b64encode(image_data).decode("utf-8")
                result["size_bytes"] = len(image_data)
        
        return result


def take_screenshot_simple(output_dir: Optional[str] = None, 
                          filename: Optional[str] = None) -> Dict[str, Any]:
    """
    简单的截屏函数接口
    
    Args:
        output_dir: 截图保存目录
        filename: 自定义文件名
        
    Returns:
        包含截图信息的字典
    """
    tool = ScreenshotTool(output_dir)
    return tool.take_screenshot(filename)


if __name__ == "__main__":
    # 测试代码
    result = take_screenshot_simple()
    if result.get("success"):
        print(f"截图成功!")
        print(f"文件路径: {result['filepath']}")
        print(f"图片尺寸: {result['width']} x {result['height']}")
        print(f"图片格式: {result['format']}")
    else:
        print(f"截图失败: {result.get('error')}")
