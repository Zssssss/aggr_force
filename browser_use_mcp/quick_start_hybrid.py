#!/usr/bin/env python3
"""快速开始 - 混合模式登录助手

使用方法:
    python3 quick_start_hybrid.py

功能:
    1. 首次登录: 显示浏览器窗口,人工完成登录和验证
    2. 保存会话: 自动保存登录状态
    3. 后续使用: 无头模式自动恢复登录状态

适用场景:
    - 需要处理 reCAPTCHA 验证
    - 需要处理图片验证码
    - 需要处理短信/邮箱验证
    - 需要扫码登录
"""

import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from browser_tools import get_browser_manager


async def interactive_login():
    """交互式登录流程"""
    print("\n" + "=" * 70)
    print("  混合模式登录助手")
    print("=" * 70)
    
    # 获取用户输入
    print("\n请输入以下信息:")
    session_name = input("  会话名称 (如 github_work): ").strip()
    if not session_name:
        session_name = "default_session"
    
    login_url = input("  登录页面URL (如 https://github.com/login): ").strip()
    if not login_url:
        print("❌ 必须提供登录URL")
        return
    
    # 确保URL包含协议
    if not login_url.startswith(('http://', 'https://')):
        login_url = 'https://' + login_url
    
    manager = get_browser_manager()
    
    # 检查是否已有保存的会话
    sessions = await manager.list_sessions()
    existing_session = any(
        s['session_id'] == session_name 
        for s in sessions.get('sessions', [])
    )
    
    if existing_session:
        print(f"\n⚠️  检测到已存在的会话: {session_name}")
        choice = input("  是否覆盖? (y/n): ").strip().lower()
        if choice != 'y':
            print("已取消")
            return
    
    print("\n" + "=" * 70)
    print("  阶段1: 首次登录 (有头模式)")
    print("=" * 70)
    
    try:
        # 创建会话 - 有头模式
        print(f"\n[1/5] 创建浏览器会话: {session_name}")
        result = await manager.create_session(
            session_id=session_name,
            headless=False  # 显示浏览器窗口
        )
        
        if not result['success']:
            print(f"❌ 创建会话失败: {result.get('error')}")
            return
        
        print(f"✓ 会话已创建 (有头模式)")
        
        # 导航到登录页面
        print(f"\n[2/5] 导航到登录页面...")
        result = await manager.navigate(login_url)
        
        if not result['success']:
            print(f"❌ 导航失败: {result.get('error')}")
            await manager.close_session(save=False)
            return
        
        print(f"✓ 已打开: {login_url}")
        
        # 等待用户完成登录
        print("\n[3/5] 等待人工登录")
        print("-" * 70)
        print("  请在浏览器窗口中完成以下操作:")
        print("    1. 输入用户名和密码")
        print("    2. 完成验证码/reCAPTCHA (如果有)")
        print("    3. 点击登录按钮")
        print("    4. 等待登录成功,进入主页面")
        print("-" * 70)
        
        input("\n  完成登录后,按 Enter 继续...")
        
        # 保存会话状态
        print("\n[4/5] 保存会话状态...")
        result = await manager.save_session()
        
        if not result['success']:
            print(f"❌ 保存失败: {result.get('error')}")
            await manager.close_session(save=False)
            return
        
        print(f"✓ 会话已保存")
        print(f"  存储位置: {result['storage_state_file']}")
        
        # 关闭浏览器
        print("\n[5/5] 关闭浏览器...")
        await manager.close_session(save=False)  # 已经保存过了
        print("✓ 浏览器已关闭")
        
        print("\n" + "=" * 70)
        print("  ✓ 登录成功! 会话状态已保存")
        print("=" * 70)
        print(f"\n后续使用方法:")
        print(f"  1. Python代码:")
        print(f"     await manager.create_session('{session_name}', headless=True)")
        print(f"\n  2. 通过AI助手:")
        print(f"     \"使用会话 {session_name} 访问...\"")
        print("\n会话将自动恢复登录状态,无需重新登录!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
        await manager.close_session(save=False)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        await manager.close_session(save=False)


async def test_saved_session():
    """测试已保存的会话"""
    print("\n" + "=" * 70)
    print("  测试已保存的会话")
    print("=" * 70)
    
    manager = get_browser_manager()
    
    # 列出所有会话
    sessions = await manager.list_sessions()
    
    if not sessions.get('sessions'):
        print("\n❌ 没有保存的会话")
        print("请先运行登录流程创建会话")
        return
    
    print("\n可用的会话:")
    for i, session in enumerate(sessions['sessions'], 1):
        import datetime
        modified = datetime.datetime.fromtimestamp(session['modified_at'])
        print(f"  {i}. {session['session_id']}")
        print(f"     最后修改: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 选择会话
    choice = input(f"\n选择要测试的会话 (1-{len(sessions['sessions'])}): ").strip()
    
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(sessions['sessions']):
            print("❌ 无效的选择")
            return
    except ValueError:
        print("❌ 无效的输入")
        return
    
    session_name = sessions['sessions'][index]['session_id']
    
    print(f"\n测试会话: {session_name}")
    
    # 询问测试URL
    test_url = input("输入要访问的URL (留空则跳过): ").strip()
    
    try:
        # 创建会话 - 无头模式
        print("\n[1/3] 恢复会话 (无头模式)...")
        result = await manager.create_session(
            session_id=session_name,
            headless=True  # 无头模式
        )
        
        if not result['success']:
            print(f"❌ 恢复会话失败: {result.get('error')}")
            return
        
        print(f"✓ 会话已恢复")
        print(f"  登录状态: {'已恢复' if result['restored'] else '新会话'}")
        
        if test_url:
            # 确保URL包含协议
            if not test_url.startswith(('http://', 'https://')):
                test_url = 'https://' + test_url
            
            # 访问测试URL
            print(f"\n[2/3] 访问测试页面...")
            result = await manager.navigate(test_url)
            
            if not result['success']:
                print(f"❌ 访问失败: {result.get('error')}")
            else:
                print(f"✓ 已访问: {test_url}")
                
                # 获取页面状态
                print(f"\n[3/3] 获取页面状态...")
                state = await manager.get_state(include_screenshot=False)
                
                if state['success']:
                    print(f"✓ 页面加载成功")
                    print(f"  标题: {state['title']}")
                    print(f"  URL: {state['url']}")
                    print(f"  可交互元素: {state['elements_count']} 个")
                    
                    # 显示部分页面文本
                    if state.get('dom_text'):
                        text = state['dom_text'][:200]
                        print(f"\n  页面内容预览:")
                        print(f"  {text}...")
        
        # 关闭
        await manager.close_session(save=True)
        print("\n✓ 测试完成,浏览器已关闭")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        await manager.close_session(save=False)


async def manage_sessions():
    """管理会话"""
    print("\n" + "=" * 70)
    print("  会话管理")
    print("=" * 70)
    
    manager = get_browser_manager()
    sessions = await manager.list_sessions()
    
    if not sessions.get('sessions'):
        print("\n没有保存的会话")
        return
    
    print("\n已保存的会话:")
    for i, session in enumerate(sessions['sessions'], 1):
        import datetime
        modified = datetime.datetime.fromtimestamp(session['modified_at'])
        size_kb = session['size_bytes'] / 1024
        print(f"\n  {i}. {session['session_id']}")
        print(f"     最后修改: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"     文件大小: {size_kb:.1f} KB")
        print(f"     存储位置: {session['storage_state_file']}")
    
    print("\n操作:")
    print("  1. 删除会话")
    print("  2. 返回")
    
    choice = input("\n选择操作 (1-2): ").strip()
    
    if choice == "1":
        session_num = input(f"选择要删除的会话 (1-{len(sessions['sessions'])}): ").strip()
        try:
            index = int(session_num) - 1
            if 0 <= index < len(sessions['sessions']):
                session_name = sessions['sessions'][index]['session_id']
                confirm = input(f"确认删除会话 '{session_name}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    result = await manager.delete_session(session_name)
                    if result['success']:
                        print(f"✓ 会话 '{session_name}' 已删除")
                    else:
                        print(f"❌ 删除失败: {result.get('error')}")
        except ValueError:
            print("❌ 无效的输入")


async def main():
    """主菜单"""
    while True:
        print("\n" + "=" * 70)
        print("  混合模式登录助手 - 主菜单")
        print("=" * 70)
        print("\n选择操作:")
        print("  1. 首次登录 (有头模式 - 人工处理验证)")
        print("  2. 测试已保存的会话 (无头模式)")
        print("  3. 管理会话")
        print("  4. 退出")
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == "1":
            await interactive_login()
        elif choice == "2":
            await test_saved_session()
        elif choice == "3":
            await manage_sessions()
        elif choice == "4":
            print("\n再见!")
            break
        else:
            print("\n❌ 无效的选择")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序已退出")
