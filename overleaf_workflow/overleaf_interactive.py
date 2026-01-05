#!/usr/bin/env python3
"""
Overleaf交互式自动化脚本 - 持久化会话
登录后保持浏览器打开，支持后续交互操作
"""

import sys
import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Overleaf登录信息
OVERLEAF_EMAIL = "1094569708@qq.com"
OVERLEAF_PASSWORD = "aggr_force123"
PROJECT_TITLE = "resume-master-260105"

class OverleafSession:
    """Overleaf会话管理类"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def start(self):
        """启动浏览器会话"""
        print("=" * 60)
        print("Overleaf交互式自动化 - 持久化会话")
        print("=" * 60)
        
        print("\n[1/6] 启动浏览器...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        self.context = self.browser.new_context(
            viewport=None,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.page = self.context.new_page()
        return self
        
    def login(self):
        """执行登录流程"""
        try:
            print("\n[2/6] 导航到Overleaf登录页面...")
            self.page.goto("https://www.overleaf.com/login", wait_until="networkidle", timeout=30000)
            time.sleep(2)
            
            print("\n[3/6] 填充登录信息...")
            
            # 填充邮箱
            email_input = self.page.locator('input[name="email"], input[type="email"], input#email')
            if email_input.count() > 0:
                email_input.first.fill(OVERLEAF_EMAIL)
                print(f"  ✓ 已填充邮箱: {OVERLEAF_EMAIL}")
            
            time.sleep(1)
            
            # 填充密码
            password_input = self.page.locator('input[name="password"], input[type="password"], input#password')
            if password_input.count() > 0:
                password_input.first.fill(OVERLEAF_PASSWORD)
                print(f"  ✓ 已填充密码")
            
            time.sleep(1)
            
            # 点击登录按钮
            login_button = self.page.locator('button[type="submit"], button:has-text("Login"), button:has-text("登录")')
            if login_button.count() > 0:
                login_button.first.click()
                print("  ✓ 已点击登录按钮")
            
            print("\n[4/6] 等待人工完成验证...")
            print("=" * 60)
            print("请在浏览器中完成验证，然后等待60秒...")
            print("=" * 60)
            
            for i in range(60, 0, -10):
                print(f"  剩余 {i} 秒...")
                time.sleep(10)
            
            print("\n[5/6] 等待页面加载...")
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"\n✗ 登录过程出错: {e}")
            return False
    
    def open_project(self, project_title=None):
        """打开指定项目"""
        if project_title is None:
            project_title = PROJECT_TITLE
            
        try:
            print(f"\n[6/6] 查找项目: {project_title}...")
            
            # 查找项目链接
            project_links = self.page.locator(f'a:has-text("{project_title}")')
            if project_links.count() > 0:
                print(f"  ✓ 找到项目链接")
                project_links.first.click()
                time.sleep(5)
                
                print("\n✓ 成功进入项目！")
                print("等待编辑器加载...")
                time.sleep(3)
                return True
            else:
                print(f"  ✗ 未找到项目: {project_title}")
                return False
                
        except Exception as e:
            print(f"\n✗ 打开项目出错: {e}")
            return False
    
    def open_file(self, filename="resume-zh_CN.tex"):
        """打开指定文件"""
        try:
            print(f"\n查找文件: {filename}...")
            time.sleep(2)
            
            tex_file = self.page.locator(f'text={filename}')
            if tex_file.count() > 0:
                print(f"  ✓ 找到文件: {filename}")
                tex_file.first.click()
                time.sleep(2)
                print("  ✓ 已打开文件")
                return True
            else:
                print(f"  ✗ 未找到文件: {filename}")
                return False
                
        except Exception as e:
            print(f"\n✗ 打开文件出错: {e}")
            return False
    
    def get_editor_content(self):
        """获取编辑器内容"""
        try:
            # Overleaf使用Ace编辑器
            editor = self.page.locator('.ace_editor')
            if editor.count() > 0:
                # 获取编辑器文本
                content = self.page.evaluate('''() => {
                    const editor = ace.edit(document.querySelector('.ace_editor'));
                    return editor.getValue();
                }''')
                return content
            return None
        except Exception as e:
            print(f"获取编辑器内容失败: {e}")
            return None
    
    def set_editor_content(self, content):
        """设置编辑器内容"""
        try:
            self.page.evaluate(f'''() => {{
                const editor = ace.edit(document.querySelector('.ace_editor'));
                editor.setValue(`{content}`);
            }}''')
            print("✓ 已更新编辑器内容")
            return True
        except Exception as e:
            print(f"设置编辑器内容失败: {e}")
            return False
    
    def insert_text(self, text, line=None):
        """在编辑器中插入文本"""
        try:
            if line is not None:
                # 在指定行插入
                self.page.evaluate(f'''() => {{
                    const editor = ace.edit(document.querySelector('.ace_editor'));
                    editor.session.insert({{row: {line}, column: 0}}, `{text}\\n`);
                }}''')
            else:
                # 在当前光标位置插入
                self.page.evaluate(f'''() => {{
                    const editor = ace.edit(document.querySelector('.ace_editor'));
                    editor.insert(`{text}`);
                }}''')
            print(f"✓ 已插入文本")
            return True
        except Exception as e:
            print(f"插入文本失败: {e}")
            return False
    
    def find_and_replace(self, find_text, replace_text):
        """查找并替换文本"""
        try:
            self.page.evaluate(f'''() => {{
                const editor = ace.edit(document.querySelector('.ace_editor'));
                const content = editor.getValue();
                const newContent = content.replace(/{find_text}/g, `{replace_text}`);
                editor.setValue(newContent);
            }}''')
            print(f"✓ 已替换文本: '{find_text}' -> '{replace_text}'")
            return True
        except Exception as e:
            print(f"替换文本失败: {e}")
            return False
    
    def compile_pdf(self):
        """编译PDF"""
        try:
            # 查找并点击Recompile按钮
            recompile_btn = self.page.locator('button:has-text("Recompile")')
            if recompile_btn.count() > 0:
                recompile_btn.first.click()
                print("✓ 已触发PDF编译")
                time.sleep(3)
                return True
            return False
        except Exception as e:
            print(f"编译PDF失败: {e}")
            return False
    
    def screenshot(self, filename="overleaf_screenshot.png"):
        """截取当前页面"""
        try:
            filepath = os.path.join(os.path.dirname(__file__), filename)
            self.page.screenshot(path=filepath)
            print(f"✓ 已保存截图: {filepath}")
            return filepath
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    def keep_alive(self):
        """保持会话活跃"""
        print("\n" + "=" * 60)
        print("浏览器会话保持活跃状态")
        print("您可以：")
        print("  1. 在浏览器中手动编辑文件")
        print("  2. 通过Python API进行自动化操作")
        print("  3. 使用browser-use MCP工具进行交互")
        print("=" * 60)
        print("\n会话将保持打开，直到手动关闭...")
        
        # 保持会话活跃，不关闭浏览器
        try:
            while True:
                time.sleep(60)
                # 可以添加心跳检测
                if self.page.is_closed():
                    print("\n页面已关闭")
                    break
        except KeyboardInterrupt:
            print("\n\n收到中断信号，准备关闭...")
    
    def close(self):
        """关闭浏览器会话"""
        print("\n关闭浏览器...")
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("完成！")


def main():
    """主函数"""
    session = OverleafSession()
    
    try:
        # 启动会话
        session.start()
        
        # 执行登录
        if not session.login():
            print("登录失败")
            return
        
        # 打开项目
        if not session.open_project():
            print("打开项目失败")
            return
        
        # 打开文件
        session.open_file("resume-zh_CN.tex")
        
        # 保持会话活跃
        session.keep_alive()
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
