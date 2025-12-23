# Screenshot MCP Server 配置指南

## 在Claude Desktop中配置

编辑Claude Desktop的配置文件，添加screenshot MCP服务器：

### Windows系统
配置文件位置: `%APPDATA%\Claude\claude_desktop_config.json`

### Linux/macOS系统
配置文件位置: `~/.config/Claude/claude_desktop_config.json`

### 配置内容

```json
{
  "mcpServers": {
    "screenshot": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp/screenshot_mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

## 在其他MCP客户端中配置

如果你使用其他MCP客户端，可以参考以下配置：

```json
{
  "name": "screenshot",
  "type": "stdio",
  "command": "python3",
  "args": ["/home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp/screenshot_mcp_server.py"]
}
```

## 验证配置

配置完成后：

1. 重启Claude Desktop或你的MCP客户端
2. 在对话中询问："请帮我截取当前屏幕"
3. 系统应该会调用 `take_screenshot` 工具

## 使用示例

### 示例1: 基本截图
```
用户: 请帮我截取当前屏幕
助手: [调用 take_screenshot 工具]
```

### 示例2: 自定义文件名
```
用户: 请截图并保存为 meeting_notes.png
助手: [调用 take_screenshot 工具，参数 filename="meeting_notes.png"]
```

### 示例3: 指定保存路径
```
用户: 请截图并保存到 /home/zsss/screenshots 目录
助手: [调用 take_screenshot 工具，参数 output_dir="/home/zsss/screenshots"]
```

### 示例4: 获取截图信息
```
用户: 查看最近一次截图的信息
助手: [调用 get_screenshot_info 工具]
```

## 故障排除

### 问题1: 找不到mcp模块
```bash
pip install mcp
```

### 问题2: 找不到PIL模块
```bash
pip install pillow
```

### 问题3: 找不到mss模块
```bash
pip install mss
```

### 问题4: WSL环境下截图失败
确保PowerShell可以正常执行：
```bash
powershell.exe -Command "Get-Date"
```

### 问题5: Linux环境下截图失败
检查DISPLAY环境变量：
```bash
echo $DISPLAY
```

如果未设置，尝试：
```bash
export DISPLAY=:0
```

或安装scrot：
```bash
sudo apt install scrot
```

## 权限要求

- 读写文件系统权限
- 访问屏幕/显示器权限
- WSL环境下需要访问Windows系统权限

## 安全说明

- 截图文件默认保存在 `screenshot_mcp` 目录下
- 可以通过 `output_dir` 参数指定其他保存位置
- 建议定期清理旧的截图文件
- 截图可能包含敏感信息，请妥善保管

## 性能说明

- 截图时间取决于屏幕分辨率
- 典型1920x1080分辨率截图耗时约0.5-2秒
- Base64编码会增加额外的处理时间
- 建议不要频繁截图以避免性能问题
