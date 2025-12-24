# Mouse Move MCP 项目总结

## 项目概述

Mouse Move MCP 是一个专注于鼠标操作的MCP服务器，与screenshot MCP和AI视觉能力配合，实现智能的鼠标定位和移动功能。

## 设计理念

### 职责分离
- **Screenshot MCP**: 负责屏幕截图和图像读取
- **AI助手**: 负责图像分析，识别鼠标位置和目标位置
- **Mouse Move MCP**: 负责鼠标位置获取和移动操作

### 工作流程
```
1. Screenshot MCP截取屏幕
   ↓
2. Screenshot MCP读取图片
   ↓
3. AI助手分析图片，识别位置
   ↓
4. Mouse Move MCP移动鼠标
   ↓
5. Mouse Move MCP验证位置
   ↓
6. 如未到达，重复步骤1-5
```

## 核心功能

### 1. 鼠标位置获取
- 实时获取当前鼠标在屏幕上的坐标
- 跨平台支持（Linux、macOS、Windows）

### 2. 鼠标移动
- 移动鼠标到指定的屏幕坐标
- 使用系统原生工具确保准确性

### 3. 距离计算
- 计算两个屏幕坐标点之间的欧几里得距离
- 用于验证鼠标是否到达目标位置

### 4. 智能移动验证
这是核心功能，自动执行：
1. 获取当前鼠标位置
2. 计算与目标位置的距离
3. 如果距离在容差范围内，返回成功
4. 否则移动鼠标到目标位置
5. 验证移动后的位置
6. 返回详细结果，指导是否需要继续调整

## 技术架构

### 文件结构
```
mouse_move_mcp/
├── __init__.py                 # 包初始化文件
├── mouse_move_tools.py         # 核心工具类实现
├── mouse_move_mcp_server.py    # MCP服务器主文件
├── requirements.txt            # Python依赖
├── README.md                   # 完整文档
├── QUICKSTART.md              # 快速开始指南
├── PROJECT_SUMMARY.md         # 项目总结（本文件）
└── test_mouse_move.py         # 测试脚本
```

### 核心类：MouseMoveTools

**主要方法**：
- `get_current_mouse_position()`: 获取鼠标位置
- `move_mouse_to_position(x, y)`: 移动鼠标
- `calculate_distance(x1, y1, x2, y2)`: 计算距离

### MCP工具接口

提供4个MCP工具：
1. `get_mouse_position` - 获取鼠标位置
2. `move_mouse` - 移动鼠标
3. `calculate_distance` - 计算距离
4. `move_to_target_with_verification` - 智能移动验证

## 跨平台支持

### Linux
- 鼠标控制: `xdotool`
- 鼠标位置: `xdotool getmouselocation`

### macOS
- 鼠标控制: `osascript` (AppleScript)
- 鼠标位置: Python库

### Windows
- 鼠标控制: PowerShell + Windows Forms
- 鼠标位置: PowerShell

## 与其他MCP的集成

### 必需的MCP工具
- **screenshot MCP**: 提供截屏和图像读取功能

### 推荐的工作流程
```python
# 1. 截屏
screenshot_result = mcp_screenshot.capture_screen()

# 2. 读取图片
image_data = mcp_screenshot.read_screenshot()

# 3. AI分析图片（由AI助手完成）
# AI识别：
# - 当前鼠标位置: (100, 100)
# - 目标"提交按钮"位置: (800, 600)

# 4. 移动鼠标
result = mcp_mouse_move.move_to_target_with_verification(
    target_x=800,
    target_y=600,
    tolerance=10
)

# 5. 检查结果
if result['status'] == '成功':
    print("鼠标已到达目标")
else:
    # 重复步骤1-4
    print("需要继续调整")
```

## 使用场景

### 1. 自动化UI测试
```python
# AI识别UI元素位置后，移动鼠标并点击
move_to_target_with_verification(target_x=button_x, target_y=button_y)
```

### 2. 机器人流程自动化（RPA）
```python
# 自动化办公流程中的鼠标操作
# 1. 截屏识别表单位置
# 2. 移动鼠标到输入框
# 3. 输入数据
# 4. 移动到提交按钮
# 5. 点击提交
```

### 3. 辅助功能
```python
# 帮助用户找到并点击屏幕上的特定元素
# AI理解用户的自然语言描述
# 自动定位并移动鼠标
```

## 配置示例

在MCP客户端配置文件中添加：

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
    }
  }
}
```

## 测试

运行测试脚本：
```bash
cd /home/zsss/zsss_useful_tools/aggr_force/mouse_move_mcp
python3 test_mouse_move.py
```

测试内容：
1. 获取鼠标位置功能
2. 移动鼠标功能
3. 距离计算功能
4. 智能移动验证功能

## 特点和优势

### 1. 职责清晰
- 专注于鼠标操作
- 不重复实现截屏功能
- 充分利用AI的视觉能力

### 2. 智能验证
- 自动验证鼠标是否到达目标
- 提供详细的反馈信息
- 支持循环调整

### 3. 跨平台
- 支持Linux、macOS、Windows
- 自动检测操作系统并使用相应工具

### 4. 灵活配置
- 可调整容差范围
- 支持精确定位
- 提供详细的位置信息

### 5. 易于集成
- 标准MCP协议
- 与其他MCP工具无缝配合
- 简单的API接口

## 关键改进点

### 相比初始设计的改进

**初始设计**：
- 包含截屏功能（重复）
- 包含图像读取功能（重复）
- 尝试在MCP内部分析图像（不合理）

**改进后设计**：
- 移除截屏功能，使用已有的screenshot MCP
- 移除图像读取功能，使用screenshot MCP
- 图像分析由AI助手完成（AI有视觉能力）
- 专注于鼠标操作功能

### 设计优势

1. **避免重复**: 不重复实现已有功能
2. **职责单一**: 每个MCP专注于自己的领域
3. **充分利用AI**: AI助手负责图像分析
4. **易于维护**: 代码更简洁，职责更清晰
5. **更好的集成**: 多个MCP协同工作

## 未来改进方向

1. **鼠标操作扩展**
   - 添加点击功能（左键、右键、双击）
   - 添加拖拽功能
   - 添加滚轮操作

2. **轨迹优化**
   - 平滑的鼠标移动轨迹
   - 模拟人类移动速度
   - 避免直线移动

3. **性能优化**
   - 减少系统调用
   - 优化位置获取
   - 缓存机制

4. **错误处理**
   - 更详细的错误信息
   - 自动恢复机制
   - 完善的日志记录

5. **高级功能**
   - 记录鼠标轨迹
   - 回放鼠标操作
   - 宏录制和播放

## 依赖关系

### 内部依赖
- `get_mouse_position_mcp`: 鼠标位置获取功能

### 外部依赖
- `screenshot_mcp`: 屏幕截图和图像读取功能
- AI助手: 图像分析和位置识别

### 系统依赖
- Linux: xdotool
- macOS: osascript
- Windows: PowerShell

## 版本信息

- **版本**: 1.0.0
- **创建日期**: 2024-12-24
- **Python版本**: 3.8+
- **MCP协议**: 支持

## 许可证

MIT License

## 总结

Mouse Move MCP 是一个设计精良的鼠标操作工具，通过与screenshot MCP和AI助手的配合，实现了智能的鼠标定位和移动功能。它的设计遵循了单一职责原则，避免了功能重复，充分利用了各个组件的优势，是一个优秀的MCP工具实现案例。
