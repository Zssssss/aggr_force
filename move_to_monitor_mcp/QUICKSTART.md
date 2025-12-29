# Move to Monitor MCP 快速开始指南

## 安装步骤

### 1. 安装Python依赖

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/move_to_monitor_mcp
pip install -r requirements.txt
```

### 2. 运行测试

在配置MCP服务器之前，建议先运行测试以确保工具正常工作：

```bash
python3 test_move_to_monitor.py
```

测试将验证：
- ✓ 能否检测到所有显示器
- ✓ 能否查找窗口
- ✓ 能否移动窗口（可选，需要至少2个显示器）

### 3. 配置MCP服务器

编辑MCP配置文件：

```bash
# 配置文件路径
~/.vscode-server/data/User/globalStorage/weiboplat.wecoder/settings/mcp_settings.json
```

添加以下配置：

```json
{
  "mcpServers": {
    "move-to-monitor": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/move_to_monitor_mcp/move_to_monitor_mcp_server.py"
      ],
      "disabled": false,
      "alwaysAllow": [],
      "disabledTools": []
    }
  }
}
```

### 4. 重启WeCoder

保存配置后，重启WeCoder以加载新的MCP服务器。

## 使用示例

### 示例1: 查看显示器信息

```
列出所有显示器
```

### 示例2: 查找窗口

```
查找标题包含"Chrome"的窗口
```

### 示例3: 移动窗口到外接显示器

```
将Chrome移动到第2个显示器
```

### 示例4: 移动并最大化窗口

```
将VSCode移动到第2个显示器并最大化
```

## 常见问题

### Q: 如何知道显示器编号？

A: 使用 `list_monitors` 工具查看所有显示器信息，显示器编号从1开始。

### Q: 窗口标题如何匹配？

A: 支持部分匹配，例如"Chrome"可以匹配"Google Chrome"。

### Q: 可以移动哪些窗口？

A: 可以移动大部分应用窗口，但系统窗口可能无法移动。

### Q: WSL环境下如何工作？

A: 工具通过PowerShell调用Windows API，在WSL中操作原生Windows窗口。

## 技术要求

- ✓ WSL环境（WSL1或WSL2）
- ✓ Python 3.7+
- ✓ 可以执行 `powershell.exe`
- ✓ 至少1个显示器（移动功能需要2个或以上）

## 下一步

查看 [README.md](README.md) 了解更多详细信息和高级用法。
