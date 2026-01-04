#!/usr/bin/env python3
"""Browser Use 工具模块 - 基于 Playwright 的浏览器操作能力

这个模块使用 Playwright 直接操作浏览器，供 AI 助手直接调用。
完全在 WSL 中执行，使用 Playwright 内置的 Chromium 浏览器。

核心功能：
1. 浏览器会话管理（创建、保存、恢复、关闭）
2. 页面导航（打开URL、前进、后退、刷新、搜索）
3. DOM 状态获取（获取可交互元素列表，带索引）
4. 元素交互（点击、输入、滚动、下拉框选择）
5. 标签页管理（切换、关闭、新建）
6. 内容提取（截图、Markdown 提取）
7. 文件上传
8. 坐标点击（用于特殊场景）

凭证管理：
- 凭证存储在 .env 文件中（browser_use_mcp/.env）
- 支持的凭证键：GITHUB_USERNAME, GITHUB_PASSWORD, EMAIL 等
- AI 只能通过 credential_key 引用凭证，无法看到实际值
"""

import asyncio
import json
import os
import base64
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging
import datetime

logger = logging.getLogger(__name__)


# 凭证存储（从 .env 文件加载）
_credentials: Dict[str, str] = {}
_credentials_loaded: bool = False


def _get_env_file_path() -> Path:
    """获取 .env 文件路径"""
    return Path(__file__).parent / ".env"


def load_credentials() -> Dict[str, str]:
    """从 .env 文件加载凭证
    
    .env 文件格式：
    GITHUB_USERNAME=your_username
    GITHUB_PASSWORD=your_password
    EMAIL=your_email@example.com
    """
    global _credentials, _credentials_loaded
    
    if _credentials_loaded:
        return _credentials
    
    env_file = _get_env_file_path()
    
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    # 解析 KEY=VALUE 格式
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 移除引号
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        _credentials[key] = value
            logger.info(f"已从 {env_file} 加载 {len(_credentials)} 个凭证")
        except Exception as e:
            logger.error(f"加载 .env 文件失败: {e}")
    else:
        logger.warning(f".env 文件不存在: {env_file}")
    
    _credentials_loaded = True
    return _credentials


def get_credential(key: str) -> Optional[str]:
    """获取凭证值（按需加载）"""
    load_credentials()
    return _credentials.get(key)


def list_credential_keys() -> List[str]:
    """列出所有可用的凭证键名（不暴露值）"""
    load_credentials()
    return list(_credentials.keys())


def reload_credentials() -> Dict[str, str]:
    """重新加载凭证"""
    global _credentials, _credentials_loaded
    _credentials = {}
    _credentials_loaded = False
    return load_credentials()


