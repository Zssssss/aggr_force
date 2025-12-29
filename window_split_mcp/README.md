# Window Split MCP - 窗口分屏管理工具

一个强大的MCP（Model Context Protocol）服务器，提供窗口分屏和管理功能。

## 功能特性

### 核心功能

- 📋 **列出所有窗口** - 获取所有打开窗口的详细信息
- 📐 **获取屏幕尺寸** - 获取当前屏幕的宽度和高度
- 🎯 **获取活动窗口** - 获取当前焦点窗口的信息
- 🔧 **移动和调整窗口** - 精确控制窗口的位置和大小

### 分屏布局

- ↔️ **水平分屏** - 左右分屏，支持1-2个窗口
- ↕️ **垂直分屏** - 上下分屏，支持1-2个窗口
- ⊞ **网格分屏** - 2x2网格布局，支持1-4个窗口
- ⛶ **最大化窗口** - 将窗口最大化到全屏

## 系统要求

### Linux系统（主要支持）

需要安装以下系统工具：

```bash
# Ubuntu/Debian
sudo apt install wmctrl xdotool x11-utils

# Fedora/RHEL
sudo dnf install wmctrl xdotool xorg-x11-utils

# Arch Linux
sudo pacman -S wmctrl xdotool xorg-xdpyinfo
```

### WSL环境（特别说明）⚠️

**当前项目位于WSL环境：** `/home/zsss/zsss_useful_tools/aggr_force`

在WSL中使用需要额外配置：
1. 安装Windows端X服务器（VcXsrv或X410）
2. 配置DISPLAY环境变量
3. 只能管理通过X服务器显示的Linux GUI应用
4. **无法管理Windows原生窗口**

详细配置请参考：[WSL_SETUP.md](WSL_SETUP.md)

### Windows系统

- 基础功能支持（屏幕尺寸获取）
- 窗口管理功能开发中

### macOS系统

- 基础功能支持（屏幕尺寸获取）
- 窗口管理功能开发中

## 安装

### 1. 安装Python依赖

```bash
cd window_split_mcp
pip install -r requirements.txt
```

### 2. 配置MCP服务器

在你的MCP配置文件中添加：

```json
{
  "mcpServers": {
    "window-split": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ],
      "env": {
        "DISPLAY": ":0"
      }
    }
  }
}
```

**注意：** 在WSL环境中，需要配置DISPLAY环境变量并安装X服务器（如VcXsrv或X410）才能使用窗口管理功能。

## 使用方法

### 通过MCP客户端使用

启动MCP服务器后，可以通过AI助手调用以下工具：

#### 1. 列出所有窗口

```
请列出所有打开的窗口
```

#### 2. 水平分屏（左右分屏）

```
请将窗口ID为0x03400006和0x03400007的窗口进行左右分屏
```

#### 3. 垂直分屏（上下分屏）

```
请将前两个窗口进行上下分屏
```

#### 4. 网格分屏（四分屏）

```
请将前四个窗口排列成2x2网格
```

#### 5. 最大化窗口

```
请最大化当前活动窗口
```

### 直接测试

运行测试脚本：

```bash
cd window_split_mcp
python3 test_window_split.py
```

## API文档

### 工具列表

#### `list_windows`

列出所有打开的窗口。

**参数：** 无

**返回：**
```json
{
  "success": true,
  "windows": [
    {
      "id": "0x03400006",
      "title": "窗口标题",
      "x": 0,
      "y": 0,
      "width": 1920,
      "height": 1080,
      "desktop": 0
    }
  ],
  "count": 1
}
```

#### `get_screen_size`

获取屏幕尺寸。

**参数：** 无

**返回：**
```json
{
  "success": true,
  "width": 1920,
  "height": 1080
}
```

#### `get_active_window`

获取当前活动窗口。

**参数：** 无

**返回：**
```json
{
  "success": true,
  "window_id": "0x03400006",
  "title": "窗口标题"
}
```

#### `move_window`

移动窗口到指定位置并调整大小。

**参数：**
- `window_id` (string): 窗口ID
- `x` (integer): X坐标
- `y` (integer): Y坐标
- `width` (integer): 宽度
- `height` (integer): 高度

**返回：**
```json
{
  "success": true,
  "window_id": "0x03400006",
  "position": {"x": 0, "y": 0},
  "size": {"width": 800, "height": 600}
}
```

#### `split_horizontal`

水平分屏（左右分屏）。

**参数：**
- `window_ids` (array): 窗口ID列表（1-2个）

**返回：**
```json
{
  "success": true,
  "layout": "horizontal",
  "screen_size": {"width": 1920, "height": 1080},
  "windows": [...]
}
```

#### `split_vertical`

垂直分屏（上下分屏）。

**参数：**
- `window_ids` (array): 窗口ID列表（1-2个）

**返回：**
```json
{
  "success": true,
  "layout": "vertical",
  "screen_size": {"width": 1920, "height": 1080},
  "windows": [...]
}
```

#### `split_grid`

网格分屏（四分屏）。

**参数：**
- `window_ids` (array): 窗口ID列表（1-4个）

**返回：**
```json
{
  "success": true,
  "layout": "grid",
  "screen_size": {"width": 1920, "height": 1080},
  "windows": [...]
}
```

#### `maximize_window`

最大化窗口。

**参数：**
- `window_id` (string): 窗口ID

**返回：**
```json
{
  "success": true,
  "window_id": "0x03400006",
  "action": "maximize"
}
```

## 使用场景

### 场景1：快速整理工作区

```
1. 列出所有窗口
2. 选择需要的窗口
3. 使用分屏功能快速排列
```

### 场景2：多任务并行工作

```
- 左侧：代码编辑器
- 右侧：浏览器文档
- 使用水平分屏快速设置
```

### 场景3：监控多个应用

```
- 左上：系统监控
- 右上：日志查看
- 左下：终端
- 右下：文档
- 使用网格分屏一次性排列
```

## 故障排除

### 问题1：找不到wmctrl命令

**解决方案：**
```bash
sudo apt install wmctrl
```

### 问题2：找不到xdotool命令

**解决方案：**
```bash
sudo apt install xdotool
```

### 问题3：无法获取屏幕尺寸

**解决方案：**
```bash
sudo apt install x11-utils
```

### 问题4：在WSL中无法使用

**说明：** WSL环境需要配置X服务器才能使用窗口管理功能。

**解决方案：**
1. 安装VcXsrv或X410
2. 设置DISPLAY环境变量：`export DISPLAY=:0`

## 技术架构

```
window_split_mcp/
├── __init__.py                    # 包初始化
├── window_split_tools.py          # 核心工具类
├── window_split_mcp_server.py     # MCP服务器
├── test_window_split.py           # 测试脚本
├── requirements.txt               # Python依赖
└── README.md                      # 本文档
```

## 开发计划

- [ ] 支持Windows原生窗口管理
- [ ] 支持macOS原生窗口管理
- [ ] 添加自定义布局配置
- [ ] 支持窗口分组管理
- [ ] 添加窗口历史记录
- [ ] 支持快捷键绑定

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 相关项目

- [screenshot_mcp](../screenshot_mcp) - 截屏工具
- [mouse_move_mcp](../mouse_move_mcp) - 鼠标控制工具
- [smart_mouse_move_mcp](../smart_mouse_move_mcp) - 智能鼠标移动工具

## 联系方式

如有问题或建议，请通过Issue联系我们。
