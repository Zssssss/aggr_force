# 快速入门指南

## 快速测试

### 1. 测试鼠标位置获取功能

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp
python3 test_mouse_position.py
```

### 2. 直接运行工具模块

```bash
python3 mouse_position_tools.py
```

## 配置 MCP 客户端

### Claude Desktop 配置

编辑配置文件 `~/.config/Claude/claude_desktop_config.json`:

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

### Cline 配置

编辑 VSCode 设置中的 MCP 服务器配置:

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

## 使用示例

### 在 MCP 客户端中使用

配置完成后,在 MCP 客户端中可以使用以下工具:

**工具名称**: `get_mouse_position`

**功能**: 获取当前鼠标的屏幕坐标位置

**示例对话**:
```
用户: 获取当前鼠标位置
助手: [调用 get_mouse_position 工具]
      
      🖱️ 鼠标位置获取成功！
      
      📍 当前坐标:
        - X坐标: 803 像素
        - Y坐标: 333 像素
        
      🔧 获取方法: powershell_wsl
      💻 操作系统: WSL
```

### 作为 Python 模块使用

```python
from get_mouse_position_mcp import get_mouse_position_simple

# 获取鼠标位置
result = get_mouse_position_simple()

if result['success']:
    print(f"鼠标位置: ({result['x']}, {result['y']})")
else:
    print(f"错误: {result['error']}")
```

## 安装依赖

### 基础依赖 (必需)

```bash
pip install mcp
```

### 可选依赖 (根据平台选择)

**推荐 - PyAutoGUI (跨平台)**:
```bash
pip install pyautogui
```

**或者 - pynput (跨平台)**:
```bash
pip install pynput
```

**Linux 额外选项**:
```bash
sudo apt install xdotool
```

**Windows 额外选项**:
```bash
pip install pywin32
```

**macOS 额外选项**:
```bash
pip install pyobjc-framework-Quartz
```

## 验证安装

运行测试确认一切正常:

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/get_mouse_position_mcp
python3 test_mouse_position.py
```

预期输出:
```
🎉 所有测试通过!
```

## 故障排除

### WSL 环境问题

如果在 WSL 中遇到问题:
1. 确保可以执行 `powershell.exe` 命令
2. 测试: `powershell.exe -Command "Write-Output 'Hello'"`

### 权限问题

如果遇到权限错误:
```bash
chmod +x mouse_position_mcp_server.py
chmod +x test_mouse_position.py
```

### 依赖问题

如果提示缺少依赖:
```bash
pip install -r requirements.txt
pip install pyautogui  # 或其他可选依赖
```

## 项目结构

```
get_mouse_position_mcp/
├── __init__.py                    # Python 包初始化
├── mouse_position_mcp_server.py   # MCP 服务器主文件
├── mouse_position_tools.py        # 鼠标位置获取工具
├── test_mouse_position.py         # 测试文件
├── requirements.txt               # 依赖列表
├── README.md                      # 完整文档
└── QUICKSTART.md                  # 本文档
```

## 下一步

- 阅读 [README.md](README.md) 了解更多详细信息
- 查看 [mouse_position_tools.py](mouse_position_tools.py) 了解实现细节
- 运行 [test_mouse_position.py](test_mouse_position.py) 进行完整测试
