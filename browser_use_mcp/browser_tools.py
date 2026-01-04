#!/usr/bin/env python3
"""Browser Use 工具模块 - 封装 browser-use 库的浏览器操作能力

这个模块将 browser-use 的浏览器操作能力（包括底层和上层功能）封装为 MCP 工具，
供 AI 助手直接调用。不使用 browser-use 内置的 Agent/LLM，由 AI 助手来做决策。

核心功能：
1. 浏览器会话管理（创建、保存、恢复、关闭）
2. 页面导航（打开URL、前进、后退、刷新、搜索）
3. DOM 状态获取（获取可交互元素列表，带索引）
4. 元素交互（点击、输入、滚动、下拉框选择）
5. 标签页管理（切换、关闭、新建）
6. 内容提取（截图、Markdown 提取、PDF 下载）
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
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

# 禁用 browser-use 的默认日志设置，避免与 MCP 冲突
os.environ['BROWSER_USE_SETUP_LOGGING'] = 'false'

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


class BrowserUseManager:
    """基于 browser-use 库的浏览器管理器
    
    将 browser-use 的浏览器操作能力封装为工具，供 AI 助手直接调用。
    AI 助手负责决策，这个管理器负责执行具体的浏览器操作。
    """
    
    def __init__(self, session_dir: Optional[str] = None):
        """
        初始化浏览器管理器
        
        Args:
            session_dir: 会话数据存储目录，默认为 ~/.browser_use_mcp/sessions
        """
        self.session_dir = Path(session_dir) if session_dir else Path.home() / ".browser_use_mcp" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self._browser_session = None
        self._current_session_id: Optional[str] = None
        self._is_started = False
        
    def _get_user_data_dir(self, session_id: str) -> Path:
        """获取用户数据目录路径"""
        return self.session_dir / f"{session_id}_profile"
    
    def _get_storage_state_file(self, session_id: str) -> Path:
        """获取存储状态文件路径"""
        return self.session_dir / f"{session_id}_storage_state.json"
    
    def _is_wsl(self) -> bool:
        """检测是否在 WSL 环境中"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    def _get_sensitive_data(self) -> Dict[str, str]:
        """获取敏感数据（从 .env 文件加载）
        
        凭证存储在 browser_use_mcp/.env 文件中，格式：
        GITHUB_USERNAME=your_username
        GITHUB_PASSWORD=your_password
        EMAIL=your_email@example.com
        
        AI 只能通过 credential_key 引用凭证，无法看到实际值。
        """
        return load_credentials()
    
    async def create_session(
        self, 
        session_id: str, 
        headless: bool = False,
    ) -> Dict[str, Any]:
        """
        创建或恢复浏览器会话
        
        Args:
            session_id: 会话标识符
            headless: 是否无头模式
            
        Returns:
            会话信息字典
        """
        import datetime
        from browser_use import BrowserSession, BrowserProfile
        
        # 关闭现有会话
        if self._browser_session:
            await self.close_session(save=True)
        
        user_data_dir = self._get_user_data_dir(session_id)
        storage_state_file = self._get_storage_state_file(session_id)
        
        # 检查是否有保存的会话状态
        restored = storage_state_file.exists()
        
        # 创建浏览器配置
        browser_profile = BrowserProfile(
            headless=headless,
            user_data_dir=str(user_data_dir),
            storage_state=str(storage_state_file) if restored else None,
            disable_security=False,
            # WSL 兼容参数
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ] if self._is_wsl() else None,
        )
        
        # 创建浏览器会话
        self._browser_session = BrowserSession(
            browser_profile=browser_profile,
            keep_alive=True,
        )
        
        self._current_session_id = session_id
        self._is_started = False
        
        now = datetime.datetime.now().isoformat()
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"会话 '{session_id}' 已创建",
            "restored": restored,
            "created_at": now,
            "user_data_dir": str(user_data_dir),
            "headless": headless,
        }
    
    async def _ensure_started(self):
        """确保浏览器已启动"""
        if not self._browser_session:
            raise RuntimeError("没有活动的浏览器会话，请先创建会话")
        
        if not self._is_started:
            await self._browser_session.start()
            self._is_started = True
    
    async def save_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """保存当前会话状态"""
        session_id = session_id or self._current_session_id
        
        if not session_id:
            return {"success": False, "error": "没有活动的会话"}
        
        if not self._browser_session:
            return {"success": False, "error": "浏览器会话未初始化"}
        
        try:
            storage_state_file = self._get_storage_state_file(session_id)
            await self._browser_session.export_storage_state(output_path=str(storage_state_file))
            
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
        
        if save and self._current_session_id:
            save_result = await self.save_session()
            result["saved"] = save_result.get("success", False)
        
        if self._browser_session:
            try:
                await self._browser_session.stop()
            except:
                pass
            self._browser_session = None
        
        self._current_session_id = None
        self._is_started = False
        
        return result
    
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
            await self._ensure_started()
            
            from browser_use.browser.events import NavigateToUrlEvent
            
            event = self._browser_session.event_bus.dispatch(
                NavigateToUrlEvent(url=url, new_tab=new_tab)
            )
            await event
            
            # 等待页面加载
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
            await self._ensure_started()
            
            from browser_use.browser.events import GoBackEvent
            
            event = self._browser_session.event_bus.dispatch(GoBackEvent())
            await event
            
            return {
                "success": True,
                "message": "已后退到上一页",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_state(self, include_screenshot: bool = True) -> Dict[str, Any]:
        """
        获取当前浏览器状态，包括可交互元素列表
        
        这是核心功能：返回页面上所有可交互元素的列表，每个元素都有一个索引号，
        AI 助手可以通过索引号来点击或操作这些元素。
        
        Args:
            include_screenshot: 是否包含截图
            
        Returns:
            浏览器状态，包括：
            - url: 当前页面 URL
            - title: 页面标题
            - tabs: 标签页列表
            - elements: 可交互元素列表（带索引）
            - screenshot: 页面截图（base64，可选）
        """
        try:
            await self._ensure_started()
            
            # 获取浏览器状态
            state = await self._browser_session.get_browser_state_summary(
                include_screenshot=include_screenshot
            )
            
            result = {
                "success": True,
                "url": state.url,
                "title": state.title,
                "tabs": [{"id": tab.tab_id, "url": tab.url, "title": tab.title} for tab in state.tabs] if state.tabs else [],
                "active_tab_index": state.active_tab_index,
            }
            
            # 提取可交互元素
            if state.dom_state and state.dom_state.selector_map:
                elements = []
                for index, node in state.dom_state.selector_map.items():
                    element_info = {
                        "index": index,
                        "tag": node.tag_name,
                        "text": node.text[:100] if node.text else "",
                        "role": node.role if hasattr(node, 'role') else None,
                    }
                    
                    # 添加重要属性
                    if hasattr(node, 'attributes') and node.attributes:
                        if 'href' in node.attributes:
                            element_info['href'] = node.attributes['href']
                        if 'placeholder' in node.attributes:
                            element_info['placeholder'] = node.attributes['placeholder']
                        if 'type' in node.attributes:
                            element_info['type'] = node.attributes['type']
                        if 'name' in node.attributes:
                            element_info['name'] = node.attributes['name']
                        if 'aria-label' in node.attributes:
                            element_info['aria_label'] = node.attributes['aria-label']
                    
                    elements.append(element_info)
                
                result["elements"] = elements
                result["elements_count"] = len(elements)
            else:
                result["elements"] = []
                result["elements_count"] = 0
            
            # 获取 DOM 的文本表示（用于 AI 理解页面结构）
            if state.dom_state:
                result["dom_text"] = state.dom_state.llm_representation()
            
            # 截图
            if include_screenshot and state.screenshot:
                result["screenshot_base64"] = state.screenshot
            
            return result
            
        except Exception as e:
            import traceback
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
    
    async def click_element(self, index: int) -> Dict[str, Any]:
        """
        点击指定索引的元素
        
        Args:
            index: 元素索引（从 get_state 返回的 elements 列表中获取）
            
        Returns:
            点击结果
        """
        try:
            await self._ensure_started()
            
            from browser_use.browser.events import ClickElementEvent
            
            # 获取元素
            node = await self._browser_session.get_element_by_index(index)
            if node is None:
                return {"success": False, "error": f"元素索引 {index} 不存在"}
            
            # 点击元素
            event = self._browser_session.event_bus.dispatch(
                ClickElementEvent(index=index, element=node)
            )
            await event
            
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
            await self._ensure_started()
            
            from browser_use.browser.events import TypeTextEvent
            
            # 获取元素
            node = await self._browser_session.get_element_by_index(index)
            if node is None:
                return {"success": False, "error": f"元素索引 {index} 不存在"}
            
            # 输入文本
            event = self._browser_session.event_bus.dispatch(
                TypeTextEvent(index=index, text=text, element=node, clear_first=clear_first)
            )
            await event
            
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
        安全地在输入框中填入敏感数据（从环境变量读取）
        
        Args:
            index: 元素索引
            credential_key: 敏感数据键名（如 'username', 'password'）
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
            keys: 按键字符串，如 'Enter', 'Tab', 'Escape', 'ArrowDown' 等
            
        Returns:
            按键结果
        """
        try:
            await self._ensure_started()
            
            from browser_use.browser.events import SendKeysEvent
            
            event = self._browser_session.event_bus.dispatch(
                SendKeysEvent(keys=keys)
            )
            await event
            
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
            index: 元素索引（可选，不指定则滚动整个页面）
            
        Returns:
            滚动结果
        """
        try:
            await self._ensure_started()
            
            from browser_use.browser.events import ScrollEvent
            
            node = None
            if index is not None and index != 0:
                node = await self._browser_session.get_element_by_index(index)
                if node is None:
                    return {"success": False, "error": f"元素索引 {index} 不存在"}
            
            event = self._browser_session.event_bus.dispatch(
                ScrollEvent(down=(direction == "down"), index=index, element=node)
            )
            await event
            
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
            tab_index: 标签页索引（从 get_state 返回的 tabs 列表中获取）
            
        Returns:
            切换结果
        """
        try:
            await self._ensure_started()
            
            from browser_use.browser.events import SwitchTabEvent
            
            event = self._browser_session.event_bus.dispatch(
                SwitchTabEvent(tab_index=tab_index)
            )
            await event
            
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
            tab_index: 标签页索引（可选，不指定则关闭当前标签页）
            
        Returns:
            关闭结果
        """
        try:
            await self._ensure_started()
            
            from browser_use.browser.events import CloseTabEvent
            
            event = self._browser_session.event_bus.dispatch(
                CloseTabEvent(tab_index=tab_index)
            )
            await event
            
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
            await self._ensure_started()
            
            import datetime
            
            if not filename:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"browser_screenshot_{timestamp}.png"
            
            screenshot_dir = self.session_dir.parent / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = screenshot_dir / filename
            
            # 获取截图
            state = await self._browser_session.get_browser_state_summary(include_screenshot=True)
            
            if state.screenshot:
                with open(filepath, 'wb') as f:
                    f.write(base64.b64decode(state.screenshot))
                
                return {
                    "success": True,
                    "filepath": str(filepath),
                    "filename": filename,
                    "message": "截图已保存",
                }
            else:
                return {"success": False, "error": "无法获取截图"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def extract_content(self) -> Dict[str, Any]:
        """
        提取当前页面的文本内容
        
        Returns:
            页面文本内容
        """
        try:
            await self._ensure_started()
            
            text = await self._browser_session.get_state_as_text()
            
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
            engine: 搜索引擎，支持 'google', 'bing', 'duckduckgo'
            
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
        
        这是 browser-use 的上层功能，可以将页面内容转换为干净的 Markdown。
        
        Args:
            extract_links: 是否保留链接
            
        Returns:
            Markdown 内容
        """
        try:
            await self._ensure_started()
            
            from browser_use.dom.markdown_extractor import extract_clean_markdown
            
            content, stats = await extract_clean_markdown(
                browser_session=self._browser_session,
                extract_links=extract_links
            )
            
            return {
                "success": True,
                "markdown": content,
                "length": len(content),
                "stats": stats,
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
            await self._ensure_started()
            
            from browser_use.browser.events import UploadFileEvent
            
            # 检查文件是否存在
            if not Path(file_path).exists():
                return {"success": False, "error": f"文件不存在: {file_path}"}
            
            # 获取元素
            node = await self._browser_session.get_element_by_index(index)
            if node is None:
                return {"success": False, "error": f"元素索引 {index} 不存在"}
            
            event = self._browser_session.event_bus.dispatch(
                UploadFileEvent(index=index, file_path=file_path, element=node)
            )
            await event
            
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
        
        用于特殊场景，如点击画布、地图等无法通过元素索引点击的区域。
        
        Args:
            x: X 坐标
            y: Y 坐标
            
        Returns:
            点击结果
        """
        try:
            await self._ensure_started()
            
            from browser_use.browser.events import ClickCoordinateEvent
            
            event = self._browser_session.event_bus.dispatch(
                ClickCoordinateEvent(x=x, y=y)
            )
            await event
            
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
            await self._ensure_started()
            
            from browser_use.browser.events import ScrollToTextEvent
            
            event = self._browser_session.event_bus.dispatch(
                ScrollToTextEvent(text=text)
            )
            await event
            
            return {
                "success": True,
                "text": text,
                "message": f"已滚动到文本: {text}",
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
            await self._ensure_started()
            
            cookies = await self._browser_session.cookies()
            
            # 转换为可序列化的格式
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
            await self._ensure_started()
            
            await self._browser_session.clear_cookies()
            
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
            await self._ensure_started()
            
            from browser_use.browser.events import GetDropdownOptionsEvent
            
            node = await self._browser_session.get_element_by_index(index)
            if node is None:
                return {"success": False, "error": f"元素索引 {index} 不存在"}
            
            event = self._browser_session.event_bus.dispatch(
                GetDropdownOptionsEvent(index=index, element=node)
            )
            await event
            result = await event.event_result()
            
            return {
                "success": True,
                "index": index,
                "options": result if result else [],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_sessions(self) -> Dict[str, Any]:
        """列出所有保存的会话"""
        sessions = []
        
        for state_file in self.session_dir.glob("*_storage_state.json"):
            session_id = state_file.stem.replace("_storage_state", "")
            stat = state_file.stat()
            
            user_data_dir = self._get_user_data_dir(session_id)
            
            sessions.append({
                "session_id": session_id,
                "storage_state_file": str(state_file),
                "user_data_dir": str(user_data_dir) if user_data_dir.exists() else None,
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
        import shutil
        
        storage_state_file = self._get_storage_state_file(session_id)
        user_data_dir = self._get_user_data_dir(session_id)
        
        deleted_items = []
        
        if storage_state_file.exists():
            storage_state_file.unlink()
            deleted_items.append(str(storage_state_file))
            
        if user_data_dir.exists():
            shutil.rmtree(user_data_dir)
            deleted_items.append(str(user_data_dir))
        
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
            "browser_active": self._browser_session is not None,
            "browser_started": self._is_started,
            "current_session": self._current_session_id,
            "session_dir": str(self.session_dir),
            "sensitive_data_keys": list(self._get_sensitive_data().keys()),
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.close_session(save=True)


# 全局浏览器管理器实例
_browser_manager: Optional[BrowserUseManager] = None


def get_browser_manager() -> BrowserUseManager:
    """获取全局浏览器管理器实例"""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserUseManager()
    return _browser_manager


async def cleanup_browser_manager():
    """清理全局浏览器管理器"""
    global _browser_manager
    if _browser_manager:
        await _browser_manager.cleanup()
        _browser_manager = None
