"""
Windows多显示器管理工具
支持在WSL环境中操作原生Windows窗口，将程序移动到指定显示器
"""

import subprocess
import json
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MonitorManager:
    """Windows多显示器管理器"""
    
    def __init__(self):
        """初始化显示器管理器"""
        self.powershell_cmd = "powershell.exe"
    
    def _run_powershell(self, script: str) -> str:
        """
        执行PowerShell脚本
        
        Args:
            script: PowerShell脚本内容
            
        Returns:
            脚本执行结果
        """
        try:
            # 在WSL中，PowerShell输出使用GBK编码
            result = subprocess.run(
                [self.powershell_cmd, "-Command", script],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                try:
                    error_msg = result.stderr.decode('gbk', errors='ignore').strip()
                except:
                    error_msg = result.stderr.decode('utf-8', errors='ignore').strip()
                logger.error(f"PowerShell执行失败: {error_msg}")
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
            logger.error(f"执行PowerShell时出错: {str(e)}")
            raise
    
    def get_monitors_info(self) -> List[Dict]:
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
            
            logger.info(f"检测到 {len(monitors)} 个显示器")
            return monitors
        except json.JSONDecodeError as e:
            logger.error(f"解析显示器信息失败: {str(e)}")
            raise RuntimeError(f"解析显示器信息失败: {str(e)}")
    
    def get_window_by_title(self, title_pattern: str) -> Optional[Dict]:
        """
        根据窗口标题查找窗口
        
        Args:
            title_pattern: 窗口标题（支持部分匹配）
            
        Returns:
            窗口信息字典，包含Handle和Title，如果未找到返回None
        """
        script = f"""
Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    using System.Text;
    public class Win32 {{
        [DllImport("user32.dll")]
        public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);
        
        [DllImport("user32.dll")]
        public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
        
        [DllImport("user32.dll")]
        public static extern bool IsWindowVisible(IntPtr hWnd);
        
        public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    }}
"@

$pattern = "{title_pattern}"
$foundWindow = $null

$callback = {{
    param($hwnd, $lParam)
    if ([Win32]::IsWindowVisible($hwnd)) {{
        $title = New-Object System.Text.StringBuilder 256
        [Win32]::GetWindowText($hwnd, $title, 256) | Out-Null
        $titleStr = $title.ToString()
        if ($titleStr -like "*$pattern*" -and $titleStr.Length -gt 0) {{
            $script:foundWindow = @{{
                Handle = $hwnd.ToInt64()
                Title = $titleStr
            }}
            return $false
        }}
    }}
    return $true
}}

[Win32]::EnumWindows($callback, [IntPtr]::Zero) | Out-Null

if ($foundWindow) {{
    $foundWindow | ConvertTo-Json
}} else {{
    Write-Output "null"
}}
"""
        try:
            output = self._run_powershell(script)
            if output == "null" or not output:
                logger.warning(f"未找到标题包含 '{title_pattern}' 的窗口")
                return None
            
            window = json.loads(output)
            logger.info(f"找到窗口: {window['Title']} (Handle: {window['Handle']})")
            return window
        except json.JSONDecodeError as e:
            logger.error(f"解析窗口信息失败: {str(e)}")
            return None
    
    def move_window_to_monitor(self, window_handle: int, monitor_number: int, 
                               maximize: bool = False) -> bool:
        """
        将窗口移动到指定显示器
        
        Args:
            window_handle: 窗口句柄
            monitor_number: 目标显示器编号（从1开始）
            maximize: 是否最大化窗口
            
        Returns:
            是否成功移动
        """
        script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {{
        [DllImport("user32.dll")]
        public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, 
            int X, int Y, int cx, int cy, uint uFlags);
        
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        
        public const uint SWP_NOZORDER = 0x0004;
        public const uint SWP_NOACTIVATE = 0x0010;
        public const int SW_RESTORE = 9;
        public const int SW_MAXIMIZE = 3;
    }}
"@

$hwnd = [IntPtr]::new({window_handle})
$monitors = [System.Windows.Forms.Screen]::AllScreens
$targetMonitor = $monitors[{monitor_number - 1}]

if (-not $targetMonitor) {{
    Write-Error "显示器编号 {monitor_number} 不存在"
    exit 1
}}

