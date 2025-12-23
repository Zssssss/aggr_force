# 打开钉钉 MCP 工具 - 快速使用指南

## 快速开始

### 1. 测试工具

在 `open_dingtalk_mcp` 目录下运行测试：

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/open_dingtalk_mcp
python3 test_open_dingtalk.py
```

### 2. 配置 MCP 客户端

在你的 MCP 客户端配置文件中添加（例如 Claude Desktop 的 `claude_desktop_config.json`）：

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

### 3. 使用工具

配置完成后，在 MCP 客户端中可以使用以下命令：

#### 打开钉钉
```
请打开钉钉
```

#### 检查钉钉安装状态
```
检查钉钉是否已安装
```

## 测试结果

✅ **测试通过**

- ✅ 成功检测到钉钉已安装
- ✅ 成功在 WSL 环境中打开钉钉
- ✅ 使用方法: `powershell.exe -Command Start-Process dingtalk://`

## 支持的平台

- ✅ Windows
- ✅ WSL (Windows Subsystem for Linux)
- ✅ Linux
- ✅ macOS

## 工具列表

### 1. open_dingtalk
打开钉钉应用

**参数**: 无

**返回示例**:
```
✅ 成功在 WSL 环境中打开钉钉应用
平台: WSL
使用方法: powershell.exe -Command Start-Process dingtalk://
```

### 2. check_dingtalk_installed
检查钉钉是否已安装

**参数**: 无

**返回示例**:
```
✅ 检测到钉钉已安装
平台: WSL
安装路径:
  - C:\Program Files (x86)\DingDing\DingtalkLauncher.exe
```

## 文件结构

```
open_dingtalk_mcp/
├── __init__.py                      # 包初始化
├── open_dingtalk_mcp_server.py      # MCP 服务器主文件
├── open_dingtalk_tools.py           # 工具函数实现
├── requirements.txt                 # Python 依赖
├── README.md                        # 详细文档
├── QUICKSTART.md                    # 本快速指南
├── test_open_dingtalk.py           # 测试脚本
└── test_output.log                 # 测试输出日志
```

## 常见问题

### Q: 如何验证工具是否正常工作？
A: 运行测试脚本：
```bash
python3 test_open_dingtalk.py
```

### Q: 在 WSL 中无法打开钉钉？
A: 确保：
1. Windows 系统中已安装钉钉
2. 可以在 WSL 终端中运行 Windows 命令
3. 尝试手动运行：`powershell.exe -Command Start-Process dingtalk://`

### Q: 如何查看详细日志？
A: 查看测试输出日志：
```bash
cat test_output.log
```

## 技术细节

### WSL 环境下的实现
在 WSL 环境中，工具会尝试以下方法打开钉钉：

1. `powershell.exe -Command Start-Process dingtalk://` ✅ **推荐**
2. `cmd.exe /c start "" dingtalk://`
3. `explorer.exe dingtalk://`
4. 直接启动钉钉可执行文件

### 自动平台检测
工具会自动检测运行环境：
- 检查 `/proc/version` 文件判断是否在 WSL 中
- 使用 `platform.system()` 获取操作系统类型
- 根据环境选择合适的启动方法

## 更新日志

### v1.0.0 (2025-12-23)
- ✅ 初始版本发布
- ✅ 支持 Windows、WSL、Linux 和 macOS
- ✅ 提供打开钉钉和检查安装状态功能
- ✅ 完整的测试套件
- ✅ 在 WSL 环境下测试通过
