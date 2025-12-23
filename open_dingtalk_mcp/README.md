# 打开钉钉 MCP 工具

这是一个 Model Context Protocol (MCP) 工具，用于在不同操作系统上打开钉钉应用。

## 功能特性

- ✅ 支持 Windows 系统
- ✅ 支持 WSL (Windows Subsystem for Linux) 环境
- ✅ 支持 Linux 系统
- ✅ 支持 macOS 系统
- ✅ 自动检测运行环境
- ✅ 多种启动方式自动切换
- ✅ 检查钉钉安装状态

## 提供的工具

### 1. open_dingtalk
打开钉钉应用。

**参数**: 无

**返回**: 
- 操作是否成功
- 运行平台信息
- 使用的启动方法

**示例**:
```json
{
  "success": true,
  "message": "成功在 WSL 环境中打开钉钉应用",
  "platform": "WSL",
  "method": "cmd.exe /c start dingtalk://"
}
```

### 2. check_dingtalk_installed
检查钉钉应用是否已安装。

**参数**: 无

**返回**:
- 是否已安装
- 运行平台信息
- 可能的安装路径列表

**示例**:
```json
{
  "installed": true,
  "message": "检测到钉钉已安装",
  "paths": ["C:\\Program Files (x86)\\DingDing\\DingtalkLauncher.exe"],
  "platform": "WSL"
}
```

## 安装

### 1. 安装依赖

```bash
cd open_dingtalk_mcp
pip install -r requirements.txt
```

### 2. 配置 MCP 客户端

在你的 MCP 客户端配置文件中添加以下配置（例如 Claude Desktop 的配置文件）:

**对于 WSL/Linux 环境**:
```json
{
  "mcpServers": {
    "open-dingtalk": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/open_dingtalk_mcp/open_dingtalk_mcp_server.py"
      ]
    }
  }
}
```

**对于 Windows 环境**:
```json
{
  "mcpServers": {
    "open-dingtalk": {
      "command": "python",
      "args": [
        "C:\\path\\to\\open_dingtalk_mcp\\open_dingtalk_mcp_server.py"
      ]
    }
  }
}
```

## 使用方法

### 在 MCP 客户端中使用

启动配置了此 MCP 服务器的客户端后，你可以直接使用以下命令：

1. **打开钉钉**:
   ```
   请打开钉钉
   ```

2. **检查钉钉是否安装**:
   ```
   检查钉钉是否已安装
   ```

### 直接运行服务器（测试用）

```bash
cd open_dingtalk_mcp
python3 open_dingtalk_mcp_server.py
```

## 工作原理

### Windows 环境
- 使用 `start dingtalk://` 协议打开钉钉
- 或直接启动钉钉可执行文件

### WSL 环境
- 通过 `cmd.exe` 调用 Windows 命令
- 使用 `explorer.exe` 打开钉钉协议
- 或直接启动 Windows 下的钉钉可执行文件

### Linux 环境
- 使用 `xdg-open dingtalk://` 打开钉钉协议
- 或直接运行 `dingtalk` 命令（如果在 PATH 中）

### macOS 环境
- 使用 `open -a DingTalk` 命令打开钉钉应用

## 常见问题

### Q: 在 WSL 中无法打开钉钉？
A: 请确保：
1. Windows 系统中已安装钉钉
2. WSL 可以访问 Windows 文件系统（通常在 `/mnt/c/` 下）
3. 尝试在 WSL 终端中运行 `cmd.exe /c start dingtalk://` 测试

### Q: 提示"无法打开钉钉"？
A: 请检查：
1. 钉钉是否已正确安装
2. 钉钉安装路径是否在常见位置
3. 使用 `check_dingtalk_installed` 工具检查安装状态

### Q: 支持哪些钉钉版本？
A: 支持所有标准安装的钉钉版本，包括企业版和个人版。

## 技术栈

- Python 3.7+
- MCP (Model Context Protocol)
- subprocess (系统命令执行)
- platform (平台检测)

## 目录结构

```
open_dingtalk_mcp/
├── __init__.py                      # 包初始化文件
├── open_dingtalk_mcp_server.py      # MCP 服务器主文件
├── open_dingtalk_tools.py           # 工具函数实现
├── requirements.txt                 # Python 依赖
├── README.md                        # 本文档
└── test_open_dingtalk.py           # 测试文件
```

## 开发和测试

运行测试：
```bash
cd open_dingtalk_mcp
python3 test_open_dingtalk.py
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0 (2025-12-23)
- 初始版本
- 支持 Windows、WSL、Linux 和 macOS
- 提供打开钉钉和检查安装状态两个工具
