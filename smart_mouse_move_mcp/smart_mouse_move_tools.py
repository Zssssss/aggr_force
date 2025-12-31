"""
智能鼠标移动工具
封装完整的工作流程:截屏 -> 分析 -> 移动 -> 验证
复用已有的 screenshot_mcp 和 mouse_move_mcp 工具
"""
import sys
import time
import subprocess
import platform
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# 配置日志，避免使用print输出到stdout干扰MCP协议
logger = logging.getLogger("smart-mouse-move-tools")

# 导入已有的工具
sys.path.append(str(Path(__file__).parent.parent / "screenshot_mcp"))
sys.path.append(str(Path(__file__).parent.parent / "mouse_move_mcp"))

from screenshot_tools import ScreenshotTool
from mouse_move_tools import MouseMoveTools as MouseTools


class SmartMouseMoveTools:
    """智能鼠标移动工具类 - 复用已有的MCP工具"""
    
    def __init__(self):
        """初始化工具"""
        # 设置截图输出目录
        screenshot_dir = Path.home() / "screenshot_mcp"
        screenshot_dir.mkdir(exist_ok=True)
        
        # 使用已有的截图工具，指定输出目录
        self.screenshot_tool = ScreenshotTool(output_dir=str(screenshot_dir))
        # 使用已有的鼠标移动工具
        self.mouse_tool = MouseTools()
        
        self.max_attempts = 5  # 最大尝试次数
        self.tolerance = 10  # 位置容差（像素）
        
        # 检查是否在WSL环境
        self.is_wsl = self._check_wsl()
        
        # 获取DPI缩放信息
        self.dpi_scale = self._get_dpi_scale()
    
    def _check_wsl(self) -> bool:
        """检查是否在WSL环境"""
        if platform.system() != "Linux":
            return False
        try:
            with open("/proc/version", "r") as f:
                version_info = f.read().lower()
                return "microsoft" in version_info or "wsl" in version_info
        except:
            return False
    
    def _convert_wsl_path_to_windows(self, wsl_path: str) -> str:
        """
        将WSL路径转换为Windows路径
        
        Args:
            wsl_path: WSL格式的路径
            
        Returns:
            Windows格式的路径
        """
        try:
            result = subprocess.run(
                ["wslpath", "-w", wsl_path],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"路径转换失败: {e}")
        return wsl_path
    
    def _get_dpi_scale(self) -> Tuple[float, float]:
        """
        获取DPI缩放比例
        
        Returns:
            (scale_x, scale_y) 缩放比例元组
        """
        if not self.is_wsl and platform.system() != "Windows":
            return (1.0, 1.0)
        
        try:
            # 检查是否有预先准备的PowerShell脚本文件
            script_path = Path(__file__).parent / "get_dpi_info.ps1"
            
            if script_path.exists():
                # 在WSL环境下，需要转换路径
                if self.is_wsl:
                    windows_script_path = self._convert_wsl_path_to_windows(str(script_path))
                else:
                    windows_script_path = str(script_path)
                
                # 使用脚本文件方式执行，更稳定
                # 在WSL中不使用creationflags参数
                cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-NoProfile", "-File", windows_script_path]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=15  # 增加超时时间到15秒
                )
            else:
                # 使用简化的内联命令，避免复杂的C#代码导致超时
                ps_script = 'Write-Output "96,96"'
                
                result = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
            
            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                # 处理可能的多行输出，只取最后一行
                lines = output.split('\n')
                for line in reversed(lines):
                    line = line.strip()
                    if ',' in line and not line.startswith('#'):
                        try:
                            dpi_x, dpi_y = map(int, line.split(','))
                            scale_x = dpi_x / 96.0
                            scale_y = dpi_y / 96.0
                            logger.debug(f"DPI信息: {dpi_x}x{dpi_y}, 缩放比例: {scale_x}x{scale_y}")
                            return (scale_x, scale_y)
                        except ValueError:
                            continue
                logger.debug(f"解析DPI输出失败: {output}")
        except subprocess.TimeoutExpired:
            logger.debug("获取DPI信息超时，使用默认缩放1.0")
        except Exception as e:
            logger.debug(f"获取DPI信息失败: {e}, 使用默认缩放1.0")
        
        return (1.0, 1.0)
    
    def _get_monitor_info(self) -> Dict[str, Any]:
        """
        获取显示器信息
        
        Returns:
            包含显示器信息的字典
        """
        try:
            monitors = self.screenshot_tool.get_monitors_info()
            return {
                "success": True,
                "monitors": monitors,
                "count": len(monitors)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        
    def _take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        截取屏幕 - 调用已有的screenshot_mcp工具
        
        Args:
            filename: 可选的文件名
            
        Returns:
            包含截图路径和状态的字典
        """
        try:
            result = self.screenshot_tool.take_screenshot_base64(filename)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_mouse_position(self) -> Optional[tuple]:
        """
        获取当前鼠标位置 - 调用已有的mouse_move_mcp工具
        
        Returns:
            (x, y) 坐标元组，失败返回None
        """
        try:
            result = self.mouse_tool.get_current_mouse_position()
            if result.get("success"):
                return (result["x"], result["y"])
            return None
        except Exception as e:
            logger.error(f"获取鼠标位置失败: {str(e)}")
            return None
    
    def _move_mouse(self, x: int, y: int) -> bool:
        """
        移动鼠标到指定位置 - 调用已有的mouse_move_mcp工具
        
        Args:
            x: 目标X坐标
            y: 目标Y坐标
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            result = self.mouse_tool.move_mouse_to_position(x, y)
            return result.get("success", False)
        except Exception as e:
            logger.error(f"移动鼠标失败: {str(e)}")
            return False
    
    def _calculate_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        计算两点之间的欧几里得距离 - 调用已有的mouse_move_mcp工具
        
        Args:
            x1, y1: 第一个点的坐标
            x2, y2: 第二个点的坐标
            
        Returns:
            距离值
        """
        return self.mouse_tool.calculate_distance(x1, y1, x2, y2)
    
    def smart_move_to_target(
        self,
        target_description: str,
        max_attempts: Optional[int] = None,
        tolerance: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        智能移动鼠标到目标位置（完整工作流）
        
        这个工具封装了完整的工作流程：
        1. 截取屏幕
        2. 读取并返回图片（供AI分析）
        3. 等待AI提供目标坐标
        4. 移动鼠标
        5. 验证是否到达
        6. 如未到达，重复步骤1-5
        
        Args:
            target_description: 目标位置的描述（供AI理解）
            max_attempts: 最大尝试次数（默认5次）
            tolerance: 位置容差，单位像素（默认10）
            
        Returns:
            包含工作流状态和截图信息的字典
        """
        if max_attempts is None:
            max_attempts = self.max_attempts
        if tolerance is None:
            tolerance = self.tolerance
        
        # 步骤1: 截取初始屏幕（已包含base64编码）
        screenshot_result = self._take_screenshot()
        
        if not screenshot_result.get("success"):
            return {
                "success": False,
                "error": f"截屏失败: {screenshot_result.get('error')}",
                "step": "screenshot"
            }
        
        filepath = screenshot_result["filepath"]
        image_base64 = screenshot_result.get("base64")
        screenshot_width = screenshot_result.get("width", 0)
        screenshot_height = screenshot_result.get("height", 0)
        
        # 获取当前鼠标位置
        current_pos = self._get_mouse_position()
        
        if current_pos is None:
            return {
                "success": False,
                "error": "获取鼠标位置失败",
                "step": "get_position"
            }
        
        # 获取显示器信息
        monitor_info = self._get_monitor_info()
        
        # 计算截图坐标系在全局桌面中的原点（用于从截图坐标转换到系统坐标）
        origin_x = 0
        origin_y = 0
        screenshot_method = screenshot_result.get("method")
        monitors = monitor_info.get("monitors") if isinstance(monitor_info, dict) else None

        try:
            if monitors and screenshot_method:
                if screenshot_method == "powershell_wsl":
                    # WSL + PowerShell 截图，仅截取主显示器
                    primary_monitor = next(
                        (m for m in monitors if m.get("IsPrimary")), None
                    )
                    if primary_monitor:
                        origin_x = int(primary_monitor.get("Left", 0))
                        origin_y = int(primary_monitor.get("Top", 0))
                elif screenshot_method == "mss":
                    # mss 全屏截图：图片 (0,0) 对应所有显示器中最小的 Left/Top
                    origin_x = min(int(m.get("Left", 0)) for m in monitors)
                    origin_y = min(int(m.get("Top", 0)) for m in monitors)
        except Exception as e:
            logger.debug(f"计算截图原点失败: {e}")
        
        return {
            "success": True,
            "step": "ready_for_analysis",
            "message": "截图已准备好，请AI分析图片并提供目标坐标",
            "screenshot_path": filepath,
            "screenshot_base64": image_base64,
            "screenshot_size": {
                "width": screenshot_width,
                "height": screenshot_height
            },
            "current_mouse_position": {
                "x": current_pos[0],
                "y": current_pos[1]
            },
            "dpi_scale": {
                "x": self.dpi_scale[0],
                "y": self.dpi_scale[1]
            },
            "monitor_info": monitor_info,
            "screenshot_origin": {
                "x": origin_x,
                "y": origin_y
            },
            "target_description": target_description,
            "instructions": (
                "请分析截图，找到目标在截图中的坐标 (sx, sy)。\n"\
                f"截图尺寸: {screenshot_width}x{screenshot_height}\n"\
                f"DPI缩放: {self.dpi_scale[0]}x (X), {self.dpi_scale[1]}x (Y)\n"\
                f"截图原点在系统坐标中的位置为: ({origin_x}, {origin_y})。\n"\
                "从截图坐标转换到系统坐标时，请使用：\n"\
                "  x = sx + screenshot_origin.x\n"\
                "  y = sy + screenshot_origin.y\n"\
                "然后调用 execute_move_to_coordinates 工具来移动鼠标"
            )
        }
    
    def execute_move_to_coordinates(
        self,
        target_x: int,
        target_y: int,
        tolerance: Optional[int] = None,
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        执行移动到指定坐标并验证
        
        Args:
            target_x: 目标X坐标
            target_y: 目标Y坐标
            tolerance: 位置容差，单位像素（默认10）
            verify: 是否验证移动结果（默认True）
            
        Returns:
            包含移动结果的字典
        """
        if tolerance is None:
            tolerance = self.tolerance
        
        # 获取移动前的位置
        before_pos = self._get_mouse_position()
        
        if before_pos is None:
            return {
                "success": False,
                "error": "获取移动前鼠标位置失败"
            }
        
        # 执行移动
        move_success = self._move_mouse(target_x, target_y)
        
        if not move_success:
            return {
                "success": False,
                "error": "移动鼠标失败"
            }
        
        # 等待一小段时间让系统响应
        time.sleep(0.1)
        
        if not verify:
            return {
                "success": True,
                "message": "鼠标已移动（未验证）",
                "target": {"x": target_x, "y": target_y}
            }
        
        # 验证移动结果
        after_pos = self._get_mouse_position()
        
        if after_pos is None:
            return {
                "success": False,
                "error": "获取移动后鼠标位置失败"
            }
        
        distance = self._calculate_distance(
            after_pos[0], after_pos[1],
            target_x, target_y
        )
        
        if distance <= tolerance:
            return {
                "success": True,
                "message": "鼠标已成功移动到目标位置",
                "before_position": {"x": before_pos[0], "y": before_pos[1]},
                "after_position": {"x": after_pos[0], "y": after_pos[1]},
                "target_position": {"x": target_x, "y": target_y},
                "distance_to_target": round(distance, 2),
                "tolerance": tolerance
            }
        else:
            return {
                "success": False,
                "message": "鼠标未能精确到达目标位置",
                "before_position": {"x": before_pos[0], "y": before_pos[1]},
                "after_position": {"x": after_pos[0], "y": after_pos[1]},
                "target_position": {"x": target_x, "y": target_y},
                "distance_to_target": round(distance, 2),
                "tolerance": tolerance,
                "suggestion": "请重新截图并尝试移动"
            }
    
    def move_to_text_target(
        self,
        target_text: str,
        max_attempts: Optional[int] = None,
        tolerance: Optional[int] = None,
        use_ocr: bool = False
    ) -> Dict[str, Any]:
        """
        直接移动鼠标到包含指定文本的位置（一次调用完成）
        
        注意：此方法需要AI助手的视觉分析能力或OCR支持。
        当use_ocr=False时，会返回截图要求AI分析；
        当use_ocr=True时，会尝试使用OCR识别文本位置（需要安装tesseract）。
        
        Args:
            target_text: 目标文本，如"文档"、"工作台"、"搜索"等
            max_attempts: 最大尝试次数（默认5次）
            tolerance: 位置容差，单位像素（默认10）
            use_ocr: 是否使用OCR自动识别（需要安装pytesseract和tesseract-ocr）
            
        Returns:
            包含工作流状态和结果的字典
        """
        if max_attempts is None:
            max_attempts = self.max_attempts
        if tolerance is None:
            tolerance = self.tolerance
        
        # 截取屏幕（已包含base64编码）
        screenshot_result = self._take_screenshot()
        
        if not screenshot_result.get("success"):
            return {
                "success": False,
                "error": f"截屏失败: {screenshot_result.get('error')}",
                "step": "screenshot"
            }
        
        filepath = screenshot_result["filepath"]
        image_base64 = screenshot_result.get("base64")
        
        # 获取当前鼠标位置
        current_pos = self._get_mouse_position()
        
        if current_pos is None:
            return {
                "success": False,
                "error": "获取鼠标位置失败",
                "step": "get_position"
            }
        
        if use_ocr:
            # 尝试使用OCR识别文本位置
            try:
                import pytesseract
                from PIL import Image
                
                # 打开图片
                img = Image.open(filepath)
                
                # 使用OCR识别文本和位置
                ocr_data = pytesseract.image_to_data(img, lang='chi_sim+eng', output_type=pytesseract.Output.DICT)
                
                # 查找目标文本
                target_coords = None
                for i, text in enumerate(ocr_data['text']):
                    if target_text in text or text in target_text:
                        # 找到目标文本，计算中心位置
                        x = ocr_data['left'][i] + ocr_data['width'][i] // 2
                        y = ocr_data['top'][i] + ocr_data['height'][i] // 2
                        target_coords = (x, y)
                        break
                
                if target_coords is None:
                    return {
                        "success": False,
                        "error": f"OCR未能找到文本'{target_text}'",
                        "step": "ocr_recognition",
                        "suggestion": "请确保文本清晰可见，或使用AI视觉分析模式",
                        "screenshot_path": filepath,
                        "screenshot_base64": image_base64
                    }
                
                # 移动鼠标到目标位置
                move_result = self.execute_move_to_coordinates(
                    target_x=target_coords[0],
                    target_y=target_coords[1],
                    tolerance=tolerance,
                    verify=True
                )
                
                return {
                    "success": move_result.get("success"),
                    "method": "ocr",
                    "target_text": target_text,
                    "found_at": {"x": target_coords[0], "y": target_coords[1]},
                    "move_result": move_result,
                    "screenshot_path": filepath
                }
                
            except ImportError:
                return {
                    "success": False,
                    "error": "OCR功能需要安装 pytesseract 和 Pillow",
                    "step": "ocr_import",
                    "install_command": "pip install pytesseract Pillow",
                    "note": "还需要安装系统级的 tesseract-ocr"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"OCR识别失败: {str(e)}",
                    "step": "ocr_execution"
                }
        else:
            # 返回截图，需要AI分析
            return {
                "success": True,
                "step": "waiting_for_ai_analysis",
                "method": "ai_vision",
                "message": f"截图已准备好，需要AI分析图片找到'{target_text}'的位置",
                "target_text": target_text,
                "screenshot_path": filepath,
                "screenshot_base64": image_base64,
                "current_mouse_position": {
                    "x": current_pos[0],
                    "y": current_pos[1]
                },
                "instructions": (
                    f"请分析截图，找到文本'{target_text}'的坐标位置，"
                    f"然后调用 execute_move_to_coordinates 工具来移动鼠标"
                )
            }
