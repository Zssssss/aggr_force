#!/usr/bin/env python3
"""
Overleaf自动化登录脚本 - Hybrid模式
使用Playwright实现自动化登录和项目访问
"""

import sys
import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Overleaf登录信息
OVERLEAF_EMAIL = "1094569708@qq.com"
OVERLEAF_PASSWORD = "aggr_force123"
PROJECT_TITLE = "resume-master-260105"

def main():
    """主函数：实现Overleaf登录和项目访问"""
    
    print("=" * 60)
    print("Overleaf自动化登录脚本 - Hybrid模式")
    print("=" * 60)
    
    with sync_playwright() as p:
        # 启动浏览器（非无头模式，方便人工验证）
        print("\n[1/6] 启动浏览器...")
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        
        context = browser.new_context(
            viewport=None,  # 使用最大化窗口
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        try:
            # 步骤1: 导航到Overleaf登录页面
            print("\n[2/6] 导航到Overleaf登录页面...")
            page.goto("https://www.overleaf.com/login", wait_until="networkidle", timeout=30000)
            time.sleep(2)
            
            # 步骤2: 填充登录信息
            print("\n[3/6] 填充登录信息...")
            
            # 查找并填充邮箱
            email_input = page.locator('input[name="email"], input[type="email"], input#email')
            if email_input.count() > 0:
                email_input.first.fill(OVERLEAF_EMAIL)
                print(f"  ✓ 已填充邮箱: {OVERLEAF_EMAIL}")
            else:
                print("  ✗ 未找到邮箱输入框")
            
            time.sleep(1)
            
            # 查找并填充密码
            password_input = page.locator('input[name="password"], input[type="password"], input#password')
            if password_input.count() > 0:
                password_input.first.fill(OVERLEAF_PASSWORD)
                print(f"  ✓ 已填充密码")
            else:
                print("  ✗ 未找到密码输入框")
            
            time.sleep(1)
            
            # 点击登录按钮
            login_button = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("登录")')
            if login_button.count() > 0:
                login_button.first.click()
                print("  ✓ 已点击登录按钮")
            else:
                print("  ✗ 未找到登录按钮")
            
            # 步骤3: 等待人工完成验证
            print("\n[4/6] 等待人工完成验证...")
            print("=" * 60)
            print("请在浏览器中完成以下操作：")
            print("  1. 如果出现验证码，请手动完成验证")
            print("  2. 如果需要二次验证，请完成相关操作")
            print("  3. 等待成功登录到Overleaf主页")
            print("=" * 60)
            
            # 使用更长的等待时间供用户完成验证
            print("\n等待60秒供您完成验证...")
            print("提示：完成验证后，脚本会自动继续")
            for i in range(60, 0, -10):
                print(f"  剩余 {i} 秒...")
                time.sleep(10)
            print("  继续执行...")
            
            # 步骤4: 等待页面加载完成
            print("\n[5/6] 等待页面加载...")
            time.sleep(3)
            
            # 步骤5: 查找并进入指定项目
            print(f"\n[6/6] 查找项目: {PROJECT_TITLE}...")
            
            # 尝试多种方式查找项目
            project_found = False
            
            # 方法1: 通过项目标题查找
            project_links = page.locator(f'a:has-text("{PROJECT_TITLE}")')
            if project_links.count() > 0:
                print(f"  ✓ 找到项目链接")
                project_links.first.click()
                project_found = True
                time.sleep(3)
            
            # 方法2: 如果方法1失败，尝试搜索所有项目链接
            if not project_found:
                print("  尝试搜索所有项目...")
                all_project_links = page.locator('a[href*="/project/"]')
                count = all_project_links.count()
                print(f"  找到 {count} 个项目链接")
                
                for i in range(count):
                    link = all_project_links.nth(i)
                    text = link.inner_text()
                    if PROJECT_TITLE in text:
                        print(f"  ✓ 找到匹配项目: {text}")
                        link.click()
                        project_found = True
                        time.sleep(3)
                        break
            
            if project_found:
                print("\n✓ 成功进入项目！")
                print("\n等待编辑器加载...")
                time.sleep(5)
                
                # 尝试查找并打开resume-zh_CN.tex文件
                print("\n查找 resume-zh_CN.tex 文件...")
                
                # 等待文件树加载
                time.sleep(2)
                
                # 尝试点击文件
                tex_file = page.locator('text=resume-zh_CN.tex')
                if tex_file.count() > 0:
                    print("  ✓ 找到 resume-zh_CN.tex 文件")
                    tex_file.first.click()
                    time.sleep(2)
                    print("  ✓ 已打开文件")
                else:
                    print("  ! 未找到 resume-zh_CN.tex 文件，请手动打开")
                
                print("\n" + "=" * 60)
                print("浏览器将保持打开状态，您可以：")
                print("  1. 在编辑器中修改 resume-zh_CN.tex 文件")
                print("  2. 查看实时编译的PDF预览")
                print("  3. 完成后关闭此窗口或按Ctrl+C退出")
                print("=" * 60)
                
                # 保持浏览器打开更长时间供用户编辑
                print("\n浏览器将保持打开180秒（3分钟）供您编辑...")
                print("提示：您可以在此期间编辑resume-zh_CN.tex文件")
                for i in range(180, 0, -30):
                    print(f"  剩余 {i} 秒...")
                    time.sleep(30)
                print("  时间到，准备关闭浏览器...")
                
            else:
                print(f"\n✗ 未找到项目: {PROJECT_TITLE}")
                print("浏览器将保持打开60秒供您手动查找项目...")
                time.sleep(60)
            
        except PlaywrightTimeout as e:
            print(f"\n✗ 超时错误: {e}")
            print("浏览器将保持打开30秒...")
            time.sleep(30)
            
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            print("浏览器将保持打开30秒...")
            time.sleep(30)
            
        finally:
            print("\n关闭浏览器...")
            browser.close()
            print("完成！")

if __name__ == "__main__":
    main()
