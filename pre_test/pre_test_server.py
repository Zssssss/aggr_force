# server.py
import os
import sys
import json
import shutil
import platform
import psutil
import requests
import re
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# 初始化 Server
mcp = FastMCP("WSL-Enhanced-Tools")

# ==================== 文件操作类函数 ====================

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    读取本地文件的内容。
    注意：在 WSL 中，Windows 的 C 盘路径通常是 /mnt/c/Users/...
    """
    try:
        # 为了安全，简单检查一下路径是否存在
        if not os.path.exists(file_path):
            return f"Error: 文件不存在: {file_path}"
        
        # 读取文件
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def list_directory(directory_path: str, show_hidden: bool = False) -> str:
    """
    列出指定目录的内容
    
    Args:
        directory_path: 目录路径
        show_hidden: 是否显示隐藏文件
    """
    try:
        if not os.path.exists(directory_path):
            return f"Error: 目录不存在: {directory_path}"
        
        if not os.path.isdir(directory_path):
            return f"Error: 路径不是目录: {directory_path}"
        
        items = os.listdir(directory_path)
        if not show_hidden:
            items = [item for item in items if not item.startswith('.')]
        
        result = []
        for item in items:
            full_path = os.path.join(directory_path, item)
            item_type = "目录" if os.path.isdir(full_path) else "文件"
            size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d %H:%M:%S")
            result.append(f"{item} ({item_type}, {size} bytes, 修改时间: {mtime})")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@mcp.tool()
def create_directory(directory_path: str) -> str:
    """
    创建目录
    
    Args:
        directory_path: 要创建的目录路径
    """
    try:
        if os.path.exists(directory_path):
            return f"目录已存在: {directory_path}"
        
        os.makedirs(directory_path, exist_ok=True)
        return f"成功创建目录: {directory_path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@mcp.tool()
def delete_file(file_path: str, recursive: bool = False) -> str:
    """
    删除文件或目录
    
    Args:
        file_path: 文件或目录路径
        recursive: 是否递归删除目录
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: 文件或目录不存在: {file_path}"
        
        if os.path.isdir(file_path):
            if recursive:
                shutil.rmtree(file_path)
                return f"成功递归删除目录: {file_path}"
            else:
                os.rmdir(file_path)
                return f"成功删除空目录: {file_path}"
        else:
            os.remove(file_path)
            return f"成功删除文件: {file_path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str, mode: str = "w") -> str:
    """
    写入文件
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        mode: 写入模式 ('w' 覆盖, 'a' 追加)
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(content)
        
        return f"成功写入文件: {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def file_exists(file_path: str) -> str:
    """
    检查文件是否存在
    
    Args:
        file_path: 文件路径
    """
    try:
        exists = os.path.exists(file_path)
        if exists:
            file_type = "目录" if os.path.isdir(file_path) else "文件"
            return f"存在: {file_type} - {file_path}"
        else:
            return f"不存在: {file_path}"
    except Exception as e:
        return f"Error checking file existence: {str(e)}"

@mcp.tool()
def get_file_info(file_path: str) -> str:
    """
    获取文件详细信息
    
    Args:
        file_path: 文件路径
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: 文件不存在: {file_path}"
        
        stat = os.stat(file_path)
        file_type = "目录" if os.path.isdir(file_path) else "文件"
        
        info = {
            "路径": file_path,
            "类型": file_type,
            "大小": f"{stat.st_size} bytes",
            "创建时间": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "修改时间": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "访问时间": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
            "权限": oct(stat.st_mode)[-3:]
        }
        
        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error getting file info: {str(e)}"

@mcp.tool()
def copy_file(source_path: str, destination_path: str) -> str:
    """
    复制文件或目录
    
    Args:
        source_path: 源路径
        destination_path: 目标路径
    """
    try:
        if not os.path.exists(source_path):
            return f"Error: 源文件不存在: {source_path}"
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
            return f"成功复制目录: {source_path} -> {destination_path}"
        else:
            shutil.copy2(source_path, destination_path)
            return f"成功复制文件: {source_path} -> {destination_path}"
    except Exception as e:
        return f"Error copying file: {str(e)}"

