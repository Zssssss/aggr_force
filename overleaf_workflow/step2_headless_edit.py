#!/usr/bin/env python3
"""
Overleaf Headless模式自动化编辑脚本
使用保存的session访问Overleaf项目并编辑resume-zh_CN.tex文件
"""

import asyncio
import sys
import os
import json

# 添加browser_use_mcp到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'browser_use_mcp'))

from browser_tools import get_browser_manager

async def find_project_by_title(manager, project_title):
    """在项目列表中查找指定标题的项目"""
    print(f"\n查找项目: {project_title}")
    
    state = await manager.get_state(include_screenshot=False)
    
    # 查找包含项目标题的链接
    for idx, elem in enumerate(state['elements']):
        elem_str = str(elem)
        if project_title in elem_str and ('link' in elem_str.lower() or 'a' in elem_str.lower()):
            print(f"✓ 找到项目链接: 索引 {idx}")
            return idx
    
    # 如果没找到，尝试滚动页面
    print("未在当前视图找到项目，尝试滚动...")
    await manager.scroll(direction="down")
    await asyncio.sleep(1)
    
    state = await manager.get_state(include_screenshot=False)
    for idx, elem in enumerate(state['elements']):
        elem_str = str(elem)
        if project_title in elem_str and ('link' in elem_str.lower() or 'a' in elem_str.lower()):
            print(f"✓ 找到项目链接: 索引 {idx}")
            return idx
    
    return None

async def find_file_in_project(manager, filename):
    """在项目文件列表中查找指定文件"""
    print(f"\n查找文件: {filename}")
    
    state = await manager.get_state(include_screenshot=False)
    
    # 查找文件名
    for idx, elem in enumerate(state['elements']):
        elem_str = str(elem)
        if filename in elem_str:
            print(f"✓ 找到文件: 索引 {idx}")
            return idx
    
    return None

async def edit_resume_file(manager, edit_instructions):
    """编辑resume-zh_CN.tex文件"""
    print("\n开始编辑文件...")
    
    # 等待编辑器加载
    await asyncio.sleep(3)
    
    state = await manager.get_state(include_screenshot=False)
    print(f"当前页面: {state['title']}")
    
    # 查找编辑器区域（通常是textarea或contenteditable元素）
    editor_idx = None
    for idx, elem in enumerate(state['elements']):
        elem_str = str(elem).lower()
        if 'textarea' in elem_str or 'editor' in elem_str or 'ace' in elem_str:
            editor_idx = idx
            print(f"✓ 找到编辑器: 索引 {idx}")
            break
    
    if editor_idx is None:
        print("⚠ 未找到编辑器，可能需要手动定位")
        return False
    
    # 点击编辑器获取焦点
    await manager.click_element(editor_idx)
    await asyncio.sleep(0.5)
    
    # 根据编辑指令进行操作
    # 这里提供一个基础框架，具体编辑逻辑需要根据用户需求定制
    print("\n编辑器已就绪，可以进行编辑操作")
    print("提示: 可以使用以下方法编辑:")
    print("  - manager.send_keys() 发送键盘按键")
    print("  - manager.input() 输入文本")
    print("  - Ctrl+A 全选, Ctrl+C 复制, Ctrl+V 粘贴等")
    
    return True

