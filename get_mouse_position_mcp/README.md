# Mouse Position MCP Server

一个用于获取鼠标屏幕坐标位置的 MCP (Model Context Protocol) 服务器。

## 功能特性

- 🖱️ **实时获取鼠标位置**: 获取当前鼠标在屏幕上的 X、Y 坐标
- 🌐 **跨平台支持**: 支持 Windows、Linux、macOS 和 WSL 环境
- 🔄 **多种实现方式**: 自动选择最佳的鼠标位置获取方法
- 📦 **简单易用**: 提供简洁的 MCP 工具接口

## 支持的平台

### Windows
- 使用 PyAutoGUI
- 使用 pynput
- 使用 win32api (pywin32)

### Linux
- 使用 PyAutoGUI
- 使用 pynput
- 使用 xdotool 命令行工具

### macOS
- 使用 PyAutoGUI
- 使用 pynput
- 使用 Quartz (PyObjC)

### WSL (Windows Subsystem for Linux)
- 自动检测 WSL 环境
- 通过 PowerShell 调用 Windows API 获取鼠标位置

## 安装

### 1. 安装依赖

```bash
# 基础依赖
pip install mcp

# 根据你的平台选择安装以下库之一:

# 推荐: PyAutoGUI (跨平台)
pip install pyautogui

# 或者: pynput (跨平台)
pip install pynput

# Windows 额外选项
pip install pywin32

# Linux 额外选项
sudo apt install xdotool

# macOS 额外选项
pip install pyobjc-framework-Quartz
```

### 2. 配置 MCP 客户端

在你的 MCP 客户端配置文件中添加:

```json
{
  "mcpServers": {
    "mouse-position": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py"
      ]
    }
  }
}
```

## 使用方法

### 作为 MCP 工具使用

服务器提供以下工具:

#### `get_mouse_position`

获取当前鼠标的屏幕坐标位置。

**参数**: 无

**返回示例**:
```
🖱️ 鼠标位置获取成功！

📍 当前坐标:
  - X坐标: 1024 像素
  - Y坐标: 768 像素
  
🔧 获取方法: pyautogui
💻 操作系统: Linux
```

### 作为 Python 模块使用

```python
from get_mouse_position_mcp.mouse_position_tools import get_mouse_position_simple

# 获取鼠标位置
result = get_mouse_position_simple()

if result.get("success"):
    print(f"X坐标: {result['x']}")
    print(f"Y坐标: {result['y']}")
    print(f"获取方法: {result['method']}")
    print(f"操作系统: {result['system']}")
else:
    print(f"获取失败: {result.get('error')}")
```

## 工作原理

### 平台检测

服务器会自动检测运行环境:

1. **WSL 检测**: 检查 `/proc/version` 文件判断是否在 WSL 环境
2. **操作系统检测**: 使用 `platform.system()` 识别操作系统类型

### 获取方法优先级

每个平台都有多个备选方法,按优先级尝试:

**WSL**:
1. PowerShell + Windows Forms API

**Linux**:
1. PyAutoGUI
2. xdotool
3. pynput

**Windows**:
1. PyAutoGUI
2. pynput
3. win32api

**macOS**:
1. PyAutoGUI
2. pynput
3. Quartz

## 故障排除

### WSL 环境

如果在 WSL 中遇到问题:
- 确保可以执行 `powershell.exe` 命令
- 确保 Windows 系统正常运行

### Linux 环境

如果遇到 "无法获取鼠标位置" 错误:
```bash
# 安装 xdotool
sudo apt install xdotool

# 或安装 Python 库
pip install pyautogui
pip install pynput
```

### Windows 环境

如果遇到导入错误:
```bash
pip install pyautogui
# 或
pip install pynput
# 或
pip install pywin32
```

### macOS 环境

如果遇到权限问题:
- 在"系统偏好设置" > "安全性与隐私" > "隐私"中授予辅助功能权限
- 安装所需库: `pip install pyautogui` 或 `pip install pynput`

## 项目结构

```
get_mouse_position_mcp/
├── mouse_position_mcp_server.py  # MCP 服务器主文件
├── mouse_position_tools.py       # 鼠标位置获取工具模块
├── __init__.py                   # Python 包初始化文件
├── requirements.txt              # 依赖列表
├── test_mouse_position.py        # 测试文件
└── README.md                     # 本文档
```

## 开发

### 运行测试

```bash
# 测试鼠标位置获取工具
python3 get_mouse_position_mcp/mouse_position_tools.py

# 运行完整测试
python3 get_mouse_position_mcp/test_mouse_position.py
```

### 启动 MCP 服务器

```bash
python3 get_mouse_position_mcp/mouse_position_mcp_server.py
```

## 技术细节

### MCP 协议

本服务器实现了 Model Context Protocol (MCP) 规范:
- 使用 stdio 传输层
- 提供标准的工具列表和调用接口
- 返回结构化的文本响应

### 依赖库

- `mcp`: MCP 协议实现
- `pyautogui` (可选): 跨平台鼠标控制库
- `pynput` (可选): 跨平台输入监控库
- `pywin32` (可选): Windows API 访问
- `pyobjc-framework-Quartz` (可选): macOS Quartz 框架

## 许可证

本项目遵循 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request!

## 更新日志

### v1.0.0 (2025-12-23)
- 初始版本
- 支持 Windows、Linux、macOS 和 WSL
- 提供 `get_mouse_position` 工具
- 多种鼠标位置获取方法支持
