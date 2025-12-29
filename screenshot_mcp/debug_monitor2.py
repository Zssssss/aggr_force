#!/usr/bin/env python3
"""调试第二个显示器截图问题"""

import sys
from pathlib import Path
from PIL import Image

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from screenshot_mcp.screenshot_tools import ScreenshotTool


def debug_monitor_screenshot():
    """调试显示器截图"""
    print("=" * 60)
    print("调试显示器截图")
    print("=" * 60)
    
    tool = ScreenshotTool()
    
    # 获取显示器信息
    print("\n【步骤1】获取显示器信息")
    monitors = tool.get_monitors_info()
    print(f"检测到 {len(monitors)} 个显示器:\n")
    
    for monitor in monitors:
        print(f"显示器 {monitor['MonitorNumber']}:")
        print(f"  位置: ({monitor['Left']}, {monitor['Top']})")
        print(f"  尺寸: {monitor['Width']} x {monitor['Height']}")
        print(f"  边界: Right={monitor['Right']}, Bottom={monitor['Bottom']}")
        print()
    
    # 测试截取第二个显示器
    if len(monitors) >= 2:
        print("\n【步骤2】截取第二个显示器")
        monitor_info = monitors[1]
        print(f"目标显示器信息:")
        print(f"  编号: 2")
        print(f"  位置: ({monitor_info['Left']}, {monitor_info['Top']})")
        print(f"  尺寸: {monitor_info['Width']} x {monitor_info['Height']}")
        
        # 执行截图
        result = tool.take_screenshot(filename="debug_monitor2.png", monitor_number=2)
        
        if result.get("success"):
            print(f"\n截图成功!")
            print(f"  文件路径: {result['filepath']}")
            print(f"  图片尺寸: {result['width']} x {result['height']}")
            print(f"  截图方法: {result.get('method')}")
            
            # 验证图片尺寸
            print(f"\n【步骤3】验证截图尺寸")
            expected_width = monitor_info['Width']
            expected_height = monitor_info['Height']
            actual_width = result['width']
            actual_height = result['height']
            
            print(f"  期望尺寸: {expected_width} x {expected_height}")
            print(f"  实际尺寸: {actual_width} x {actual_height}")
            
            if actual_width == expected_width and actual_height == expected_height:
                print(f"  ✅ 尺寸匹配!")
            else:
                print(f"  ❌ 尺寸不匹配!")
                print(f"  宽度差异: {actual_width - expected_width}")
                print(f"  高度差异: {actual_height - expected_height}")
            
            # 检查图片内容
            print(f"\n【步骤4】检查图片内容")
            try:
                with Image.open(result['filepath']) as img:
                    # 获取图片的一些像素来检查
                    pixels = img.load()
                    # 检查四个角的像素
                    corners = [
                        (0, 0, "左上角"),
                        (img.width - 1, 0, "右上角"),
                        (0, img.height - 1, "左下角"),
                        (img.width - 1, img.height - 1, "右下角")
                    ]
                    
                    print(f"  图片四角像素值:")
                    for x, y, name in corners:
                        pixel = pixels[x, y]
                        print(f"    {name} ({x}, {y}): {pixel}")
                    
                    # 检查中心像素
                    center_x = img.width // 2
                    center_y = img.height // 2
                    center_pixel = pixels[center_x, center_y]
                    print(f"    中心 ({center_x}, {center_y}): {center_pixel}")
                    
            except Exception as e:
                print(f"  ❌ 读取图片失败: {e}")
        else:
            print(f"\n❌ 截图失败: {result.get('error')}")
    else:
        print("\n⚠️ 只有一个显示器，无法测试第二个显示器")
    
    # 同时截取第一个显示器作为对比
    print("\n【步骤5】截取第一个显示器作为对比")
    result1 = tool.take_screenshot(filename="debug_monitor1.png", monitor_number=1)
    if result1.get("success"):
        print(f"第一个显示器截图成功:")
        print(f"  文件路径: {result1['filepath']}")
        print(f"  图片尺寸: {result1['width']} x {result1['height']}")


if __name__ == "__main__":
    debug_monitor_screenshot()
