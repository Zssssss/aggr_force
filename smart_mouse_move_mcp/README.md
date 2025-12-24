# 智能鼠标移动 MCP 服务器

这是一个封装了完整鼠标移动工作流程的 MCP 服务器，可以智能地将鼠标移动到屏幕上的目标位置。

## 功能特性

### 完整工作流程

1. **截取屏幕** - 自动截取当前屏幕
2. **AI分析** - 返回截图供AI助手分析，识别目标位置
3. **移动鼠标** - 根据AI识别的坐标移动鼠标
4. **验证位置** - 验证鼠标是否到达目标位置
5. **循环重试** - 如果未到达，重复上述步骤

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
执行移动鼠标到指定坐标。

**参数：**
- `target_x` (必需): 目标X坐标
- `target_y` (必需): 目标Y坐标
- `tolerance` (可选): 位置容差（像素），默认10
- `verify` (可选): 是否验证移动结果，默认true

**返回：**
- 移动前后的位置信息
- 与目标的距离
- 是否成功到达

#### 3. `verify_position_with_screenshot`
截图并验证当前位置。

**参数：**
- `expected_x` (必需): 期望的X坐标
- `expected_y` (必需): 期望的Y坐标
- `tolerance` (可选): 位置容差（像素），默认10

**返回：**
- 新的截图
- 当前位置与期望位置的对比
- 是否到达目标

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

1. **启动工作流**

AI助手调用：
```
smart_move_to_target(target_description="搜索框")
```

2. **AI分析截图**

服务器返回截图后，AI助手分析图片，识别目标位置坐标。

3. **执行移动**

AI助手调用：
```
execute_move_to_coordinates(target_x=500, target_y=300)
```

4. **验证结果**

如果需要验证，AI助手调用：
```
verify_position_with_screenshot(expected_x=500, expected_y=300)
```

5. **重试（如需要）**

如果未到达目标，重复步骤1-4。

### 完整示例

**用户请求：** "请将鼠标移动到屏幕右上角的关闭按钮"

**AI助手执行：**

```python
# 步骤1: 开始工作流
result1 = smart_move_to_target(
    target_description="屏幕右上角的关闭按钮"
)
# 返回截图和当前鼠标位置

# 步骤2: AI分析截图，识别关闭按钮位置为 (1900, 50)

# 步骤3: 执行移动
result2 = execute_move_to_coordinates(
    target_x=1900,
    target_y=50
)
# 返回移动结果

# 步骤4: 如果未到达，验证并重试
if not result2["success"]:
    result3 = verify_position_with_screenshot(
        expected_x=1900,
        expected_y=50
    )
    # 返回新截图，AI重新分析并调整坐标
```

## 工作原理

### 架构设计

```
用户请求
    ↓
AI助手调用 smart_move_to_target
    ↓
服务器截取屏幕
    ↓
返回截图给AI助手
    ↓
AI助手分析图片，识别目标坐标
    ↓
AI助手调用 execute_move_to_coordinates
    ↓
服务器移动鼠标并验证
    ↓
返回结果
    ↓
如果未到达，AI助手调用 verify_position_with_screenshot
    ↓
重复上述流程直到成功
```

### 关键特性

- **跨平台支持**: 支持 Linux、macOS 和 Windows
- **智能验证**: 自动验证鼠标是否到达目标位置
- **容错机制**: 支持位置容差配置，适应不同精度需求
- **循环重试**: 未到达目标时可以重新截图分析
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

使用欧几里得距离计算当前位置与目标位置的距离：

```python
distance = sqrt((x2 - x1)² + (y2 - y1)²)
```

如果距离小于等于容差值，则认为到达目标。

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

### v1.0.0 (2024-12-24)
- 初始版本
- 实现完整的智能鼠标移动工作流
- 支持 Linux、macOS 和 Windows
- 提供三个核心工具：smart_move_to_target、execute_move_to_coordinates、verify_position_with_screenshot
