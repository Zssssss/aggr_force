#!/usr/bin/env python3
"""验证多显示器截图是否正确"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from screenshot_mcp.screenshot_tools import ScreenshotTool


def compare_images(img1_path, img2_path):
    """比较两张图片是否相同"""
    try:
        img1 = Image.open(img1_path)
        img2 = Image.open(img2_path)
        
        # 转换为numpy数组
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # 检查尺寸
        if arr1.shape != arr2.shape:
            return False, f"尺寸不同: {arr1.shape} vs {arr2.shape}"
        
        # 计算差异
        diff = np.abs(arr1.astype(int) - arr2.astype(int))
        max_diff = np.max(diff)
        mean_diff = np.mean(diff)
        
        # 如果差异很小，认为是相同的
        if max_diff < 5 and mean_diff < 1:
            return True, f"图片相同 (最大差异: {max_diff}, 平均差异: {mean_diff:.2f})"
        else:
            return False, f"图片不同 (最大差异: {max_diff}, 平均差异: {mean_diff:.2f})"
    except Exception as e:
        return False, f"比较失败: {e}"


def verify_monitor_screenshots():
    """验证多显示器截图"""
    print("=" * 70)
    print("验证多显示器截图功能")
    print("=" * 70)
    
    tool = ScreenshotTool()
    
    # 获取显示器信息
    monitors = tool.get_monitors_info()
    print(f"\n检测到 {len(monitors)} 个显示器")
    
    if len(monitors) < 2:
        print("⚠️ 只有一个显示器，无法测试多显示器功能")
        return
    
    # 截取全屏
    print("\n【测试1】截取全屏")
    result_all = tool.take_screenshot(filename="verify_all_monitors.png")
    if result_all.get("success"):
        print(f"✅ 全屏截图成功: {result_all['width']}x{result_all['height']}")
    else:
        print(f"❌ 全屏截图失败: {result_all.get('error')}")
        return
    
    # 截取第一个显示器
    print("\n【测试2】截取第一个显示器")
    result_m1 = tool.take_screenshot(filename="verify_monitor1.png", monitor_number=1)
    if result_m1.get("success"):
        print(f"✅ 显示器1截图成功: {result_m1['width']}x{result_m1['height']}")
        print(f"   期望尺寸: {monitors[0]['Width']}x{monitors[0]['Height']}")
        if result_m1['width'] == monitors[0]['Width'] and result_m1['height'] == monitors[0]['Height']:
            print(f"   ✅ 尺寸匹配")
        else:
            print(f"   ❌ 尺寸不匹配")
    else:
        print(f"❌ 显示器1截图失败: {result_m1.get('error')}")
        return
    
    # 截取第二个显示器
    print("\n【测试3】截取第二个显示器")
    result_m2 = tool.take_screenshot(filename="verify_monitor2.png", monitor_number=2)
    if result_m2.get("success"):
        print(f"✅ 显示器2截图成功: {result_m2['width']}x{result_m2['height']}")
        print(f"   期望尺寸: {monitors[1]['Width']}x{monitors[1]['Height']}")
        if result_m2['width'] == monitors[1]['Width'] and result_m2['height'] == monitors[1]['Height']:
            print(f"   ✅ 尺寸匹配")
        else:
            print(f"   ❌ 尺寸不匹配")
    else:
        print(f"❌ 显示器2截图失败: {result_m2.get('error')}")
        return
    
    # 比较显示器1和显示器2的截图
    print("\n【测试4】验证两个显示器截图内容不同")
    is_same, msg = compare_images(result_m1['filepath'], result_m2['filepath'])
    if is_same:
        print(f"❌ 警告: 两个显示器的截图内容相同!")
        print(f"   {msg}")
        print(f"   这可能意味着第二个显示器没有正确截取")
    else:
        print(f"✅ 两个显示器的截图内容不同")
        print(f"   {msg}")
    
    # 分析图片内容
    print("\n【测试5】分析图片内容")
    try:
        img1 = Image.open(result_m1['filepath'])
        img2 = Image.open(result_m2['filepath'])
        
        # 计算平均颜色
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        avg_color1 = np.mean(arr1, axis=(0, 1))
        avg_color2 = np.mean(arr2, axis=(0, 1))
        
        print(f"显示器1平均颜色: R={avg_color1[0]:.1f}, G={avg_color1[1]:.1f}, B={avg_color1[2]:.1f}")
        print(f"显示器2平均颜色: R={avg_color2[0]:.1f}, G={avg_color2[1]:.1f}, B={avg_color2[2]:.1f}")
        
        # 计算颜色差异
        color_diff = np.abs(avg_color1 - avg_color2)
        print(f"颜色差异: R={color_diff[0]:.1f}, G={color_diff[1]:.1f}, B={color_diff[2]:.1f}")
        
        if np.max(color_diff) > 10:
            print("✅ 两个显示器的平均颜色有明显差异，说明截取了不同内容")
        else:
            print("⚠️ 两个显示器的平均颜色相似，可能显示了相似的内容")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
    
    print("\n" + "=" * 70)
    print("验证完成")
    print("=" * 70)
    print("\n💡 提示:")
    print("   - 请手动查看生成的截图文件，确认它们是否正确")
    print("   - verify_monitor1.png 应该是第一个显示器的内容")
    print("   - verify_monitor2.png 应该是第二个显示器的内容")
    print("   - 如果两个文件内容相同，说明截图功能有问题")


if __name__ == "__main__":
    try:
        import numpy
        verify_monitor_screenshots()
    except ImportError:
        print("需要安装numpy: pip install numpy")
        sys.exit(1)
