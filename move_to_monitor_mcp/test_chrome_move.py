#!/usr/bin/env python3
"""
测试将Chrome窗口移动到外接显示器
"""

import sys
import json
from monitor_tools import MonitorManager

def main():
    print("=" * 60)
    print("测试 Move to Monitor MCP - Chrome窗口移动")
    print("=" * 60)
    
    manager = MonitorManager()
    
    # 步骤1: 获取所有显示器信息
    print("\n步骤1: 获取显示器信息...")
    try:
        monitors = manager.get_monitors_info()
        print(f"✓ 检测到 {len(monitors)} 个显示器:")
        for monitor in monitors:
            primary = "主显示器" if monitor['IsPrimary'] else "外接显示器"
            print(f"  显示器 {monitor['MonitorNumber']} ({primary}):")
            print(f"    位置: ({monitor['Left']}, {monitor['Top']})")
            print(f"    尺寸: {monitor['Width']}x{monitor['Height']}")
    except Exception as e:
        print(f"✗ 获取显示器信息失败: {e}")
        return 1
    
    if len(monitors) < 2:
        print("\n⚠ 警告: 只检测到1个显示器，无法测试移动到外接显示器")
        print("请确保外接显示器已连接")
        return 1
    
    # 步骤2: 查找Chrome窗口
    print("\n步骤2: 查找Chrome窗口...")
    chrome_patterns = ["Chrome", "chrome", "Google Chrome", "谷歌浏览器"]
    chrome_window = None
    
    for pattern in chrome_patterns:
        try:
            window = manager.get_window_by_title(pattern)
            if window:
                chrome_window = window
                print(f"✓ 找到Chrome窗口: {window['Title']}")
                print(f"  窗口句柄: {window['Handle']}")
                break
        except Exception as e:
            continue
    
    if not chrome_window:
        print("✗ 未找到Chrome窗口")
        print("请确保Chrome浏览器已打开")
        return 1
    
    # 步骤3: 确定目标显示器（外接显示器）
    print("\n步骤3: 确定目标显示器...")
    # 找到非主显示器作为目标
    target_monitor = None
    for monitor in monitors:
        if not monitor['IsPrimary']:
            target_monitor = monitor
            break
    
    if not target_monitor:
        # 如果没有非主显示器，使用第2个显示器
        target_monitor = monitors[1] if len(monitors) > 1 else monitors[0]
    
    print(f"✓ 目标显示器: 显示器 {target_monitor['MonitorNumber']}")
    print(f"  位置: ({target_monitor['Left']}, {target_monitor['Top']})")
    print(f"  尺寸: {target_monitor['Width']}x{target_monitor['Height']}")
    
    # 步骤4: 移动Chrome窗口到外接显示器并最大化
    print(f"\n步骤4: 移动Chrome窗口到显示器 {target_monitor['MonitorNumber']}并最大化...")
    try:
        result = manager.move_window_by_title_to_monitor(
            "Chrome",
            target_monitor['MonitorNumber'],
            maximize=True  # 默认最大化
        )
        
        if result['success']:
            print("✓ 成功移动并最大化Chrome窗口!")
            print(f"  窗口标题: {result['window_title']}")
            print(f"  目标显示器: {result['monitor_number']}")
            print("\n请检查Chrome窗口是否已移动到外接显示器并最大化")
        else:
            print(f"✗ 移动失败: {result.get('error', '未知错误')}")
            return 1
    except Exception as e:
        print(f"✗ 移动窗口时出错: {e}")
        return 1
    
    # 步骤5: 完成
    print("\n步骤5: 测试完成")
    print("✓ Chrome窗口已移动到外接显示器并最大化")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    print("\n测试结果:")
    print(f"  ✓ 显示器检测: {len(monitors)} 个显示器")
    print(f"  ✓ 窗口查找: 找到 {chrome_window['Title']}")
    print(f"  ✓ 窗口移动: 移动到显示器 {target_monitor['MonitorNumber']}")
    print(f"  ✓ 窗口最大化: 已最大化")
    print("\n建议:")
    print("  1. 检查Chrome窗口是否在外接显示器上并已最大化")
    print("  2. 可以尝试移动其他窗口(如VSCode、Terminal等)")
    print("  3. 如需不最大化,可以修改maximize=False参数")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
