"""
打开钉钉应用的工具函数
支持 Linux (WSL) 和 Windows 环境
"""

import subprocess
import platform
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def is_wsl() -> bool:
    """检测是否在 WSL 环境中运行"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
    except:
        return False


def open_dingtalk() -> Dict[str, Any]:
    """
    打开钉钉应用
    
    Returns:
        Dict[str, Any]: 包含操作结果的字典
            - success: bool, 操作是否成功
            - message: str, 结果消息
            - platform: str, 运行平台
    """
    system = platform.system()
    wsl = is_wsl()
    
    try:
        if system == "Windows" or wsl:
            # Windows 或 WSL 环境
            if wsl:
                # 在 WSL 中调用 Windows 命令
                    logger.info("检测到 WSL 环境，使用 Windows 命令打开钉钉")
                    # 尝试多种方式打开钉钉（优先使用直接启动可执行文件）
                    commands = [
                        # 方式1: 使用 powershell 直接启动可执行文件（最可靠）
                        ['powershell.exe', '-Command', 'Start-Process', r'C:\Program Files (x86)\DingDing\DingtalkLauncher.exe'],
                        # 方式2: 使用 cmd 启动可执行文件
                        ['cmd.exe', '/c', 'start', '', r'C:\Program Files (x86)\DingDing\DingtalkLauncher.exe'],
                        # 方式3: 尝试其他常见安装路径
                        ['powershell.exe', '-Command', 'Start-Process', r'C:\Program Files\DingDing\DingtalkLauncher.exe'],
                        # 方式4: 使用协议打开
                        ['powershell.exe', '-Command', 'Start-Process', 'dingtalk://'],
                        # 方式5: 使用 cmd.exe 启动协议
                        ['cmd.exe', '/c', 'start', '', 'dingtalk://'],
                    ]
            else:
                # 纯 Windows 环境
                logger.info("检测到 Windows 环境，打开钉钉")
                commands = [
                    # 方式1: 使用协议打开
                    ['cmd', '/c', 'start', 'dingtalk://'],
                    # 方式2: 尝试启动钉钉可执行文件
                    ['cmd', '/c', 'start', '', r'C:\Program Files (x86)\DingDing\DingtalkLauncher.exe'],
                ]
            
            # 尝试各种方式打开钉钉
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        platform_info = "WSL" if wsl else "Windows"
                        return {
                            "success": True,
                            "message": f"成功在 {platform_info} 环境中打开钉钉应用",
                            "platform": platform_info,
                            "method": " ".join(cmd)
                        }
                except Exception as e:
                    logger.debug(f"尝试命令 {cmd} 失败: {str(e)}")
                    continue
            
            # 所有方式都失败
            return {
                "success": False,
                "message": "无法打开钉钉，请确保钉钉已安装",
                "platform": "WSL" if wsl else "Windows",
                "error": "所有启动方式均失败"
            }
            
        elif system == "Linux":
            # 纯 Linux 环境
            logger.info("检测到 Linux 环境，打开钉钉")
            # 尝试使用 xdg-open 打开钉钉协议
            commands = [
                ['xdg-open', 'dingtalk://'],
                ['dingtalk'],  # 如果钉钉在 PATH 中
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "message": "成功在 Linux 环境中打开钉钉应用",
                            "platform": "Linux",
                            "method": " ".join(cmd)
                        }
                except Exception as e:
                    logger.debug(f"尝试命令 {cmd} 失败: {str(e)}")
                    continue
            
            return {
                "success": False,
                "message": "无法打开钉钉，请确保钉钉已安装并配置正确",
                "platform": "Linux",
                "error": "所有启动方式均失败"
            }
            
        elif system == "Darwin":
            # macOS 环境
            logger.info("检测到 macOS 环境，打开钉钉")
            result = subprocess.run(
                ['open', '-a', 'DingTalk'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "成功在 macOS 环境中打开钉钉应用",
                    "platform": "macOS"
                }
            else:
                return {
                    "success": False,
                    "message": "无法打开钉钉，请确保钉钉已安装",
                    "platform": "macOS",
                    "error": result.stderr
                }
        else:
            return {
                "success": False,
                "message": f"不支持的操作系统: {system}",
                "platform": system
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "打开钉钉超时",
            "platform": "WSL" if wsl else system,
            "error": "命令执行超时"
        }
    except Exception as e:
        logger.error(f"打开钉钉时发生错误: {str(e)}")
        return {
            "success": False,
            "message": f"打开钉钉时发生错误: {str(e)}",
            "platform": "WSL" if wsl else system,
            "error": str(e)
        }


def check_dingtalk_installed() -> Dict[str, Any]:
    """
    检查钉钉是否已安装
    
    Returns:
        Dict[str, Any]: 包含检查结果的字典
            - installed: bool, 是否已安装
            - message: str, 结果消息
            - paths: list, 可能的安装路径
    """
    system = platform.system()
    wsl = is_wsl()
    installed = False
    paths = []
    
    try:
        if system == "Windows" or wsl:
            # 检查常见的钉钉安装路径
            common_paths = [
                r'C:\Program Files (x86)\DingDing\DingtalkLauncher.exe',
                r'C:\Program Files\DingDing\DingtalkLauncher.exe',
                r'D:\Program Files (x86)\DingDing\DingtalkLauncher.exe',
                r'D:\Program Files\DingDing\DingtalkLauncher.exe',
            ]
            
            for path in common_paths:
                if wsl:
                    # 在 WSL 中检查 Windows 路径
                    wsl_path = path.replace('C:', '/mnt/c').replace('D:', '/mnt/d').replace('\\', '/')
                    if os.path.exists(wsl_path):
                        installed = True
                        paths.append(path)
                else:
                    if os.path.exists(path):
                        installed = True
                        paths.append(path)
            
            if installed:
                return {
                    "installed": True,
                    "message": "检测到钉钉已安装",
                    "paths": paths,
                    "platform": "WSL" if wsl else "Windows"
                }
            else:
                return {
                    "installed": False,
                    "message": "未检测到钉钉安装，但可能安装在其他位置",
                    "paths": [],
                    "platform": "WSL" if wsl else "Windows"
                }
                
        elif system == "Linux":
            # 检查 Linux 下的钉钉
            result = subprocess.run(
                ['which', 'dingtalk'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return {
                    "installed": True,
                    "message": "检测到钉钉已安装",
                    "paths": [result.stdout.strip()],
                    "platform": "Linux"
                }
            else:
                return {
                    "installed": False,
                    "message": "未检测到钉钉安装",
                    "paths": [],
                    "platform": "Linux"
                }
                
        elif system == "Darwin":
            # 检查 macOS 下的钉钉
            app_path = "/Applications/DingTalk.app"
            if os.path.exists(app_path):
                return {
                    "installed": True,
                    "message": "检测到钉钉已安装",
                    "paths": [app_path],
                    "platform": "macOS"
                }
            else:
                return {
                    "installed": False,
                    "message": "未检测到钉钉安装",
                    "paths": [],
                    "platform": "macOS"
                }
        else:
            return {
                "installed": False,
                "message": f"不支持的操作系统: {system}",
                "paths": [],
                "platform": system
            }
            
    except Exception as e:
        logger.error(f"检查钉钉安装时发生错误: {str(e)}")
        return {
            "installed": False,
            "message": f"检查时发生错误: {str(e)}",
            "paths": [],
            "platform": "WSL" if wsl else system,
            "error": str(e)
        }
