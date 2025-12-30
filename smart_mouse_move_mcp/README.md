# 智能鼠标移动 MCP 服务器

这是一个封装了完整鼠标移动工作流程的 MCP 服务器，可以智能地将鼠标移动到屏幕上的目标位置。

## 功能特性

### 完整工作流程（只需一次截图）

1. **截取屏幕** - 自动截取当前屏幕（仅一次）
2. **AI分析** - 返回截图供AI助手分析，识别目标位置
3. **移动鼠标** - 根据AI识别的坐标移动鼠标
4. **验证位置** - 通过获取鼠标位置并计算距离来验证（无需再次截图）

### 提供的工具

#### 1. `smart_move_to_target`
开始智能移动工作流的第一步。

**参数：**
- `target_description` (必需): 目标位置的描述，例如"屏幕右上角的关闭按钮"
- `max_attempts` (可选): 最大尝试次数，默认5次
- `tolerance` (可选): 位置容差（像素），默认10

**返回：**
- 当前屏幕截图（base64编码）
- 当前鼠标位置
- 下一步操作指引

#### 2. `execute_move_to_coordinates`
执行移动鼠标到指定坐标并通过鼠标位置验证。

**参数：**
- `target_x` (必需): 目标X坐标
- `target_y` (必需): 目标Y坐标
- `tolerance` (可选): 位置容差（像素），默认10
- `verify` (可选): 是否验证移动结果，默认true

**返回：**
- 移动前后的位置信息
- 与目标的距离
- 是否成功到达

**验证方式：** 通过获取鼠标当前位置并与目标位置计算欧几里得距离来验证，无需额外截图。

## 安装

### 1. 安装依赖

```bash
cd smart_mouse_move_mcp
pip install -r requirements.txt
```

### 2. 系统依赖

根据您的操作系统，需要安装以下工具：

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install xdotool imagemagick

# Fedora/RHEL
sudo dnf install xdotool ImageMagick
```

**macOS:**
- 系统自带所需工具，无需额外安装

**Windows:**
- 系统自带PowerShell，无需额外安装

### 3. 配置 MCP 服务器

将以下配置添加到 MCP 设置文件中：

**文件位置：** `~/.vscode-server/data/User/globalStorage/weiboplat.wecoder/settings/mcp_settings.json`

```json
{
  "mcpServers": {
    "smart-mouse-move": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/smart_mouse_move_mcp/smart_mouse_move_mcp_server.py"
      ],
      "disabled": false,
      "alwaysAllow": [],
      "disabledTools": []
    }
  }
}
```

## 使用示例

### 基本使用流程

1. **启动工作流（截图一次）**

AI助手调用：
```
smart_move_to_target(target_description="搜索框")
```

2. **AI分析截图**

服务器返回截图后，AI助手分析图片，识别目标位置坐标。

3. **执行移动并验证**

AI助手调用：
```
execute_move_to_coordinates(target_x=500, target_y=300)
```

此步骤会自动通过鼠标位置计算验证是否到达目标，无需再次截图。

### 完整示例

**用户请求：** "请将鼠标移动到屏幕右上角的关闭按钮"

**AI助手执行：**

```python
# 步骤1: 开始工作流（唯一的截图）
result1 = smart_move_to_target(
    target_description="屏幕右上角的关闭按钮"
)
# 返回截图和当前鼠标位置

# 步骤2: AI分析截图，识别关闭按钮位置为 (1900, 50)

# 步骤3: 执行移动并自动验证（通过鼠标位置计算）
result2 = execute_move_to_coordinates(
    target_x=1900,
    target_y=50
)
# 返回移动结果，包含验证信息（距离目标的像素距离）
# 验证通过获取鼠标位置并计算距离完成，无需再次截图
```

## 工作原理

### 架构设计

```
用户请求
    ↓
AI助手调用 smart_move_to_target
    ↓
服务器截取屏幕（唯一的截图）
    ↓
返回截图给AI助手
    ↓
AI助手分析图片，识别目标坐标
    ↓
AI助手调用 execute_move_to_coordinates
    ↓
服务器移动鼠标
    ↓
获取鼠标当前位置
    ↓
计算与目标位置的距离
    ↓
返回验证结果（无需截图）
```

### 关键特性

- **高效验证**: 整个流程只需一次截图，验证通过鼠标位置计算完成
- **跨平台支持**: 支持 Linux、macOS 和 Windows
- **智能验证**: 自动验证鼠标是否到达目标位置
- **容错机制**: 支持位置容差配置，适应不同精度需求
- **视觉反馈**: 返回截图供AI分析，提高准确性

## 技术细节

### 截图实现

- **Linux**: 使用 `import` 命令（ImageMagick）
- **WSL**: 调用 Windows PowerShell 截图脚本
- **macOS**: 使用 `screencapture` 命令
- **Windows**: 使用 PowerShell 脚本

### 鼠标控制

- **Linux**: 使用 `xdotool` 命令
- **macOS**: 使用 AppleScript
- **Windows**: 使用 PowerShell 和 System.Windows.Forms

### 位置验证

验证方式已优化为通过鼠标位置计算，无需额外截图：

1. 移动鼠标到目标位置
2. 获取鼠标当前位置
3. 使用欧几里得距离计算当前位置与目标位置的距离：

```python
distance = sqrt((x2 - x1)² + (y2 - y1)²)
```

4. 如果距离小于等于容差值，则认为到达目标

**优势：** 相比截图验证方式，此方法更快速、更高效，整个流程只需一次截图。

## 故障排除

### 常见问题

1. **截图失败**
   - 检查是否安装了必要的系统工具
   - Linux: 确保安装了 ImageMagick
   - 检查截图目录权限

2. **鼠标移动失败**
   - Linux: 确保安装了 xdotool
   - 检查是否有足够的系统权限

3. **位置验证不准确**
   - 调整 `tolerance` 参数
   - 检查屏幕分辨率和缩放设置

### 日志查看

服务器日志会输出到标准错误流，可以通过 MCP 客户端查看。

## 开发

### 项目结构

```
smart_mouse_move_mcp/
├── __init__.py                      # 包初始化
├── smart_mouse_move_mcp_server.py   # MCP 服务器主文件
├── smart_mouse_move_tools.py        # 核心工具实现
├── requirements.txt                 # Python 依赖
├── README.md                        # 本文档
└── test_smart_mouse_move.py         # 测试文件
```

### 运行测试

```bash
python3 test_smart_mouse_move.py
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.1.0 (2024-12-30)
- **重大优化**: 验证方式改为通过鼠标位置计算，整个流程只需一次截图
- 移除 `verify_position_with_screenshot` 工具（不再需要）
- `execute_move_to_coordinates` 现在通过获取鼠标位置并计算距离来验证
- 提高了执行效率，减少了截图开销

### v1.0.0 (2024-12-24)
- 初始版本
- 实现完整的智能鼠标移动工作流
- 支持 Linux、macOS 和 Windows
- 提供三个核心工具：smart_move_to_target、execute_move_to_coordinates、verify_position_with_screenshot
