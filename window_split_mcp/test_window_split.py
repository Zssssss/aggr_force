#!/usr/bin/env python3
"""Window Split MCP 测试脚本

测试窗口分屏工具的各项功能
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from window_split_mcp.window_split_tools import WindowSplitTool


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_screen_size():
    """测试获取屏幕尺寸"""
    print_section("测试1: 获取屏幕尺寸")
    
    tool = WindowSplitTool()
    result = tool.get_screen_size()
    
    if result.get("success"):
        print(f"✅ 成功获取屏幕尺寸")
        print(f"   宽度: {result['width']} 像素")
        print(f"   高度: {result['height']} 像素")
        print(f"   方法: {result.get('method', 'unknown')}")
    else:
        print(f"❌ 获取屏幕尺寸失败")
        print(f"   错误: {result.get('error')}")
    
    return result


def test_list_windows():
    """测试列出窗口"""
    print_section("测试2: 列出所有窗口")
    
    tool = WindowSplitTool()
    result = tool.list_windows()
    
    if result.get("success"):
        windows = result.get("windows", [])
        print(f"✅ 成功获取窗口列表")
        print(f"   窗口总数: {result['count']}")
        print(f"   方法: {result.get('method', 'unknown')}")
        
        if windows:
            print(f"\n   前5个窗口:")
            for i, win in enumerate(windows[:5], 1):
                print(f"   {i}. {win['title'][:50]}")
                print(f"      ID: {win['id']}")
                print(f"      位置: ({win['x']}, {win['y']})")
                print(f"      大小: {win['width']} x {win['height']}")
        
        return windows
    else:
        print(f"❌ 获取窗口列表失败")
        print(f"   错误: {result.get('error')}")
        return []


def test_active_window():
    """测试获取活动窗口"""
    print_section("测试3: 获取活动窗口")
    
    tool = WindowSplitTool()
    result = tool.get_active_window()
    
    if result.get("success"):
        print(f"✅ 成功获取活动窗口")
        print(f"   标题: {result['title']}")
        print(f"   ID (十六进制): {result['window_id']}")
        print(f"   ID (十进制): {result['window_id_decimal']}")
        print(f"   方法: {result.get('method', 'unknown')}")
    else:
        print(f"❌ 获取活动窗口失败")
        print(f"   错误: {result.get('error')}")
    
    return result


def test_move_window(windows):
    """测试移动窗口"""
    print_section("测试4: 移动窗口")
    
    if not windows:
        print("⚠️  没有可用的窗口进行测试")
        return
    
    # 选择第一个窗口进行测试
    test_window = windows[0]
    window_id = test_window['id']
    
    print(f"测试窗口: {test_window['title'][:50]}")
    print(f"窗口ID: {window_id}")
    print(f"原始位置: ({test_window['x']}, {test_window['y']})")
    print(f"原始大小: {test_window['width']} x {test_window['height']}")
    
    # 移动到屏幕左上角，大小为800x600
    tool = WindowSplitTool()
    result = tool.move_window(window_id, 0, 0, 800, 600)
    
    if result.get("success"):
        print(f"\n✅ 窗口移动成功")
        print(f"   新位置: (0, 0)")
        print(f"   新大小: 800 x 600")
    else:
        print(f"\n❌ 窗口移动失败")
        print(f"   错误: {result.get('error')}")


def test_split_horizontal(windows):
    """测试水平分屏"""
    print_section("测试5: 水平分屏（左右分屏）")
    
    if len(windows) < 2:
        print("⚠️  需要至少2个窗口进行测试")
        return
    
    # 选择前两个窗口
    window_ids = [windows[0]['id'], windows[1]['id']]
    
    print(f"窗口1: {windows[0]['title'][:50]}")
    print(f"窗口2: {windows[1]['title'][:50]}")
    
    tool = WindowSplitTool()
    result = tool.split_windows_horizontal(window_ids)
    
    if result.get("success"):
        print(f"\n✅ 水平分屏成功")
        screen = result.get('screen_size', {})
        print(f"   屏幕尺寸: {screen.get('width')} x {screen.get('height')}")
        print(f"   布局: {result.get('layout')}")
    else:
        print(f"\n❌ 水平分屏失败")
        print(f"   错误: {result.get('error')}")


def test_split_vertical(windows):
    """测试垂直分屏"""
    print_section("测试6: 垂直分屏（上下分屏）")
    
    if len(windows) < 2:
        print("⚠️  需要至少2个窗口进行测试")
        return
    
    # 选择前两个窗口
    window_ids = [windows[0]['id'], windows[1]['id']]
    
    print(f"窗口1: {windows[0]['title'][:50]}")
    print(f"窗口2: {windows[1]['title'][:50]}")
    
    tool = WindowSplitTool()
    result = tool.split_windows_vertical(window_ids)
    
    if result.get("success"):
        print(f"\n✅ 垂直分屏成功")
        screen = result.get('screen_size', {})
        print(f"   屏幕尺寸: {screen.get('width')} x {screen.get('height')}")
        print(f"   布局: {result.get('layout')}")
    else:
        print(f"\n❌ 垂直分屏失败")
        print(f"   错误: {result.get('error')}")


def test_split_grid(windows):
    """测试网格分屏"""
    print_section("测试7: 网格分屏（四分屏）")
    
    if len(windows) < 4:
        print(f"⚠️  需要至少4个窗口进行测试（当前有{len(windows)}个）")
        return
    
    # 选择前四个窗口
    window_ids = [windows[i]['id'] for i in range(4)]
    
    for i in range(4):
        print(f"窗口{i+1}: {windows[i]['title'][:50]}")
    
    tool = WindowSplitTool()
    result = tool.split_windows_grid(window_ids)
    
    if result.get("success"):
        print(f"\n✅ 网格分屏成功")
        screen = result.get('screen_size', {})
        print(f"   屏幕尺寸: {screen.get('width')} x {screen.get('height')}")
        print(f"   布局: {result.get('layout')}")
    else:
        print(f"\n❌ 网格分屏失败")
        print(f"   错误: {result.get('error')}")


def test_maximize_window(windows):
    """测试最大化窗口"""
    print_section("测试8: 最大化窗口")
    
    if not windows:
        print("⚠️  没有可用的窗口进行测试")
        return
    
    # 选择第一个窗口
    window_id = windows[0]['id']
    
    print(f"测试窗口: {windows[0]['title'][:50]}")
    print(f"窗口ID: {window_id}")
    
    tool = WindowSplitTool()
    result = tool.maximize_window(window_id)
    
    if result.get("success"):
        print(f"\n✅ 窗口最大化成功")
        print(f"   方法: {result.get('method')}")
    else:
        print(f"\n❌ 窗口最大化失败")
        print(f"   错误: {result.get('error')}")


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("  Window Split MCP 工具测试")
    print("="*60)
    
    # 测试1: 获取屏幕尺寸
    test_screen_size()
    
    # 测试2: 列出窗口
    windows = test_list_windows()
    
    # 测试3: 获取活动窗口
    test_active_window()
    
    # 如果有窗口，继续测试其他功能
    if windows:
        print("\n" + "="*60)
        print("  以下测试会实际移动窗口，请确认是否继续？")
        print("  按Enter继续，按Ctrl+C取消")
        print("="*60)
        
        try:
            input()
        except KeyboardInterrupt:
            print("\n\n测试已取消")
            return
        
        # 测试4: 移动窗口
        test_move_window(windows)
        
        # 测试5: 水平分屏
        if len(windows) >= 2:
            test_split_horizontal(windows)
        
        # 测试6: 垂直分屏
        if len(windows) >= 2:
            test_split_vertical(windows)
        
        # 测试7: 网格分屏
        if len(windows) >= 4:
            test_split_grid(windows)
        
        # 测试8: 最大化窗口
        test_maximize_window(windows)
    
    print_section("测试完成")
    print("所有测试已完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
