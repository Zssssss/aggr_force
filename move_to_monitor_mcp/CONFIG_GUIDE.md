# Move to Monitor MCP 配置指南

## MCP服务器配置

### 配置文件位置

MCP配置文件位于：
```
/home/zsss/.vscode-server/data/User/globalStorage/weiboplat.wecoder/settings/mcp_settings.json
```

### 配置内容

在 `mcp_settings.json` 文件的 `mcpServers` 对象中添加以下配置：

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

### 完整配置示例

如果配置文件中已有其他MCP服务器，应该像这样添加：

```json
{
  "mcpServers": {
    "screenshot": {
      "command": "python3",
      "args": ["/home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp/screenshot_mcp_server.py"]
    },
    "open-dingtalk": {
      "command": "python3",
      "args": ["/home/zsss/zsss_useful_tools/aggr_force/open_dingtalk_mcp/open_dingtalk_mcp_server.py"]
    },
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

## 配置说明

### 必需字段

- **command**: Python3解释器命令
- **args**: MCP服务器脚本的完整路径

### 可选字段

- **disabled**: 是否禁用此服务器（默认为false）
- **alwaysAllow**: 不需要用户确认的工具列表（默认为空数组）
- **disabledTools**: 禁用的工具列表（默认为空数组）

## 配置步骤

### 1. 安装依赖

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/move_to_monitor_mcp
pip install -r requirements.txt
```

### 2. 测试工具

在配置MCP服务器之前，建议先测试工具是否正常工作：

```bash
python3 test_move_to_monitor.py
```

### 3. 编辑配置文件

使用文本编辑器打开配置文件：

```bash
nano /home/zsss/.vscode-server/data/User/globalStorage/weiboplat.wecoder/settings/mcp_settings.json
```

或使用VSCode打开：

```bash
code /home/zsss/.vscode-server/data/User/globalStorage/weiboplat.wecoder/settings/mcp_settings.json
```

### 4. 添加配置

将上述配置内容添加到 `mcpServers` 对象中。

### 5. 保存并重启

保存配置文件后，重启WeCoder以加载新的MCP服务器。

## 验证配置

配置成功后，你应该能够：

1. 在WeCoder中看到 `move-to-monitor` 服务器已连接
2. 使用以下工具：
   - `mcp_move-to-monitor_list_monitors` - 列出所有显示器
   - `mcp_move-to-monitor_find_window` - 查找窗口
   - `mcp_move-to-monitor_move_to_monitor` - 移动窗口到指定显示器

## 故障排除

### 问题1: 服务器无法启动

**检查项**：
- Python3是否已安装：`python3 --version`
- 依赖是否已安装：`pip list | grep mcp`
- 脚本路径是否正确
- 脚本是否有执行权限：`chmod +x move_to_monitor_mcp_server.py`

### 问题2: 工具无法使用

**检查项**：
- 是否在WSL环境中
- 是否可以执行PowerShell：`powershell.exe -Command "Write-Host 'test'"`
- 查看WeCoder输出面板中的错误日志

### 问题3: 找不到窗口

**检查项**：
- 窗口是否真的存在
- 窗口标题是否正确
- 窗口是否可见（未最小化）

## 高级配置

### 禁用特定工具

如果你不想使用某些工具，可以将它们添加到 `disabledTools` 列表：

```json
{
  "move-to-monitor": {
    "command": "python3",
    "args": [
      "/home/zsss/zsss_useful_tools/aggr_force/move_to_monitor_mcp/move_to_monitor_mcp_server.py"
    ],
    "disabledTools": ["find_window"]
  }
}
```

### 自动允许工具

如果你信任某些工具，可以将它们添加到 `alwaysAllow` 列表，这样使用时不需要确认：

```json
{
  "move-to-monitor": {
    "command": "python3",
    "args": [
      "/home/zsss/zsss_useful_tools/aggr_force/move_to_monitor_mcp/move_to_monitor_mcp_server.py"
    ],
    "alwaysAllow": ["list_monitors"]
  }
}
```

## 相关文档

- [README.md](README.md) - 完整功能说明
- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [test_move_to_monitor.py](test_move_to_monitor.py) - 测试脚本
