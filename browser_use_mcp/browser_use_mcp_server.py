#!/usr/bin/env python3
"""Browser Use MCP Server - 基于 browser-use 库的浏览器自动化 MCP 服务器

这个 MCP 服务器将 browser-use 的浏览器操作能力封装为工具，供 AI 助手直接调用。
不使用 browser-use 内置的 Agent/LLM，由 AI 助手来做决策和控制。

特性：
1. 完整的浏览器控制 - 导航、点击、输入、滚动等
2. DOM 状态获取 - 获取可交互元素列表，通过索引操作
3. 会话持久化 - 浏览器会话在多次对话间保持
4. 安全凭证处理 - 用户名密码通过环境变量传递，不暴露给 AI
5. 内容提取 - 截图、Markdown 提取
6. WSL 兼容 - 支持在 WSL 环境中运行
"""

import asyncio
import json
import sys
import signal
import os
from typing import Any, Optional
from pathlib import Path

# 禁用 browser-use 的默认日志设置
os.environ['BROWSER_USE_SETUP_LOGGING'] = 'false'

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from browser_use_mcp.browser_tools import get_browser_manager, cleanup_browser_manager, BrowserUseManager, list_credential_keys


# 创建 MCP 服务器实例
app = Server("browser-use-mcp-server")

# 全局浏览器管理器
browser_manager: Optional[BrowserUseManager] = None


