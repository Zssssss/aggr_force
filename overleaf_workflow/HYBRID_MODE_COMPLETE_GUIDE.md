# Overleaf Hybrid模式完整操作指南

## 概述

本指南展示如何使用browser-use MCP工具实现Overleaf的Hybrid模式工作流：
1. **步骤1**：有界面登录并保存session（人工处理验证）
2. **步骤2**：headless模式恢复session（自动化操作）

## 前置准备

### 1. 配置凭证

已配置文件：[`browser_use_mcp/.env`](../browser_use_mcp/.env)

```bash
OVERLEAF_EMAIL=1094569708@qq.com
OVERLEAF_PASSWORD=aggr_force123
```

### 2. 确认MCP服务运行

browser-use MCP服务应该已经在运行中。

## 步骤1：有界面登录并保存Session

### 1.1 创建有界面Session

由于WSL环境限制，我们需要使用Windows端的浏览器。有两种方案：

#### 方案A：使用X Server（推荐）

```bash
# 1. 在Windows上启动VcXsrv
# 2. 配置WSL的DISPLAY环境变量
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# 3. 测试X Server
xclock  # 如果能看到时钟窗口，说明配置成功
```

然后使用MCP工具：

```python
mcp--browser-use--browser_create_session(
    session_id="overleaf_session",
    headless=False
)
```

#### 方案B：直接在Windows上运行Python脚本

创建Windows端脚本：`overleaf_login_windows.py`

```python
# 在Windows PowerShell中运行
cd \\wsl$\Ubuntu\home\zsss\zsss_useful_tools\aggr_force\overleaf_workflow
python overleaf_login_windows.py
```

### 1.2 导航到Overleaf登录页

```python
mcp--browser-use--browser_navigate(
    url="https://www.overleaf.com/login"
)
```

### 1.3 获取页面状态

```python
mcp--browser-use--browser_get_state(
    include_screenshot=True
)
```

这将返回页面上所有可交互元素的列表，每个元素都有一个index。

### 1.4 填充登录信息

根据`browser_get_state`返回的元素列表，找到邮箱和密码输入框的index：

```python
# 填充邮箱
mcp--browser-use--browser_input(
    index=<email_input_index>,  # 例如：0
    text="1094569708@qq.com"
)

# 填充密码（使用敏感数据输入）
mcp--browser-use--browser_input_sensitive(
    index=<password_input_index>,  # 例如：1
    credential_key="OVERLEAF_PASSWORD"
)
```

### 1.5 点击登录按钮

```python
mcp--browser-use--browser_click(
    index=<login_button_index>  # 例如：2
)
```

### 1.6 等待并完成人工验证

```python
# 等待60秒供用户完成验证码
mcp--browser-use--browser_wait(seconds=60)
```

在这60秒内，请在浏览器中：
- 完成验证码（如果有）
- 完成二次验证（如果需要）
- 等待成功登录到Overleaf主页

### 1.7 保存Session

```python
mcp--browser-use--browser_save_session()
```

这将保存：
- Cookies
- LocalStorage
- SessionStorage
- 其他浏览器状态

### 1.8 关闭浏览器

```python
mcp--browser-use--browser_close_session(save=True)
```

✅ **步骤1完成！** Session已保存，可以随时恢复。

---

## 步骤2：Headless模式恢复Session

### 2.1 创建Headless Session（自动恢复）

```python
mcp--browser-use--browser_create_session(
    session_id="overleaf_session",  # 使用相同的session_id
    headless=True  # 无界面模式
)
```

这将自动恢复之前保存的session，包括登录状态。

### 2.2 导航到项目列表页

```python
mcp--browser-use--browser_navigate(
    url="https://www.overleaf.com/project"
)
```

### 2.3 获取页面状态

```python
mcp--browser-use--browser_get_state(
    include_screenshot=True
)
```

### 2.4 查找并点击项目

根据返回的元素列表，找到"resume-master-260105"项目的index：

```python
mcp--browser-use--browser_click(
    index=<project_link_index>
)
```

或者使用搜索功能：

```python
mcp--browser-use--browser_scroll_to_text(
    text="resume-master-260105"
)
```

### 2.5 等待项目加载

```python
mcp--browser-use--browser_wait(seconds=5)
```

