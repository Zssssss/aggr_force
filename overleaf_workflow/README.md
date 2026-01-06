# Overleaf 自动化工作流

这个工作流使用混合模式(Hybrid Mode)来自动化Overleaf项目的编辑，支持处理reCAPTCHA验证。

## 工作原理

### 两阶段流程

```
阶段1: Hybrid模式登录 (有头模式 - 手动编写代码)
  ├─ 手动编写代码打开浏览器窗口
  ├─ 手动编写代码导航到登录页
  ├─ 手动编写代码填入用户名密码
  ├─ 等待用户手动完成reCAPTCHA验证
  ├─ 手动编写代码检查登录状态
  └─ 手动编写代码保存登录会话
           ↓
阶段2: Headless模式自动化 (无头模式)
  ├─ 后台运行，不显示窗口
  ├─ 自动恢复登录状态
  ├─ 访问指定项目
  ├─ 编辑目标文件
  └─ 自动保存更改
```

### 改进说明

**step1_hybrid_login.py** 现在使用手动编写的代码来打开浏览器，而不是调用封装好的`hybrid_login`方法。这样做的好处：

1. **更透明**: 每一步操作都清晰可见
2. **更灵活**: 可以根据需要调整每个步骤
3. **更易调试**: 出问题时容易定位
4. **更好理解**: 学习浏览器自动化的最佳方式

## 前置准备

### 1. 确认环境配置

确保已安装browser_use_mcp的依赖：

```bash
cd ../browser_use_mcp
pip install -r requirements.txt
```

### 2. 配置登录凭证

编辑 `../browser_use_mcp/.env` 文件，确认Overleaf凭证已配置：

```bash
# ===== Overleaf 凭证 =====
OVERLEAF_EMAIL=1094569708@qq.com
OVERLEAF_PASSWORD=aggr_force123
```

## 使用步骤

### 步骤1: 首次登录 (Hybrid模式)

运行登录脚本，完成人工验证：

```bash
cd overleaf_workflow
python3 step1_hybrid_login.py
```

**操作流程：**

1. 脚本会打开浏览器窗口
2. 自动导航到Overleaf登录页
3. 自动填入用户名和密码
4. **等待你手动完成reCAPTCHA验证**
5. 登录成功后，按Enter键
6. 脚本自动保存登录会话

**预期输出：**

```
==============================================================
Overleaf Hybrid模式登录
==============================================================

[1/6] 创建浏览器会话(有头模式)...
✓ 会话创建成功: overleaf_session

[2/6] 导航到Overleaf登录页...
✓ 已打开登录页面

[3/6] 查找登录表单...
当前页面: Login - Overleaf
  找到邮箱输入框: 索引 5
  找到密码输入框: 索引 7

[4/6] 自动填入登录凭证...
✓ 已填入邮箱
✓ 已填入密码

==============================================================
请在浏览器中完成以下操作:
  1. 检查用户名和密码是否正确
  2. 点击登录按钮
  3. 完成reCAPTCHA验证(如果出现)
  4. 等待登录成功，进入Overleaf主页
==============================================================

完成登录后，按Enter键继续...
```

### 步骤2: 自动化编辑 (Headless模式)

登录成功后，使用headless模式自动访问项目：

```bash
python3 step2_headless_edit.py
```

**默认行为：**
- 项目标题: `resume-master-260105`
- 目标文件: `resume-zh_CN.tex`

**自定义参数：**

```bash
# 指定不同的项目和文件
python3 step2_headless_edit.py --project "my-project" --file "main.tex"

# 使用交互式模式（有头模式，方便调试）
python3 step2_headless_edit.py --interactive
```

**预期输出：**

```
==============================================================
Overleaf Headless模式自动化
==============================================================

[1/7] 恢复浏览器会话(headless模式)...
✓ 会话恢复成功: overleaf_session

[2/7] 导航到Overleaf主页...
✓ 当前页面: Your Projects - Overleaf
  URL: https://www.overleaf.com/project

[3/7] 查找项目: resume-master-260105
✓ 找到项目链接: 索引 12

[4/7] 进入项目...
✓ 当前页面: resume-master-260105 - Overleaf
  URL: https://www.overleaf.com/project/xxxxx

[5/7] 查找文件: resume-zh_CN.tex
✓ 找到文件: 索引 8

[6/7] 打开文件...
✓ 文件已打开

[7/7] 编辑文件...
✓ 文件编辑完成

==============================================================
✓ Headless模式自动化完成!
==============================================================
```

## 交互式编辑模式

如果需要更灵活的控制，可以使用交互式模式：

```bash
python3 step2_headless_edit.py --interactive
```

交互式模式提供以下功能：

1. **查看当前页面状态** - 显示页面标题、URL和可交互元素
2. **点击元素** - 通过索引点击页面元素
3. **输入文本** - 在输入框中输入文本
4. **发送按键** - 发送键盘按键（Enter, Ctrl+A等）
5. **滚动页面** - 上下滚动页面
6. **截图** - 保存当前页面截图
7. **提取页面内容** - 提取页面文本内容

## 文件编辑功能

### 基础编辑框架

