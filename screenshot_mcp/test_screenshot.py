"""测试Screenshot MCP工具"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from screenshot_mcp.screenshot_tools import ScreenshotTool, take_screenshot_simple


def test_basic_screenshot():
    """测试基本截图功能"""
    print("=" * 60)
    print("测试1: 基本截图功能")
    print("=" * 60)
    
    result = take_screenshot_simple()
    
    if result.get("success"):
        print("✅ 截图成功!")
        print(f"  文件路径: {result['filepath']}")
        print(f"  图片尺寸: {result['width']} x {result['height']}")
        print(f"  图片格式: {result['format']}")
        print(f"  截图方法: {result.get('method', 'unknown')}")
    else:
        print("❌ 截图失败!")
        print(f"  错误信息: {result.get('error')}")
        print(f"  操作系统: {result.get('system')}")
    
    print()
    return result.get("success", False)


def test_custom_filename():
    """测试自定义文件名"""
    print("=" * 60)
    print("测试2: 自定义文件名")
    print("=" * 60)
    
    tool = ScreenshotTool()
    result = tool.take_screenshot("test_custom_name.png")
    
    if result.get("success"):
        print("✅ 自定义文件名截图成功!")
        print(f"  文件名: {result['filename']}")
        print(f"  文件路径: {result['filepath']}")
    else:
        print("❌ 截图失败!")
        print(f"  错误信息: {result.get('error')}")
    
    print()
    return result.get("success", False)


def test_base64_screenshot():
    """测试Base64编码截图"""
    print("=" * 60)
    print("测试3: Base64编码截图")
    print("=" * 60)
    
    tool = ScreenshotTool()
    result = tool.take_screenshot_base64("test_base64.png")
    
    if result.get("success"):
        print("✅ Base64编码截图成功!")
        print(f"  文件路径: {result['filepath']}")
        print(f"  文件大小: {result.get('size_bytes', 0)} 字节")
        print(f"  Base64长度: {len(result.get('base64', ''))} 字符")
        print(f"  Base64前50字符: {result.get('base64', '')[:50]}...")
    else:
        print("❌ 截图失败!")
        print(f"  错误信息: {result.get('error')}")
    
    print()
    return result.get("success", False)


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Screenshot MCP 工具测试")
    print("=" * 60)
    print()
    
    results = []
    
    # 运行所有测试
    results.append(("基本截图", test_basic_screenshot()))
    results.append(("自定义文件名", test_custom_filename()))
    results.append(("Base64编码", test_base64_screenshot()))
    
    # 输出测试总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print()
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
