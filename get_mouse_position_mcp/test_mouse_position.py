#!/usr/bin/env python3
"""测试鼠标位置获取功能"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from get_mouse_position_mcp.mouse_position_tools import MousePositionTool, get_mouse_position_simple


def test_mouse_position_tool():
    """测试 MousePositionTool 类"""
    print("=" * 60)
    print("测试 MousePositionTool 类")
    print("=" * 60)
    
    tool = MousePositionTool()
    
    print(f"\n检测到的操作系统: {tool.system}")
    print(f"是否为 WSL 环境: {tool.is_wsl}")
    
    print("\n正在获取鼠标位置...")
    result = tool.get_mouse_position()
    
    if result.get("success"):
        print("\n✅ 鼠标位置获取成功!")
        print(f"  X坐标: {result['x']} 像素")
        print(f"  Y坐标: {result['y']} 像素")
        print(f"  获取方法: {result['method']}")
        print(f"  操作系统: {result['system']}")
    else:
        print("\n❌ 鼠标位置获取失败!")
        print(f"  错误信息: {result.get('error')}")
        print(f"  操作系统: {result.get('system')}")
    
    return result.get("success", False)


def test_simple_function():
    """测试简单函数接口"""
    print("\n" + "=" * 60)
    print("测试简单函数接口 get_mouse_position_simple()")
    print("=" * 60)
    
    print("\n正在获取鼠标位置...")
    result = get_mouse_position_simple()
    
    if result.get("success"):
        print("\n✅ 鼠标位置获取成功!")
        print(f"  X坐标: {result['x']} 像素")
        print(f"  Y坐标: {result['y']} 像素")
        print(f"  获取方法: {result['method']}")
        print(f"  操作系统: {result['system']}")
    else:
        print("\n❌ 鼠标位置获取失败!")
        print(f"  错误信息: {result.get('error')}")
        print(f"  操作系统: {result.get('system')}")
    
    return result.get("success", False)


def test_multiple_calls():
    """测试多次调用"""
    print("\n" + "=" * 60)
    print("测试多次调用 (连续获取5次鼠标位置)")
    print("=" * 60)
    
    tool = MousePositionTool()
    success_count = 0
    
    for i in range(5):
        print(f"\n第 {i+1} 次获取:")
        result = tool.get_mouse_position()
        
        if result.get("success"):
            print(f"  ✅ 成功 - X: {result['x']}, Y: {result['y']}")
            success_count += 1
        else:
            print(f"  ❌ 失败 - {result.get('error')}")
        
        # 短暂延迟
        import time
        time.sleep(0.5)
    
    print(f"\n成功率: {success_count}/5 ({success_count*20}%)")
    return success_count == 5


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("鼠标位置获取 MCP 服务器 - 功能测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: MousePositionTool 类
    try:
        result1 = test_mouse_position_tool()
        results.append(("MousePositionTool 类测试", result1))
    except Exception as e:
        print(f"\n❌ MousePositionTool 类测试异常: {e}")
        results.append(("MousePositionTool 类测试", False))
    
    # 测试2: 简单函数接口
    try:
        result2 = test_simple_function()
        results.append(("简单函数接口测试", result2))
    except Exception as e:
        print(f"\n❌ 简单函数接口测试异常: {e}")
        results.append(("简单函数接口测试", False))
    
    # 测试3: 多次调用
    try:
        result3 = test_multiple_calls()
        results.append(("多次调用测试", result3))
    except Exception as e:
        print(f"\n❌ 多次调用测试异常: {e}")
        results.append(("多次调用测试", False))
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
