#!/usr/bin/env python3
"""VSCode和浏览器左右分屏脚本"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from window_split_mcp.window_split_tools import WindowSplitTool


def main():
    """主函数 - 实现VSCode和浏览器左右分屏"""
    tool = WindowSplitTool()
    
    print("=== VSCode和浏览器左右分屏 ===\n")
    
    # 1. 列出所有窗口
    print("1. 正在获取窗口列表...")
    windows_result = tool.list_windows()
    
    if not windows_result.get("success"):
        print(f"❌ 获取窗口列表失败: {windows_result.get('error')}")
        return 1
    
    windows = windows_result.get("windows", [])
    print(f"✅ 找到 {len(windows)} 个窗口\n")
    
    # 2. 查找VSCode和浏览器窗口
    vscode_window = None
    browser_window = None
    
    print("2. 正在查找VSCode和浏览器窗口...")
    for win in windows:
        title = win['title'].lower()
        
        # 查找VSCode窗口
        if not vscode_window and ('visual studio code' in title or 'vscode' in title or 'code' in title):
            vscode_window = win
            print(f"   找到VSCode: {win['title'][:60]}")
        
        # 查找浏览器窗口
        if not browser_window and any(browser in title for browser in ['chrome', 'firefox', 'edge', 'safari', 'browser', '浏览器']):
            browser_window = win
            print(f"   找到浏览器: {win['title'][:60]}")
        
        if vscode_window and browser_window:
            break
    
    # 3. 检查是否找到窗口
    if not vscode_window and not browser_window:
        print("\n❌ 未找到VSCode或浏览器窗口")
        print("\n可用窗口列表:")
        for i, win in enumerate(windows, 1):
            print(f"   {i}. {win['title'][:60]} (ID: {win['id']})")
        return 1
    
    # 4. 执行分屏
    print("\n3. 正在执行左右分屏...")
    
    if vscode_window and browser_window:
        # 两个窗口都找到了，VSCode在左，浏览器在右
        window_ids = [vscode_window['id'], browser_window['id']]
        print(f"   VSCode (左侧): {vscode_window['title'][:40]}")
        print(f"   浏览器 (右侧): {browser_window['title'][:40]}")
    elif vscode_window:
        # 只找到VSCode
        window_ids = [vscode_window['id']]
        print(f"   VSCode (左侧): {vscode_window['title'][:40]}")
        print("   ⚠️  未找到浏览器窗口")
    else:
        # 只找到浏览器
        window_ids = [browser_window['id']]
        print(f"   浏览器 (左侧): {browser_window['title'][:40]}")
        print("   ⚠️  未找到VSCode窗口")
    
    # 执行水平分屏
    result = tool.split_windows_horizontal(window_ids)
    
    if result.get("success"):
        print("\n✅ 分屏成功!")
        screen_size = result.get('screen_size', {})
        print(f"   屏幕尺寸: {screen_size.get('width')} x {screen_size.get('height')}")
        
        for i, win_result in enumerate(result.get('windows', []), 1):
            if win_result.get('success'):
                pos = win_result.get('position', {})
                size = win_result.get('size', {})
                print(f"   窗口{i}: 位置({pos.get('x')}, {pos.get('y')}), 大小{size.get('width')}x{size.get('height')}")
    else:
        print(f"\n❌ 分屏失败: {result.get('error')}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
