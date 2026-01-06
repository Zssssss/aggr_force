#!/usr/bin/env python3
"""混合模式示例 - 先有头登录,后无头自动化

这个示例展示如何处理需要人工验证(如reCAPTCHA)的登录场景:
1. 首次使用有头模式,手动编写代码打开浏览器,人工完成登录和验证
2. 手动编写代码保存会话状态
3. 后续使用无头模式,自动恢复登录状态进行自动化操作

改进版本：展示手动编写代码的方式，而不是使用封装的hybrid_login方法
"""

import asyncio
from browser_tools import get_browser_manager


async def first_time_login():
    """首次登录 - 有头模式,手动编写代码,人工处理验证"""
    print("=" * 60)
    print("阶段1: 首次登录 (有头模式 - 手动编写代码)")
    print("=" * 60)
    
    manager = get_browser_manager()
    
    # 步骤1: 手动创建会话 - 使用有头模式
    print("\n[步骤1] 手动创建浏览器会话...")
    result = await manager.create_session(
        session_id="github_session",  # 使用有意义的会话名
        headless=False  # 关键: 显示浏览器窗口
    )
    
    if not result.get('success'):
        print(f"❌ 创建会话失败: {result.get('error')}")
        return
    
    print(f"✓ 会话创建成功")
    print(f"  - 会话ID: {result['session_id']}")
    print(f"  - 模式: {'无头' if result.get('headless') else '有头(显示窗口)'}")
    
    # 步骤2: 手动导航到登录页面
    print("\n[步骤2] 手动导航到登录页...")
    result = await manager.navigate("https://github.com/login")
    
    if not result.get('success'):
        print(f"❌ 导航失败: {result.get('error')}")
        await manager.close_session(save=False)
        return
    
    print(f"✓ 已打开登录页面")
    print(f"  - URL: https://github.com/login")
    
    # 步骤3: 等待页面加载
    print("\n[步骤3] 等待页面加载...")
    await asyncio.sleep(2)
    print("✓ 页面加载完成")
    
    # 步骤4: 可选 - 获取页面状态
    print("\n[步骤4] 获取页面状态...")
    state = await manager.get_state(include_screenshot=False)
    
    if state.get('success'):
        print(f"✓ 页面信息:")
        print(f"  - 标题: {state['title']}")
        print(f"  - 可交互元素: {state['elements_count']} 个")
    
    # 步骤5: 等待用户手动完成登录
    print("\n" + "=" * 60)
    print("请在浏览器窗口中手动完成以下操作:")
    print("  1. 输入用户名和密码")
    print("  2. 完成 reCAPTCHA 或其他验证")
    print("  3. 点击登录按钮")
    print("  4. 等待登录成功")
    print("=" * 60)
    
    input("\n✋ 完成登录后,按 Enter 继续...")
    
    # 步骤6: 等待登录状态稳定
    print("\n[步骤5] 等待登录状态稳定...")
    await asyncio.sleep(2)
    print("✓ 等待完成")
    
    # 步骤7: 手动保存会话状态
    print("\n[步骤6] 手动保存会话状态...")
    result = await manager.save_session()
    
    if result.get('success'):
        print(f"✓ 会话已保存")
        print(f"  - 会话ID: {result['session_id']}")
        print(f"  - 存储位置: {result['storage_state_file']}")
    else:
        print(f"⚠ 保存失败: {result.get('error')}")
    
    # 步骤8: 手动关闭浏览器
    print("\n[步骤7] 手动关闭浏览器...")
    await manager.close_session(save=False)  # 已经手动保存过了
    print("✓ 浏览器已关闭")
    
    print("\n" + "=" * 60)
    print("✓ 首次登录完成! 会话状态已保存")
    print("  后续可以使用无头模式自动恢复登录状态")
    print("=" * 60)


async def automated_task():
    """自动化任务 - 无头模式,恢复登录状态"""
    print("\n" + "=" * 60)
    print("阶段2: 自动化任务 (无头模式)")
    print("=" * 60)
    
    manager = get_browser_manager()
    
    # 创建会话 - 使用无头模式,自动恢复之前保存的状态
    result = await manager.create_session(
        session_id="github_session",  # 使用相同的会话名
        headless=True  # 关键: 无头模式,后台运行
    )
    print(f"✓ 会话恢复: {result['message']}")
    print(f"  已恢复登录状态: {result['restored']}")
    
    # 直接访问需要登录的页面
    result = await manager.navigate("https://github.com/settings/profile")
    print(f"✓ 导航到个人设置: {result['message']}")
    
    # 获取页面状态
    state = await manager.get_state(include_screenshot=False)
    if state['success']:
        print(f"✓ 页面加载成功")
        print(f"  标题: {state['title']}")
        print(f"  URL: {state['url']}")
        print(f"  可交互元素: {state['elements_count']} 个")
    
    # 执行自动化操作...
    print("\n执行自动化操作...")
    await asyncio.sleep(2)
    
    # 保存并关闭
    await manager.close_session(save=True)
    print("✓ 任务完成,浏览器已关闭")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("混合模式示例: 处理需要人工验证的登录")
    print("=" * 60)
    
    # 检查是否已有保存的会话
    manager = get_browser_manager()
    sessions = await manager.list_sessions()
    
    has_saved_session = any(
        s['session_id'] == 'github_session' 
        for s in sessions.get('sessions', [])
    )
    
    if has_saved_session:
        print("\n检测到已保存的会话")
        choice = input("选择操作:\n  1. 重新登录(有头模式)\n  2. 使用已保存的会话(无头模式)\n请输入 (1/2): ")
        
        if choice == "1":
            await first_time_login()
        else:
            await automated_task()
    else:
        print("\n未检测到保存的会话,将进行首次登录")
        await first_time_login()
        
        # 询问是否立即执行自动化任务
        choice = input("\n是否立即执行自动化任务? (y/n): ")
        if choice.lower() == 'y':
            await automated_task()


if __name__ == "__main__":
    asyncio.run(main())
