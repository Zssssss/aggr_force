#!/usr/bin/env python3
"""
Mouse Move MCP 测试脚本
测试所有工具功能
"""

import sys
import time
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from mouse_move_tools import (
    get_mouse_position_tool,
    move_mouse_tool,
    calculate_distance_tool
)


def print_result(title: str, result: dict):
    """打印测试结果"""
    print(f"\n{'='*60}")
    print(f"测试: {title}")
    print(f"{'='*60}")
    print(f"成功: {result.get('success')}")
    if result.get('success'):
        for key, value in result.items():
            if key != 'success':
                print(f"{key}: {value}")
    else:
        print(f"错误: {result.get('error')}")
    print(f"{'='*60}\n")


def test_get_mouse_position():
    """测试获取鼠标位置功能"""
    print("\n>>> 测试1: 获取鼠标位置")
    result = get_mouse_position_tool()
    print_result("获取鼠标位置", result)
    return result.get('success'), result.get('x'), result.get('y')


def test_calculate_distance(x1, y1, x2, y2):
    """测试计算距离功能"""
    print(f"\n>>> 测试2: 计算距离 ({x1}, {y1}) 到 ({x2}, {y2})")
    result = calculate_distance_tool(x1, y1, x2, y2)
    print_result(f"计算距离", result)
    return result.get('success'), result.get('distance')


def test_move_mouse(x, y):
    """测试移动鼠标功能"""
    print(f"\n>>> 测试3: 移动鼠标到 ({x}, {y})")
    result = move_mouse_tool(x, y)
    print_result(f"移动鼠标到 ({x}, {y})", result)
    return result.get('success')


def test_move_and_verify(target_x, target_y, tolerance=10):
    """测试移动并验证功能"""
    print(f"\n>>> 测试4: 移动鼠标到 ({target_x}, {target_y}) 并验证")
    
    # 获取当前位置
    current_pos = get_mouse_position_tool()
    if not current_pos.get('success'):
        print("错误: 无法获取当前鼠标位置")
        return False
    
    current_x = current_pos.get('x')
    current_y = current_pos.get('y')
    print(f"当前位置: ({current_x}, {current_y})")
    
    # 计算距离
    distance_result = calculate_distance_tool(
        current_x, current_y,
        target_x, target_y
    )
    distance = distance_result.get('distance')
    print(f"目标距离: {distance:.2f}px")
    
    # 检查是否已在目标位置
    if distance <= tolerance:
        print(f"鼠标已在目标位置附近（距离: {distance:.2f}px）")
        return True
    
    # 移动鼠标
    print(f"移动鼠标到目标位置...")
    move_result = move_mouse_tool(target_x, target_y)
    if not move_result.get('success'):
        print(f"移动失败: {move_result.get('error')}")
        return False
    
    # 等待一下让鼠标稳定
    time.sleep(0.5)
    
    # 验证新位置
    new_pos = get_mouse_position_tool()
    if not new_pos.get('success'):
        print("警告: 无法验证新位置")
        return False
    
    new_x = new_pos.get('x')
    new_y = new_pos.get('y')
    print(f"新位置: ({new_x}, {new_y})")
    
    # 计算新距离
    new_distance_result = calculate_distance_tool(
        new_x, new_y,
        target_x, target_y
    )
    new_distance = new_distance_result.get('distance')
    print(f"新距离: {new_distance:.2f}px")
    
    success = new_distance <= tolerance
    if success:
        print(f"✓ 成功到达目标位置（容差: {tolerance}px）")
    else:
        print(f"✗ 未到达目标位置，需要继续调整")
    
    return success


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Mouse Move MCP 工具测试")
    print("="*60)
    
    test_results = []
    
    # 测试1: 获取鼠标位置
    success, current_x, current_y = test_get_mouse_position()
    test_results.append(("获取鼠标位置功能", success))
    
    if not success or current_x is None or current_y is None:
        print("\n错误: 无法获取鼠标位置，后续测试无法进行")
        return False
    
    time.sleep(1)
    
    # 测试2: 计算距离
    target_x = current_x + 100
    target_y = current_y + 100
    success, distance = test_calculate_distance(
        current_x, current_y,
        target_x, target_y
    )
    test_results.append(("计算距离功能", success))
    time.sleep(1)
    
    # 测试3: 移动鼠标
    print(f"\n准备移动鼠标到 ({target_x}, {target_y})")
    print("等待3秒...")
    time.sleep(3)
    
    success = test_move_mouse(target_x, target_y)
    test_results.append(("移动鼠标功能", success))
    time.sleep(1)
    
    # 测试4: 移动并验证（移动回原位置）
    print(f"\n准备移动鼠标回原位置 ({current_x}, {current_y})")
    print("等待3秒...")
    time.sleep(3)
    
    success = test_move_and_verify(current_x, current_y, tolerance=15)
    test_results.append(("移动并验证功能", success))
    
    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {test_name}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result)
    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")
    print("="*60 + "\n")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
