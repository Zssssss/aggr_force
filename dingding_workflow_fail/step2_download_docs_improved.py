#!/usr/bin/env python3
"""
钉钉文档自动下载脚本 - 改进版
使用MCP工具直接操作浏览器，更智能地查找下载按钮
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

async def find_and_click_more_button(manager):
    """查找并点击"更多"按钮（三个点）"""
    print("  查找'更多'按钮...")
    
    # 获取页面状态
    state = await manager.get_state(include_screenshot=True)
    if not state.get('success'):
        print("  ❌ 获取页面状态失败")
        return False
    
    elements = state.get('elements', [])
    print(f"  页面元素数量: {len(elements)}")
    
    # 保存截图用于调试
    screenshot_file = os.path.join(DOWNLOAD_DIR, 'debug_page.png')
    await manager.take_screenshot(filename='debug_page.png')
    print(f"  已保存调试截图")
    
    # 策略1: 查找包含特定文本的按钮
    keywords = ['更多', '...', '⋯', '︙', 'more', 'More', 'MORE', '操作', '设置']
    for idx, elem in enumerate(elements):
        text = elem.get('text', '').strip()
        tag = elem.get('tag', '')
        aria_label = elem.get('attributes', {}).get('aria-label', '')
        title = elem.get('attributes', {}).get('title', '')
        
        # 检查文本、aria-label或title
        search_text = f"{text} {aria_label} {title}".lower()
        if any(kw.lower() in search_text for kw in keywords):
            print(f"  找到候选按钮 [索引{idx}]: text='{text}', tag={tag}, aria-label='{aria_label}'")
            return idx
    
    # 策略2: 查找特定class或role的元素
    for idx, elem in enumerate(elements):
        attrs = elem.get('attributes', {})
        class_name = attrs.get('class', '')
        role = attrs.get('role', '')
        
        # 查找可能是菜单按钮的元素
        if 'menu' in class_name.lower() or 'more' in class_name.lower():
            print(f"  通过class找到候选 [索引{idx}]: class={class_name}")
            return idx
        
        if role in ['button', 'menuitem']:
            tag = elem.get('tag', '')
            if tag in ['button', 'a', 'div']:
                text = elem.get('text', '').strip()
                if len(text) < 10:  # 短文本更可能是按钮
                    print(f"  通过role找到候选 [索引{idx}]: role={role}, text='{text}'")
                    return idx
    
    print("  ❌ 未找到'更多'按钮")
    
    # 打印所有可能的按钮供调试
    print("\n  所有可交互元素:")
    for idx, elem in enumerate(elements[:50]):  # 只显示前50个
        text = elem.get('text', '').strip()
        tag = elem.get('tag', '')
        if tag in ['button', 'a'] and text:
            print(f"    [{idx}] {tag}: {text[:40]}")
    
    return None

async def find_and_click_download_option(manager):
    """查找并点击下载选项"""
    print("  查找下载选项...")
    
    state = await manager.get_state(include_screenshot=True)
    if not state.get('success'):
        print("  ❌ 获取页面状态失败")
        return False
    
    elements = state.get('elements', [])
    print(f"  菜单元素数量: {len(elements)}")
    
    # 查找下载相关选项
    keywords = ['下载到本地', '下载', 'download', 'Download', '导出', 'export', 'Export']
    for idx, elem in enumerate(elements):
        text = elem.get('text', '').strip()
        aria_label = elem.get('attributes', {}).get('aria-label', '')
        title = elem.get('attributes', {}).get('title', '')
        
        search_text = f"{text} {aria_label} {title}"
        if any(kw in search_text for kw in keywords):
            print(f"  找到下载选项 [索引{idx}]: {text}")
            return idx
    
    print("  ❌ 未找到下载选项")
    
    # 打印所有文本供调试
    print("\n  菜单中的所有文本:")
    for idx, elem in enumerate(elements[:30]):
        text = elem.get('text', '').strip()
        if text:
            print(f"    [{idx}] {text[:50]}")
    
    return None

async def find_and_click_md_format(manager):
    """查找并点击.md格式选项"""
    print("  查找.md格式选项...")
    
    state = await manager.get_state(include_screenshot=False)
    if not state.get('success'):
        return False
    
    elements = state.get('elements', [])
    
    # 查找.md或markdown选项
    for idx, elem in enumerate(elements):
        text = elem.get('text', '').strip().lower()
        if '.md' in text or 'markdown' in text:
            print(f"  找到.md格式 [索引{idx}]: {elem.get('text', '')}")
            return idx
    
    print("  未找到.md格式选项（可能已经是默认格式）")
    return None

async def download_document(manager, doc_title="文档"):
    """下载单个文档"""
    print(f"\n{'='*60}")
    print(f"下载: {doc_title}")
    print('='*60)
    
    try:
        # 等待页面稳定
        print("  等待页面加载...")
        await asyncio.sleep(3)
        
        # 步骤1: 查找并点击"更多"按钮
        more_idx = await find_and_click_more_button(manager)
        if more_idx is None:
            print("  ❌ 无法找到'更多'按钮")
            return False
        
        print(f"  点击'更多'按钮 [索引{more_idx}]...")
        result = await manager.click(more_idx)
        if not result.get('success'):
            print(f"  ❌ 点击失败: {result.get('error')}")
            return False
        
        print("  ✓ 已点击'更多'按钮")
        
        # 等待菜单出现
        await asyncio.sleep(2)
        
        # 步骤2: 查找并点击下载选项
        download_idx = await find_and_click_download_option(manager)
        if download_idx is None:
            print("  ❌ 无法找到下载选项")
            return False
        
        print(f"  点击下载选项 [索引{download_idx}]...")
        result = await manager.click(download_idx)
        if not result.get('success'):
            print(f"  ❌ 点击失败: {result.get('error')}")
            return False
        
        print("  ✓ 已点击下载选项")
        
        # 等待格式选择对话框
        await asyncio.sleep(2)
        
        # 步骤3: 选择.md格式（如果有）
        md_idx = await find_and_click_md_format(manager)
        if md_idx is not None:
            print(f"  选择.md格式 [索引{md_idx}]...")
            result = await manager.click(md_idx)
            if result.get('success'):
                print("  ✓ 已选择.md格式")
            await asyncio.sleep(1)
        
        # 等待下载开始
        print("  等待下载...")
        await asyncio.sleep(5)
        
        # 检查下载文件
        md_files = list(Path(DOWNLOAD_DIR).glob('*.md'))
        if md_files:
            latest_file = max(md_files, key=lambda p: p.stat().st_mtime)
            print(f"  ✓ 下载成功: {latest_file.name}")
            return True
        else:
            print("  ⚠ 未检测到下载文件")
            return False
        
    except Exception as e:
        print(f"  ❌ 下载出错: {e}")
        import traceback
        traceback.print_exc()
        return False

async def get_subdocuments(manager):
    """获取所有子文档链接"""
    print("\n查找子文档...")
    
    try:
        state = await manager.get_state(include_screenshot=False)
        if not state.get('success'):
            print("  ❌ 获取页面状态失败")
            return []
        
        elements = state.get('elements', [])
        subdocs = []
        seen_urls = set()
        
        # 查找钉钉文档链接
        for idx, elem in enumerate(elements):
            href = elem.get('attributes', {}).get('href', '')
            text = elem.get('text', '').strip()
            
            # 查找钉钉文档链接
            if 'alidocs.dingtalk.com' in href and '/nodes/' in href:
                if href not in seen_urls:
                    seen_urls.add(href)
                    subdocs.append({
                        'title': text if text else f'子文档{len(subdocs)+1}',
                        'url': href,
                        'index': idx
                    })
                    print(f"  找到子文档: {text[:40]}")
        
        print(f"  共找到 {len(subdocs)} 个子文档")
        return subdocs
        
    except Exception as e:
        print(f"  ❌ 查找子文档出错: {e}")
        return []

async def main():
    """主函数"""
    manager = get_browser_manager()
    
    print("=" * 60)
    print("钉钉文档自动下载 - 改进版")
    print("=" * 60)
    print(f"\n下载目录: {DOWNLOAD_DIR}")
    
    # 确保下载目录存在
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    try:
        # 步骤1: 恢复会话
        print("\n[步骤1] 恢复浏览器会话...")
        result = await manager.create_session(
            session_id="dingtalk_docs_session",
            headless=False  # 使用有头模式便于调试
        )
        
        if not result.get('success'):
            print(f"❌ 恢复会话失败: {result.get('error')}")
            print("   请先运行 step1_hybrid_login.py 完成登录")
            return False
        
        print(f"✓ 会话恢复成功")
        
        # 步骤2: 导航到主文档
        print("\n[步骤2] 导航到主文档...")
        doc_url = "https://alidocs.dingtalk.com/i/nodes/Amq4vjg89nvwRrTpkorOjKW3kdP0wQ"
        result = await manager.navigate(doc_url)
        
        if not result.get('success'):
            print(f"❌ 导航失败: {result.get('error')}")
            await manager.close_session(save=False)
            return False
        
        print(f"✓ 已打开主文档")
        
        # 步骤3: 下载主文档
        print("\n[步骤3] 下载主文档...")
        success = await download_document(manager, "2026-0105-0111(主文档)")
        
        if not success:
            print("⚠ 主文档下载失败")
        
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
                
                await asyncio.sleep(2)
                
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
        for md_file in sorted(md_files):
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

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
