#!/usr/bin/env python3
"""测试上下分屏功能"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from window_split_mcp.window_split_tools import WindowSplitTool

if __name__ == "__main__":
    tool = WindowSplitTool()
    
    # 1. 列出所有窗口
    print("=" * 60)
    print("步骤1: 列出所有窗口")
    print("=" * 60)
    result = tool.list_windows()
    
    if not result.get("success"):
        print(f"❌ 获取窗口列表失败: {result.get('error')}")
        sys.exit(1)
    
    windows = result.get("windows", [])
    print(f"找到 {len(windows)} 个窗口\n")
    
    # 显示所有窗口
    for i, w in enumerate(windows, 1):
        print(f"{i}. {w['title'][:50]} (ID: {w['id']})")
    
    # 2. 查找Chrome和VSCode窗口
    print("\n" + "=" * 60)
    print("步骤2: 查找Chrome和VSCode窗口")
    print("=" * 60)
    
    chrome_windows = [w for w in windows if 'chrome' in w['title'].lower()]
    vscode_windows = [w for w in windows if 'visual studio code' in w['title'].lower() or 'vscode' in w['title'].lower()]
    
    print(f"Chrome窗口: {len(chrome_windows)}")
    for w in chrome_windows:
        print(f"  - {w['title'][:50]} (ID: {w['id']})")
    
    print(f"\nVSCode窗口: {len(vscode_windows)}")
    for w in vscode_windows:
        print(f"  - {w['title'][:50]} (ID: {w['id']})")
    
    if not chrome_windows:
        print("\n⚠️  未找到Chrome窗口，将只使用VSCode窗口测试")
        if not vscode_windows:
            print("❌ 也未找到VSCode窗口")
            sys.exit(1)
        window_ids = [vscode_windows[0]['id']]
        window_names = ["VSCode"]
    elif not vscode_windows:
        print("\n⚠️  未找到VSCode窗口，将只使用Chrome窗口测试")
        window_ids = [chrome_windows[0]['id']]
        window_names = ["Chrome"]
    else:
        window_ids = [chrome_windows[0]['id'], vscode_windows[0]['id']]
        window_names = ["Chrome", "VSCode"]
    
    # 3. 执行上下分屏
    print("\n" + "=" * 60)
    if len(window_ids) == 2:
        print(f"步骤3: 执行上下分屏 ({window_names[0]}上, {window_names[1]}下)")
    else:
        print(f"步骤3: 执行上下分屏 ({window_names[0]}占上半屏)")
    print("=" * 60)
    
    for i, wid in enumerate(window_ids):
        print(f"{window_names[i]}窗口ID: {wid}")
    
    print("\n开始分屏...")
    
    split_result = tool.split_windows_vertical(window_ids)
    
    if split_result.get("success"):
        print("\n✅ 上下分屏成功！")
        screen_size = split_result.get('screen_size', {})
        print(f"\n屏幕尺寸: {screen_size.get('width')} x {screen_size.get('height')}")
        print(f"布局类型: {split_result.get('layout')}")
        
        print("\n窗口详情:")
        for i, win in enumerate(split_result.get('windows', []), 1):
            if win.get('success'):
                pos = win.get('position', {})
                size = win.get('size', {})
                print(f"\n{i}. {window_names[i-1]}窗口")
                print(f"   窗口ID: {win['window_id']}")
                print(f"   位置: ({pos.get('x')}, {pos.get('y')})")
                print(f"   大小: {size.get('width')} x {size.get('height')}")
                print(f"   状态: ✅ 成功")
            else:
                print(f"\n{i}. {window_names[i-1]}窗口")
                print(f"   窗口ID: {win.get('window_id', 'unknown')}")
                print(f"   状态: ❌ 失败")
                print(f"   错误: {win.get('error', '未知错误')}")
    else:
        print(f"\n❌ 上下分屏失败: {split_result.get('error')}")
        sys.exit(1)
