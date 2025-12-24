# Mouse Move MCP 快速开始指南

## 快速安装

### 1. 安装系统依赖

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install xdotool python3-tk python3-dev
```

**macOS**:
```bash
# macOS系统自带所需工具，无需额外安装
# 但需要授予终端辅助功能权限
```

**Windows**:
```bash
# Windows系统自带PowerShell，无需额外安装
```

### 2. 安装Python依赖

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/mouse_move_mcp
pip install -r requirements.txt
```

### 3. 配置MCP客户端

在你的MCP客户端配置文件中添加：

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

## 快速测试

### 测试1: 获取鼠标位置
```python
# 调用 get_mouse_position 工具
# 将返回当前鼠标的X和Y坐标
```

### 测试2: 移动鼠标
```python
# 调用 move_mouse 工具
# 参数: x=500, y=300
# 将鼠标移动到屏幕坐标(500, 300)
```

### 测试3: 计算距离
```python
# 调用 calculate_distance 工具
# 参数: x1=100, y1=100, x2=500, y2=300
# 计算两点之间的距离
```

### 测试4: 智能移动并验证
```python
# 调用 move_to_target_with_verification 工具
# 参数: target_x=800, target_y=600, tolerance=10
# 将自动移动鼠标到目标位置并验证
```

## 完整使用流程示例

### 场景：移动鼠标到屏幕上的"提交"按钮

**步骤1: 截取屏幕**
```
调用: mcp-screenshot.capture_screen()
```

**步骤2: 读取图片**
```
调用: mcp-screenshot.read_screenshot()
获得: 图片的base64数据
```

**步骤3: AI分析图片**
```
AI查看图片，识别：
- 当前鼠标位置: (100, 100)
- "提交"按钮位置: (800, 600)
```

**步骤4: 移动鼠标**
```
调用: mouse-move.move_to_target_with_verification(
  target_x=800,
  target_y=600,
  tolerance=10
)
```

**步骤5: 检查结果**
```
如果返回"成功" -> 完成
如果返回"需要继续调整" -> 重复步骤1-4
```

## 常见使用场景

### 场景1: 简单移动鼠标
```python
# 1. 获取当前位置
current = get_mouse_position()

# 2. 移动到新位置
move_mouse(x=500, y=300)

# 3. 验证
new_pos = get_mouse_position()
```

### 场景2: 精确移动到目标
```python
# 一次调用完成移动和验证
move_to_target_with_verification(
    target_x=800,
    target_y=600,
    tolerance=5  # 5像素容差
)
```

### 场景3: 配合截屏的完整流程
```
1. 截屏 -> 2. AI分析 -> 3. 移动鼠标 -> 4. 验证
如果未到达目标，重复上述流程
```

## 工具说明

### 1. get_mouse_position
- **功能**: 获取当前鼠标位置
- **参数**: 无
- **返回**: {x, y, success, message}

### 2. move_mouse
- **功能**: 移动鼠标到指定位置
- **参数**: x, y
- **返回**: {success, x, y, message}

### 3. calculate_distance
- **功能**: 计算两点距离
- **参数**: x1, y1, x2, y2
- **返回**: {distance, point1, point2, success}

### 4. move_to_target_with_verification
- **功能**: 智能移动并验证
- **参数**: target_x, target_y, tolerance(可选)
- **返回**: 详细的移动和验证结果

## 故障排除

### 问题1: "未找到xdotool命令" (Linux)
```bash
sudo apt-get install xdotool
```

### 问题2: macOS权限问题
1. 打开"系统偏好设置"
2. 进入"安全性与隐私"
3. 选择"辅助功能"标签
4. 添加终端或Python到允许列表

### 问题3: 鼠标移动不准确
- 增加 `tolerance` 参数值
- 多次调用验证工具进行微调
- 确保屏幕分辨率设置正确

### 问题4: 无法获取鼠标位置
- 检查是否安装了必要的系统工具
- 检查是否有足够的系统权限
- 查看错误日志获取详细信息

## 与AI助手配合使用

AI助手可以：
1. 调用screenshot MCP截取屏幕
2. 查看和分析截屏图片
3. 识别鼠标当前位置和目标位置
4. 调用本MCP移动鼠标
5. 循环上述步骤直到到达目标

这种设计充分利用了AI的视觉能力和MCP的操作能力。

## 下一步

- 查看完整文档：[README.md](README.md)
- 查看项目总结：[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- 运行测试：`python3 test_mouse_move.py`
