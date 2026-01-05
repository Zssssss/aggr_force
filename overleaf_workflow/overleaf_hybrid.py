#!/usr/bin/env python3
"""
Overleaf Hybrid模式工作流
步骤1: 有界面登录并保存session
步骤2: 使用headless模式恢复session进行后续操作
"""

import sys
import os

# 添加browser_use_mcp到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'browser_use_mcp'))

print("=" * 70)
print("Overleaf Hybrid模式工作流")
print("=" * 70)

print("""
工作流程：

【步骤1】有界面登录（需要人工验证）
  1. 启动有界面浏览器
  2. 自动填充登录信息
  3. 人工完成验证码
  4. 保存session（cookies + localStorage）
  5. 手动关闭浏览器

【步骤2】无界面操作（自动化）
  1. 使用headless模式
  2. 恢复保存的session
  3. 自动进入项目和文件
  4. 执行各种自动化操作

开始执行...
""")

# 配置
SESSION_ID = "overleaf_session"
OVERLEAF_EMAIL = "1094569708@qq.com"
PROJECT_TITLE = "resume-master-260105"
TARGET_FILE = "resume-zh_CN.tex"

print(f"""
配置信息：
- Session ID: {SESSION_ID}
- 邮箱: {OVERLEAF_EMAIL}
- 项目: {PROJECT_TITLE}
- 文件: {TARGET_FILE}
""")

print("=" * 70)
print("请选择操作模式：")
print("  1. 步骤1 - 有界面登录并保存session")
print("  2. 步骤2 - 使用headless模式恢复session")
print("  3. 查看已保存的sessions")
print("  4. 删除session")
print("=" * 70)

choice = input("\n请输入选择 (1-4): ").strip()

if choice == "1":
    print("\n【步骤1】启动有界面登录流程...")
    print("\n提示：此步骤需要使用browser-use MCP工具")
    print("请在WeCoder中执行以下命令：\n")
    
    print("# 1. 创建有界面session")
    print(f'mcp--browser-use--browser_create_session(session_id="{SESSION_ID}", headless=False)')
    print()
    
    print("# 2. 导航到Overleaf登录页")
    print('mcp--browser-use--browser_navigate(url="https://www.overleaf.com/login")')
    print()
    
    print("# 3. 获取页面状态，查看可交互元素")
    print('mcp--browser-use--browser_get_state(include_screenshot=True)')
    print()
    
    print("# 4. 填充邮箱（根据get_state返回的index）")
    print(f'mcp--browser-use--browser_input(index=<email_index>, text="{OVERLEAF_EMAIL}")')
    print()
    
    print("# 5. 填充密码（使用敏感数据输入）")
    print('mcp--browser-use--browser_input_sensitive(index=<password_index>, credential_key="OVERLEAF_PASSWORD")')
    print()
    
    print("# 6. 点击登录按钮")
    print('mcp--browser-use--browser_click(index=<login_button_index>)')
    print()
    
    print("# 7. 等待60秒，手动完成验证")
    print('mcp--browser-use--browser_wait(seconds=60)')
    print()
    
    print("# 8. 保存session")
    print('mcp--browser-use--browser_save_session()')
    print()
    
    print("# 9. 关闭浏览器（session已保存）")
    print('mcp--browser-use--browser_close_session(save=True)')
    print()
    
    print("=" * 70)
    print("完成步骤1后，session将被保存")
    print("之后可以使用步骤2以headless模式恢复")
    print("=" * 70)

elif choice == "2":
    print("\n【步骤2】使用headless模式恢复session...")
    print("\n提示：此步骤需要使用browser-use MCP工具")
    print("请在WeCoder中执行以下命令：\n")
    
    print("# 1. 创建headless session（自动恢复之前保存的session）")
    print(f'mcp--browser-use--browser_create_session(session_id="{SESSION_ID}", headless=True)')
    print()
    
    print("# 2. 导航到Overleaf主页（session会自动恢复登录状态）")
    print('mcp--browser-use--browser_navigate(url="https://www.overleaf.com/project")')
    print()
    
    print("# 3. 获取页面状态")
    print('mcp--browser-use--browser_get_state(include_screenshot=True)')
    print()
    
    print(f"# 4. 查找并点击项目: {PROJECT_TITLE}")
    print('# 根据get_state返回的项目链接index')
    print('mcp--browser-use--browser_click(index=<project_index>)')
    print()
    
    print("# 5. 等待项目加载")
    print('mcp--browser-use--browser_wait(seconds=5)')
    print()
    
    print("# 6. 获取项目页面状态")
    print('mcp--browser-use--browser_get_state()')
    print()
    
    print(f"# 7. 点击文件: {TARGET_FILE}")
    print('mcp--browser-use--browser_click(index=<file_index>)')
    print()
    
    print("# 8. 提取文件内容")
    print('mcp--browser-use--browser_extract_content()')
    print()
    
    print("# 9. 或者提取为Markdown格式")
    print('mcp--browser-use--browser_extract_markdown()')
    print()
    
    print("# 10. 截图保存当前状态")
    print('mcp--browser-use--browser_screenshot(filename="overleaf_editor.png")')
    print()
    
    print("# 11. 完成后关闭session")
    print('mcp--browser-use--browser_close_session(save=True)')
    print()
    
    print("=" * 70)
    print("在headless模式下，所有操作都是自动化的")
    print("您可以通过截图查看当前状态")
    print("=" * 70)

elif choice == "3":
    print("\n查看已保存的sessions...")
    print("\n使用MCP工具：")
    print('mcp--browser-use--browser_list_sessions()')
    print()

elif choice == "4":
    print("\n删除session...")
    print("\n使用MCP工具：")
    print(f'mcp--browser-use--browser_delete_session(session_id="{SESSION_ID}")')
    print()

else:
    print("\n无效的选择")

print("\n" + "=" * 70)
print("Hybrid模式优势：")
print("  ✓ 步骤1：人工处理验证码（有界面）")
print("  ✓ 步骤2：自动化操作（无界面，高效）")
print("  ✓ Session持久化：登录一次，多次使用")
print("  ✓ 跨会话：关闭后可以恢复")
print("=" * 70)
