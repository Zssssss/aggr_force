# Window Split MCP - 项目总结

## 项目概述

Window Split MCP是一个基于Model Context Protocol (MCP)的窗口分屏管理工具，提供跨平台的窗口管理和自动分屏功能。

**项目名称：** Window Split MCP  
**版本：** 1.0.0  
**创建日期：** 2025-12-29  
**主要语言：** Python 3  
**协议：** Model Context Protocol (MCP)  

## 核心功能

### 1. 窗口信息获取
- 列出所有打开的窗口
- 获取窗口详细信息（ID、标题、位置、大小）
- 获取当前活动窗口
- 获取屏幕尺寸

### 2. 窗口操作
- 移动窗口到指定位置
- 调整窗口大小
- 最大化窗口

### 3. 自动分屏布局
- **水平分屏**：左右分屏，支持1-2个窗口
- **垂直分屏**：上下分屏，支持1-2个窗口
- **网格分屏**：2x2网格，支持1-4个窗口

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    AI Assistant                          │
│                  (MCP Client)                            │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol
                     │ (stdio)
┌────────────────────▼────────────────────────────────────┐
│           Window Split MCP Server                        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Tool Handlers                                    │  │
│  │  - list_windows                                   │  │
│  │  - get_screen_size                                │  │
│  │  - get_active_window                              │  │
│  │  - move_window                                    │  │
│  │  - split_horizontal/vertical/grid                 │  │
│  │  - maximize_window                                │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐  │
│  │  WindowSplitTool Core                            │  │
│  │  - Window management logic                        │  │
│  │  - Screen size detection                          │  │
│  │  - Layout calculation                             │  │
│  └──────────────────┬───────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              System Layer                                │
│                                                          │
│  Linux:    wmctrl, xdotool, xdpyinfo                    │
│  Windows:  ctypes (Win32 API)                           │
│  macOS:    system_profiler, AppleScript                 │
└─────────────────────────────────────────────────────────┘
```

### 模块结构

```
window_split_mcp/
│
├── __init__.py                    # 包初始化，导出公共接口
│   └── 导出: WindowSplitTool, WindowInfo, 便捷函数
│
├── window_split_tools.py          # 核心工具类
│   ├── WindowInfo (dataclass)     # 窗口信息数据类
│   └── WindowSplitTool (class)    # 主工具类
│       ├── __init__()             # 初始化，检查依赖
│       ├── get_screen_size()      # 获取屏幕尺寸
│       ├── list_windows()         # 列出所有窗口
│       ├── get_active_window()    # 获取活动窗口
│       ├── move_window()          # 移动窗口
│       ├── split_windows_horizontal()  # 水平分屏
│       ├── split_windows_vertical()    # 垂直分屏
│       ├── split_windows_grid()        # 网格分屏
│       └── maximize_window()           # 最大化窗口
│
├── window_split_mcp_server.py     # MCP服务器
│   ├── handle_list_tools()        # 列出可用工具
│   ├── handle_call_tool()         # 处理工具调用
│   └── 格式化函数                  # 格式化输出结果
│
├── test_window_split.py           # 测试脚本
│   └── 测试所有功能模块
│
├── requirements.txt               # Python依赖
├── README.md                      # 完整文档
├── QUICKSTART.md                  # 快速入门
└── PROJECT_SUMMARY.md             # 本文档
```

## 依赖关系

### Python依赖
- `mcp>=0.1.0` - MCP SDK核心库
- `Pillow` - 图像处理（可选）

### 系统依赖（Linux）
- `wmctrl` - 窗口管理控制工具
- `xdotool` - X11自动化工具
- `xdpyinfo` - X显示信息工具（x11-utils包）

### 系统依赖（Windows）
- 内置ctypes库（无需额外安装）

### 系统依赖（macOS）
- 内置system_profiler（无需额外安装）

## 核心算法

### 1. 水平分屏算法

```python
def split_windows_horizontal(window_ids):
    screen_width = get_screen_width()
    screen_height = get_screen_height()
    
    if len(window_ids) == 1:
        # 单窗口占左半屏
        move_window(window_ids[0], 0, 0, screen_width//2, screen_height)
    else:
        # 两窗口左右分屏
        move_window(window_ids[0], 0, 0, screen_width//2, screen_height)
        move_window(window_ids[1], screen_width//2, 0, screen_width//2, screen_height)
```

### 2. 垂直分屏算法

```python
def split_windows_vertical(window_ids):
    screen_width = get_screen_width()
    screen_height = get_screen_height()
    
    if len(window_ids) == 1:
        # 单窗口占上半屏
        move_window(window_ids[0], 0, 0, screen_width, screen_height//2)
    else:
        # 两窗口上下分屏
        move_window(window_ids[0], 0, 0, screen_width, screen_height//2)
        move_window(window_ids[1], 0, screen_height//2, screen_width, screen_height//2)
```

### 3. 网格分屏算法

```python
def split_windows_grid(window_ids):
    screen_width = get_screen_width()
    screen_height = get_screen_height()
    
    half_width = screen_width // 2
    half_height = screen_height // 2
    
    positions = [
        (0, 0, half_width, half_height),              # 左上
        (half_width, 0, half_width, half_height),     # 右上
        (0, half_height, half_width, half_height),    # 左下
        (half_width, half_height, half_width, half_height)  # 右下
    ]
    
    for i, window_id in enumerate(window_ids):
        x, y, w, h = positions[i]
        move_window(window_id, x, y, w, h)
```

## 平台支持

### Linux（完全支持）✅
- ✅ 列出窗口
- ✅ 获取屏幕尺寸
- ✅ 获取活动窗口
- ✅ 移动窗口
- ✅ 所有分屏布局
- ✅ 最大化窗口

**依赖工具：** wmctrl, xdotool, xdpyinfo

### Windows（部分支持）⚠️
- ✅ 获取屏幕尺寸
- ⚠️ 其他功能开发中

### macOS（部分支持）⚠️
- ✅ 获取屏幕尺寸
- ⚠️ 其他功能开发中

## MCP工具定义

### 工具1: list_windows
- **描述：** 列出所有打开的窗口
- **参数：** 无
- **返回：** 窗口列表（ID、标题、位置、大小）

### 工具2: get_screen_size
- **描述：** 获取屏幕尺寸
- **参数：** 无
- **返回：** 宽度和高度

### 工具3: get_active_window
- **描述：** 获取当前活动窗口
- **参数：** 无
- **返回：** 窗口ID和标题

### 工具4: move_window
- **描述：** 移动和调整窗口
- **参数：** window_id, x, y, width, height
- **返回：** 操作结果

### 工具5: split_horizontal
- **描述：** 水平分屏
- **参数：** window_ids (1-2个)
- **返回：** 分屏结果

### 工具6: split_vertical
- **描述：** 垂直分屏
- **参数：** window_ids (1-2个)
- **返回：** 分屏结果

### 工具7: split_grid
- **描述：** 网格分屏
- **参数：** window_ids (1-4个)
- **返回：** 分屏结果

### 工具8: maximize_window
- **描述：** 最大化窗口
- **参数：** window_id
- **返回：** 操作结果

## 使用场景

### 场景1：开发环境
- 左侧：代码编辑器
- 右侧：浏览器/文档
- 使用水平分屏快速设置

### 场景2：监控仪表板
- 左上：系统监控
- 右上：日志查看
- 左下：终端
- 右下：文档
- 使用网格分屏一次性排列

### 场景3：多任务处理
- 上方：主要工作窗口
- 下方：参考资料
- 使用垂直分屏

## 性能特点

- **快速响应：** 窗口操作通常在100ms内完成
- **低资源占用：** 仅在调用时执行，无后台进程
- **批量处理：** 支持同时处理多个窗口
- **错误恢复：** 单个窗口失败不影响其他窗口

## 安全考虑

- **权限控制：** 仅操作用户可见的窗口
- **输入验证：** 所有参数都经过验证
- **错误处理：** 完善的异常捕获和错误提示
- **无副作用：** 不修改系统配置

## 测试覆盖

### 单元测试
- ✅ 屏幕尺寸获取
- ✅ 窗口列表获取
- ✅ 活动窗口获取
- ✅ 窗口移动
- ✅ 各种分屏布局
- ✅ 窗口最大化

### 集成测试
- ✅ MCP服务器启动
- ✅ 工具调用流程
- ✅ 错误处理
- ✅ 结果格式化

## 已知限制

1. **窗口管理器限制**
   - 某些窗口管理器可能限制窗口移动
   - 全屏应用可能无法调整

2. **平台限制**
   - Windows和macOS支持有限
   - WSL需要X服务器

3. **窗口类型限制**
   - 某些系统窗口可能无法操作
   - 模态对话框可能有特殊行为

## 未来计划

### 短期计划（v1.1）
- [ ] 完善Windows支持
- [ ] 完善macOS支持
- [ ] 添加更多预设布局
- [ ] 支持自定义分屏比例

### 中期计划（v1.2）
- [ ] 窗口分组管理
- [ ] 布局保存和恢复
- [ ] 快捷键支持
- [ ] 配置文件支持

### 长期计划（v2.0）
- [ ] GUI配置界面
- [ ] 多显示器支持
- [ ] 窗口历史记录
- [ ] 智能布局推荐

## 贡献指南

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解
- 添加详细的文档字符串
- 编写单元测试

### 提交流程
1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

## 相关资源

- [MCP官方文档](https://modelcontextprotocol.io/)
- [wmctrl文档](http://tripie.sweb.cz/utils/wmctrl/)
- [xdotool文档](https://github.com/jordansissel/xdotool)

## 版本历史

### v1.0.0 (2025-12-29)
- ✨ 初始版本发布
- ✅ 完整的Linux支持
- ✅ 8个MCP工具
- ✅ 3种分屏布局
- ✅ 完整的文档和测试

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过Issue联系我们。

---

**最后更新：** 2025-12-29  
**维护者：** Window Split MCP Team
