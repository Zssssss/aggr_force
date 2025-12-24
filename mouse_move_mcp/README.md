# Mouse Move MCP

一个集成了鼠标位置获取、移动和智能验证功能的MCP（Model Context Protocol）服务器。

## 功能特性

- **鼠标位置获取**: 获取当前鼠标在屏幕上的坐标位置
- **鼠标移动**: 移动鼠标到指定的屏幕坐标
- **距离计算**: 计算两个屏幕坐标点之间的距离
- **智能移动验证**: 自动移动鼠标到目标位置并验证，支持循环调整

## 设计理念

本MCP服务器专注于鼠标操作功能，与其他MCP工具配合使用：

1. **截屏功能**: 使用已有的 `screenshot` MCP工具
2. **图像分析**: 由调用此MCP的AI助手完成（AI具有视觉能力）
3. **鼠标操作**: 本MCP提供鼠标位置获取和移动功能

## 系统要求

### Linux
- Python 3.8+
- `xdotool` (鼠标控制工具)

安装依赖：
```bash
sudo apt-get install xdotool python3-tk python3-dev
```

### macOS
- Python 3.8+
- 系统自带的 `osascript`

### Windows
- Python 3.8+
- PowerShell（系统自带）

## 安装

1. 克隆或下载此项目到本地

2. 安装Python依赖：
```bash
cd mouse_move_mcp
pip install -r requirements.txt
```

3. 确保服务器文件有执行权限（Linux/macOS）：
```bash
chmod +x mouse_move_mcp_server.py
```

## 配置

在你的MCP客户端配置文件中添加此服务器：

```json
{
  "mcpServers": {
    "mouse-move": {
      "command": "python3",
      "args": [
        "/path/to/mouse_move_mcp/mouse_move_mcp_server.py"
      ]
    }
  }
}
```

## 可用工具

### 1. get_mouse_position
获取当前鼠标在屏幕上的位置坐标。

**参数**: 无

**返回**:
```json
{
  "success": true,
  "x": 1024,
  "y": 768,
  "message": "当前鼠标位置: (1024, 768)"
}
```

### 2. move_mouse
移动鼠标到屏幕上的指定位置。

**参数**:
- `x` (必需): 目标X坐标（像素）
- `y` (必需): 目标Y坐标（像素）

**返回**:
```json
{
  "success": true,
  "x": 500,
  "y": 300,
  "message": "鼠标已移动到位置 (500, 300)"
}
```

### 3. calculate_distance
计算两个屏幕坐标点之间的欧几里得距离。

**参数**:
- `x1` (必需): 第一个点的X坐标
- `y1` (必需): 第一个点的Y坐标
- `x2` (必需): 第二个点的X坐标
- `y2` (必需): 第二个点的Y坐标

**返回**:
```json
{
  "success": true,
  "distance": 447.21,
  "point1": {"x": 100, "y": 100},
  "point2": {"x": 500, "y": 300},
  "message": "两点之间的距离: 447.21px"
}
```

### 4. move_to_target_with_verification
智能移动鼠标到目标位置并验证。这是一个高级工具，会自动执行移动和验证流程。

**参数**:
- `target_x` (必需): 目标X坐标（像素）
- `target_y` (必需): 目标Y坐标（像素）
- `tolerance` (可选): 允许的误差范围（像素），默认为10

**返回**:
```json
{
  "status": "成功",
  "original_position": {"x": 100, "y": 100},
  "target_position": {"x": 500, "y": 300},
  "current_position": {"x": 498, "y": 302},
  "original_distance": 447.21,
  "current_distance": 2.83,
  "tolerance": 10,
  "message": "鼠标已到达目标位置"
}
```

## 完整使用流程

### 场景：移动鼠标到屏幕上的特定文本位置

**步骤1: 截取屏幕**
```python
# 调用screenshot MCP工具
mcp_screenshot.capture_screen()
```

**步骤2: 读取截屏图片**
```python
# 调用screenshot MCP工具读取图片
screenshot_data = mcp_screenshot.read_screenshot()
```

**步骤3: AI分析图片**
AI助手查看图片，识别：
- 当前鼠标位置（通常有光标标记）
- 目标文本的位置（例如"提交按钮"）

