#!/usr/bin/env python3
"""
钉钉文档 Hybrid模式登录脚本
用于首次登录钉钉文档并保存session，支持人工完成验证

目标文档: https://alidocs.dingtalk.com/i/nodes/Amq4vjg89nvwRrZwTpkorOjKW3kdP0wQ
文档标题: 2026-0105-0111
"""

import asyncio
import sys
import os

# 添加browser_use_mcp到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'browser_use_mcp'))

from browser_tools import get_browser_manager

async def dingtalk_hybrid_login():
    """使用hybrid模式登录钉钉文档"""
    manager = get_browser_manager()
    
    print("=" * 60)
    print("钉钉文档 Hybrid模式登录")
    print("=" * 60)
    print("\n目标文档: 2026-0105-0111")
    print("URL: https://alidocs.dingtalk.com/i/nodes/Amq4vjg89nvwRrZwTpkorOjKW3kdP0wQ")
    print("\n这将打开浏览器窗口，等待你手动完成登录和验证")
    print("=" * 60)
    
    try:
        # 步骤1: 创建会话 - 使用有头模式
        print("\n[步骤1] 创建浏览器会话...")
        result = await manager.create_session(
            session_id="dingtalk_docs_session",
            headless=False  # 显示浏览器窗口
        )
        
        if not result.get('success'):
            print(f"❌ 创建会话失败: {result.get('error')}")
            return False
        
        print(f"✓ 会话创建成功")
        print(f"  - 会话ID: {result['session_id']}")
        print(f"  - 模式: 有头模式(显示窗口)")
        
        # 步骤2: 导航到目标文档
        print("\n[步骤2] 导航到钉钉文档...")
        doc_url = "https://alidocs.dingtalk.com/i/nodes/Amq4vjg89nvwRrZwTpkorOjKW3kdP0wQ?doc_type=wiki_doc&iframeQuery=utm_source%3Dportal&utm_medium=portal_recent&rnd=0.8008429858047323"
        result = await manager.navigate(doc_url)
        
        if not result.get('success'):
            print(f"❌ 导航失败: {result.get('error')}")
            await manager.close_session(save=False)
            return False
        
        print(f"✓ 已打开文档页面")
        
        # 步骤3: 等待页面加载
        print("\n[步骤3] 等待页面加载...")
        await asyncio.sleep(3)
        print("✓ 页面加载完成")
        
        # 步骤4: 获取页面状态
        print("\n[步骤4] 获取页面状态...")
        state = await manager.get_state(include_screenshot=False)
        
        if state.get('success'):
            print(f"✓ 页面信息:")
            print(f"  - 标题: {state.get('title', 'N/A')}")
            print(f"  - URL: {state.get('url', 'N/A')[:80]}...")
        
        # 步骤5: 等待用户手动完成登录
        print("\n" + "=" * 60)
        print("请在浏览器窗口中手动完成以下操作:")
        print("  1. 如果需要登录，请完成钉钉登录")
        print("  2. 完成任何验证（扫码、验证码等）")
        print("  3. 确保能看到文档内容")
        print("  4. 等待页面完全加载")
        print("=" * 60)
        
        # 等待120秒供用户完成登录
        wait_time = 120
        print(f"\n⏳ 等待 {wait_time} 秒供你完成登录...")
        print("   浏览器窗口应该已经打开")
        print("   请在浏览器中完成登录操作")
        
        for i in range(wait_time, 0, -10):
            print(f"   剩余时间: {i} 秒...")
            await asyncio.sleep(10)
        
        # 步骤6: 等待登录状态稳定
        print("\n[步骤5] 等待登录状态稳定...")
        await asyncio.sleep(3)
        print("✓ 等待完成")
        
        # 步骤7: 保存会话状态
        print("\n[步骤6] 保存会话状态...")
        result = await manager.save_session()
        
        if result.get('success'):
            print(f"✓ 会话已保存")
            print(f"  - 会话ID: {result['session_id']}")
            print(f"  - 存储位置: {result['storage_state_file']}")
        else:
            print(f"⚠ 保存失败: {result.get('error')}")
            await manager.close_session(save=False)
            return False
        
        # 步骤8: 关闭浏览器
        print("\n[步骤7] 关闭浏览器...")
        await manager.close_session(save=False)  # 已经手动保存过了
        print("✓ 浏览器已关闭")
        
        print("\n" + "=" * 60)
        print("✓ 首次登录完成! 会话状态已保存")
        print("  后续可以使用无头模式自动下载文档")
        print("=" * 60)
        print("\n💡 下一步:")
        print("  运行 step2_download_docs.py 下载文档")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        try:
            await manager.close_session(save=False)
        except:
            pass
        return False

def main():
    """主函数"""
    success = asyncio.run(dingtalk_hybrid_login())
    
    if success:
        print("\n✓ 登录成功！")
        sys.exit(0)
    else:
        print("\n❌ 登录失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