class PlaywrightBrowserManager:
    """基于 Playwright 的浏览器管理器
    
    直接使用 Playwright 操作浏览器，完全在 WSL 中执行。
    """
    
    def __init__(self, session_dir: Optional[str] = None):
        """
        初始化浏览器管理器
        
        Args:
            session_dir: 会话数据存储目录，默认为 ~/.browser_use_mcp/sessions
        """
        self.session_dir = Path(session_dir) if session_dir else Path.home() / ".browser_use_mcp" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._current_session_id: Optional[str] = None
        
        # 元素索引映射
        self._element_map: Dict[int, dict] = {}
        
    def _get_storage_state_file(self, session_id: str) -> Path:
        """获取存储状态文件路径"""
        return self.session_dir / f"{session_id}_storage_state.json"
    
    def _get_sensitive_data(self) -> Dict[str, str]:
        """获取敏感数据（从 .env 文件加载）"""
        return load_credentials()
    
    async def create_session(
        self,
        session_id: str,
        headless: bool = False,
    ) -> Dict[str, Any]:
        """
        创建或恢复浏览器会话
        
        使用 Playwright 内置的 Chromium 浏览器，完全在 WSL 中执行。
        
        Args:
            session_id: 会话标识符
            headless: 是否无头模式
            
        Returns:
            会话信息字典
        """
        from playwright.async_api import async_playwright
        
        # 关闭现有会话
        if self._browser:
            await self.close_session(save=True)
        
        storage_state_file = self._get_storage_state_file(session_id)
        
        # 检查是否有保存的会话状态
        restored = storage_state_file.exists()
        
        try:
            # 启动 Playwright
            self._playwright = await async_playwright().start()
            
            # 启动浏览器
            self._browser = await self._playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                ]
            )
            
            # 创建浏览器上下文
            context_options = {
                'viewport': {'width': 1280, 'height': 720},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            if restored:
                context_options['storage_state'] = str(storage_state_file)
            
            self._context = await self._browser.new_context(**context_options)
            
            # 创建页面
            self._page = await self._context.new_page()
            
            self._current_session_id = session_id
            
            now = datetime.datetime.now().isoformat()
            
            return {
                "success": True,
                "session_id": session_id,
                "message": f"会话 '{session_id}' 已创建 (Playwright 模式)",
                "restored": restored,
                "created_at": now,
                "headless": headless,
            }
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
    
    async def save_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """保存当前会话状态"""
        session_id = session_id or self._current_session_id
        
        if not session_id:
            return {"success": False, "error": "没有活动的会话"}
        
        if not self._context:
            return {"success": False, "error": "浏览器上下文未初始化"}
        
        try:
            storage_state_file = self._get_storage_state_file(session_id)
            await self._context.storage_state(path=str(storage_state_file))
            
            return {
                "success": True,
                "session_id": session_id,
                "storage_state_file": str(storage_state_file),
                "message": f"会话 '{session_id}' 已保存",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close_session(self, save: bool = True) -> Dict[str, Any]:
        """关闭当前会话"""
        result = {"success": True, "message": "会话已关闭"}
        
        if save and self._current_session_id and self._context:
            save_result = await self.save_session()
            result["saved"] = save_result.get("success", False)
        
        try:
            if self._page:
                await self._page.close()
                self._page = None
            
            if self._context:
                await self._context.close()
                self._context = None
            
            if self._browser:
                await self._browser.close()
                self._browser = None
            
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
        except Exception as e:
            logger.error(f"关闭会话时出错: {e}")
        
        self._current_session_id = None
        self._element_map = {}
        
        return result
    
    async def _ensure_page(self):
        """确保页面已创建"""
        if not self._page:
            raise RuntimeError("没有活动的浏览器会话，请先创建会话")
    
    async def navigate(self, url: str, new_tab: bool = False) -> Dict[str, Any]:
        """
        导航到指定 URL
        
        Args:
            url: 目标 URL
            new_tab: 是否在新标签页打开
            
        Returns:
            导航结果
        """
        try:
            await self._ensure_page()
            
            if new_tab:
                self._page = await self._context.new_page()
            
            await self._page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # 等待页面稳定
            await asyncio.sleep(1)
            
            return {
                "success": True,
                "url": url,
                "new_tab": new_tab,
                "message": f"已导航到 {url}" + (" (新标签页)" if new_tab else ""),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def go_back(self) -> Dict[str, Any]:
        """后退到上一页"""
        try:
            await self._ensure_page()
            await self._page.go_back()
            
            return {
                "success": True,
                "message": "已后退到上一页",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _build_element_map(self) -> List[dict]:
        """构建可交互元素映射"""
        await self._ensure_page()
        
        # 获取所有可交互元素
        elements = await self._page.evaluate('''() => {
            const interactiveSelectors = [
                'a[href]',
                'button',
                'input',
                'textarea',
                'select',
                '[role="button"]',
                '[role="link"]',
                '[role="textbox"]',
                '[role="checkbox"]',
                '[role="radio"]',
                '[role="combobox"]',
                '[role="menuitem"]',
                '[role="tab"]',
                '[onclick]',
                '[tabindex]:not([tabindex="-1"])',
            ];
            
            const elements = [];
            const seen = new Set();
            
            for (const selector of interactiveSelectors) {
                const nodes = document.querySelectorAll(selector);
                for (const node of nodes) {
                    // 跳过隐藏元素
                    const style = window.getComputedStyle(node);
                    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                        continue;
                    }
                    
                    // 跳过已处理的元素
                    if (seen.has(node)) continue;
                    seen.add(node);
                    
                    const rect = node.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    
                    const element = {
                        tag: node.tagName.toLowerCase(),
                        text: (node.innerText || node.value || '').substring(0, 100).trim(),
                        type: node.type || null,
                        name: node.name || null,
                        placeholder: node.placeholder || null,
                        href: node.href || null,
                        role: node.getAttribute('role') || null,
                        ariaLabel: node.getAttribute('aria-label') || null,
                        id: node.id || null,
                        className: node.className || null,
                        rect: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                        },
                        // 生成唯一选择器
                        selector: generateSelector(node),
                    };
                    
                    elements.push(element);
                }
            }
            
            function generateSelector(el) {
                if (el.id) return '#' + CSS.escape(el.id);
                
                let path = [];
                while (el && el.nodeType === Node.ELEMENT_NODE) {
                    let selector = el.tagName.toLowerCase();
                    if (el.id) {
                        selector = '#' + CSS.escape(el.id);
                        path.unshift(selector);
                        break;
                    }
                    
                    let sibling = el;
                    let nth = 1;
                    while (sibling = sibling.previousElementSibling) {
                        if (sibling.tagName === el.tagName) nth++;
                    }
                    
                    if (nth > 1) selector += ':nth-of-type(' + nth + ')';
                    path.unshift(selector);
                    el = el.parentElement;
                    
                    if (path.length > 5) break;
                }
                
                return path.join(' > ');
            }
            
            return elements;
        }''')
        
        # 构建索引映射
        self._element_map = {}
        result = []
        
        for i, el in enumerate(elements):
            self._element_map[i] = el
            result.append({
                "index": i,
                "tag": el['tag'],
                "text": el['text'],
                "type": el.get('type'),
                "name": el.get('name'),
                "placeholder": el.get('placeholder'),
                "href": el.get('href'),
                "role": el.get('role'),
                "aria_label": el.get('ariaLabel'),
            })
        
        return result
    
    async def get_state(self, include_screenshot: bool = True) -> Dict[str, Any]:
        """
        获取当前浏览器状态，包括可交互元素列表
        
        Args:
            include_screenshot: 是否包含截图
            
        Returns:
            浏览器状态
        """
        try:
            await self._ensure_page()
            
            # 获取基本信息
            url = self._page.url
            title = await self._page.title()
            
            # 获取所有标签页
            tabs = []
            for i, page in enumerate(self._context.pages):
                tabs.append({
                    "id": i,
                    "url": page.url,
                    "title": await page.title(),
                })
            
            # 构建元素映射
            elements = await self._build_element_map()
            
            result = {
                "success": True,
                "url": url,
                "title": title,
                "tabs": tabs,
                "elements": elements,
                "elements_count": len(elements),
            }
            
            # 获取页面文本内容（简化版）
            dom_text = await self._page.evaluate('''() => {
                return document.body.innerText.substring(0, 5000);
            }''')
            result["dom_text"] = dom_text
            
            # 截图
            if include_screenshot:
                screenshot_bytes = await self._page.screenshot(type='png')
                result["screenshot_base64"] = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            return result
            
        except Exception as e:
            import traceback
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
    
    async def click_element(self, index: int) -> Dict[str, Any]:
        """
        点击指定索引的元素
        
        Args:
            index: 元素索引
            
        Returns:
            点击结果
        """
        try:
            await self._ensure_page()
            
            if index not in self._element_map:
                # 重新构建元素映射
                await self._build_element_map()
                if index not in self._element_map:
                    return {"success": False, "error": f"元素索引 {index} 不存在"}
            
            element = self._element_map[index]
            selector = element['selector']
            
            await self._page.click(selector, timeout=5000)
            
            # 等待页面响应
            await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "index": index,
                "message": f"已点击元素 {index}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def input_text(self, index: int, text: str, clear_first: bool = True) -> Dict[str, Any]:
        """
        在指定索引的输入框中输入文本
        
        Args:
            index: 元素索引
            text: 要输入的文本
            clear_first: 是否先清空输入框
            
        Returns:
            输入结果
        """
        try:
            await self._ensure_page()
            
            if index not in self._element_map:
                await self._build_element_map()
                if index not in self._element_map:
                    return {"success": False, "error": f"元素索引 {index} 不存在"}
            
            element = self._element_map[index]
            selector = element['selector']
            
            if clear_first:
                await self._page.fill(selector, text, timeout=5000)
            else:
                await self._page.type(selector, text, timeout=5000)
            
            return {
                "success": True,
                "index": index,
                "text_length": len(text),
                "message": f"已在元素 {index} 中输入 {len(text)} 个字符",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def input_sensitive(self, index: int, credential_key: str, clear_first: bool = True) -> Dict[str, Any]:
        """
        安全地在输入框中填入敏感数据
        
        Args:
            index: 元素索引
            credential_key: 敏感数据键名
            clear_first: 是否先清空输入框
            
        Returns:
            输入结果（不包含实际值）
        """
        sensitive_data = self._get_sensitive_data()
        
        if credential_key not in sensitive_data:
            available_keys = list(sensitive_data.keys())
            env_file = _get_env_file_path()
            return {
                "success": False,
                "error": f"凭证 '{credential_key}' 未配置",
                "available_keys": available_keys,
                "hint": f"请在 {env_file} 文件中添加: {credential_key}=your_value",
            }
        
        text = sensitive_data[credential_key]
        result = await self.input_text(index, text, clear_first)
        
        if result.get("success"):
            result["message"] = f"已安全填入 {credential_key}（值已隐藏）"
            result.pop("text_length", None)
        
        return result
    
    async def send_keys(self, keys: str) -> Dict[str, Any]:
        """
        发送键盘按键
        
        Args:
            keys: 按键字符串，如 'Enter', 'Tab', 'Escape' 等
            
        Returns:
            按键结果
        """
        try:
            await self._ensure_page()
            
            await self._page.keyboard.press(keys)
            
            return {
                "success": True,
                "keys": keys,
                "message": f"已发送按键: {keys}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def scroll(self, direction: str = "down", index: Optional[int] = None) -> Dict[str, Any]:
        """
        滚动页面或元素
        
        Args:
            direction: 滚动方向，'up' 或 'down'
            index: 元素索引（可选）
            
        Returns:
            滚动结果
        """
        try:
            await self._ensure_page()
            
            delta = 500 if direction == "down" else -500
            
            if index is not None and index in self._element_map:
                element = self._element_map[index]
                selector = element['selector']
                await self._page.evaluate(f'''(delta) => {{
                    const el = document.querySelector("{selector}");
                    if (el) el.scrollBy(0, delta);
                }}''', delta)
            else:
                await self._page.evaluate(f'window.scrollBy(0, {delta})')
            
            target = f"元素 {index}" if index else "页面"
            return {
                "success": True,
                "direction": direction,
                "target": target,
                "message": f"已向{'下' if direction == 'down' else '上'}滚动{target}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def switch_tab(self, tab_index: int) -> Dict[str, Any]:
        """
        切换到指定标签页
        
        Args:
            tab_index: 标签页索引
            
        Returns:
            切换结果
        """
        try:
            await self._ensure_page()
            
            pages = self._context.pages
            if tab_index < 0 or tab_index >= len(pages):
                return {"success": False, "error": f"标签页索引 {tab_index} 不存在"}
            
            self._page = pages[tab_index]
            await self._page.bring_to_front()
            
            # 重新构建元素映射
            self._element_map = {}
            
            return {
                "success": True,
                "tab_index": tab_index,
                "message": f"已切换到标签页 {tab_index}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close_tab(self, tab_index: Optional[int] = None) -> Dict[str, Any]:
        """
        关闭标签页
        
        Args:
            tab_index: 标签页索引（可选）
            
        Returns:
            关闭结果
        """
        try:
            await self._ensure_page()
            
            pages = self._context.pages
            
            if tab_index is not None:
                if tab_index < 0 or tab_index >= len(pages):
                    return {"success": False, "error": f"标签页索引 {tab_index} 不存在"}
                page_to_close = pages[tab_index]
            else:
                page_to_close = self._page
            
            await page_to_close.close()
            
            # 如果关闭的是当前页面，切换到其他页面
            if page_to_close == self._page:
                remaining_pages = self._context.pages
                if remaining_pages:
                    self._page = remaining_pages[-1]
                else:
                    self._page = await self._context.new_page()
            
            self._element_map = {}
            
            return {
                "success": True,
                "tab_index": tab_index,
                "message": f"已关闭标签页" + (f" {tab_index}" if tab_index is not None else ""),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        截取当前页面截图并保存
        
        Args:
            filename: 截图文件名（可选）
            
        Returns:
            截图结果
        """
        try:
            await self._ensure_page()
            
            if not filename:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"browser_screenshot_{timestamp}.png"
            
            screenshot_dir = self.session_dir.parent / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = screenshot_dir / filename
            
            await self._page.screenshot(path=str(filepath))
            
            return {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "message": "截图已保存",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def extract_content(self) -> Dict[str, Any]:
        """
        提取当前页面的文本内容
        
        Returns:
            页面文本内容
        """
        try:
            await self._ensure_page()
            
            text = await self._page.evaluate('() => document.body.innerText')
            
            return {
                "success": True,
                "content": text,
                "length": len(text),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search(self, query: str, engine: str = "google") -> Dict[str, Any]:
        """
        使用搜索引擎搜索
        
        Args:
            query: 搜索关键词
            engine: 搜索引擎
            
        Returns:
            搜索结果
        """
        import urllib.parse
        
        search_engines = {
            'duckduckgo': f'https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}',
            'google': f'https://www.google.com/search?q={urllib.parse.quote_plus(query)}&udm=14',
            'bing': f'https://www.bing.com/search?q={urllib.parse.quote_plus(query)}',
        }
        
        if engine.lower() not in search_engines:
            return {
                "success": False,
                "error": f"不支持的搜索引擎: {engine}",
                "supported_engines": list(search_engines.keys()),
            }
        
        url = search_engines[engine.lower()]
        result = await self.navigate(url)
        
        if result.get("success"):
            result["query"] = query
            result["engine"] = engine
            result["message"] = f"已在 {engine} 搜索: {query}"
        
        return result
    
    async def extract_markdown(self, extract_links: bool = True) -> Dict[str, Any]:
        """
        提取当前页面内容为 Markdown 格式
        
        Args:
            extract_links: 是否保留链接
            
        Returns:
            Markdown 内容
        """
        try:
            await self._ensure_page()
            
            # 简单的 HTML 到 Markdown 转换
            content = await self._page.evaluate('''(extractLinks) => {
                function htmlToMarkdown(element) {
                    let result = '';
                    
                    for (const node of element.childNodes) {
                        if (node.nodeType === Node.TEXT_NODE) {
                            result += node.textContent;
                        } else if (node.nodeType === Node.ELEMENT_NODE) {
                            const tag = node.tagName.toLowerCase();
                            
                            switch (tag) {
                                case 'h1':
                                    result += '\\n# ' + node.innerText + '\\n';
                                    break;
                                case 'h2':
                                    result += '\\n## ' + node.innerText + '\\n';
                                    break;
                                case 'h3':
                                    result += '\\n### ' + node.innerText + '\\n';
                                    break;
                                case 'h4':
                                    result += '\\n#### ' + node.innerText + '\\n';
                                    break;
                                case 'p':
                                    result += '\\n' + htmlToMarkdown(node) + '\\n';
                                    break;
                                case 'a':
                                    if (extractLinks && node.href) {
                                        result += '[' + node.innerText + '](' + node.href + ')';
                                    } else {
                                        result += node.innerText;
                                    }
                                    break;
                                case 'strong':
                                case 'b':
                                    result += '**' + node.innerText + '**';
                                    break;
                                case 'em':
                                case 'i':
                                    result += '*' + node.innerText + '*';
                                    break;
                                case 'code':
                                    result += '`' + node.innerText + '`';
                                    break;
                                case 'pre':
                                    result += '\\n```\\n' + node.innerText + '\\n```\\n';
                                    break;
                                case 'ul':
                                case 'ol':
                                    result += '\\n' + htmlToMarkdown(node) + '\\n';
                                    break;
                                case 'li':
                                    result += '- ' + htmlToMarkdown(node) + '\\n';
                                    break;
                                case 'br':
                                    result += '\\n';
                                    break;
                                case 'script':
                                case 'style':
                                case 'noscript':
                                    break;
                                default:
                                    result += htmlToMarkdown(node);
                            }
                        }
                    }
                    
                    return result;
                }
                
                return htmlToMarkdown(document.body);
            }''', extract_links)
            
            # 清理多余的空行
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = content.strip()
            
            return {
                "success": True,
                "markdown": content,
                "length": len(content),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def upload_file(self, index: int, file_path: str) -> Dict[str, Any]:
        """
        上传文件到文件输入框
        
        Args:
            index: 文件输入框元素索引
            file_path: 要上传的文件路径
            
        Returns:
            上传结果
        """
        try:
            await self._ensure_page()
            
            # 检查文件是否存在
            if not Path(file_path).exists():
                return {"success": False, "error": f"文件不存在: {file_path}"}
            
            if index not in self._element_map:
                await self._build_element_map()
                if index not in self._element_map:
                    return {"success": False, "error": f"元素索引 {index} 不存在"}
            
            element = self._element_map[index]
            selector = element['selector']
            
            await self._page.set_input_files(selector, file_path)
            
            return {
                "success": True,
                "index": index,
                "file_path": file_path,
                "message": f"已上传文件: {file_path}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def click_coordinate(self, x: int, y: int) -> Dict[str, Any]:
        """
        点击指定坐标位置
        
        Args:
            x: X 坐标
            y: Y 坐标
            
        Returns:
            点击结果
        """
        try:
            await self._ensure_page()
            
            await self._page.mouse.click(x, y)
            
            return {
                "success": True,
                "x": x,
                "y": y,
                "message": f"已点击坐标 ({x}, {y})",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def scroll_to_text(self, text: str) -> Dict[str, Any]:
        """
        滚动到包含指定文本的位置
        
        Args:
            text: 要滚动到的文本
            
        Returns:
            滚动结果
        """
        try:
            await self._ensure_page()
            
            # 查找包含文本的元素并滚动到视图
            found = await self._page.evaluate(f'''(text) => {{
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                while (walker.nextNode()) {{
                    if (walker.currentNode.textContent.includes(text)) {{
                        walker.currentNode.parentElement.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'center'
                        }});
                        return true;
                    }}
                }}
                return false;
            }}''', text)
            
            if found:
                return {
                    "success": True,
                    "text": text,
                    "message": f"已滚动到文本: {text}",
                }
            else:
                return {
                    "success": False,
                    "error": f"未找到文本: {text}",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def wait(self, seconds: int = 3) -> Dict[str, Any]:
        """
        等待指定秒数
        
        Args:
            seconds: 等待秒数（最大 30 秒）
            
        Returns:
            等待结果
        """
        actual_seconds = min(max(seconds, 0), 30)
        await asyncio.sleep(actual_seconds)
        
        return {
            "success": True,
            "seconds": actual_seconds,
            "message": f"已等待 {actual_seconds} 秒",
        }
    
    async def get_cookies(self) -> Dict[str, Any]:
        """
        获取当前页面的 cookies
        
        Returns:
            cookies 列表
        """
        try:
            await self._ensure_page()
            
            cookies = await self._context.cookies()
            
            cookies_list = []
            for cookie in cookies:
                cookies_list.append({
                    "name": cookie.get("name"),
                    "value": cookie.get("value"),
                    "domain": cookie.get("domain"),
                    "path": cookie.get("path"),
                })
            
            return {
                "success": True,
                "cookies": cookies_list,
                "count": len(cookies_list),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def clear_cookies(self) -> Dict[str, Any]:
        """
        清除所有 cookies
        
        Returns:
            清除结果
        """
        try:
            await self._ensure_page()
            
            await self._context.clear_cookies()
            
            return {
                "success": True,
                "message": "已清除所有 cookies",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_dropdown_options(self, index: int) -> Dict[str, Any]:
        """
        获取下拉框的选项列表
        
        Args:
            index: 下拉框元素索引
            
        Returns:
            选项列表
        """
        try:
            await self._ensure_page()
            
            if index not in self._element_map:
                await self._build_element_map()
                if index not in self._element_map:
                    return {"success": False, "error": f"元素索引 {index} 不存在"}
            
            element = self._element_map[index]
            selector = element['selector']
            
            options = await self._page.evaluate(f'''() => {{
                const select = document.querySelector("{selector}");
                if (!select || select.tagName !== 'SELECT') return [];
                
                return Array.from(select.options).map(opt => ({{
                    value: opt.value,
                    text: opt.text,
                    selected: opt.selected,
                }}));
            }}''')
            
            return {
                "success": True,
                "index": index,
                "options": options,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_sessions(self) -> Dict[str, Any]:
        """列出所有保存的会话"""
        sessions = []
        
        for state_file in self.session_dir.glob("*_storage_state.json"):
            session_id = state_file.stem.replace("_storage_state", "")
            stat = state_file.stat()
            
            sessions.append({
                "session_id": session_id,
                "storage_state_file": str(state_file),
                "size_bytes": stat.st_size,
                "modified_at": stat.st_mtime,
            })
        
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions),
            "current_session": self._current_session_id,
        }
    
    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """删除保存的会话"""
        storage_state_file = self._get_storage_state_file(session_id)
        
        deleted_items = []
        
        if storage_state_file.exists():
            storage_state_file.unlink()
            deleted_items.append(str(storage_state_file))
        
        if deleted_items:
            return {
                "success": True,
                "session_id": session_id,
                "deleted_items": deleted_items,
                "message": f"会话 '{session_id}' 已删除",
            }
        else:
            return {
                "success": False,
                "error": f"会话 '{session_id}' 不存在",
            }
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "browser_active": self._browser is not None,
            "page_active": self._page is not None,
            "current_session": self._current_session_id,
            "session_dir": str(self.session_dir),
            "sensitive_data_keys": list(self._get_sensitive_data().keys()),
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.close_session(save=True)


# 使用新的 Playwright 管理器
BrowserUseManager = PlaywrightBrowserManager


# 全局浏览器管理器实例
_browser_manager: Optional[PlaywrightBrowserManager] = None


def get_browser_manager() -> PlaywrightBrowserManager:
    """获取全局浏览器管理器实例"""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = PlaywrightBrowserManager()
    return _browser_manager


async def cleanup_browser_manager():
    """清理全局浏览器管理器"""
    global _browser_manager
    if _browser_manager:
        await _browser_manager.cleanup()
        _browser_manager = None
