#!/usr/bin/env python3
"""
打开钉钉 MCP 工具测试脚本
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_dingtalk_tools import open_dingtalk, check_dingtalk_installed


def test_check_dingtalk_installed():
    """测试检查钉钉安装状态"""
    print("=" * 60)
    print("测试 1: 检查钉钉是否已安装")
    print("=" * 60)
    
    result = check_dingtalk_installed()
    
    print(f"\n检查结果:")
    print(f"  已安装: {result['installed']}")
    print(f"  消息: {result['message']}")
    print(f"  平台: {result['platform']}")
    
    if result['paths']:
        print(f"  安装路径:")
        for path in result['paths']:
            print(f"    - {path}")
    
    if 'error' in result:
        print(f"  错误: {result['error']}")
    
    print()
    return result


def test_open_dingtalk():
    """测试打开钉钉"""
    print("=" * 60)
    print("测试 2: 打开钉钉应用")
    print("=" * 60)
    
    result = open_dingtalk()
    
    print(f"\n执行结果:")
    print(f"  成功: {result['success']}")
    print(f"  消息: {result['message']}")
    print(f"  平台: {result['platform']}")
    
    if 'method' in result:
        print(f"  使用方法: {result['method']}")
    
    if 'error' in result:
        print(f"  错误: {result['error']}")
    
    print()
    return result


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("打开钉钉 MCP 工具 - 测试套件")
    print("=" * 60 + "\n")
    
    # 测试 1: 检查钉钉安装状态
    check_result = test_check_dingtalk_installed()
    
    # 测试 2: 打开钉钉
    open_result = test_open_dingtalk()
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    if check_result['installed']:
        print("✅ 检测到钉钉已安装")
    else:
        print("❌ 未检测到钉钉安装")
    
    if open_result['success']:
        print("✅ 成功打开钉钉")
    else:
        print("❌ 打开钉钉失败")
    
    print("\n提示:")
    if not check_result['installed']:
        print("  - 请确保钉钉已正确安装")
        print("  - 如果钉钉安装在非标准位置，工具可能无法检测到")
    
    if not open_result['success']:
        print("  - 请检查钉钉是否已安装")
        print("  - 在 WSL 环境中，请确保 Windows 系统中已安装钉钉")
        print("  - 尝试手动运行命令测试: cmd.exe /c start dingtalk://")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
