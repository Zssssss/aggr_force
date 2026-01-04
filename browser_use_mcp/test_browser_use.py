#!/usr/bin/env python3
"""测试 browser_use_mcp 工具"""

import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from browser_use_mcp.browser_tools import BrowserUseManager


async def test_browser():
    """测试浏览器功能"""
    print("=" * 60)
    print("测试 browser_use_mcp 工具")
    print("=" * 60)
    
    manager = BrowserUseManager()
    
    # 检测WSL环境
    print(f"\n1. 检测WSL环境: {manager._is_wsl()}")
    
    # 测试创建会话
    print("\n2. 测试创建浏览器会话...")
    try:
        result = await manager.create_session("test_session", headless=False)
        print(f"   结果: {result}")
        
        if not result.get("success"):
            print(f"   ❌ 创建会话失败: {result.get('error')}")
            return
        
        print("   ✅ 会话创建成功")
        
        # 测试导航
        print("\n3. 测试导航到百度...")
        nav_result = await manager.navigate("https://www.baidu.com")
        print(f"   结果: {nav_result}")
        
        if nav_result.get("success"):
            print("   ✅ 导航成功")
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 测试获取状态
            print("\n4. 测试获取页面状态...")
            state_result = await manager.get_state(include_screenshot=False)
            
            if state_result.get("success"):
                print(f"   URL: {state_result.get('url')}")
                print(f"   标题: {state_result.get('title')}")
                print(f"   元素数量: {state_result.get('elements_count')}")
                print("   ✅ 获取状态成功")
            else:
                print(f"   ❌ 获取状态失败: {state_result.get('error')}")
        else:
            print(f"   ❌ 导航失败: {nav_result.get('error')}")
        
        # 关闭会话
        print("\n5. 关闭会话...")
        close_result = await manager.close_session(save=False)
        print(f"   结果: {close_result}")
        
    except Exception as e:
        import traceback
        print(f"   ❌ 发生异常: {e}")
        print(traceback.format_exc())
        
        # 尝试清理
        try:
            await manager.cleanup()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(test_browser())
