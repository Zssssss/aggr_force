#!/usr/bin/env python3
"""测试 browser_use_mcp 工具 - 导航到 remote3 网页"""

import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from browser_use_mcp.browser_tools import BrowserUseManager


async def test_remote3():
    """测试导航到 remote3 网页"""
    print("=" * 60)
    print("测试 browser_use_mcp 工具 - 导航到 remote3")
    print("=" * 60)
    
    manager = BrowserUseManager()
    
    try:
        # 测试创建会话
        print("\n1. 创建浏览器会话...")
        result = await manager.create_session("remote3_session", headless=False)
        print(f"   结果: {result}")
        
        if not result.get("success"):
            print(f"   ❌ 创建会话失败: {result.get('error')}")
            return
        
        print("   ✅ 会话创建成功")
        
        # 测试导航到 remote3
        print("\n2. 导航到 remote3 网页...")
        remote3_url = "https://remote3.co"
        nav_result = await manager.navigate(remote3_url)
        print(f"   结果: {nav_result}")
        
        if nav_result.get("success"):
            print("   ✅ 导航成功")
            
            # 等待页面加载
            await asyncio.sleep(3)
            
            # 测试获取状态
            print("\n3. 获取页面状态...")
            state_result = await manager.get_state(include_screenshot=False)
            
            if state_result.get("success"):
                print(f"   URL: {state_result.get('url')}")
                print(f"   标题: {state_result.get('title')}")
                print(f"   元素数量: {state_result.get('elements_count')}")
                
                # 打印前几个元素
                elements = state_result.get('elements', [])
                if elements:
                    print("\n   页面元素:")
                    for i, elem in enumerate(elements[:10]):  # 只显示前10个
                        print(f"      [{elem['index']}] <{elem['tag']}> {elem.get('text', '')[:50]}")
                    if len(elements) > 10:
                        print(f"      ... 还有 {len(elements) - 10} 个元素")
                
                print("   ✅ 获取状态成功")
            else:
                print(f"   ❌ 获取状态失败: {state_result.get('error')}")
        else:
            print(f"   ❌ 导航失败: {nav_result.get('error')}")
        
        # 等待用户查看页面
        print("\n4. 页面已打开，请查看浏览器...")
        print("   按 Ctrl+C 关闭浏览器并退出")
        
        # 保持会话活跃，直到用户中断
        while True:
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        print("\n\n5. 用户中断，关闭会话...")
    except Exception as e:
        import traceback
        print(f"\n   ❌ 发生异常: {e}")
        print(traceback.format_exc())
    finally:
        # 清理
        try:
            close_result = await manager.close_session(save=False)
            print(f"   结果: {close_result}")
            print("   ✅ 会话已关闭")
        except Exception as e:
            print(f"   ❌ 关闭会话时出错: {e}")


if __name__ == "__main__":
    asyncio.run(test_remote3())