@mcp.tool()
def move_file(source_path: str, destination_path: str) -> str:
    """
    移动或重命名文件
    
    Args:
        source_path: 源路径
        destination_path: 目标路径
    """
    try:
        if not os.path.exists(source_path):
            return f"Error: 源文件不存在: {source_path}"
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        shutil.move(source_path, destination_path)
        return f"成功移动文件: {source_path} -> {destination_path}"
    except Exception as e:
        return f"Error moving file: {str(e)}"

# ==================== 系统信息类函数 ====================

@mcp.tool()
def get_system_info() -> str:
    """
    获取系统信息
    """
    try:
        info = {
            "操作系统": platform.system(),
            "操作系统版本": platform.version(),
            "架构": platform.architecture()[0],
            "处理器": platform.processor(),
            "主机名": platform.node(),
            "Python版本": platform.python_version(),
            "当前工作目录": os.getcwd(),
            "用户名": os.getlogin(),
            "环境": "WSL" if "microsoft" in platform.uname().release.lower() else "Native Linux"
        }
        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error getting system info: {str(e)}"

@mcp.tool()
def get_disk_usage(path: str = "/") -> str:
    """
    获取磁盘使用情况
    
    Args:
        path: 要检查的路径，默认为根目录
    """
    try:
        disk_usage = shutil.disk_usage(path)
        
        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        used_percent = (disk_usage.used / disk_usage.total) * 100
        
        info = {
            "路径": path,
            "总容量": f"{total_gb:.2f} GB",
            "已使用": f"{used_gb:.2f} GB",
            "可用空间": f"{free_gb:.2f} GB",
            "使用率": f"{used_percent:.1f}%"
        }
        
        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error getting disk usage: {str(e)}"

