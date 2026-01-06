# 混合模式使用指南 - 处理人工验证场景

## 问题场景

在使用浏览器自动化时,经常遇到需要人工处理的验证:
- ✅ reCAPTCHA 验证码
- ✅ 图片验证码
- ✅ 短信验证码
- ✅ 邮箱验证
- ✅ 二维码扫码登录
- ✅ 人脸识别等生物验证

**传统headless模式的困境**: 无法显示浏览器窗口,无法人工操作

## 解决方案: 混合模式

### 核心思路

```
┌─────────────────────────────────────────────────────────────┐
│  阶段1: 首次登录 (有头模式 headless=False)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. 显示浏览器窗口                                     │   │
│  │  2. 人工完成登录和验证                                 │   │
│  │  3. 保存会话状态 (cookies + localStorage)             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    会话状态持久化
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  阶段2: 自动化操作 (无头模式 headless=True)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. 后台运行,不显示窗口                                │   │
│  │  2. 自动恢复登录状态                                   │   │
│  │  3. 执行自动化任务                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 优势

1. **兼顾人工和自动化**: 登录时人工处理,后续完全自动化
2. **会话持久化**: 登录状态可以保持数天甚至数周
3. **多会话管理**: 可以为不同网站/账号创建独立会话
4. **安全性**: 敏感信息(密码)可以通过.env文件管理,不暴露给AI

## 使用方法

### 方法1: 手动编写代码打开浏览器（推荐）

这是最透明、最灵活的方式，每一步操作都清晰可见：

```python
import asyncio
from browser_tools import get_browser_manager

async def main():
    manager = get_browser_manager()
    
    # === 首次登录: 有头模式 - 手动编写每一步 ===
    print("步骤1: 创建浏览器会话...")
    result = await manager.create_session(
        session_id="my_session",
        headless=False  # 显示浏览器窗口
    )
    print(f"✓ 会话创建: {result['message']}")
    
    print("\n步骤2: 导航到登录页...")
    await manager.navigate("https://example.com/login")
    print("✓ 已打开登录页面")
    
    print("\n步骤3: 等待页面加载...")
    await asyncio.sleep(2)
    
    # 可选：自动填入凭证
    print("\n步骤4: 获取页面状态...")
    state = await manager.get_state(include_screenshot=False)
    print(f"✓ 页面标题: {state['title']}")
    
    # 人工完成登录...
    print("\n请在浏览器中完成登录...")
    input("完成登录后按Enter...")
    
    print("\n步骤5: 保存会话...")
    await manager.save_session()
    print("✓ 会话已保存")
    
    print("\n步骤6: 关闭浏览器...")
    await manager.close_session()
    print("✓ 浏览器已关闭")
    
    # === 后续自动化: 无头模式 ===
    print("\n\n=== 后续自动化 ===")
    await manager.create_session(
        session_id="my_session",
        headless=True  # 后台运行
    )
    # 会话自动恢复,已登录状态
    await manager.navigate("https://example.com/dashboard")
    # 执行自动化操作...
    
    await manager.close_session()

asyncio.run(main())
```

**优势：**
- ✅ 每一步都清晰可见，易于理解
- ✅ 可以在任何步骤添加调试信息
- ✅ 灵活调整等待时间和操作顺序
- ✅ 出问题时容易定位和修复

### 方法2: 使用封装的hybrid_login方法

如果你想要更简洁的代码，可以使用封装好的方法：

```python
import asyncio
from browser_tools import get_browser_manager

async def main():
    manager = get_browser_manager()
    
    # 一行代码完成混合模式登录
    result = await manager.hybrid_login(
        session_id="my_session",
        login_url="https://example.com/login",
        wait_seconds=60  # 等待60秒让用户完成登录
    )
    
    if result['success']:
        print("✓ 登录完成，会话已保存")
    
    # 后续使用无头模式
    await manager.create_session("my_session", headless=True)
    await manager.navigate("https://example.com/dashboard")
    await manager.close_session()

asyncio.run(main())
```

### 方法3: 使用MCP工具(通过AI助手)

#### 步骤1: 首次登录(有头模式)

```
用户: 帮我登录GitHub,我需要手动处理验证

AI助手会执行:
1. browser_create_session(session_id="github_login", headless=False)
2. browser_navigate(url="https://github.com/login")
3. 等待你完成人工登录
4. browser_save_session()
5. browser_close_session()
```

#### 步骤2: 后续自动化(无头模式)

```
用户: 用之前保存的GitHub会话,帮我查看我的仓库列表

AI助手会执行:
1. browser_create_session(session_id="github_login", headless=True)
   # 自动恢复登录状态
2. browser_navigate(url="https://github.com/你的用户名?tab=repositories")
3. browser_get_state() # 获取页面内容
4. 提取仓库信息...
```

## 完整示例

### 示例1: GitHub登录

```python
#!/usr/bin/env python3
import asyncio
from browser_tools import get_browser_manager

async def github_login_once():
    """首次登录GitHub - 有头模式"""
    manager = get_browser_manager()
    
    # 创建会话(有头模式)
    await manager.create_session(
        session_id="github_work",
        headless=False
    )
    
    # 导航到登录页
    await manager.navigate("https://github.com/login")
    
    print("请在浏览器中完成登录...")
    print("  1. 输入用户名密码")
    print("  2. 完成验证(如果有)")
    print("  3. 等待登录成功")
    
    input("\n完成后按Enter...")
    
    # 保存会话
    await manager.save_session()
    print("✓ 登录状态已保存!")
    
    await manager.close_session()