### 2.6 获取项目页面状态

```python
mcp--browser-use--browser_get_state()
```

### 2.7 打开目标文件

找到"resume-zh_CN.tex"文件的index并点击：

```python
mcp--browser-use--browser_click(
    index=<file_index>
)
```

### 2.8 提取文件内容

```python
# 提取纯文本内容
mcp--browser-use--browser_extract_content()

# 或提取为Markdown格式
mcp--browser-use--browser_extract_markdown()
```

### 2.9 截图保存状态

```python
mcp--browser-use--browser_screenshot(
    filename="overleaf_editor.png"
)
```

### 2.10 执行编辑操作（可选）

如果需要编辑文件，可以使用：

```python
# 在输入框中输入文本
mcp--browser-use--browser_input(
    index=<editor_index>,
    text="新的LaTeX内容"
)

# 或发送键盘命令
mcp--browser-use--browser_send_keys(
    keys="Control+a"  # 全选
)
mcp--browser-use--browser_send_keys(
    keys="Control+c"  # 复制
)
```

### 2.11 保存并关闭

```python
# 保存session（如果有更改）
mcp--browser-use--browser_save_session()

# 关闭浏览器
mcp--browser-use--browser_close_session(save=True)
```

✅ **步骤2完成！** 已在headless模式下完成所有操作。

---

## 其他有用的命令

### 查看已保存的Sessions

```python
mcp--browser-use--browser_list_sessions()
```

### 删除Session

```python
mcp--browser-use--browser_delete_session(
    session_id="overleaf_session"
)
```

### 获取浏览器状态

```python
mcp--browser-use--browser_get_status()
```

### 查看可用凭证

```python
mcp--browser-use--browser_list_credentials()
```

---

## 完整示例脚本

### Python脚本示例

```python
#!/usr/bin/env python3
"""
Overleaf自动化操作示例
使用browser-use MCP工具
"""

# 注意：这些是MCP工具调用，需要在WeCoder环境中执行

# 步骤1：有界面登录（首次）
# mcp--browser-use--browser_create_session(session_id="overleaf_session", headless=False)
# mcp--browser-use--browser_navigate(url="https://www.overleaf.com/login")
# ... 填充表单、登录、保存session ...

# 步骤2：headless模式操作（后续）
# mcp--browser-use--browser_create_session(session_id="overleaf_session", headless=True)
# mcp--browser-use--browser_navigate(url="https://www.overleaf.com/project")
# ... 打开项目、编辑文件 ...
```

---

## 故障排除

### 问题1：无法启动有界面浏览器（WSL）

**原因**：WSL没有X Server

**解决方案**：
1. 安装并启动VcXsrv（Windows端）
2. 配置DISPLAY环境变量
3. 或者直接在Windows上运行Python脚本

### 问题2：Session恢复失败

**原因**：Session过期或被清除

**解决方案**：
1. 重新执行步骤1，重新登录并保存session
2. 检查session文件是否存在

### 问题3：找不到元素

**原因**：页面结构变化或加载未完成

**解决方案**：
1. 使用`browser_wait()`等待页面加载
2. 使用`browser_get_state()`重新获取元素列表
3. 使用`browser_screenshot()`查看当前页面状态

---

## Hybrid模式的优势

| 特性 | 有界面模式 | Headless模式 |
|------|-----------|-------------|
| 速度 | 较慢 | 快速 |
| 资源占用 | 高 | 低 |
| 可视化 | ✅ | ❌ |
| 验证码处理 | ✅ 人工 | ❌ |
| 自动化程度 | 中 | 高 |
| 适用场景 | 首次登录 | 后续操作 |

**Hybrid模式结合了两者的优势**：
- 首次登录使用有界面模式，人工处理验证
- 后续操作使用headless模式，高效自动化
- Session持久化，登录一次，多次使用

---

## 总结

通过Hybrid模式，您可以：

1. ✅ **一次登录，多次使用** - Session持久化
2. ✅ **人工验证，自动操作** - 结合人工和自动化优势
3. ✅ **跨会话恢复** - 关闭后可以恢复
4. ✅ **高效自动化** - Headless模式性能优秀
5. ✅ **灵活控制** - 可随时切换模式

这正是browser-use MCP工具设计的核心理念！