@mcp.tool()
def get_memory_usage() -> str:
    """
    获取内存使用情况
    """
    try:
        memory = psutil.virtual_memory()
        
        total_gb = memory.total / (1024**3)
        used_gb = memory.used / (1024**3)
        available_gb = memory.available / (1024**3)
        used_percent = memory.percent
        
        info = {
            "总内存": f"{total_gb:.2f} GB",
            "已使用": f"{used_gb:.2f} GB",
            "可用内存": f"{available_gb:.2f} GB",
            "使用率": f"{used_percent:.1f}%"
        }
        
        return json.dumps(info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error getting memory usage: {str(e)}"

@mcp.tool()
def get_running_processes(limit: int = 20) -> str:
    """
    获取运行中的进程列表
    
    Args:
        limit: 返回的进程数量限制
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
            try:
                proc_info = proc.info
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # 按CPU使用率排序
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        
        # 限制返回数量
        processes = processes[:limit]
        
        result = []
        for proc in processes:
            result.append(f"PID: {proc['pid']}, 名称: {proc['name']}, CPU: {proc.get('cpu_percent', 0):.1f}%, 内存: {proc.get('memory_percent', 0):.1f}%, 用户: {proc.get('username', 'N/A')}")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error getting running processes: {str(e)}"

@mcp.tool()
def get_environment_variables() -> str:
    """
    获取环境变量
    """
    try:
        env_vars = dict(os.environ)
        return json.dumps(env_vars, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error getting environment variables: {str(e)}"

# ==================== 网络请求类函数 ====================

@mcp.tool()
def http_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> str:
    """
    发送HTTP GET请求
    
    Args:
        url: 请求的URL
        headers: 请求头
        timeout: 超时时间（秒）
    """
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        
        result = {
            "状态码": response.status_code,
            "响应头": dict(response.headers),
            "响应内容": response.text[:5000]  # 限制返回内容长度
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error making HTTP GET request: {str(e)}"

@mcp.tool()
def http_post(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None,
              headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> str:
    """
    发送HTTP POST请求
    
    Args:
        url: 请求的URL
        data: 表单数据
        json_data: JSON数据
        headers: 请求头
        timeout: 超时时间（秒）
    """
    try:
        response = requests.post(url, data=data, json=json_data, headers=headers, timeout=timeout)
        
        result = {
            "状态码": response.status_code,
            "响应头": dict(response.headers),
            "响应内容": response.text[:5000]  # 限制返回内容长度
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error making HTTP POST request: {str(e)}"

# ==================== 文本处理类函数 ====================

@mcp.tool()
def search_text_in_file(file_path: str, pattern: str, case_sensitive: bool = False) -> str:
    """
    在文件中搜索文本
    
    Args:
        file_path: 文件路径
        pattern: 搜索模式（支持正则表达式）
        case_sensitive: 是否区分大小写
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: 文件不存在: {file_path}"
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        flags = 0 if case_sensitive else re.IGNORECASE
        matches = re.finditer(pattern, content, flags)
        
        results = []
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            line_content = content.split('\n')[line_num - 1].strip()
            results.append(f"第{line_num}行: {line_content}")
        
        if results:
            return f"找到 {len(results)} 个匹配:\n" + "\n".join(results)
        else:
            return f"未找到匹配: {pattern}"
    except Exception as e:
        return f"Error searching text in file: {str(e)}"

@mcp.tool()
def replace_text_in_file(file_path: str, old_pattern: str, new_text: str,
                         case_sensitive: bool = False, backup: bool = True) -> str:
    """
    在文件中替换文本
    
    Args:
        file_path: 文件路径
        old_pattern: 要替换的模式（支持正则表达式）
        new_text: 替换文本
        case_sensitive: 是否区分大小写
        backup: 是否创建备份文件
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: 文件不存在: {file_path}"
        
        # 创建备份
        if backup:
            backup_path = file_path + ".backup"
            shutil.copy2(file_path, backup_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        flags = 0 if case_sensitive else re.IGNORECASE
        new_content = re.sub(old_pattern, new_text, content, flags=flags)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        # 计算替换次数
        replace_count = len(re.findall(old_pattern, content, flags=flags))
        
        return f"成功替换 {replace_count} 处，备份文件: {backup_path if backup else '无'}"
    except Exception as e:
        return f"Error replacing text in file: {str(e)}"

# ==================== 文件监控类函数 ====================

@mcp.tool()
def watch_file_changes(file_path: str, duration: int = 60) -> str:
    """
    监控文件变化
    
    Args:
        file_path: 要监控的文件路径
        duration: 监控持续时间（秒）
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: 文件不存在: {file_path}"
        
        initial_mtime = os.path.getmtime(file_path)
        initial_size = os.path.getsize(file_path)
        
        changes = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                current_mtime = os.path.getmtime(file_path)
                current_size = os.path.getsize(file_path)
                
                if current_mtime != initial_mtime or current_size != initial_size:
                    change_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    changes.append(f"{change_time}: 文件发生变化 (大小: {current_size} bytes)")
                    
                    initial_mtime = current_mtime
                    initial_size = current_size
                
                time.sleep(1)
            except FileNotFoundError:
                changes.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: 文件被删除")
                break
        
        if changes:
            return f"监控完成，发现 {len(changes)} 次变化:\n" + "\n".join(changes)
        else:
            return f"监控完成，未发现文件变化"
    except Exception as e:
        return f"Error watching file changes: {str(e)}"

# ==================== 命令执行类函数 ====================

@mcp.tool()
def execute_command(command: str, timeout: int = 30, working_directory: Optional[str] = None) -> str:
    """
    安全执行shell命令
    
    Args:
        command: 要执行的命令
        timeout: 超时时间（秒）
        working_directory: 工作目录
    """
    try:
        # 安全检查：禁止危险命令
        dangerous_commands = ['rm -rf /', 'format', 'del /s', 'shutdown', 'reboot']
        for dangerous in dangerous_commands:
            if dangerous in command.lower():
                return f"Error: 禁止执行危险命令: {dangerous}"
        
        # 设置工作目录
        cwd = working_directory if working_directory else os.getcwd()
        
        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        output = {
            "命令": command,
            "工作目录": cwd,
            "返回码": result.returncode,
            "标准输出": result.stdout,
            "标准错误": result.stderr
        }
        
        return json.dumps(output, ensure_ascii=False, indent=2)
    except subprocess.TimeoutExpired:
        return f"Error: 命令执行超时 ({timeout}秒)"
    except Exception as e:
        return f"Error executing command: {str(e)}"

if __name__ == "__main__":
    # 这一步很重要，它会在 stdio 上启动服务
    mcp.run()