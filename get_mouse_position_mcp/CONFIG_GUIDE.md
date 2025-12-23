# MCP 配置指南

本文档提供了如何在不同 MCP 客户端中配置 Mouse Position MCP Server 的详细说明。

## 配置文件位置

### Claude Desktop

**Linux/WSL**:
```
~/.config/Claude/claude_desktop_config.json
```

**Windows**:
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS**:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Cline (VSCode 扩展)

在 VSCode 设置中搜索 "MCP" 或编辑 `settings.json`。

## 配置示例

### 1. Claude Desktop 配置

编辑 `claude_desktop_config.json`:

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

### 2. 多个 MCP 服务器配置

如果你已经有其他 MCP 服务器,添加到现有配置中:

```json
{
  "mcpServers": {
    "screenshot": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp/screenshot_mcp_server.py"
      ]
    },
    "mouse-position": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py"
      ]
    },
    "open-dingtalk": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/open_dingtalk_mcp/open_dingtalk_mcp_server.py"
      ]
    }
  }
}
```

### 3. Cline (VSCode) 配置

在 VSCode 的 `settings.json` 中添加:

```json
{
  "mcp.servers": {
    "mouse-position": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py"
      ]
    }
  }
}
```

### 4. 使用相对路径配置 (不推荐)

如果需要使用相对路径:

```json
{
  "mcpServers": {
    "mouse-position": {
      "command": "python3",
      "args": [
        "./get_mouse_position_mcp/mouse_position_mcp_server.py"
      ],
      "cwd": "/home/zsss/zsss_useful_tools/aggr_force"
    }
  }
}
```

### 5. Windows 路径配置

在 Windows 系统上:

```json
{
  "mcpServers": {
    "mouse-position": {
      "command": "python",
      "args": [
        "C:\\Users\\YourUsername\\path\\to\\get_mouse_position_mcp\\mouse_position_mcp_server.py"
      ]
    }
  }
}
```

### 6. 使用虚拟环境

如果使用 Python 虚拟环境:

```json
{
  "mcpServers": {
    "mouse-position": {
      "command": "/path/to/venv/bin/python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py"
      ]
    }
  }
}
```

## 配置步骤

### 步骤 1: 找到配置文件

根据你使用的客户端,找到对应的配置文件位置。

### 步骤 2: 编辑配置文件

使用文本编辑器打开配置文件:

```bash
# Linux/WSL - Claude Desktop
nano ~/.config/Claude/claude_desktop_config.json

# 或使用 VSCode
code ~/.config/Claude/claude_desktop_config.json
```

### 步骤 3: 添加配置

将上面的配置示例复制到文件中,注意:
- 使用正确的绝对路径
- 确保 JSON 格式正确
- 如果已有其他服务器,添加到 `mcpServers` 对象中

### 步骤 4: 保存并重启

保存配置文件后,重启 MCP 客户端使配置生效。

### 步骤 5: 验证配置

在客户端中测试:
```
请获取当前鼠标位置
```

预期响应:
```
🖱️ 鼠标位置获取成功！

📍 当前坐标:
  - X坐标: 803 像素
  - Y坐标: 333 像素
  
🔧 获取方法: powershell_wsl
💻 操作系统: WSL
```

## 故障排除

### 问题 1: 找不到 Python

**错误**: `command not found: python3`

**解决方案**:
```json
{
  "mcpServers": {
    "mouse-position": {
      "command": "/usr/bin/python3",  // 使用完整路径
      "args": [...]
    }
  }
}
```

查找 Python 路径:
```bash
which python3
```

### 问题 2: 找不到模块

**错误**: `ModuleNotFoundError: No module named 'mcp'`

**解决方案**:
```bash
pip install mcp
```

### 问题 3: 权限问题

**错误**: `Permission denied`

**解决方案**:
```bash
chmod +x /home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py
```

### 问题 4: 路径错误

**错误**: `No such file or directory`

**解决方案**:
- 检查路径是否正确
- 使用绝对路径而不是相对路径
- 确保文件存在:
```bash
ls -l /home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py
```

### 问题 5: JSON 格式错误

**错误**: `JSON parse error`

**解决方案**:
- 检查 JSON 格式是否正确
- 使用在线 JSON 验证器验证
- 注意逗号、引号、括号是否匹配

## 测试配置

### 手动测试服务器

在配置前,先手动测试服务器是否能正常运行:

```bash
python3 /home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py
```

服务器应该启动并等待输入。按 `Ctrl+C` 退出。

### 运行测试套件

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp
python3 test_mouse_position.py
```

应该看到:
```
🎉 所有测试通过!
```

## 配置模板

### 完整配置模板

```json
{
  "mcpServers": {
    "mouse-position": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/zsss/zsss_useful_tools/aggr_force"
      }
    }
  }
}
```

### 最小配置模板

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

## 环境变量

如果需要设置环境变量:

```json
{
  "mcpServers": {
    "mouse-position": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/zsss/zsss_useful_tools/aggr_force",
        "DISPLAY": ":0"
      }
    }
  }
}
```

## 日志和调试

### 启用详细日志

```json
{
  "mcpServers": {
    "mouse-position": {
      "command": "python3",
      "args": [
        "-u",  // 无缓冲输出
        "/home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp/mouse_position_mcp_server.py"
      ]
    }
  }
}
```

### 查看日志

不同客户端的日志位置:
- **Claude Desktop**: 查看应用程序日志
- **Cline**: 查看 VSCode 输出面板

## 更多信息

- 查看 [README.md](README.md) 了解功能详情
- 查看 [QUICKSTART.md](QUICKSTART.md) 快速开始
- 查看 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 项目总结
