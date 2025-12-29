# Window Split MCP - 配置指南

## MCP服务器配置

### 配置文件位置

MCP配置文件通常位于：
- `.wecode/mcp.json` (WeCoder)
- 或其他MCP客户端指定的配置文件

### 基本配置

在MCP配置文件中添加以下内容：

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

### 完整配置示例

如果你有多个MCP服务器，配置文件可能如下：

```json
{
  "mcpServers": {
    "screenshot": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp/screenshot_mcp_server.py"
      ]
    },
    "mouse-move": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/mouse_move_mcp/mouse_move_mcp_server.py"
      ]
    },
    "window-split": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ]
    }
  }
}
```

## 环境变量配置

### Linux环境

如果需要特定的环境变量，可以这样配置：

```json
{
  "mcpServers": {
    "window-split": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ],
      "env": {
        "DISPLAY": ":0",
        "PYTHONPATH": "/home/zsss/zsss_useful_tools/aggr_force"
      }
    }
  }
}
```

### WSL环境

在WSL中使用时，需要配置X服务器：

```json
{
  "mcpServers": {
    "window-split": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ],
      "env": {
        "DISPLAY": "localhost:0",
        "LIBGL_ALWAYS_INDIRECT": "1"
      }
    }
  }
}
```

## 系统依赖安装

### Ubuntu/Debian

```bash
# 安装所有必需的工具
sudo apt update
sudo apt install wmctrl xdotool x11-utils

# 验证安装
wmctrl -v
xdotool version
xdpyinfo | grep dimensions
```

### Fedora/RHEL

```bash
# 安装所有必需的工具
sudo dnf install wmctrl xdotool xorg-x11-utils

# 验证安装
wmctrl -v
xdotool version
xdpyinfo | grep dimensions
```

### Arch Linux

```bash
# 安装所有必需的工具
sudo pacman -S wmctrl xdotool xorg-xdpyinfo

# 验证安装
wmctrl -v
xdotool version
xdpyinfo | grep dimensions
```

## Python依赖安装

### 使用pip安装

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp
pip install -r requirements.txt
```

### 使用虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

如果使用虚拟环境，需要在MCP配置中指定Python路径：

```json
{
  "mcpServers": {
    "window-split": {
      "command": "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/venv/bin/python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ]
    }
  }
}
```

## 权限配置

### 文件权限

确保服务器文件有执行权限：

```bash
chmod +x /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py
```

### X服务器权限

如果遇到X服务器权限问题：

```bash
# 允许本地连接
xhost +local:

# 或者允许特定用户
xhost +SI:localuser:$(whoami)
```

## 测试配置

### 测试1：验证Python环境

```bash
python3 -c "import sys; print(sys.version)"
```

### 测试2：验证MCP SDK

```bash
python3 -c "import mcp; print('MCP SDK已安装')"
```

### 测试3：验证工具模块

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp
python3 -c "from window_split_tools import WindowSplitTool; print('工具模块正常')"
```

### 测试4：运行完整测试

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp
python3 test_window_split.py
```

### 测试5：测试MCP服务器

```bash
# 启动服务器（会等待stdin输入）
python3 /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py
```

## 故障排除

### 问题1：找不到模块

**错误信息：**
```
ModuleNotFoundError: No module named 'mcp'
```

**解决方案：**
```bash
pip install mcp
```

### 问题2：找不到wmctrl

**错误信息：**
```
需要安装wmctrl: sudo apt install wmctrl
```

**解决方案：**
```bash
sudo apt install wmctrl
```

### 问题3：DISPLAY未设置

**错误信息：**
```
cannot open display
```

**解决方案：**
```bash
export DISPLAY=:0
```

### 问题4：权限被拒绝

**错误信息：**
```
Permission denied
```

**解决方案：**
```bash
chmod +x window_split_mcp_server.py
```

### 问题5：MCP服务器无法启动

**调试步骤：**

1. 检查Python路径：
```bash
which python3
```

2. 检查文件是否存在：
```bash
ls -l /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py
```

3. 手动运行服务器查看错误：
```bash
python3 /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py
```

4. 检查日志输出（如果MCP客户端提供）

## 高级配置

### 自定义工作目录

```json
{
  "mcpServers": {
    "window-split": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ],
      "cwd": "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp"
    }
  }
}
```

### 日志配置

如果需要调试，可以重定向输出：

```json
{
  "mcpServers": {
    "window-split": {
      "command": "bash",
      "args": [
        "-c",
        "python3 /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py 2>/tmp/window_split_mcp.log"
      ]
    }
  }
}
```

### 超时配置

某些MCP客户端支持超时配置：

```json
{
  "mcpServers": {
    "window-split": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ],
      "timeout": 30000
    }
  }
}
```

## 性能优化

### 1. 使用Python优化模式

```json
{
  "mcpServers": {
    "window-split": {
      "command": "python3",
      "args": [
        "-O",
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ]
    }
  }
}
```

### 2. 预加载模块

创建启动脚本 `start_server.sh`：

```bash
#!/bin/bash
export PYTHONPATH=/home/zsss/zsss_useful_tools/aggr_force
exec python3 /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py
```

然后在配置中使用：

```json
{
  "mcpServers": {
    "window-split": {
      "command": "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/start_server.sh"
    }
  }
}
```

## 安全建议

1. **限制访问权限**
   - 确保配置文件权限正确：`chmod 600 .wecode/mcp.json`
   - 限制服务器文件权限：`chmod 755 window_split_mcp_server.py`

2. **使用虚拟环境**
   - 隔离Python依赖
   - 避免系统级包冲突

3. **定期更新**
   - 更新MCP SDK：`pip install --upgrade mcp`
   - 更新系统工具：`sudo apt update && sudo apt upgrade`

## 验证配置

配置完成后，重启AI助手并尝试：

```
请列出所有打开的窗口
```

如果看到窗口列表，说明配置成功！

## 获取帮助

如果遇到问题：
1. 查看本配置指南
2. 运行测试脚本诊断
3. 查看 [README.md](README.md) 的故障排除部分
4. 提交Issue描述问题

---

**最后更新：** 2025-12-29