`step2_headless_edit.py` 中的 `edit_resume_file()` 函数提供了基础的编辑框架。你可以根据需求扩展：

```python
async def edit_resume_file(manager, edit_instructions):
    """编辑resume-zh_CN.tex文件"""
    # 等待编辑器加载
    await asyncio.sleep(3)
    
    # 查找编辑器
    state = await manager.get_state(include_screenshot=False)
    editor_idx = None
    for idx, elem in enumerate(state['elements']):
        if 'editor' in str(elem).lower():
            editor_idx = idx
            break
    
    # 点击编辑器获取焦点
    await manager.click(editor_idx)
    
    # 执行编辑操作
    # 示例：全选并替换内容
    await manager.send_keys("Ctrl+a")  # 全选
    await manager.send_keys("Delete")  # 删除
    await manager.input(editor_idx, "新的内容")  # 输入新内容
    
    return True
```

### 常用编辑操作

```python
# 全选
await manager.send_keys("Ctrl+a")

# 复制
await manager.send_keys("Ctrl+c")

# 粘贴
await manager.send_keys("Ctrl+v")

# 查找
await manager.send_keys("Ctrl+f")

# 撤销
await manager.send_keys("Ctrl+z")

# 保存（Overleaf自动保存，但可以手动触发）
await manager.send_keys("Ctrl+s")

# 移动光标
await manager.send_keys("Home")  # 行首
await manager.send_keys("End")   # 行尾
await manager.send_keys("Ctrl+Home")  # 文件开头
await manager.send_keys("Ctrl+End")   # 文件结尾

# 输入文本
await manager.input(editor_idx, "你的LaTeX代码")
```

## 会话管理

### 查看保存的会话

```python
from browser_tools import get_browser_manager

manager = get_browser_manager()
sessions = await manager.list_sessions()

for session in sessions['sessions']:
    print(f"会话: {session['session_id']}")
    print(f"  修改时间: {session['modified_at']}")
```

### 删除过期会话

```python
await manager.delete_session("overleaf_session")
```

### 会话存储位置

```
~/.browser_use_mcp/sessions/
└── overleaf_session_storage_state.json
```

## 故障排除

### 问题1: 会话恢复失败

**症状：** 运行step2时提示"未找到保存的会话"

**解决：**
```bash
# 重新运行登录脚本
python3 step1_hybrid_login.py
```

### 问题2: 会话已过期

**症状：** Headless模式下被重定向到登录页

**解决：**
```bash
# 会话过期，需要重新登录
python3 step1_hybrid_login.py
```

### 问题3: 找不到项目或文件

**症状：** 提示"未找到项目"或"未找到文件"

**解决：**
```bash
# 使用交互式模式手动查看
python3 step2_headless_edit.py --interactive

# 或指定正确的项目名称
python3 step2_headless_edit.py --project "正确的项目名称"
```

### 问题4: 编辑器定位失败

**症状：** 提示"未找到编辑器"

**解决：**
- 使用交互式模式查看页面元素
- 手动定位编辑器元素的索引
- 修改 `edit_resume_file()` 函数中的查找逻辑

## 高级用法

### 自定义编辑逻辑

创建自己的编辑脚本：

```python
#!/usr/bin/env python3
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'browser_use_mcp'))
from browser_tools import get_browser_manager

async def my_custom_edit():
    manager = get_browser_manager()
    
    # 恢复会话
    await manager.create_session("overleaf_session", headless=True)
    
    # 导航到项目
    await manager.navigate("https://www.overleaf.com/project/xxxxx")
    await asyncio.sleep(5)
    
    # 你的自定义编辑逻辑
    # ...
    
    await manager.close_session(save=True)

asyncio.run(my_custom_edit())
```

### 批量处理多个文件

```python
async def batch_edit_files(file_list):
    manager = get_browser_manager()
    await manager.create_session("overleaf_session", headless=True)
    
    for filename in file_list:
        # 查找并打开文件
        file_idx = await find_file_in_project(manager, filename)
        await manager.click(file_idx)
        await asyncio.sleep(2)
        
        # 编辑文件
        await edit_resume_file(manager, None)
        
        # 等待保存
        await asyncio.sleep(1)
    
    await manager.close_session(save=True)
```

## 注意事项

1. **会话有效期**: Overleaf的登录会话通常可以保持几天到几周，但可能会过期
2. **自动保存**: Overleaf会自动保存编辑内容，无需手动保存
3. **并发限制**: 不要同时运行多个脚本访问同一个会话
4. **网络延迟**: 根据网络情况调整 `asyncio.sleep()` 的等待时间
5. **元素索引**: 页面元素的索引可能会变化，建议使用交互式模式确认

## 相关文档

- [Browser Use MCP 文档](../browser_use_mcp/README.md)
- [Hybrid模式指南](../browser_use_mcp/HYBRID_MODE_GUIDE.md)
- [快速开始示例](../browser_use_mcp/quick_start_hybrid.py)

## 支持

如有问题，请查看：
1. Browser Use MCP的日志输出
2. 使用交互式模式调试
3. 检查会话文件是否存在