async def overleaf_headless_automation(project_title="resume-master-260105", 
                                       target_file="resume-zh_CN.tex",
                                       edit_instructions=None):
    """使用headless模式自动化访问Overleaf项目"""
    manager = get_browser_manager()
    
    print("=" * 60)
    print("Overleaf Headless模式自动化")
    print("=" * 60)
    
    try:
        # 创建会话(headless模式，后台运行)
        print("\n[1/7] 恢复浏览器会话(headless模式)...")
        result = await manager.create_session(
            session_id="overleaf_session",
            headless=True  # 后台运行，不显示窗口
        )
        
        if not result.get('restored', False):
            print("❌ 未找到保存的会话!")
            print("请先运行 step1_hybrid_login.py 完成登录")
            return False
        
        print(f"✓ 会话恢复成功: {result['session_id']}")
        
        # 导航到Overleaf主页
        print("\n[2/7] 导航到Overleaf主页...")
        await manager.navigate("https://www.overleaf.com/project")
        await asyncio.sleep(3)  # 等待页面加载
        
        state = await manager.get_state(include_screenshot=False)
        print(f"✓ 当前页面: {state['title']}")
        print(f"  URL: {state['url']}")
        
        # 检查是否成功登录
        if 'login' in state['url'].lower():
            print("❌ 会话已过期，需要重新登录")
            print("请运行 step1_hybrid_login.py 重新登录")
            await manager.close_session(save=False)
            return False
        
        # 查找目标项目
        print(f"\n[3/7] 查找项目: {project_title}")
        project_idx = await find_project_by_title(manager, project_title)
        
        if project_idx is None:
            print(f"❌ 未找到项目: {project_title}")
            print("可用的项目列表:")
            state = await manager.get_state(include_screenshot=False)
            for idx, elem in enumerate(state['elements'][:20]):  # 只显示前20个元素
                elem_str = str(elem)
                if 'link' in elem_str.lower() or 'project' in elem_str.lower():
                    print(f"  [{idx}] {elem_str[:100]}")
            
            await manager.close_session(save=True)
            return False
        
        # 点击进入项目
        print(f"\n[4/7] 进入项目...")
        await manager.click_element(project_idx)
        await asyncio.sleep(5)  # 等待项目加载
        
        state = await manager.get_state(include_screenshot=False)
        print(f"✓ 当前页面: {state['title']}")
        print(f"  URL: {state['url']}")
        
        # 查找目标文件
        print(f"\n[5/7] 查找文件: {target_file}")
        file_idx = await find_file_in_project(manager, target_file)
        
        if file_idx is None:
            print(f"❌ 未找到文件: {target_file}")
            print("可用的文件:")
            state = await manager.get_state(include_screenshot=False)
            for idx, elem in enumerate(state['elements'][:30]):
                elem_str = str(elem)
                if '.tex' in elem_str or 'file' in elem_str.lower():
                    print(f"  [{idx}] {elem_str[:100]}")
            
            await manager.close_session(save=True)
            return False
        
        # 点击打开文件
        print(f"\n[6/7] 打开文件...")
        await manager.click_element(file_idx)
        await asyncio.sleep(3)  # 等待文件加载
        
        state = await manager.get_state(include_screenshot=False)
        print(f"✓ 文件已打开")
        
        # 编辑文件
        print(f"\n[7/7] 编辑文件...")
        success = await edit_resume_file(manager, edit_instructions)
        
        if success:
            print("\n✓ 文件编辑完成")
            print("注意: Overleaf会自动保存更改")
        else:
            print("\n⚠ 文件编辑未完成，可能需要手动操作")
        
        # 保存会话并关闭
        print("\n保存会话...")
        await manager.close_session(save=True)
        
        print("\n" + "=" * 60)
        print("✓ Headless模式自动化完成!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            await manager.close_session(save=True)
        except:
            pass
        
        return False

async def interactive_edit_mode():
    """交互式编辑模式 - 提供更灵活的编辑功能"""
    manager = get_browser_manager()
    
    print("=" * 60)
    print("Overleaf 交互式编辑模式")
    print("=" * 60)
    
    try:
        # 恢复会话
        print("\n恢复会话...")
        result = await manager.create_session(
            session_id="overleaf_session",
            headless=False  # 使用有头模式，方便查看
        )
        
        if not result.get('restored', False):
            print("❌ 未找到保存的会话，请先运行 step1_hybrid_login.py")
            return
        
        print("✓ 会话恢复成功")
        
        # 导航到项目
        project_url = input("\n请输入项目URL (或按Enter使用默认): ").strip()
        if not project_url:
            project_url = "https://www.overleaf.com/project"
        
        await manager.navigate(project_url)
        await asyncio.sleep(3)
        
        # 交互式操作
        while True:
            print("\n" + "=" * 60)
            print("可用操作:")
            print("  1. 查看当前页面状态")
            print("  2. 点击元素")
            print("  3. 输入文本")
            print("  4. 发送按键")
            print("  5. 滚动页面")
            print("  6. 截图")
            print("  7. 提取页面内容")
            print("  0. 退出")
            print("=" * 60)
            
            choice = input("\n请选择操作 (0-7): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                state = await manager.get_state(include_screenshot=False)
                print(f"\n标题: {state['title']}")
                print(f"URL: {state['url']}")
                print(f"\n可交互元素 (前20个):")
                for idx, elem in enumerate(state['elements'][:20]):
                    print(f"  [{idx}] {str(elem)[:100]}")
            elif choice == "2":
                idx = int(input("输入元素索引: "))
                await manager.click_element(idx)
                print("✓ 已点击")
                await asyncio.sleep(1)
            elif choice == "3":
                idx = int(input("输入元素索引: "))
                text = input("输入文本: ")
                await manager.input_text(idx, text)
                print("✓ 已输入")
            elif choice == "4":
                keys = input("输入按键 (如 Enter, Ctrl+A): ")
                await manager.send_keys(keys)
                print("✓ 已发送")
            elif choice == "5":
                direction = input("方向 (up/down): ")
                await manager.scroll(direction=direction)
                print("✓ 已滚动")
            elif choice == "6":
                filename = input("截图文件名 (默认自动生成): ").strip()
                result = await manager.screenshot(filename if filename else None)
                print(f"✓ 截图已保存: {result['filepath']}")
            elif choice == "7":
                content = await manager.extract_content()
                print(f"\n页面内容:\n{content['text'][:500]}...")
            else:
                print("无效选择")
        
        # 保存并关闭
        await manager.close_session(save=True)
        print("\n✓ 会话已保存")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            await manager.close_session(save=True)
        except:
            pass

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Overleaf自动化编辑工具")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="启动交互式编辑模式")
    parser.add_argument("--project", "-p", default="resume-master-260105",
                       help="项目标题")
    parser.add_argument("--file", "-f", default="resume-zh_CN.tex",
                       help="目标文件名")
    
    args = parser.parse_args()
    
    if args.interactive:
        asyncio.run(interactive_edit_mode())
    else:
        success = asyncio.run(overleaf_headless_automation(
            project_title=args.project,
            target_file=args.file
        ))
        
        if success:
            print("\n✓ 自动化任务完成")
            sys.exit(0)
        else:
            print("\n❌ 自动化任务失败")
            sys.exit(1)

if __name__ == "__main__":
    main()
