#!/usr/bin/env python3
"""
Overleaf简历润色脚本
读取resume-zh_CN.tex内容，进行润色完善
"""

import asyncio
import sys
import os

# 添加browser_use_mcp到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'browser_use_mcp'))

from browser_tools import get_browser_manager

async def get_resume_content(manager):
    """获取简历内容"""
    print("\n获取简历内容...")
    
    # 等待编辑器加载
    await asyncio.sleep(3)
    
    # 提取页面内容
    content_result = await manager.extract_content()
    
    if content_result.get('success'):
        return content_result.get('text', '')
    else:
        print(f"⚠ 获取内容失败: {content_result.get('error')}")
        return None

async def polish_resume_content(original_content):
    """润色简历内容 - 这里可以集成AI进行润色"""
    print("\n正在润色简历内容...")
    
    # 这里可以调用AI API进行润色
    # 目前先返回一些基本的改进建议
    
    improvements = """
简历润色建议：

1. 教育背景部分：
   - 添加GPA或主要课程
   - 突出学术成就和奖项

2. 工作经验部分：
   - 使用动词开头描述工作内容（如：开发、设计、实现、优化）
   - 量化工作成果（如：提升性能30%，减少bug率50%）
   - 突出技术栈和项目规模

3. 项目经验部分：
   - 明确项目背景和目标
   - 详细描述技术方案和架构
   - 强调个人贡献和项目成果

4. 技能部分：
   - 按熟练程度分类（精通/熟悉/了解）
   - 突出核心技能和特长
   - 添加相关证书或认证

5. 格式优化：
   - 保持一致的格式和间距
   - 使用清晰的标题层级
   - 确保排版美观易读
"""
    
    return improvements

async def update_resume_in_editor(manager, new_content):
    """在编辑器中更新简历内容"""
    print("\n更新简历内容...")
    
    state = await manager.get_state(include_screenshot=False)
    
    # 查找编辑器
    editor_idx = None
    for idx, elem in enumerate(state['elements']):
        elem_str = str(elem).lower()
        if 'textarea' in elem_str or 'editor' in elem_str or 'ace' in elem_str:
            editor_idx = idx
            print(f"✓ 找到编辑器: 索引 {idx}")
            break
    
    if editor_idx is None:
        print("⚠ 未找到编辑器")
        return False
    
    # 点击编辑器获取焦点
    await manager.click_element(editor_idx)
    await asyncio.sleep(0.5)
    
    # 全选当前内容
    await manager.send_keys("Ctrl+a")
    await asyncio.sleep(0.3)
    
    # 输入新内容
    await manager.input_text(editor_idx, new_content, clear_first=False)
    await asyncio.sleep(1)
    
    print("✓ 简历内容已更新")
    return True

async def polish_resume_workflow():
    """简历润色工作流"""
    manager = get_browser_manager()
    
    print("=" * 60)
    print("Overleaf简历润色工作流")
    print("=" * 60)
    
    try:
        # 恢复会话
        print("\n[1/6] 恢复浏览器会话...")
        result = await manager.create_session(
            session_id="overleaf_session",
            headless=False  # 使用有头模式，方便查看
        )
        
        if not result.get('restored', False):
            print("❌ 未找到保存的会话，请先运行 step1_hybrid_login.py")
            return False
        
        print("✓ 会话恢复成功")
        
        # 导航到项目
        print("\n[2/6] 导航到项目...")
        await manager.navigate("https://www.overleaf.com/project")
        await asyncio.sleep(3)
        
        # 查找并进入项目
        print("\n[3/6] 进入项目 resume-master-260105...")
        state = await manager.get_state(include_screenshot=False)
        
        project_idx = None
        for idx, elem in enumerate(state['elements']):
            if 'resume-master-260105' in str(elem):
                project_idx = idx
                break
        
        if project_idx is None:
            print("❌ 未找到项目")
            await manager.close_session(save=True)
            return False
        
        await manager.click_element(project_idx)
        await asyncio.sleep(5)
        print("✓ 已进入项目")
        
        # 查找并打开文件
        print("\n[4/6] 打开文件 resume-zh_CN.tex...")
        state = await manager.get_state(include_screenshot=False)
        
        file_idx = None
        for idx, elem in enumerate(state['elements']):
            if 'resume-zh_CN.tex' in str(elem):
                file_idx = idx
                break
        
        if file_idx is None:
            print("⚠ 未找到文件，可能已经打开")
        else:
            await manager.click_element(file_idx)
            await asyncio.sleep(3)
            print("✓ 文件已打开")
        
        # 获取当前简历内容
        print("\n[5/6] 分析简历内容...")
        current_content = await get_resume_content(manager)
        
        if current_content:
            print(f"✓ 已获取简历内容 (长度: {len(current_content)} 字符)")
            
            # 保存原始内容到文件
            backup_file = "overleaf_workflow/resume_backup.txt"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(current_content)
            print(f"✓ 原始内容已备份到: {backup_file}")
            
            # 生成润色建议
            improvements = await polish_resume_content(current_content)
            
            # 保存润色建议
            suggestions_file = "overleaf_workflow/resume_polish_suggestions.txt"
            with open(suggestions_file, 'w', encoding='utf-8') as f:
                f.write(improvements)
            print(f"✓ 润色建议已保存到: {suggestions_file}")
            
            print("\n" + "=" * 60)
            print("润色建议：")
            print("=" * 60)
            print(improvements)
            print("=" * 60)
        
        # 交互式编辑模式
        print("\n[6/6] 进入交互式编辑模式...")
        print("\n可用操作:")
        print("  1. 查看当前页面状态")
        print("  2. 手动编辑（在浏览器中）")
        print("  3. 截图保存")
        print("  0. 完成并退出")
        
        while True:
            choice = input("\n请选择操作 (0-3): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                state = await manager.get_state(include_screenshot=False)
                print(f"\n标题: {state['title']}")
                print(f"URL: {state['url']}")
            elif choice == "2":
                print("\n请在浏览器窗口中手动编辑简历")
                input("编辑完成后按Enter继续...")
                print("✓ Overleaf会自动保存更改")
            elif choice == "3":
                result = await manager.screenshot()
                if result.get('success'):
                    print(f"✓ 截图已保存: {result['filepath']}")
            else:
                print("无效选择")
        
        # 保存会话
        await manager.close_session(save=True)
        
        print("\n" + "=" * 60)
        print("✓ 简历润色工作流完成!")
        print("=" * 60)
        print("\n📋 生成的文件:")
        print("  - resume_backup.txt: 原始简历备份")
        print("  - resume_polish_suggestions.txt: 润色建议")
        print("\n💡 提示:")
        print("  - Overleaf会自动保存所有更改")
        print("  - 可以在浏览器中查看编译后的PDF效果")
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

def main():
    """主函数"""
    success = asyncio.run(polish_resume_workflow())
    
    if success:
        print("\n✓ 简历润色完成")
        sys.exit(0)
    else:
        print("\n❌ 简历润色失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
