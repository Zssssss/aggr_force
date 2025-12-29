#!/usr/bin/env python3
"""
Move to Monitor MCP 测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor_tools import MonitorManager
import json


def test_list_monitors():
    """测试列出显示器"""
    print("=" * 60)
    print("测试1: 列出所有显示器")
    print("=" * 60)
    
    try:
        manager = MonitorManager()
        monitors = manager.get_monitors_info()
        
        print(f"\n检测到 {len(monitors)} 个显示器:\n")
        for monitor in monitors:
            print(f"显示器 {monitor['MonitorNumber']}:")
            print(f"  主显示器: {'是' if monitor['IsPrimary'] else '否'}")
            print(f"  位置: ({monitor['Left']}, {monitor['Top']})")
            print(f"  尺寸: {monitor['Width']} x {monitor['Height']}")
            print(f"  边界: Left={monitor['Left']}, Top={monitor['Top']}, "
                  f"Right={monitor['Right']}, Bottom={monitor['Bottom']}")
            print()
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


def test_find_window():
    """测试查找窗口"""
    print("=" * 60)
    print("测试2: 查找窗口")
    print("=" * 60)
    
    # 测试查找常见窗口
    test_patterns = [
        "Chrome",
        "VSCode",
        "Code",
        "PowerShell",
        "cmd"
    ]
    
    manager = MonitorManager()
    found_any = False
    
    for pattern in test_patterns:
        print(f"\n查找标题包含 '{pattern}' 的窗口...")
        try:
            window = manager.get_window_by_title(pattern)
            if window:
                print(f"✓ 找到窗口:")
                print(f"  标题: {window['Title']}")
                print(f"  句柄: {window['Handle']}")
                found_any = True
            else:
                print(f"  未找到")
        except Exception as e:
            print(f"  错误: {str(e)}")
    
    if not found_any:
        print("\n⚠️  未找到任何测试窗口，请确保有浏览器或编辑器窗口打开")
    
    return found_any


def test_move_window():
    """测试移动窗口"""
    print("=" * 60)
    print("测试3: 移动窗口")
    print("=" * 60)
    
    manager = MonitorManager()
    
    # 获取显示器信息
    try:
        monitors = manager.get_monitors_info()
        if len(monitors) < 2:
            print("\n⚠️  只检测到1个显示器，跳过移动测试")
            print("   （移动窗口功能需要至少2个显示器）")
            return True
    except Exception as e:
        print(f"❌ 获取显示器信息失败: {str(e)}")
        return False
    
    # 查找一个窗口进行测试
    test_patterns = ["Chrome", "VSCode", "Code", "PowerShell"]
    test_window = None
    test_pattern = None
    
    for pattern in test_patterns:
        try:
            window = manager.get_window_by_title(pattern)
            if window:
                test_window = window
                test_pattern = pattern
                break
        except:
            continue
    
    if not test_window:
        print("\n⚠️  未找到可用于测试的窗口")
        print("   请打开Chrome、VSCode或其他应用后重试")
        return True
    
    print(f"\n将使用窗口进行测试: {test_window['Title']}")
    
    # 询问用户是否继续
    print("\n⚠️  此测试将移动窗口到第2个显示器")
    response = input("是否继续? (y/n): ").strip().lower()
    
    if response != 'y':
        print("已取消测试")
        return True
    
    # 执行移动
    print(f"\n移动窗口到显示器2...")
    try:
        result = manager.move_window_by_title_to_monitor(
            test_pattern,
            2,
            maximize=False
        )
        
        if result['success']:
            print("✓ 移动成功!")
            print(f"  窗口: {result['window_title']}")
            print(f"  目标显示器: {result['monitor_number']}")
            print(f"  显示器信息: {result['monitor_info']['Width']}x{result['monitor_info']['Height']}")
            
            # 询问是否移回
            response = input("\n是否将窗口移回显示器1? (y/n): ").strip().lower()
            if response == 'y':
                print("\n移动窗口回显示器1...")
                result2 = manager.move_window_by_title_to_monitor(
                    test_pattern,
                    1,
                    maximize=False
                )
                if result2['success']:
                    print("✓ 已移回显示器1")
                else:
                    print(f"❌ 移回失败: {result2.get('error', '未知错误')}")
            
            return True
        else:
            print(f"❌ 移动失败: {result.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 移动窗口时出错: {str(e)}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Move to Monitor MCP 工具测试")
    print("=" * 60 + "\n")
    
    results = []
    
    # 测试1: 列出显示器
    results.append(("列出显示器", test_list_monitors()))
    
    # 测试2: 查找窗口
    results.append(("查找窗口", test_find_window()))
    
    # 测试3: 移动窗口（可选）
    print("\n是否测试移动窗口功能? (需要至少2个显示器)")
    response = input("(y/n): ").strip().lower()
    if response == 'y':
        results.append(("移动窗口", test_move_window()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
