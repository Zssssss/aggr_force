# Window Split MCP - 快速入门指南

## 5分钟快速上手

### 重要提示：WSL环境配置

**当前环境：** WSL (Windows Subsystem for Linux)
**工作目录：** `/home/zsss/zsss_useful_tools/aggr_force`

在WSL中使用窗口管理功能需要：
1. 安装Windows端的X服务器（VcXsrv或X410）
2. 配置DISPLAY环境变量
3. 安装Linux端的窗口管理工具

### 第一步：配置WSL的X服务器

#### 1.1 安装VcXsrv（Windows端）

下载并安装：https://sourceforge.net/projects/vcxsrv/

启动配置：
- Display number: 0
- Start no client
- 勾选 "Disable access control"

#### 1.2 配置DISPLAY环境变量（WSL端）

```bash
# 临时设置
export DISPLAY=:0

# 永久设置（添加到~/.bashrc）
echo 'export DISPLAY=:0' >> ~/.bashrc
source ~/.bashrc
```

### 第二步：安装系统依赖（Linux）

```bash
# Ubuntu/Debian系统
sudo apt install wmctrl xdotool x11-utils

# 验证安装
wmctrl -v
xdotool version
xdpyinfo | grep dimensions
```

### 第二步：安装Python依赖

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp
pip install -r requirements.txt
```

### 第三步：测试工具

```bash
# 运行测试脚本
python3 test_window_split.py
```

测试脚本会：
1. ✅ 获取屏幕尺寸
2. ✅ 列出所有窗口
3. ✅ 获取活动窗口
4. ⚠️ 询问是否继续（会实际移动窗口）
5. 🔧 测试移动窗口
6. ↔️ 测试水平分屏
7. ↕️ 测试垂直分屏
8. ⊞ 测试网格分屏
9. ⛶ 测试最大化窗口

### 第四步：配置MCP服务器

编辑你的MCP配置文件（通常在 `.wecode/mcp.json`）：

```json
{
  "mcpServers": {
    "window-split": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ]
    }
  }
}
```

### 第五步：重启AI助手并使用

重启你的AI助手，然后就可以使用了！

## 常用命令示例

### 示例1：查看所有窗口

```
请列出所有打开的窗口
```

AI助手会调用 `list_windows` 工具，返回类似：

```
✅ 成功获取窗口列表

📊 统计信息:
  - 窗口总数: 5
  - 检测方法: wmctrl

📋 窗口列表:

1. Google Chrome
   ID: 0x03400006
   位置: (0, 0)
   大小: 1920 x 1080
   桌面: 0

2. Visual Studio Code
   ID: 0x03400007
   位置: (100, 100)
   大小: 1600 x 900
   桌面: 0
...
```

### 示例2：左右分屏

```
请将窗口ID为0x03400006和0x03400007的窗口进行左右分屏
```

或者更简单：

```
请将Chrome和VSCode窗口左右分屏
```

AI助手会：
1. 列出窗口找到对应ID
2. 调用 `split_horizontal` 工具
3. Chrome显示在左半屏，VSCode显示在右半屏

### 示例3：上下分屏

```
请将前两个窗口上下分屏
```

### 示例4：四分屏

```
请将前四个窗口排列成2x2网格
```

结果：
- 左上：窗口1
- 右上：窗口2
- 左下：窗口3
- 右下：窗口4

### 示例5：最大化当前窗口

```
请最大化当前活动窗口
```

## 工作流程示例

### 工作流1：开发环境设置

```
1. "请列出所有窗口"
2. "请将VSCode和Chrome左右分屏"
3. "请将终端窗口放在下方"
```

### 工作流2：监控仪表板

```
1. "请列出所有窗口"
2. "请将系统监控、日志查看器、终端和文档窗口排列成四分屏"
```

### 工作流3：快速整理

```
1. "请获取当前活动窗口"
2. "请最大化这个窗口"
```

## 编程接口使用

### Python直接调用

```python
from window_split_mcp import WindowSplitTool

# 创建工具实例
tool = WindowSplitTool()

# 获取屏幕尺寸
screen = tool.get_screen_size()
print(f"屏幕尺寸: {screen['width']} x {screen['height']}")

# 列出窗口
windows = tool.list_windows()
for win in windows['windows']:
    print(f"{win['title']}: {win['id']}")

# 水平分屏
if len(windows['windows']) >= 2:
    window_ids = [w['id'] for w in windows['windows'][:2]]
    result = tool.split_windows_horizontal(window_ids)
    print(f"分屏结果: {result['success']}")
```

### 便捷函数

```python
from window_split_mcp import (
    list_windows_simple,
    split_horizontal_simple,
    split_vertical_simple,
    split_grid_simple
)

# 列出窗口
windows = list_windows_simple()

# 水平分屏
if windows['success']:
    window_ids = [w['id'] for w in windows['windows'][:2]]
    split_horizontal_simple(window_ids)
```

## 常见问题

### Q1: 提示"需要安装wmctrl"

**A:** 运行安装命令：
```bash
sudo apt install wmctrl
```

### Q2: 提示"需要安装xdotool"

**A:** 运行安装命令：
```bash
sudo apt install xdotool
```

### Q3: 无法获取屏幕尺寸

**A:** 安装x11-utils：
```bash
sudo apt install x11-utils
```

### Q4: 在WSL中无法使用

**A:** WSL需要X服务器支持：
1. 安装VcXsrv或X410
2. 启动X服务器
3. 设置环境变量：
```bash
export DISPLAY=:0
```

### Q5: 窗口没有按预期移动

**A:** 某些窗口管理器可能有限制：
- 检查窗口是否被锁定
- 尝试先取消最大化
- 某些全屏应用可能无法移动

## 进阶技巧

### 技巧1：批量处理窗口

```python
tool = WindowSplitTool()
windows = tool.list_windows()

# 将所有Chrome窗口移到左侧
chrome_windows = [w for w in windows['windows'] 
                  if 'Chrome' in w['title']]
for i, win in enumerate(chrome_windows):
    tool.move_window(win['id'], 0, i*300, 960, 300)
```

### 技巧2：保存和恢复布局

```python
import json

# 保存当前布局
tool = WindowSplitTool()
windows = tool.list_windows()
with open('layout.json', 'w') as f:
    json.dump(windows, f)

# 恢复布局
with open('layout.json', 'r') as f:
    saved_layout = json.load(f)
    for win in saved_layout['windows']:
        tool.move_window(
            win['id'], 
            win['x'], win['y'], 
            win['width'], win['height']
        )
```

### 技巧3：自定义分屏比例

```python
tool = WindowSplitTool()
screen = tool.get_screen_size()
windows = tool.list_windows()

if len(windows['windows']) >= 2:
    # 左侧占70%，右侧占30%
    w1, w2 = windows['windows'][:2]
    
    left_width = int(screen['width'] * 0.7)
    right_width = screen['width'] - left_width
    
    tool.move_window(w1['id'], 0, 0, left_width, screen['height'])
    tool.move_window(w2['id'], left_width, 0, right_width, screen['height'])
```

## 下一步

- 📖 阅读完整的 [README.md](README.md)
- 🔧 查看 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 了解技术细节
- 🧪 运行 `test_window_split.py` 进行完整测试
- 💡 探索更多使用场景

## 获取帮助

如果遇到问题：
1. 查看 [README.md](README.md) 的故障排除部分
2. 运行测试脚本诊断问题
3. 提交Issue描述问题

祝使用愉快！🎉
