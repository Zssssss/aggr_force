# Screenshot MCP Server

一个提供截屏功能的MCP (Model Context Protocol) 服务器，支持跨平台全屏截图。

## 功能特性

- ✅ 跨平台支持：Windows、Linux、macOS
- ✅ WSL环境支持：在WSL中自动调用Windows截图功能
- ✅ 自动文件命名：基于时间戳生成文件名
- ✅ 灵活配置：支持自定义文件名和保存路径
- ✅ 详细信息：返回截图的尺寸、格式等详细信息
- ✅ Base64编码：可选返回图片的base64编码数据

## 安装依赖

```bash
# 安装Python依赖
pip install mcp pillow mss

# Linux系统可选安装scrot（如果不使用mss）
# sudo apt install scrot
```

## 使用方法

### 1. 作为MCP服务器运行

在你的MCP客户端配置文件中添加：

```json
{
  "mcpServers": {
    "screenshot": {
      "command": "python",
      "args": ["/home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp/screenshot_mcp_server.py"]
    }
  }
}
```

### 2. 直接测试截屏功能

```bash
# 测试截屏工具
cd /home/zsss/zsss_useful_tools/aggr_force
python screenshot_mcp/screenshot_tools.py
```

## MCP工具说明

### 1. take_screenshot

截取当前全屏并保存为PNG图片文件。

**参数：**
- `filename` (可选): 自定义截图文件名（不含路径），例如 'my_screenshot.png'
- `output_dir` (可选): 截图保存目录的绝对路径
- `return_base64` (可选): 是否返回图片的base64编码数据，默认为false

**示例：**
```json
{
  "name": "take_screenshot",
  "arguments": {
    "filename": "test_screenshot.png",
    "output_dir": "/home/zsss/screenshots"
  }
}
```

**返回信息：**
- 文件名和完整路径
- 图片尺寸（宽度、高度）
- 图片格式和颜色模式
- 截图方法（mss、powershell、scrot等）

### 2. get_screenshot_info

获取最近一次截图的详细信息。

**参数：** 无

**返回信息：**
- 文件信息（名称、路径、大小）
- 图片尺寸和格式
- 创建时间

## 技术实现

### 跨平台截图方案

1. **Windows原生环境**：使用 `mss` 库
2. **WSL环境**：调用Windows的PowerShell脚本
3. **Linux环境**：优先使用 `mss` 库，备选 `scrot` 命令
4. **macOS环境**：使用系统自带的 `screencapture` 命令

### 文件结构

```
screenshot_mcp/
├── __init__.py                 # 包初始化文件
├── screenshot_tools.py         # 截屏工具核心实现
├── screenshot_mcp_server.py    # MCP服务器主程序
└── README.md                   # 本文档
```

## 注意事项

### WSL环境

在WSL环境下使用时，会自动调用Windows的PowerShell脚本进行截图。确保：
- PowerShell可以正常执行
- 有访问Windows文件系统的权限

### Linux环境

如果使用 `mss` 库，需要确保：
- 已设置 `DISPLAY` 环境变量
- 有X服务器运行（图形界面环境）

如果使用 `scrot` 命令，需要先安装：
```bash
sudo apt install scrot
```

### macOS环境

使用系统自带的 `screencapture` 命令，无需额外安装。

## 错误处理

服务器会返回详细的错误信息，包括：
- 错误描述
- 当前操作系统
- 解决建议

## 示例输出

成功截图时的输出：
```
✅ 截图成功！

📁 文件信息:
  - 文件名: screenshot_20231223_103045.png
  - 完整路径: /home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp/screenshot_20231223_103045.png
  - 文件格式: PNG
  
📐 图片尺寸:
  - 宽度: 1920 像素
  - 高度: 1080 像素
  - 颜色模式: RGB
  
🔧 截图方法: mss
```

## 开发者信息

- 版本：1.0.0
- 基于：Model Context Protocol (MCP)
- 依赖：mcp, pillow, mss

## 许可证

本项目遵循MIT许可证。