def get_manager() -> BrowserUseManager:
    """获取浏览器管理器实例"""
    global browser_manager
    if browser_manager is None:
        browser_manager = get_browser_manager()
    return browser_manager


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        # ===== 会话管理工具 =====
        Tool(
            name="browser_create_session",
            description="""创建或恢复浏览器会话。

如果指定的 session_id 已存在保存的状态，将自动恢复该会话（包括 cookies、localStorage 等）。
这使得登录状态可以在多次对话间保持。

⚠️ 每次新对话开始时，需要先调用此工具来创建/恢复会话。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "会话标识符，用于区分不同的浏览器会话。建议使用有意义的名称，如 'github_session', 'work_session' 等",
                    },
                    "headless": {
                        "type": "boolean",
                        "description": "是否使用无头模式（不显示浏览器窗口）。默认为 false",
                        "default": False,
                    },
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="browser_save_session",
            description="保存当前浏览器会话状态（cookies、localStorage 等）",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="browser_close_session",
            description="关闭当前浏览器会话",
            inputSchema={
                "type": "object",
                "properties": {
                    "save": {
                        "type": "boolean",
                        "description": "关闭前是否保存会话状态，默认为 true",
                        "default": True,
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="browser_list_sessions",
            description="列出所有已保存的浏览器会话",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="browser_delete_session",
            description="删除指定的已保存会话",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "要删除的会话标识符",
                    },
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="browser_get_status",
            description="获取浏览器当前状态信息",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        
        # ===== 核心工具：获取页面状态 =====
        Tool(
            name="browser_get_state",
            description="""🔍 获取当前浏览器状态和可交互元素列表（核心工具）

返回页面上所有可交互元素的列表，每个元素都有一个索引号。
你可以通过索引号来点击（browser_click）或输入（browser_input）这些元素。

返回内容：
- url: 当前页面 URL
- title: 页面标题
- tabs: 标签页列表
- elements: 可交互元素列表（带索引、标签、文本、属性等）
- dom_text: DOM 的文本表示（用于理解页面结构）
- screenshot_base64: 页面截图（可选）

使用流程：
1. 调用 browser_get_state 获取页面状态
2. 分析 elements 列表，找到目标元素的索引
3. 使用 browser_click 或 browser_input 操作该元素""",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_screenshot": {
                        "type": "boolean",
                        "description": "是否包含页面截图，默认为 true",
                        "default": True,
                    },
                },
                "required": [],
            },
        ),
        
        # ===== 导航工具 =====
        Tool(
            name="browser_navigate",
            description="导航到指定的 URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "目标 URL，需要包含协议（如 https://）",
                    },
                    "new_tab": {
                        "type": "boolean",
                        "description": "是否在新标签页打开，默认为 false",
                        "default": False,
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="browser_go_back",
            description="后退到上一页",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="browser_search",
            description="使用搜索引擎搜索",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词",
                    },
                    "engine": {
                        "type": "string",
                        "description": "搜索引擎：google, bing, duckduckgo",
                        "enum": ["google", "bing", "duckduckgo"],
                        "default": "google",
                    },
                },
                "required": ["query"],
            },
        ),
        
        # ===== 元素交互工具 =====
        Tool(
            name="browser_click",
            description="""点击指定索引的元素

使用 browser_get_state 获取元素列表后，通过索引点击元素。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "元素索引（从 browser_get_state 返回的 elements 列表中获取）",
                    },
                },
                "required": ["index"],
            },
        ),
        Tool(
            name="browser_input",
            description="""在指定索引的输入框中输入文本

使用 browser_get_state 获取元素列表后，通过索引在输入框中输入文本。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "输入框元素索引",
                    },
                    "text": {
                        "type": "string",
                        "description": "要输入的文本",
                    },
                    "clear_first": {
                        "type": "boolean",
                        "description": "输入前是否先清空输入框，默认为 true",
                        "default": True,
                    },
                },
                "required": ["index", "text"],
            },
        ),
        Tool(
            name="browser_input_sensitive",
            description="""安全地在输入框中填入敏感数据（用户名、密码等）

从 .env 文件读取凭证，凭证值不会暴露给 AI。

使用前请先：
1. 复制 browser_use_mcp/.env.example 为 browser_use_mcp/.env
2. 在 .env 文件中填入你的凭证

示例 .env 内容：
GITHUB_USERNAME=your_username
GITHUB_PASSWORD=your_password

然后使用 credential_key="GITHUB_USERNAME" 或 "GITHUB_PASSWORD" 来引用。

使用 browser_list_credentials 查看所有可用的凭证键名。""",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "输入框元素索引",
                    },
                    "credential_key": {
                        "type": "string",
                        "description": "凭证键名（.env 文件中的键），如 'GITHUB_USERNAME', 'GITHUB_PASSWORD'",
                    },
                    "clear_first": {
                        "type": "boolean",
                        "description": "输入前是否先清空输入框，默认为 true",
                        "default": True,
                    },
                },
                "required": ["index", "credential_key"],
            },
        ),
        Tool(
            name="browser_list_credentials",
            description="""列出所有可用的凭证键名（不显示值）

返回 .env 文件中配置的所有凭证键名，用于 browser_input_sensitive 工具。""",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="browser_send_keys",
            description="发送键盘按键",
            inputSchema={
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "string",
                        "description": "按键字符串，如 'Enter', 'Tab', 'Escape', 'ArrowDown', 'Control+a' 等",
                    },
                },
                "required": ["keys"],
            },
        ),
        Tool(
            name="browser_scroll",
            description="滚动页面或元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "description": "滚动方向",
                        "enum": ["up", "down"],
                        "default": "down",
                    },
                    "index": {
                        "type": "integer",
                        "description": "元素索引（可选，不指定则滚动整个页面）",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="browser_scroll_to_text",
            description="滚动到包含指定文本的位置",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要滚动到的文本",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="browser_click_coordinate",
            description="点击指定坐标位置（用于画布、地图等特殊场景）",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X 坐标",
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y 坐标",
                    },
                },
                "required": ["x", "y"],
            },
        ),
        
        # ===== 标签页管理 =====
        Tool(
            name="browser_switch_tab",
            description="切换到指定标签页",
            inputSchema={
                "type": "object",
                "properties": {
                    "tab_index": {
                        "type": "integer",
                        "description": "标签页索引（从 browser_get_state 返回的 tabs 列表中获取）",
                    },
                },
                "required": ["tab_index"],
            },
        ),
        Tool(
            name="browser_close_tab",
            description="关闭标签页",
            inputSchema={
                "type": "object",
                "properties": {
                    "tab_index": {
                        "type": "integer",
                        "description": "标签页索引（可选，不指定则关闭当前标签页）",
                    },
                },
                "required": [],
            },
        ),
        
        # ===== 内容提取工具 =====
        Tool(
            name="browser_screenshot",
            description="截取当前页面的截图并保存",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "截图文件名（可选，默认自动生成）",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="browser_extract_content",
            description="提取当前页面的文本内容（DOM 文本表示）",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="browser_extract_markdown",
            description="提取当前页面内容为 Markdown 格式",
            inputSchema={
                "type": "object",
                "properties": {
                    "extract_links": {
                        "type": "boolean",
                        "description": "是否保留链接，默认为 true",
                        "default": True,
                    },
                },
                "required": [],
            },
        ),
        
        # ===== 表单和文件工具 =====
        Tool(
            name="browser_get_dropdown_options",
            description="获取下拉框的选项列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "下拉框元素索引",
                    },
                },
                "required": ["index"],
            },
        ),
        Tool(
            name="browser_upload_file",
            description="上传文件到文件输入框",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "文件输入框元素索引",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "要上传的文件路径",
                    },
                },
                "required": ["index", "file_path"],
            },
        ),
        
        # ===== Cookie 管理 =====
        Tool(
            name="browser_get_cookies",
            description="获取当前页面的 cookies",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="browser_clear_cookies",
            description="清除所有 cookies",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        
        # ===== 其他工具 =====
        Tool(
            name="browser_wait",
            description="等待指定秒数",
            inputSchema={
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "integer",
                        "description": "等待秒数（最大 30 秒）",
                        "default": 3,
                    },
                },
                "required": [],
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """处理工具调用"""
    manager = get_manager()
    
    try:
        # ===== 会话管理 =====
        if name == "browser_create_session":
            session_id = arguments.get("session_id")
            headless = arguments.get("headless", False)
            
            result = await manager.create_session(session_id, headless)
            
            if result.get("success"):
                restored_msg = "（已恢复之前的会话状态）" if result.get("restored") else "（新会话）"
                return [TextContent(
                    type="text",
                    text=f"""✅ 浏览器会话已创建 {restored_msg}

📋 会话信息:
  - 会话 ID: {result['session_id']}
  - 状态恢复: {'是' if result.get('restored') else '否'}
  - 无头模式: {'是' if result.get('headless') else '否'}

💡 下一步: 使用 browser_navigate 导航到目标网站，或使用 browser_get_state 获取当前页面状态"""
                )]
            else:
                return [TextContent(type="text", text=f"❌ 创建会话失败: {result.get('error')}")]
        
        elif name == "browser_save_session":
            result = await manager.save_session()
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ 会话 '{result['session_id']}' 已保存")]
            else:
                return [TextContent(type="text", text=f"❌ 保存失败: {result.get('error')}")]
        
        elif name == "browser_close_session":
            save = arguments.get("save", True)
            result = await manager.close_session(save)
            
            saved_msg = "（状态已保存）" if result.get("saved") else ""
            return [TextContent(type="text", text=f"✅ 会话已关闭 {saved_msg}")]
        
        elif name == "browser_list_sessions":
            result = await manager.list_sessions()
            
            if not result.get("sessions"):
                return [TextContent(type="text", text="📭 没有保存的会话")]
            
            sessions_text = "📋 已保存的会话列表:\n\n"
            for session in result["sessions"]:
                import datetime
                modified = datetime.datetime.fromtimestamp(session["modified_at"]).strftime("%Y-%m-%d %H:%M:%S")
                current = " (当前)" if session["session_id"] == result.get("current_session") else ""
                sessions_text += f"  • {session['session_id']}{current}\n"
                sessions_text += f"    最后修改: {modified}\n\n"
            
            return [TextContent(type="text", text=sessions_text)]
        
        elif name == "browser_delete_session":
            session_id = arguments.get("session_id")
            result = await manager.delete_session(session_id)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ 会话 '{session_id}' 已删除")]
            else:
                return [TextContent(type="text", text=f"❌ 删除失败: {result.get('error')}")]
        
        elif name == "browser_get_status":
            status = manager.get_status()
            
            sensitive_keys = ", ".join(status['sensitive_data_keys']) if status['sensitive_data_keys'] else "无"
            
            return [TextContent(
                type="text",
                text=f"""🔍 浏览器状态:

  - 浏览器运行中: {'是' if status['browser_active'] else '否'}
  - 浏览器已启动: {'是' if status['browser_started'] else '否'}
  - 当前会话: {status['current_session'] or '无'}
  - 已配置的敏感数据: {sensitive_keys}"""
            )]
        
        # ===== 核心：获取页面状态 =====
        elif name == "browser_get_state":
            include_screenshot = arguments.get("include_screenshot", True)
            result = await manager.get_state(include_screenshot)
            
            if result.get("success"):
                # 构建元素列表文本
                elements_text = ""
                if result.get("elements"):
                    elements_text = "\n\n📋 可交互元素列表:\n"
                    for el in result["elements"][:50]:  # 限制显示数量
                        el_text = f"  [{el['index']}] <{el['tag']}>"
                        if el.get('text'):
                            el_text += f" \"{el['text'][:30]}{'...' if len(el.get('text', '')) > 30 else ''}\""
                        if el.get('placeholder'):
                            el_text += f" (placeholder: {el['placeholder']})"
                        if el.get('type'):
                            el_text += f" [type={el['type']}]"
                        if el.get('href'):
                            el_text += f" -> {el['href'][:50]}..."
                        elements_text += el_text + "\n"
                    
                    if len(result["elements"]) > 50:
                        elements_text += f"\n  ... 还有 {len(result['elements']) - 50} 个元素\n"
                
                # 标签页信息
                tabs_text = ""
                if result.get("tabs"):
                    tabs_text = "\n\n📑 标签页:\n"
                    for i, tab in enumerate(result["tabs"]):
                        active = " (当前)" if i == result.get("active_tab_index") else ""
                        tabs_text += f"  [{i}] {tab['title'][:30]}{active}\n"
                
                response_text = f"""📄 页面状态

🌐 URL: {result['url']}
📑 标题: {result['title']}
📊 可交互元素数: {result['elements_count']}
{tabs_text}{elements_text}

💡 使用 browser_click(index) 点击元素，browser_input(index, text) 输入文本"""
                
                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text=f"❌ 获取状态失败: {result.get('error')}")]
        
        # ===== 导航 =====
        elif name == "browser_navigate":
            url = arguments.get("url")
            new_tab = arguments.get("new_tab", False)
            
            result = await manager.navigate(url, new_tab)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 导航失败: {result.get('error')}")]
        
        elif name == "browser_go_back":
            result = await manager.go_back()
            
            if result.get("success"):
                return [TextContent(type="text", text="✅ 已后退到上一页")]
            else:
                return [TextContent(type="text", text=f"❌ 后退失败: {result.get('error')}")]
        
        elif name == "browser_search":
            query = arguments.get("query")
            engine = arguments.get("engine", "google")
            
            result = await manager.search(query, engine)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 搜索失败: {result.get('error')}")]
        
        # ===== 元素交互 =====
        elif name == "browser_click":
            index = arguments.get("index")
            result = await manager.click_element(index)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 点击失败: {result.get('error')}")]
        
        elif name == "browser_input":
            index = arguments.get("index")
            text = arguments.get("text")
            clear_first = arguments.get("clear_first", True)
            
            result = await manager.input_text(index, text, clear_first)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 输入失败: {result.get('error')}")]
        
        elif name == "browser_input_sensitive":
            index = arguments.get("index")
            credential_key = arguments.get("credential_key")
            clear_first = arguments.get("clear_first", True)
            
            result = await manager.input_sensitive(index, credential_key, clear_first)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                error_msg = f"❌ 填入失败: {result.get('error')}"
                if result.get("available_keys"):
                    error_msg += f"\n可用的键: {', '.join(result['available_keys'])}"
                return [TextContent(type="text", text=error_msg)]
        
        elif name == "browser_list_credentials":
            keys = list_credential_keys()
            
            if keys:
                keys_text = "\n".join([f"  • {key}" for key in keys])
                return [TextContent(
                    type="text",
                    text=f"""🔑 可用的凭证键名（共 {len(keys)} 个）:

{keys_text}

💡 使用 browser_input_sensitive(index, credential_key) 来填入凭证
📁 凭证配置文件: browser_use_mcp/.env"""
                )]
            else:
                return [TextContent(
                    type="text",
                    text="""📭 没有配置凭证

请按以下步骤配置：
1. 复制 browser_use_mcp/.env.example 为 browser_use_mcp/.env
2. 在 .env 文件中填入你的凭证，格式：
   GITHUB_USERNAME=your_username
   GITHUB_PASSWORD=your_password"""
                )]
        
        elif name == "browser_send_keys":
            keys = arguments.get("keys")
            result = await manager.send_keys(keys)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 按键失败: {result.get('error')}")]
        
        elif name == "browser_scroll":
            direction = arguments.get("direction", "down")
            index = arguments.get("index")
            
            result = await manager.scroll(direction, index)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 滚动失败: {result.get('error')}")]
        
        elif name == "browser_scroll_to_text":
            text = arguments.get("text")
            result = await manager.scroll_to_text(text)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 滚动失败: {result.get('error')}")]
        
        elif name == "browser_click_coordinate":
            x = arguments.get("x")
            y = arguments.get("y")
            result = await manager.click_coordinate(x, y)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 点击失败: {result.get('error')}")]
        
        # ===== 标签页管理 =====
        elif name == "browser_switch_tab":
            tab_index = arguments.get("tab_index")
            result = await manager.switch_tab(tab_index)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 切换失败: {result.get('error')}")]
        
        elif name == "browser_close_tab":
            tab_index = arguments.get("tab_index")
            result = await manager.close_tab(tab_index)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 关闭失败: {result.get('error')}")]
        
        # ===== 内容提取 =====
        elif name == "browser_screenshot":
            filename = arguments.get("filename")
            result = await manager.take_screenshot(filename)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ 截图已保存: {result['filepath']}")]
            else:
                return [TextContent(type="text", text=f"❌ 截图失败: {result.get('error')}")]
        
        elif name == "browser_extract_content":
            result = await manager.extract_content()
            
            if result.get("success"):
                content = result['content']
                if len(content) > 5000:
                    content = content[:5000] + f"\n\n... (内容已截断，共 {result['length']} 字符)"
                return [TextContent(type="text", text=f"📄 页面内容:\n\n{content}")]
            else:
                return [TextContent(type="text", text=f"❌ 提取失败: {result.get('error')}")]
        
        elif name == "browser_extract_markdown":
            extract_links = arguments.get("extract_links", True)
            result = await manager.extract_markdown(extract_links)
            
            if result.get("success"):
                markdown = result['markdown']
                if len(markdown) > 5000:
                    markdown = markdown[:5000] + f"\n\n... (内容已截断，共 {result['length']} 字符)"
                return [TextContent(type="text", text=f"📄 Markdown 内容:\n\n{markdown}")]
            else:
                return [TextContent(type="text", text=f"❌ 提取失败: {result.get('error')}")]
        
        # ===== 表单和文件 =====
        elif name == "browser_get_dropdown_options":
            index = arguments.get("index")
            result = await manager.get_dropdown_options(index)
            
            if result.get("success"):
                options = result.get("options", [])
                options_text = "\n".join([f"  - {opt}" for opt in options]) if options else "  (无选项)"
                return [TextContent(type="text", text=f"📋 下拉框选项:\n{options_text}")]
            else:
                return [TextContent(type="text", text=f"❌ 获取失败: {result.get('error')}")]
        
        elif name == "browser_upload_file":
            index = arguments.get("index")
            file_path = arguments.get("file_path")
            result = await manager.upload_file(index, file_path)
            
            if result.get("success"):
                return [TextContent(type="text", text=f"✅ {result['message']}")]
            else:
                return [TextContent(type="text", text=f"❌ 上传失败: {result.get('error')}")]
        
        # ===== Cookie 管理 =====
        elif name == "browser_get_cookies":
            result = await manager.get_cookies()
            
            if result.get("success"):
                cookies = result.get("cookies", [])
                if cookies:
                    cookies_text = "\n".join([f"  - {c['name']}: {c['value'][:20]}..." for c in cookies[:20]])
                    if len(cookies) > 20:
                        cookies_text += f"\n  ... 还有 {len(cookies) - 20} 个 cookies"
                else:
                    cookies_text = "  (无 cookies)"
                return [TextContent(type="text", text=f"🍪 Cookies ({result['count']} 个):\n{cookies_text}")]
            else:
                return [TextContent(type="text", text=f"❌ 获取失败: {result.get('error')}")]
        
        elif name == "browser_clear_cookies":
            result = await manager.clear_cookies()
            
            if result.get("success"):
                return [TextContent(type="text", text="✅ 已清除所有 cookies")]
            else:
                return [TextContent(type="text", text=f"❌ 清除失败: {result.get('error')}")]
        
        # ===== 其他 =====
        elif name == "browser_wait":
            seconds = arguments.get("seconds", 3)
            result = await manager.wait(seconds)
            
            return [TextContent(type="text", text=f"✅ {result['message']}")]
        
        else:
            return [TextContent(type="text", text=f"❌ 未知的工具: {name}")]
    
    except Exception as e:
        import traceback
        return [TextContent(
            type="text",
            text=f"❌ 执行出错: {str(e)}\n\n{traceback.format_exc()}"
        )]


async def cleanup():
    """清理资源"""
    global browser_manager
    if browser_manager:
        try:
            await browser_manager.save_session()
        except:
            pass
        await browser_manager.cleanup()


async def main():
    """主函数"""
    # 注册清理函数
    def signal_handler(sig, frame):
        asyncio.create_task(cleanup())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 使用 stdio 传输运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="browser-use-mcp-server",
                server_version="2.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
