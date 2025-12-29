#!/usr/bin/env python3
"""测试多显示器截图功能"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from screenshot_mcp.screenshot_tools import ScreenshotTool


def test_multi_monitor():
    """测试多显示器功能"""
    print("=" * 60)
    print("多显示器截图功能测试")
    print("=" * 60)
    
    # 创建截图工具实例
    tool = ScreenshotTool()
    
    # 测试1: 获取显示器信息
    print("\n【测试1】获取显示器信息")
    print("-" * 60)
    try:
        monitors = tool.get_monitors_info()
        print(f"✅ 成功检测到 {len(monitors)} 个显示器:\n")
        
        for monitor in monitors:
            print(f"📺 显示器 {monitor['MonitorNumber']}:")
            print(f"   - 是否为主显示器: {'是' if monitor['IsPrimary'] else '否'}")
            print(f"   - 位置: ({monitor['Left']}, {monitor['Top']})")
            print(f"   - 尺寸: {monitor['Width']} x {monitor['Height']} 像素")
            print(f"   - 边界: Left={monitor['Left']}, Top={monitor['Top']}, "
                  f"Right={monitor['Right']}, Bottom={monitor['Bottom']}")
            print()
        
        monitor_count = len(monitors)
    except Exception as e:
        print(f"❌ 获取显示器信息失败: {e}")
        return False
    
    # 测试2: 截取全屏
    print("\n【测试2】截取全屏（所有显示器）")
    print("-" * 60)
    try:
        result = tool.take_screenshot()
        if result.get("success"):
            print(f"✅ 截图成功!")
            print(f"   - 文件路径: {result['filepath']}")
            print(f"   - 图片尺寸: {result['width']} x {result['height']} 像素")
            print(f"   - 截图方法: {result.get('method', 'unknown')}")
        else:
            print(f"❌ 截图失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        return False
    
    # 测试3: 截取每个显示器
    print(f"\n【测试3】分别截取每个显示器（共 {monitor_count} 个）")
    print("-" * 60)
    for i in range(1, monitor_count + 1):
        try:
            result = tool.take_screenshot(monitor_number=i)
            if result.get("success"):
                print(f"✅ 显示器 {i} 截图成功!")
                print(f"   - 文件路径: {result['filepath']}")
                print(f"   - 图片尺寸: {result['width']} x {result['height']} 像素")
                print(f"   - 截图方法: {result.get('method', 'unknown')}")
            else:
                print(f"❌ 显示器 {i} 截图失败: {result.get('error')}")
                return False
        except Exception as e:
            print(f"❌ 显示器 {i} 截图失败: {e}")
            return False
    
    # 测试4: 测试无效的显示器编号
    print(f"\n【测试4】测试无效的显示器编号")
    print("-" * 60)
    invalid_number = monitor_count + 1
    try:
        result = tool.take_screenshot(monitor_number=invalid_number)
        if not result.get("success"):
            print(f"✅ 正确处理了无效的显示器编号 {invalid_number}")
            print(f"   - 错误信息: {result.get('error')}")
        else:
            print(f"⚠️ 应该失败但成功了，这可能是个问题")
    except Exception as e:
        print(f"✅ 正确抛出异常: {e}")
    
    # 测试5: 测试base64编码
    print(f"\n【测试5】测试base64编码功能")
    print("-" * 60)
    try:
        result = tool.take_screenshot_base64(monitor_number=1)
        if result.get("success"):
            print(f"✅ Base64编码截图成功!")
            print(f"   - 文件路径: {result['filepath']}")
            print(f"   - 图片尺寸: {result['width']} x {result['height']} 像素")
            print(f"   - 数据大小: {result.get('size_bytes', 0)} 字节")
            print(f"   - Base64长度: {len(result.get('base64', ''))} 字符")
        else:
            print(f"❌ Base64编码截图失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Base64编码截图失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_multi_monitor()
    sys.exit(0 if success else 1)