async def github_auto_task():
    """自动化任务 - 无头模式"""
    manager = get_browser_manager()
    
    # 恢复会话(无头模式)
    result = await manager.create_session(
        session_id="github_work",
        headless=True
    )
    
    if not result['restored']:
        print("❌ 未找到保存的会话,请先执行首次登录")
        return
    
    print("✓ 已恢复登录状态")
    
    # 访问需要登录的页面
    await manager.navigate("https://github.com/settings/profile")
    
    # 获取页面状态
    state = await manager.get_state()
    print(f"当前页面: {state['title']}")
    
    # 执行自动化操作...
    
    await manager.close_session()

# 运行
asyncio.run(github_login_once())  # 首次运行
# asyncio.run(github_auto_task())  # 后续运行
```

### 示例2: 企业内网系统

```python
async def intranet_login():
    """企业内网登录 - 可能需要VPN、多因素认证等"""
    manager = get_browser_manager()
    
    await manager.create_session(
        session_id="company_intranet",
        headless=False  # 显示窗口
    )
    
    await manager.navigate("https://intranet.company.com")
    
    print("请完成以下步骤:")
    print("  1. 输入工号和密码")
    print("  2. 完成短信验证码")
    print("  3. 可能需要扫描二维码")
    
    input("完成后按Enter...")
    
    await manager.save_session()
    await manager.close_session()
    
    print("✓ 内网登录状态已保存,后续可以无头模式访问")
```

## 会话管理

### 查看所有保存的会话

```python
manager = get_browser_manager()
sessions = await manager.list_sessions()

for session in sessions['sessions']:
    print(f"会话: {session['session_id']}")
    print(f"  修改时间: {session['modified_at']}")
    print(f"  文件大小: {session['size_bytes']} bytes")
```

### 删除过期会话

```python
await manager.delete_session("old_session_id")
```

### 会话存储位置

```
~/.browser_use_mcp/sessions/
├── github_work_storage_state.json
├── company_intranet_storage_state.json
└── other_session_storage_state.json
```

## 高级技巧

### 技巧1: 定期刷新会话

某些网站的登录状态会过期,可以定期刷新:

```python
async def refresh_session():
    """定期刷新会话,保持登录状态"""
    manager = get_browser_manager()
    
    # 使用有头模式恢复会话
    await manager.create_session(
        session_id="my_session",
        headless=False  # 可以看到是否需要重新登录
    )
    
    await manager.navigate("https://example.com/dashboard")
    
    # 检查是否还在登录状态
    state = await manager.get_state()
    if "login" in state['url'].lower():
        print("会话已过期,需要重新登录")
        input("请重新登录后按Enter...")
    
    # 保存刷新后的会话
    await manager.save_session()
    await manager.close_session()
```

### 技巧2: 多账号管理

为不同账号创建不同会话:

```python
# 账号1
await manager.create_session("github_account1", headless=False)
# ... 登录账号1 ...
await manager.save_session()

# 账号2
await manager.create_session("github_account2", headless=False)
# ... 登录账号2 ...
await manager.save_session()

# 使用时切换
await manager.create_session("github_account1", headless=True)  # 使用账号1
await manager.create_session("github_account2", headless=True)  # 使用账号2
```

### 技巧3: 结合敏感数据管理

对于不需要验证码的登录,可以结合`.env`文件:

```bash
# browser_use_mcp/.env
GITHUB_USERNAME=your_username
GITHUB_PASSWORD=your_password
```

```python
# 半自动登录
await manager.create_session("github", headless=False)
await manager.navigate("https://github.com/login")

# 获取页面状态,找到输入框
state = await manager.get_state()

# 自动填入用户名密码(从.env读取)
await manager.input_sensitive(0, "GITHUB_USERNAME")  # 用户名输入框
await manager.input_sensitive(1, "GITHUB_PASSWORD")  # 密码输入框

# 人工处理验证码
input("请完成验证码后按Enter...")

await manager.save_session()
```

## 常见问题

### Q1: 会话能保持多久?

A: 取决于网站的cookie过期策略,通常可以保持几天到几周。定期刷新可以延长有效期。

### Q2: 无头模式下会话恢复失败怎么办?

A: 可能是会话过期,重新使用有头模式登录一次即可。

### Q3: 可以在不同机器间共享会话吗?

A: 理论上可以,复制`~/.browser_use_mcp/sessions/`目录即可,但某些网站会检测IP变化。

### Q4: 如何处理需要定期输入验证码的网站?

A: 这种情况建议使用有头模式,或者考虑使用API而不是浏览器自动化。

## 最佳实践

1. **首次登录使用有头模式**: 确保能看到并处理所有验证
2. **及时保存会话**: 登录成功后立即保存
3. **使用有意义的会话名**: 如`github_work`, `company_intranet`
4. **定期刷新长期使用的会话**: 避免过期
5. **敏感信息使用.env**: 不要硬编码密码
6. **测试会话有效性**: 自动化前先检查会话是否还有效

## 运行示例代码

```bash
cd browser_use_mcp
python3 example_hybrid_mode.py
```

这个示例会引导你完成完整的混合模式流程。

## 总结

混合模式是处理需要人工验证场景的最佳方案:
- ✅ 首次登录: 有头模式 (`headless=False`) + 人工处理验证
- ✅ 保存会话: `save_session()` 持久化登录状态
- ✅ 后续自动化: 无头模式 (`headless=True`) + 自动恢复会话

这样既能处理复杂的人工验证,又能享受无头模式的高效自动化!