# 先恢复窗口（如果是最大化状态）
[Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE) | Out-Null
Start-Sleep -Milliseconds 100

# 计算窗口在目标显示器上的位置（居中）
$monitorBounds = $targetMonitor.Bounds
$windowWidth = [int]($monitorBounds.Width * 0.8)
$windowHeight = [int]($monitorBounds.Height * 0.8)
$x = $monitorBounds.Left + [int](($monitorBounds.Width - $windowWidth) / 2)
$y = $monitorBounds.Top + [int](($monitorBounds.Height - $windowHeight) / 2)

# 移动窗口
$result = [Win32]::SetWindowPos($hwnd, [IntPtr]::Zero, $x, $y, 
    $windowWidth, $windowHeight, [Win32]::SWP_NOZORDER)

if (-not $result) {{
    Write-Error "移动窗口失败"
    exit 1
}}

Start-Sleep -Milliseconds 100

# 如果需要最大化
if ({str(maximize).lower()}) {{
    [Win32]::ShowWindow($hwnd, [Win32]::SW_MAXIMIZE) | Out-Null
}}

Write-Output "success"
"""
        try:
            output = self._run_powershell(script)
            if "success" in output:
                logger.info(f"成功将窗口移动到显示器 {monitor_number}")
                return True
            else:
                logger.error(f"移动窗口失败: {output}")
                return False
        except Exception as e:
            logger.error(f"移动窗口时出错: {str(e)}")
            return False
    
    def move_window_by_title_to_monitor(self, title_pattern: str, 
                                       monitor_number: int,
                                       maximize: bool = False) -> Dict:
        """
        根据窗口标题将窗口移动到指定显示器
        
        Args:
            title_pattern: 窗口标题（支持部分匹配）
            monitor_number: 目标显示器编号（从1开始）
            maximize: 是否最大化窗口
            
        Returns:
            操作结果字典
        """
        # 获取显示器信息
        monitors = self.get_monitors_info()
        if monitor_number < 1 or monitor_number > len(monitors):
            return {
                "success": False,
                "error": f"显示器编号 {monitor_number} 无效，当前有 {len(monitors)} 个显示器"
            }
        
        # 查找窗口
        window = self.get_window_by_title(title_pattern)
        if not window:
            return {
                "success": False,
                "error": f"未找到标题包含 '{title_pattern}' 的窗口"
            }
        
        # 移动窗口
        success = self.move_window_to_monitor(
            window['Handle'], 
            monitor_number, 
            maximize
        )
        
        if success:
            return {
                "success": True,
                "window_title": window['Title'],
                "monitor_number": monitor_number,
                "monitor_info": monitors[monitor_number - 1]
            }
        else:
            return {
                "success": False,
                "error": "移动窗口失败"
            }


# MCP工具函数
def list_monitors() -> str:
    """
    列出所有显示器信息
    
    Returns:
        显示器信息的JSON字符串
    """
    try:
        manager = MonitorManager()
        monitors = manager.get_monitors_info()
        
        result = {
            "success": True,
            "monitor_count": len(monitors),
            "monitors": monitors
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"获取显示器信息失败: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2, ensure_ascii=False)


def find_window(title_pattern: str) -> str:
    """
    查找窗口
    
    Args:
        title_pattern: 窗口标题（支持部分匹配）
        
    Returns:
        窗口信息的JSON字符串
    """
    try:
        manager = MonitorManager()
        window = manager.get_window_by_title(title_pattern)
        
        if window:
            result = {
                "success": True,
                "window": window
            }
        else:
            result = {
                "success": False,
                "error": f"未找到标题包含 '{title_pattern}' 的窗口"
            }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"查找窗口失败: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2, ensure_ascii=False)


def move_to_monitor(title_pattern: str, monitor_number: int, 
                   maximize: bool = False) -> str:
    """
    将窗口移动到指定显示器
    
    Args:
        title_pattern: 窗口标题（支持部分匹配）
        monitor_number: 目标显示器编号（从1开始）
        maximize: 是否最大化窗口
        
    Returns:
        操作结果的JSON字符串
    """
    try:
        manager = MonitorManager()
        result = manager.move_window_by_title_to_monitor(
            title_pattern, 
            monitor_number, 
            maximize
        )
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"移动窗口失败: {str(e)}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2, ensure_ascii=False)
