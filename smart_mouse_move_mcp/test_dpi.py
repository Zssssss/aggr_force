#!/usr/bin/env python3
"""
测试DPI获取功能
"""
import sys
from pathlib import Path

# 添加路径
sys.path.append(str(Path(__file__).parent))

from smart_mouse_move_tools import SmartMouseMoveTools

def test_dpi():
    """测试DPI获取"""
    print("=" * 50)
    print("测试DPI获取功能")
    print("=" * 50)
    
    # 创建工具实例
    tools = SmartMouseMoveTools()
    
    print(f"\n是否在WSL环境: {tools.is_wsl}")
    print(f"DPI缩放比例: X={tools.dpi_scale[0]}, Y={tools.dpi_scale[1]}")
    
    # 测试获取鼠标位置
    print("\n测试获取鼠标位置...")
    pos = tools._get_mouse_position()
    if pos:
        print(f"当前鼠标位置: ({pos[0]}, {pos[1]})")
    else:
        print("获取鼠标位置失败")
    
    # 测试获取显示器信息
    print("\n测试获取显示器信息...")
    monitor_info = tools._get_monitor_info()
    if monitor_info.get("success"):
        print(f"显示器数量: {monitor_info['count']}")
        for i, monitor in enumerate(monitor_info['monitors'], 1):
            print(f"  显示器 {i}: {monitor}")
    else:
        print(f"获取显示器信息失败: {monitor_info.get('error')}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_dpi()
