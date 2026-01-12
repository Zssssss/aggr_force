#!/usr/bin/env python3
"""
钉钉文档自动下载脚本 - 使用保存的session
下载主文档及所有子文档为markdown格式

目标文档: https://alidocs.dingtalk.com/i/nodes/Amq4vjg89nvwRrZwTpkorOjKW3kdP0wQ
文档标题: 2026-0105-0111
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# 添加browser_use_mcp到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'browser_use_mcp'))

from browser_tools import get_browser_manager

# 下载目录
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloaded_docs')

async def wait_for_download(download_dir, timeout=30):
    """等待下载完成"""
    print(f"  等待下载完成...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # 检查是否有.crdownload临时文件（Chrome下载中）
        temp_files = list(Path(download_dir).glob('*.crdownload'))
        if not temp_files:
            # 检查是否有新的.md文件
            md_files = list(Path(download_dir).glob('*.md'))
            if md_files:
                print(f"  ✓ 下载完成")
                return True
        await asyncio.sleep(1)
    
    print(f"  ⚠ 下载超时")
    return False

async def download_document(manager, doc_title="主文档"):
    """下载单个文档"""
    print(f"\n[下载] {doc_title}")
    
    try:
        # 等待页面稳定
        await asyncio.sleep(2)
        
        # 获取页面状态
        state = await manager.get_state(include_screenshot=True)
        if not state.get('success'):
            print(f"  ❌ 获取页面状态失败")
            return False
        
        print(f"  当前页面: {state.get('title', 'N/A')}")
        print(f"  可交互元素数量: {len(state.get('elements', []))}")
        
        # 查找"更多"按钮或菜单
        elements = state.get('elements', [])
        more_button_idx = None
        
        # 尝试多种可能的文本匹配
        for idx, elem in enumerate(elements):
            text = elem.get('text', '').strip()
            tag = elem.get('tag', '')
            
            # 查找"更多"、"..."、"⋯"等按钮
            if any(keyword in text for keyword in ['更多', '...', '⋯', 'more', 'More']):
                print(f"  找到更多按钮 [索引{idx}]: {text} ({tag})")
                more_button_idx = idx
                break
        
        if more_button_idx is None:
            print(f"  ⚠ 未找到'更多'按钮，尝试查找下载相关按钮...")
            # 直接查找下载按钮
            for idx, elem in enumerate(elements):
                text = elem.get('text', '').strip()
                if any(keyword in text for keyword in ['下载', 'download', 'Download', '导出', 'export']):
                    print(f"  找到下载相关按钮 [索引{idx}]: {text}")
                    more_button_idx = idx
                    break
        
        if more_button_idx is None:
            print(f"  ❌ 未找到下载入口")
            # 保存截图用于调试
            screenshot_result = await manager.take_screenshot(filename=f'debug_{doc_title}.png')
            if screenshot_result.get('success'):
                print(f"  已保存调试截图: {screenshot_result['filepath']}")
            return False
        
        # 点击"更多"按钮
        print(f"  点击按钮 [索引{more_button_idx}]...")
        result = await manager.click(more_button_idx)
        if not result.get('success'):
            print(f"  ❌ 点击失败: {result.get('error')}")
            return False
        
        # 等待菜单出现
        await asyncio.sleep(2)
        
        # 获取新的页面状态
        state = await manager.get_state(include_screenshot=True)
        if not state.get('success'):
            print(f"  ❌ 获取菜单状态失败")
            return False
        
        elements = state.get('elements', [])
        print(f"  菜单展开后元素数量: {len(elements)}")
        
        # 查找"下载到本地"或".md"选项
        download_idx = None
        for idx, elem in enumerate(elements):
            text = elem.get('text', '').strip()
            # 查找下载相关选项
            if any(keyword in text for keyword in ['下载到本地', '下载', '.md', 'markdown', 'Markdown', 'MD']):
                print(f"  找到下载选项 [索引{idx}]: {text}")
                download_idx = idx
                break
        
        if download_idx is None:
            print(f"  ⚠ 未找到下载选项，列出所有可见文本:")
            for idx, elem in enumerate(elements):
                text = elem.get('text', '').strip()
                if text:
                    print(f"    [{idx}] {text[:50]}")
            return False
        
        # 点击下载选项
        print(f"  点击下载选项 [索引{download_idx}]...")
        result = await manager.click(download_idx)
        if not result.get('success'):
            print(f"  ❌ 点击失败: {result.get('error')}")
            return False
        
        # 等待下载开始
        await asyncio.sleep(2)
        
        # 如果出现格式选择，查找.md格式
        state = await manager.get_state(include_screenshot=False)
        elements = state.get('elements', [])
        
        md_format_idx = None
        for idx, elem in enumerate(elements):
            text = elem.get('text', '').strip()
            if '.md' in text.lower() or 'markdown' in text.lower():
                print(f"  找到.md格式选项 [索引{idx}]: {text}")
                md_format_idx = idx
                break
        
        if md_format_idx is not None:
            print(f"  选择.md格式...")
            result = await manager.click(md_format_idx)
            if not result.get('success'):
                print(f"  ❌ 选择格式失败: {result.get('error')}")
                return False
            await asyncio.sleep(1)
        
        # 等待下载完成
        success = await wait_for_download(DOWNLOAD_DIR, timeout=30)
        
        if success:
            print(f"  ✓ {doc_title} 下载成功")
            return True
        else:
            print(f"  ⚠ {doc_title} 下载可能未完成")
            return False
            
    except Exception as e:
        print(f"  ❌ 下载出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def get_subdocuments(manager):
    """获取所有子文档链接"""
    print("\n[查找子文档]")
    
    try:
        state = await manager.get_state(include_screenshot=False)
        if not state.get('success'):
            print("  ❌ 获取页面状态失败")
            return []
        
        elements = state.get('elements', [])
        subdocs = []
        
        # 查找文档树或子文档链接
        for idx, elem in enumerate(elements):
            tag = elem.get('tag', '')
            text = elem.get('text', '').strip()
            href = elem.get('attributes', {}).get('href', '')
            
            # 查找钉钉文档链接
            if 'alidocs.dingtalk.com' in href and '/nodes/' in href:
                if href not in [sd['url'] for sd in subdocs]:
                    subdocs.append({
                        'title': text if text else f'子文档{len(subdocs)+1}',
                        'url': href,
                        'index': idx
                    })
                    print(f"  找到子文档: {text[:30]}")
        
        print(f"  共找到 {len(subdocs)} 个子文档")
        return subdocs
        
    except Exception as e:
        print(f"  ❌ 查找子文档出错: {e}")
        return []

async def download_all_documents():
    """下载主文档及所有子文档"""
    manager = get_browser_manager()
    
    print("=" * 60)
    print("钉钉文档自动下载")
    print("=" * 60)
    print(f"\n下载目录: {DOWNLOAD_DIR}")
    
    # 确保下载目录存在
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    try:
        # 步骤1: 使用保存的session创建会话（headless模式）
        print("\n[步骤1] 恢复浏览器会话...")
        result = await manager.create_session(
            session_id="dingtalk_docs_session",
            headless=False  # 使用有头模式以便调试
        )
        
        if not result.get('success'):
            print(f"❌ 恢复会话失败: {result.get('error')}")
            print("   请先运行 step1_hybrid_login.py 完成登录")
            return False
        
        print(f"✓ 会话恢复成功")
        
        # 步骤2: 导航到主文档
        print("\n[步骤2] 导航到主文档...")
        doc_url = "https://alidocs.dingtalk.com/i/nodes/Amq4vjg89nvwRrZwTpkorOjKW3kdP0wQ"
        result = await manager.navigate(doc_url)
        
        if not result.get('success'):
            print(f"❌ 导航失败: {result.get('error')}")
            await manager.close_session(save=False)
            return False
        
        print(f"✓ 已打开主文档")
        
        # 等待页面加载
        await asyncio.sleep(5)
        
        # 步骤3: 下载主文档
        print("\n[步骤3] 下载主文档...")
        success = await download_document(manager, "2026-0105-0111(主文档)")
        
        if not success:
            print("⚠ 主文档下载失败，但继续尝试子文档...")
        
        # 步骤4: 查找并下载子文档
        print("\n[步骤4] 查找子文档...")
        subdocs = await get_subdocuments(manager)
        
        if subdocs:
            print(f"\n找到 {len(subdocs)} 个子文档，开始下载...")
            
            for i, subdoc in enumerate(subdocs, 1):
                print(f"\n--- 子文档 {i}/{len(subdocs)} ---")
                
                # 导航到子文档
                print(f"  导航到: {subdoc['title']}")
                result = await manager.navigate(subdoc['url'])
                
                if not result.get('success'):
                    print(f"  ❌ 导航失败，跳过")
                    continue
                
                await asyncio.sleep(3)
                
                # 下载子文档
                await download_document(manager, subdoc['title'])
        else:
            print("  未找到子文档")
        
        # 步骤5: 关闭浏览器
        print("\n[步骤5] 关闭浏览器...")
        await manager.close_session(save=True)
        print("✓ 浏览器已关闭")
        
        # 统计下载结果
        print("\n" + "=" * 60)
        print("下载完成!")
        print("=" * 60)
        
        md_files = list(Path(DOWNLOAD_DIR).glob('*.md'))
        print(f"\n已下载 {len(md_files)} 个文档:")
        for md_file in md_files:
            size = md_file.stat().st_size
            print(f"  - {md_file.name} ({size} bytes)")
        
        print(f"\n文档保存位置: {DOWNLOAD_DIR}")
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
    success = asyncio.run(download_all_documents())
    
    if success:
        print("\n✓ 任务完成！")
        sys.exit(0)
    else:
        print("\n❌ 任务失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
