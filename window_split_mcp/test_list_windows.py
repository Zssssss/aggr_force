#!/usr/bin/env python3
"""测试窗口列表功能"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from window_split_mcp.window_split_tools import WindowSplitTool

def format_list_windows_result(result: dict) -> str:
    """格式化窗口列表结果"""
    if not result.get("success"):
        return f"""❌ 获取窗口列表失败

错误信息: {result.get('error', '未知错误')}

💡 提示:
- 在Linux系统上需要安装wmctrl: sudo apt install wmctrl
- 确保在图形界面环境中运行
"""
    
    windows = result.get("windows", [])
    count = result.get("count", 0)
    
    if count == 0:
        return "📋 当前没有打开的窗口"
    
    text = f"""✅ 成功获取窗口列表

📊 统计信息:
  - 窗口总数: {count}
  - 检测方法: {result.get('method', 'unknown')}

📋 窗口列表:
"""
    
    for i, win in enumerate(windows, 1):
        text += f"""
{i}. {win['title'][:60]}
   ID: {win['id']}
   位置: ({win['x']}, {win['y']})
   大小: {win['width']} x {win['height']}"""
        # desktop字段可能不存在（例如在Windows后端）
        if 'desktop' in win:
            text += f"""
   桌面: {win['desktop']}"""
        text += "\n"
    
    return text


if __name__ == "__main__":
    tool = WindowSplitTool()
    result = tool.list_windows()
    print(format_list_windows_result(result))
    
    # 如果有窗口，尝试找到Chrome和VSCode
    if result.get("success") and result.get("count", 0) > 0:
        windows = result.get("windows", [])
        
        chrome_windows = [w for w in windows if 'chrome' in w['title'].lower()]
        vscode_windows = [w for w in windows if 'visual studio code' in w['title'].lower() or 'vscode' in w['title'].lower()]
        
        print("\n" + "="*60)
        print("🔍 查找Chrome和VSCode窗口:")
        print(f"  - Chrome窗口数: {len(chrome_windows)}")
        if chrome_windows:
            for w in chrome_windows:
                print(f"    * {w['title'][:50]} (ID: {w['id']})")
        
        print(f"  - VSCode窗口数: {len(vscode_windows)}")
        if vscode_windows:
            for w in vscode_windows:
                print(f"    * {w['title'][:50]} (ID: {w['id']})")
