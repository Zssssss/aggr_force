#!/usr/bin/env python3
"""调试测试脚本"""

import sys
from pathlib import Path

# 添加路径
sys.path.append(str(Path(__file__).parent.parent / "screenshot_mcp"))
sys.path.append(str(Path(__file__).parent.parent / "mouse_move_mcp"))

from screenshot_tools import ScreenshotTool
from mouse_move_tools import MouseMoveTools as MouseTools

def test_screenshot():
    """测试截图工具"""
    print("=" * 50)
    print("测试截图工具")
    print("=" * 50)
    
    # 设置输出目录
    screenshot_dir = Path.home() / "screenshot_mcp"
    screenshot_dir.mkdir(exist_ok=True)
    print(f"截图目录: {screenshot_dir}")
    
    # 创建截图工具
    tool = ScreenshotTool(output_dir=str(screenshot_dir))
    print(f"截图工具输出目录: {tool.output_dir}")
    
    # 测试截图
    print("\n开始截图...")
    result = tool.take_screenshot_base64("debug_test.png")
    
    print(f"\n截图结果:")
    print(f"  成功: {result.get('success')}")
    if result.get('success'):
        print(f"  文件路径: {result.get('filepath')}")
        print(f"  文件名: {result.get('filename')}")
        print(f"  图片尺寸: {result.get('width')} x {result.get('height')}")
        print(f"  Base64长度: {len(result.get('base64', ''))}")
    else:
        print(f"  错误: {result.get('error')}")
    
    return result

def test_mouse_position():
    """测试鼠标位置获取"""
    print("\n" + "=" * 50)
    print("测试鼠标位置获取")
    print("=" * 50)
    
    tool = MouseTools()
    result = tool.get_current_mouse_position()
    
    print(f"\n鼠标位置结果:")
    print(f"  成功: {result.get('success')}")
    if result.get('success'):
        print(f"  X坐标: {result.get('x')}")
        print(f"  Y坐标: {result.get('y')}")
    else:
        print(f"  错误: {result.get('error')}")
    
    return result

def test_smart_mouse_move():
    """测试智能鼠标移动工具"""
    print("\n" + "=" * 50)
    print("测试智能鼠标移动工具")
    print("=" * 50)
    
    from smart_mouse_move_tools import SmartMouseMoveTools
    
    tool = SmartMouseMoveTools()
    print(f"工具初始化成功")
    print(f"  截图工具输出目录: {tool.screenshot_tool.output_dir}")
    
    # 测试截图
    print("\n测试内部截图方法...")
    result = tool._take_screenshot("smart_test.png")
    
    print(f"\n截图结果:")
    print(f"  成功: {result.get('success')}")
    if result.get('success'):
        print(f"  文件路径: {result.get('filepath')}")
        print(f"  Base64长度: {len(result.get('base64', ''))}")
    else:
        print(f"  错误: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    print("开始调试测试...\n")
    
    # 测试1: 直接测试截图工具
    test_screenshot()
    
    # 测试2: 测试鼠标位置
    test_mouse_position()
    
    # 测试3: 测试智能鼠标移动工具
    test_smart_mouse_move()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