**步骤4: 移动鼠标到目标位置**
```python
# 调用本MCP工具
result = mouse_move.move_to_target_with_verification(
    target_x=800,
    target_y=600,
    tolerance=10
)
```

**步骤5: 验证和循环**
- 如果返回"成功"，鼠标已到达目标
- 如果返回"需要继续调整"，重复步骤1-4

## 使用示例

### 示例1: 基本鼠标操作
```python
# 1. 获取当前鼠标位置
current_pos = get_mouse_position()
print(f"当前位置: ({current_pos['x']}, {current_pos['y']})")

# 2. 移动鼠标到新位置
move_mouse(x=500, y=300)

# 3. 验证移动
new_pos = get_mouse_position()
print(f"新位置: ({new_pos['x']}, {new_pos['y']})")
```

### 示例2: 智能移动到目标
```python
# 直接移动到目标位置并验证
result = move_to_target_with_verification(
    target_x=800,
    target_y=600,
    tolerance=10
)

if result['status'] == '成功':
    print("鼠标已到达目标位置")
else:
    print("需要继续调整，建议重新截屏")
```

### 示例3: 配合AI视觉分析
```
AI助手工作流程：

1. 用户: "移动鼠标到'提交'按钮"

2. AI调用: mcp_screenshot.capture_screen()
   结果: 截屏保存到 ~/screenshot_mcp/screenshot_xxx.png

3. AI调用: mcp_screenshot.read_screenshot()
   结果: 获取图片的base64数据

4. AI分析图片:
   - 识别当前鼠标位置: (100, 100)
   - 识别"提交"按钮位置: (800, 600)

5. AI调用: mouse_move.move_to_target_with_verification(
              target_x=800, 
              target_y=600, 
              tolerance=10
           )
   结果: 鼠标移动到目标位置

6. 如果未到达，AI重复步骤2-5
```

## 工作原理

### move_to_target_with_verification 工具流程

1. **获取当前位置**: 调用 `get_mouse_position` 获取鼠标当前坐标
2. **计算距离**: 使用 `calculate_distance` 计算当前位置与目标位置的距离
3. **检查是否到达**: 如果距离小于容差值，返回成功
4. **移动鼠标**: 如果未到达，使用 `move_mouse` 移动到目标位置
5. **验证位置**: 再次获取鼠标位置，计算新距离
6. **返回结果**: 告知是否成功，以及是否需要继续调整

## 与其他MCP工具的集成

### 必需的MCP工具
- **screenshot MCP**: 用于截取屏幕和读取图片

### 推荐的配置
```json
{
  "mcpServers": {
    "screenshot": {
      "command": "python3",
      "args": ["/path/to/screenshot_mcp/screenshot_mcp_server.py"]
    },
    "mouse-move": {
      "command": "python3",
      "args": ["/path/to/mouse_move_mcp/mouse_move_mcp_server.py"]
    }
  }
}
```

## 故障排除

### Linux系统
如果遇到 "未找到xdotool命令" 错误：
```bash
sudo apt-get install xdotool
```

### macOS系统
如果遇到权限问题，需要在"系统偏好设置" → "安全性与隐私" → "辅助功能"中授予终端或Python权限。

### Windows系统
确保PowerShell可以正常运行，某些企业环境可能限制了PowerShell脚本执行。

### 鼠标移动不准确
- 增加 `tolerance` 参数值（默认10像素）
- 多次调用 `move_to_target_with_verification` 进行微调
- 确保屏幕分辨率和坐标系统正确

## 技术细节

### 跨平台实现
- **Linux**: 使用 `xdotool` 命令行工具
- **macOS**: 使用 `osascript` 执行AppleScript
- **Windows**: 使用 PowerShell 和 .NET Windows.Forms

### 坐标系统
- 原点 (0, 0) 在屏幕左上角
- X轴向右增加
- Y轴向下增加

## 依赖项目

- `get_mouse_position_mcp`: 鼠标位置获取功能
- `screenshot_mcp`: 屏幕截图功能（外部依赖）

## 许可证

MIT License

## 版本

1.0.0
