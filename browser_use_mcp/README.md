# Browser Use MCP Server

基于 [browser-use](https://github.com/browser-use/browser-use) 库的浏览器自动化 MCP 服务器。

**核心理念**：将 browser-use 的浏览器操作能力封装为 MCP 工具，由 AI 助手（你）来做决策和控制，而不是使用 browser-use 内置的 Agent/LLM。

## 特性

### 🎯 AI 助手直接控制
- 不使用 browser-use 内置的 Agent/LLM
- AI 助手通过 MCP 工具直接控制浏览器
- 获取页面状态 → 分析元素 → 执行操作

### 🔍 DOM 状态获取
- 获取页面上所有可交互元素列表
- 每个元素都有索引号，通过索引操作元素
- 包含元素的标签、文本、属性等信息

### 💾 会话持久化
- 浏览器会话（cookies、localStorage）在多次对话间保持
- 登录状态自动保存和恢复
- 支持多个独立会话

### 🔐 安全凭证处理
- 用户名、密码等敏感信息存储在 `.env` 文件中
- 凭证值不会暴露给 AI 助手
- AI 只能通过键名引用凭证

### 🐧 WSL 兼容
- 完全支持在 WSL 环境中运行

## 安装

```bash
cd browser_use_mcp
pip install -r requirements.txt
playwright install chromium
```

## 凭证配置

**重要**：凭证存储在 `.env` 文件中，不通过 MCP JSON 配置传递。

### 1. 创建 .env 文件

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

```bash
# browser_use_mcp/.env
GITHUB_USERNAME=your_github_username
GITHUB_PASSWORD=your_github_password
EMAIL=your_email@example.com
```

### 3. 使用凭证

AI 助手通过 `browser_input_sensitive(index, credential_key)` 工具填入凭证：
- `credential_key` 是 `.env` 文件中的键名（如 `GITHUB_USERNAME`）
- AI 看不到凭证的实际值

## MCP 配置

在 `mcp_settings.json` 中添加（无需配置凭证）：

```json
{
  "mcpServers": {
    "browser-use": {
      "command": "python3",
      "args": ["/home/zsss/zsss_useful_tools/aggr_force/browser_use_mcp/browser_use_mcp_server.py"],
      "disabled": false,
      "alwaysAllow": [],
      "disabledTools": []
    }
  }
}
```

## 工具列表

### 会话管理
| 工具 | 描述 |
|------|------|
| `browser_create_session` | 创建或恢复浏览器会话 |
| `browser_save_session` | 保存当前会话状态 |
| `browser_close_session` | 关闭当前会话 |
| `browser_list_sessions` | 列出所有已保存的会话 |
| `browser_delete_session` | 删除指定会话 |
| `browser_get_status` | 获取浏览器状态 |

### 核心工具
| 工具 | 描述 |
|------|------|
| `browser_get_state` | 🔍 **核心** - 获取页面状态和可交互元素列表 |

### 导航
| 工具 | 描述 |
|------|------|
| `browser_navigate` | 导航到指定 URL |
| `browser_go_back` | 后退到上一页 |
| `browser_search` | 使用搜索引擎搜索 |

### 元素交互
| 工具 | 描述 |
|------|------|
| `browser_click` | 点击指定索引的元素 |
| `browser_input` | 在输入框中输入文本 |
| `browser_input_sensitive` | 安全填入敏感数据（从 .env 读取） |
| `browser_list_credentials` | 列出所有可用的凭证键名 |
| `browser_send_keys` | 发送键盘按键 |
| `browser_scroll` | 滚动页面或元素 |
| `browser_scroll_to_text` | 滚动到包含指定文本的位置 |
| `browser_click_coordinate` | 点击指定坐标位置 |

### 标签页管理
| 工具 | 描述 |
|------|------|
| `browser_switch_tab` | 切换到指定标签页 |
| `browser_close_tab` | 关闭标签页 |

### 内容提取
| 工具 | 描述 |
|------|------|
| `browser_screenshot` | 截取页面截图 |
| `browser_extract_content` | 提取页面文本内容 |
| `browser_extract_markdown` | 提取页面内容为 Markdown |

### 表单和文件
| 工具 | 描述 |
|------|------|
| `browser_get_dropdown_options` | 获取下拉框选项 |
| `browser_upload_file` | 上传文件 |

### Cookie 管理
| 工具 | 描述 |
|------|------|
| `browser_get_cookies` | 获取 cookies |
| `browser_clear_cookies` | 清除 cookies |

### 其他
| 工具 | 描述 |
|------|------|
| `browser_wait` | 等待指定秒数 |

## 使用示例

### 基本流程

```
1. browser_create_session(session_id="my_session")  # 创建会话
2. browser_navigate(url="https://example.com")       # 导航到网站
3. browser_get_state()                               # 获取页面状态和元素列表
4. browser_click(index=5)                            # 点击索引为 5 的元素
5. browser_input(index=3, text="hello")              # 在索引为 3 的输入框输入
6. browser_save_session()                            # 保存会话
```

---

## 🌟 GitHub 登录完整示例

以下是使用 Browser Use MCP 自动登录 GitHub 并获取首页内容的完整流程：

### 前提条件

1. 确保 `.env` 文件已配置：
```bash
# browser_use_mcp/.env
GITHUB_USERNAME=your_github_username
GITHUB_PASSWORD=your_github_password
```

### 步骤 1：创建浏览器会话

```
用户: 帮我登录 GitHub

AI 调用: browser_create_session(session_id="github_session")
返回: ✅ 浏览器会话已创建（新会话）
```

### 步骤 2：导航到 GitHub 登录页

```
AI 调用: browser_navigate(url="https://github.com/login")
返回: ✅ 已导航到 https://github.com/login
```

### 步骤 3：获取页面状态，分析元素

```
AI 调用: browser_get_state()
返回:
📄 页面状态
🌐 URL: https://github.com/login
📑 标题: Sign in to GitHub
📊 可交互元素数: 15

📋 可交互元素列表:
  [1] <input> (placeholder: Username or email address) [type=text]
  [2] <input> (placeholder: Password) [type=password]
  [3] <button> "Sign in"
  [4] <a> "Forgot password?"
  ...
```

### 步骤 4：查看可用凭证

```
AI 调用: browser_list_credentials()
返回:
🔑 可用的凭证键名（共 2 个）:
  • GITHUB_USERNAME
  • GITHUB_PASSWORD
```

### 步骤 5：填入用户名

```
AI 调用: browser_input_sensitive(index=1, credential_key="GITHUB_USERNAME")
返回: ✅ 已安全填入 GITHUB_USERNAME（值已隐藏）
```

### 步骤 6：填入密码

```
AI 调用: browser_input_sensitive(index=2, credential_key="GITHUB_PASSWORD")
返回: ✅ 已安全填入 GITHUB_PASSWORD（值已隐藏）
```

### 步骤 7：点击登录按钮

```
AI 调用: browser_click(index=3)
返回: ✅ 已点击元素 3
```

### 步骤 8：等待页面加载

```
AI 调用: browser_wait(seconds=3)
返回: ✅ 已等待 3 秒
```

### 步骤 9：保存登录状态

```
AI 调用: browser_save_session()
返回: ✅ 会话 'github_session' 已保存
```

### 步骤 10：获取首页内容

```
AI 调用: browser_get_state()
返回:
📄 页面状态
🌐 URL: https://github.com
📑 标题: GitHub
📊 可交互元素数: 50+

（显示已登录的 GitHub 首页元素）
```

### 步骤 11：提取首页 Markdown 内容

```
AI 调用: browser_extract_markdown()
返回:
📄 Markdown 内容:

# GitHub

Welcome back, your_username!

## Your repositories
- repo1
- repo2
...
```

---

### 下次对话恢复登录状态

```
用户: 打开 GitHub

AI 调用: browser_create_session(session_id="github_session")
返回: ✅ 浏览器会话已创建（已恢复之前的会话状态）

AI 调用: browser_navigate(url="https://github.com")
返回: ✅ 已导航到 https://github.com
（此时已经是登录状态，无需重新登录）
```

---

## 数据存储

```
~/.browser_use_mcp/
├── sessions/
│   ├── {session_id}_profile/           # 浏览器用户数据
│   └── {session_id}_storage_state.json # 存储状态
└── screenshots/
    └── browser_screenshot_*.png        # 截图

browser_use_mcp/
└── .env                                # 凭证配置文件（不要提交到版本控制）
```

## 与 browser-use 原库的区别

| 特性 | browser-use 原库 | 本 MCP 服务器 |
|------|-----------------|--------------|
| 决策者 | 内置 Agent/LLM | AI 助手（你） |
| 控制方式 | 自然语言任务描述 | MCP 工具调用 |
| 灵活性 | Agent 自主决策 | 完全可控 |
| 适用场景 | 自动化任务 | 需要精确控制的场景 |

## 故障排除

### WSL 依赖

```bash
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2
```

### 会话恢复失败

```bash
ls -la ~/.browser_use_mcp/sessions/
```

### 凭证未加载

确保 `.env` 文件存在且格式正确：
```bash
cat browser_use_mcp/.env
```

## 许可证

MIT License
