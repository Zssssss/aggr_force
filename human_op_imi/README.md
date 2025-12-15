# Human Operation Simulator MCP Module

人类操作模拟 MCP 模块，用于模拟人类对电脑的各种操作动作。

## 功能特性

- 鼠标操作模拟：点击、移动
- 键盘操作模拟：输入、按键
- 剪贴板操作模拟：复制、粘贴
- 窗口操作模拟：切换窗口
- 模拟状态管理：获取当前模拟环境状态

## 工具列表

### mouse_click
模拟鼠标点击操作

参数：
- x: 鼠标点击的 X 坐标
- y: 鼠标点击的 Y 坐标
- button: 点击的鼠标按钮 (left/right/middle)，默认 left
- double_click: 是否为双击，默认 False

### mouse_move
模拟鼠标移动操作

参数：
- x: 目标 X 坐标
- y: 目标 Y 坐标
- duration: 移动持续时间 (秒)，默认 0.5

### keyboard_type
模拟键盘输入操作

参数：
- text: 要输入的文本
- speed: 按键间隔时间 (秒)，默认 0.1

### keyboard_press
模拟键盘按键操作

参数：
- key: 要按下的键 (如: Enter, Ctrl, Alt, Shift)
- modifier: 修饰键 (如: Ctrl, Alt, Shift)

### clipboard_copy
模拟复制到剪贴板操作

参数：
- content: 要复制的内容

### clipboard_paste
模拟从剪贴板粘贴操作

无参数

### window_switch
模拟窗口切换操作

参数：
- window_title: 目标窗口标题

### get_simulation_state
获取当前模拟环境状态

无参数

### screenshot
模拟全局截图操作

无参数

## 运行方式

```bash
cd /home/zsss/zsss_useful_tools/aggr_force
python -m human_op_imi.human_op_server
```

## 使用示例

```python
import asyncio
from human_op_imi import create_server

async def main():
    server = create_server()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())