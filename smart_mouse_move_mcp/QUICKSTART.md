# 快速开始指南

## 安装步骤

### 1. 安装Python依赖

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/smart_mouse_move_mcp
pip install -r requirements.txt
```

### 2. 安装系统依赖

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install xdotool imagemagick
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install xdotool ImageMagick
```

**macOS:**
无需额外安装，系统自带所需工具。

**Windows:**
无需额外安装，系统自带PowerShell。

### 3. 配置MCP服务器

将以下配置添加到MCP设置文件中：

**配置文件路径：**
```
/home/zsss/.vscode-server/data/User/globalStorage/weiboplat.wecoder/settings/mcp_settings.json
```

**添加的配置：**
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

**注意：** 如果配置文件中已经有其他MCP服务器，请将 `"smart-mouse-move"` 部分添加到现有的 `"mcpServers"` 对象中。

### 4. 运行测试

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/smart_mouse_move_mcp
python3 test_smart_mouse_move.py
```

### 5. 重启WeCoder

配置完成后，需要重启WeCoder以加载新的MCP服务器。

## 使用示例

配置完成后，您可以通过AI助手使用以下命令：

### 示例1：移动鼠标到搜索框

```
请将鼠标移动到屏幕上的搜索框
```

AI助手会：
1. 调用 `smart_move_to_target(target_description="搜索框")`
2. 分析返回的截图
3. 识别搜索框的坐标
4. 调用 `execute_move_to_coordinates(target_x=X, target_y=Y)`
5. 验证是否到达目标

### 示例2：移动鼠标到关闭按钮

```
请将鼠标移动到窗口右上角的关闭按钮
```

### 示例3：移动鼠标到特定文本

```
请将鼠标移动到屏幕上显示"提交"的按钮
```

## 工作流程

```
用户请求
    ↓
AI调用: smart_move_to_target("目标描述")
    ↓
返回截图
    ↓
AI分析截图，识别目标坐标
    ↓
AI调用: execute_move_to_coordinates(x, y)
    ↓
移动鼠标并验证
    ↓
如果未到达，调用: verify_position_with_screenshot(x, y)
    ↓
返回新截图，重复上述流程
```

## 可用工具

### 1. smart_move_to_target
开始智能移动工作流，截取屏幕并返回图片供AI分析。

### 2. execute_move_to_coordinates
执行移动鼠标到指定坐标。

### 3. verify_position_with_screenshot
验证当前位置并返回新截图。

## 故障排除

### 问题1：截图失败
- 检查是否安装了ImageMagick（Linux）
- 检查截图目录权限：`~/screenshot_mcp`

### 问题2：鼠标移动失败
- 检查是否安装了xdotool（Linux）
- 确保有足够的系统权限

### 问题3：服务器无法启动
- 检查Python依赖是否安装：`pip list | grep mcp`
- 检查服务器文件权限：`ls -l smart_mouse_move_mcp_server.py`

## 更多信息

详细文档请参阅 [README.md](README.md)
