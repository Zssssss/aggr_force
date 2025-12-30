#!/usr/bin/env python3
"""
智能鼠标移动 MCP 服务器测试脚本
"""

import sys
import time
from smart_mouse_move_tools import SmartMouseMoveTools


def test_screenshot():
    """测试截图功能"""
    print("=" * 60)
    print("测试1: 截图功能")
    print("=" * 60)
    
    tools = SmartMouseMoveTools()
    result = tools._take_screenshot("test_screenshot.png")
    
    if result.get("success"):
        print(f"✅ 截图成功")
        print(f"   文件路径: {result['filepath']}")
        print(f"   文件名: {result['filename']}")
    else:
        print(f"❌ 截图失败: {result.get('error')}")
    
    return result.get("success", False)


def test_get_mouse_position():
    """测试获取鼠标位置"""
    print("\n" + "=" * 60)
    print("测试2: 获取鼠标位置")
    print("=" * 60)
    
    tools = SmartMouseMoveTools()
    position = tools._get_mouse_position()
    
    if position:
        print(f"✅ 获取鼠标位置成功")
        print(f"   当前位置: ({position[0]}, {position[1]})")
    else:
        print(f"❌ 获取鼠标位置失败")
    
    return position is not None


def test_move_mouse():
    """测试移动鼠标"""
    print("\n" + "=" * 60)
    print("测试3: 移动鼠标")
    print("=" * 60)
    
    tools = SmartMouseMoveTools()
    
    # 获取当前位置
    start_pos = tools._get_mouse_position()
    if not start_pos:
        print("❌ 无法获取起始位置")
        return False
    
    print(f"   起始位置: ({start_pos[0]}, {start_pos[1]})")
    
    # 移动到新位置（相对移动100像素）
    target_x = start_pos[0] + 100
    target_y = start_pos[1] + 100
    
    print(f"   目标位置: ({target_x}, {target_y})")
    print("   正在移动鼠标...")
    
    success = tools._move_mouse(target_x, target_y)
    
    if not success:
        print("❌ 移动鼠标失败")
        return False
    
    time.sleep(0.2)  # 等待系统响应
    
    # 验证位置
    end_pos = tools._get_mouse_position()
    if not end_pos:
        print("❌ 无法获取结束位置")
        return False
    
    print(f"   实际位置: ({end_pos[0]}, {end_pos[1]})")
    
    distance = tools._calculate_distance(end_pos[0], end_pos[1], target_x, target_y)
    print(f"   距离目标: {distance:.2f} 像素")
    
    if distance <= 10:
        print("✅ 移动鼠标成功")
        
        # 移回原位置
        print("   正在移回原位置...")
        tools._move_mouse(start_pos[0], start_pos[1])
        time.sleep(0.2)
        
        return True
    else:
        print(f"❌ 移动不够精确（距离: {distance:.2f} > 10）")
        return False


def test_smart_move_workflow():
    """测试完整的智能移动工作流"""
    print("\n" + "=" * 60)
    print("测试4: 智能移动工作流")
    print("=" * 60)
    
    tools = SmartMouseMoveTools()
    
    # 步骤1: 开始工作流
    print("\n步骤1: 开始智能移动工作流")
    result = tools.smart_move_to_target(
        target_description="测试目标位置",
        max_attempts=3,
        tolerance=10
    )
    
    if not result.get("success"):
        print(f"❌ 工作流启动失败: {result.get('error')}")
        return False
    
    print(f"✅ 工作流已启动")
    print(f"   截图路径: {result['screenshot_path']}")
    print(f"   当前鼠标位置: ({result['current_mouse_position']['x']}, {result['current_mouse_position']['y']})")
    print(f"   截图已准备好供AI分析")
    
    # 步骤2: 模拟AI分析后执行移动
    print("\n步骤2: 执行移动到坐标")
    current_pos = tools._get_mouse_position()
    if not current_pos:
        print("❌ 无法获取当前位置")
        return False
    
    # 移动到相对位置
    target_x = current_pos[0] + 50
    target_y = current_pos[1] + 50
    
    print(f"   目标坐标: ({target_x}, {target_y})")
    
    move_result = tools.execute_move_to_coordinates(
        target_x=target_x,
        target_y=target_y,
        tolerance=10,
        verify=True
    )
    
    if not move_result.get("success"):
        print(f"❌ 移动失败: {move_result.get('message')}")
        return False
    
    print(f"✅ {move_result['message']}")
    print(f"   移动前: ({move_result['before_position']['x']}, {move_result['before_position']['y']})")
    print(f"   移动后: ({move_result['after_position']['x']}, {move_result['after_position']['y']})")
    print(f"   距离目标: {move_result['distance_to_target']} 像素")
    
    # 步骤3: 验证已在execute_move_to_coordinates中完成
    print("\n步骤3: 验证结果")
    print(f"✅ 验证已通过鼠标位置计算完成（无需额外截图）")
    print(f"   移动前位置: ({move_result['before_position']['x']}, {move_result['before_position']['y']})")
    print(f"   移动后位置: ({move_result['after_position']['x']}, {move_result['after_position']['y']})")
    print(f"   目标位置: ({move_result['target_position']['x']}, {move_result['target_position']['y']})")
    print(f"   距离目标: {move_result['distance_to_target']} 像素")
    print(f"   容差范围: {move_result['tolerance']} 像素")
    
    # 移回原位置
    print("\n   正在移回原位置...")
    tools._move_mouse(current_pos[0], current_pos[1])
    time.sleep(0.2)
    
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("智能鼠标移动 MCP 服务器 - 测试套件")
    print("=" * 60)
    
    tests = [
        ("截图功能", test_screenshot),
        ("获取鼠标位置", test_get_mouse_position),
        ("移动鼠标", test_move_mouse),
        ("智能移动工作流", test_smart_move_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            results.append((test_name, False))
    
    # 打印测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
