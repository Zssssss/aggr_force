# Overleaf交互式工作流 - 使用指南

## 问题说明

在WSL环境中，直接启动有界面的浏览器需要X Server支持。有以下几种解决方案：

## 方案1: 使用已有的Playwright脚本（推荐）

之前创建的[`overleaf_interactive.py`](overleaf_interactive.py)脚本已经可以保持浏览器打开。

### 修改脚本使其永久保持打开

编辑[`overleaf_interactive.py`](overleaf_interactive.py:265)，将`keep_alive()`方法改为无限循环：

```python
def keep_alive(self):
    """保持会话活跃"""
    print("\n" + "=" * 60)
    print("浏览器会话保持活跃状态")
    print("按Ctrl+C退出")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(3600)  # 每小时检查一次
            if self.page.is_closed():
                print("\n页面已关闭")
                break
    except KeyboardInterrupt:
        print("\n\n收到中断信号")
```

### 运行方式

```bash
cd overleaf_workflow
python3 overleaf_interactive.py &
```

浏览器将保持打开，您可以：
1. 在浏览器中手动操作
2. 通过Python API调用session对象的方法

## 方案2: 使用X Server（Windows + WSL）

### 安装VcXsrv（Windows端）

1. 下载安装VcXsrv: https://sourceforge.net/projects/vcxsrv/
2. 启动XLaunch，选择"Multiple windows"
3. 勾选"Disable access control"

### 配置WSL

```bash
# 在~/.bashrc中添加
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
export LIBGL_ALWAYS_INDIRECT=1

# 重新加载配置
source ~/.bashrc
```

### 测试X Server

```bash
# 安装测试工具
sudo apt-get install x11-apps

# 测试
xclock
```

### 运行browser-use MCP

```bash
# 现在可以使用MCP工具了
python3 -c "
from browser_use_mcp import *
# 创建会话
"
```

## 方案3: 使用xvfb（虚拟显示）

### 安装xvfb

```bash
sudo apt-get update
sudo apt-get install xvfb
```

### 使用xvfb运行

```bash
cd overleaf_workflow
xvfb-run python3 overleaf_interactive.py
```

注意：这种方式浏览器在虚拟显示中运行，您看不到界面，但可以通过截图查看。

## 方案4: 使用browser-use MCP的远程模式

### 创建远程浏览器服务

```python
# remote_browser_server.py
from playwright.sync_api import sync_playwright
import time

def start_remote_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized', '--remote-debugging-port=9222']
        )
        context = browser.new_context()
        page = context.new_page()
        
        print("浏览器已启动，调试端口: 9222")
        print("保持运行...")
        
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("关闭浏览器...")
            browser.close()

if __name__ == "__main__":
    start_remote_browser()
```

### 连接到远程浏览器

```python
# 在另一个脚本中连接
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    # 现在可以控制浏览器了
```

## 方案5: 直接在Windows上运行（最简单）

### 安装Python和Playwright（Windows端）

```powershell
# 在Windows PowerShell中
pip install playwright
playwright install chromium
```

### 运行脚本

```powershell
cd \\wsl$\Ubuntu\home\zsss\zsss_useful_tools\aggr_force\overleaf_workflow
python overleaf_interactive.py
```

## 推荐方案

根据您的需求，我推荐：

### 如果需要看到浏览器界面
- **方案2**: 安装VcXsrv（一次性设置，长期使用）
- **方案5**: 直接在Windows上运行（最简单）

### 如果不需要看到界面
- **方案3**: 使用xvfb（适合自动化）
- 使用headless模式

## 当前最佳实践

由于您在WSL环境中，建议：

1. **立即可用**: 修改[`overleaf_interactive.py`](overleaf_interactive.py)，使用后台运行
2. **长期方案**: 安装VcXsrv，配置X Server

## 交互式操作示例

一旦浏览器保持打开，您可以通过Python API进行操作：

```python
# 假设session对象已创建并保持活跃
session = OverleafSession()
session.start()
session.login()
session.open_project()
session.open_file("resume-zh_CN.tex")

# 获取内容
content = session.get_editor_content()
print(content)

# 查找替换
session.find_and_replace("旧文本", "新文本")

# 插入文本
session.insert_text("新的一行内容", line=10)

# 编译PDF
session.compile_pdf()

# 截图
session.screenshot("current_state.png")

# 保持打开
session.keep_alive()
```

## 下一步

请告诉我您希望使用哪种方案，我可以帮您：
1. 配置X Server
2. 修改脚本以支持后台运行
3. 创建Windows端的运行脚本
4. 设置远程浏览器连接
