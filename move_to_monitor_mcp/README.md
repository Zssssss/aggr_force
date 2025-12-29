# Move to Monitor MCP

将Windows程序移动到指定显示器的MCP工具。支持在WSL环境中操作原生Windows窗口，实现多显示器场景下的窗口管理。

## 功能特性

- 🖥️ **多显示器支持**：列出所有连接的显示器信息
- 🔍 **窗口查找**：根据窗口标题查找目标窗口
- 📍 **窗口移动**：将窗口移动到指定显示器
- 🔲 **窗口最大化**：可选择移动后是否最大化窗口
- 🌉 **WSL兼容**：在WSL环境中操作原生Windows窗口

## 安装

### 1. 安装依赖

```bash
cd move_to_monitor_mcp
pip install -r requirements.txt
```

### 2. 配置MCP服务器

编辑MCP配置文件（通常位于 `~/.vscode-server/data/User/globalStorage/weiboplat.wecoder/settings/mcp_settings.json`），添加以下配置：

```json
{
  "mcpServers": {
    "move-to-monitor": {
      "command": "python3",
      "args": ["/home/zsss/zsss_useful_tools/aggr_force/move_to_monitor_mcp/move_to_monitor_mcp_server.py"]
    }
  }
}
```

### 3. 重启WeCoder

配置完成后，重启WeCoder以加载新的MCP服务器。

## 使用方法

### 工具1: list_monitors

列出所有显示器信息。

**参数**：无

**示例**：
```
请列出所有显示器
```

**返回示例**：
```json
{
  "success": true,
  "monitor_count": 2,
  "monitors": [
    {
      "MonitorNumber": 1,
      "IsPrimary": true,
      "Left": 0,
      "Top": 0,
      "Width": 1920,
      "Height": 1080,
      "Right": 1920,
      "Bottom": 1080
    },
    {
      "MonitorNumber": 2,
      "IsPrimary": false,
      "Left": 1920,
      "Top": 0,
      "Width": 1920,
      "Height": 1080,
      "Right": 3840,
      "Bottom": 1080
    }
  ]
}
```

### 工具2: find_window

根据窗口标题查找窗口。

**参数**：
- `title_pattern` (string): 窗口标题（支持部分匹配）

**示例**：
```
查找标题包含"Chrome"的窗口
```

**返回示例**：
```json
{
  "success": true,
  "window": {
    "Handle": 123456,
    "Title": "Google Chrome"
  }
}
```

### 工具3: move_to_monitor

将窗口移动到指定显示器。

**参数**：
- `title_pattern` (string): 窗口标题（支持部分匹配）
- `monitor_number` (integer): 目标显示器编号（从1开始）
- `maximize` (boolean, 可选): 是否最大化窗口（默认为false）

**示例**：
```
将Chrome窗口移动到第2个显示器并最大化
```

**返回示例**：
```json
{
  "success": true,
  "window_title": "Google Chrome",
  "monitor_number": 2,
  "monitor_info": {
    "MonitorNumber": 2,
    "IsPrimary": false,
    "Left": 1920,
    "Top": 0,
    "Width": 1920,
    "Height": 1080,
    "Right": 3840,
    "Bottom": 1080
  }
}
```

## 使用场景

### 场景1: 将浏览器移动到外接显示器

```
将Chrome移动到第2个显示器
```

### 场景2: 将编辑器移动到主显示器

```
将VSCode移动到第1个显示器并最大化
```

### 场景3: 查看显示器布局

```
列出所有显示器信息
```

## 技术实现

- **跨平台调用**：通过PowerShell在WSL中操作Windows窗口
- **Win32 API**：使用Windows API进行窗口管理
- **显示器检测**：使用System.Windows.Forms获取显示器信息
- **窗口操作**：使用SetWindowPos和ShowWindow API移动和调整窗口

## 注意事项

1. **WSL环境**：此工具设计用于WSL环境，通过PowerShell调用Windows API
2. **窗口标题**：窗口标题支持部分匹配，会返回第一个匹配的窗口
3. **显示器编号**：显示器编号从1开始，主显示器通常为1号
4. **权限要求**：需要有权限操作目标窗口

## 故障排除

### 问题1: 找不到窗口

**原因**：窗口标题不匹配或窗口不可见

**解决方案**：
- 使用`find_window`工具先查找窗口
- 确保窗口标题正确
- 检查窗口是否最小化到任务栏

### 问题2: 移动失败

**原因**：显示器编号无效或窗口无法移动

**解决方案**：
- 使用`list_monitors`确认显示器编号
- 确保目标窗口不是系统窗口
- 检查窗口是否被锁定

### 问题3: PowerShell执行失败

**原因**：WSL无法调用PowerShell

**解决方案**：
- 确保在WSL环境中可以执行`powershell.exe`
- 检查Windows路径是否正确配置

## 开发

### 运行测试

```bash
python3 test_move_to_monitor.py
```

### 日志

服务器日志会输出到标准错误流，可以在WeCoder的输出面板中查看。

## 版本历史

- **v0.1.0** (2025-12-29)
  - 初始版本
  - 支持列出显示器、查找窗口、移动窗口功能
  - WSL环境支持

## 许可证

MIT License

## 作者

WeCoder Team
