# Window Split MCP - WSL环境配置指南

## 环境说明

**当前环境：** WSL (Windows Subsystem for Linux)  
**工作目录：** `/home/zsss/zsss_useful_tools/aggr_force`  
**系统：** Linux 6.6 (WSL)

## WSL环境特殊说明

在WSL中使用窗口管理功能需要特别配置，因为WSL本身没有图形界面，需要通过Windows端的X服务器来显示和管理窗口。

## 完整配置步骤

### 步骤1：安装Windows端X服务器

#### 选项A：VcXsrv（推荐）

1. 下载VcXsrv：https://sourceforge.net/projects/vcxsrv/
2. 安装到Windows系统
3. 启动XLaunch，配置如下：
   - Display settings: Multiple windows, Display number: 0
   - Start no client
   - Extra settings: 勾选 "Disable access control"
   - 保存配置以便下次使用

#### 选项B：X410（付费）

1. 从Microsoft Store安装X410
2. 启动X410
3. 使用默认配置即可

### 步骤2：配置WSL环境变量

```bash
# 设置DISPLAY环境变量
export DISPLAY=:0

# 永久设置（推荐）
echo 'export DISPLAY=:0' >> ~/.bashrc
source ~/.bashrc

# 验证设置
echo $DISPLAY
```

### 步骤3：安装WSL端依赖

```bash
# 更新包列表
sudo apt update

# 安装窗口管理工具
sudo apt install -y wmctrl xdotool x11-utils

# 验证安装
wmctrl -v
xdotool version
xdpyinfo | grep dimensions
```

### 步骤4：测试X服务器连接

```bash
# 测试X服务器是否可用
xdpyinfo | head

# 如果成功，会显示X服务器信息
# 如果失败，检查：
# 1. VcXsrv是否正在运行
# 2. DISPLAY变量是否正确设置
# 3. Windows防火墙是否阻止了连接
```

### 步骤5：安装Python依赖

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp
pip install -r requirements.txt
```

### 步骤6：运行测试

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp
python3 test_window_split.py
```

## MCP服务器配置

在 `.wecode/mcp.json` 中添加（注意DISPLAY环境变量）：

```json
{
  "mcpServers": {
    "window-split": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/window_split_mcp/window_split_mcp_server.py"
      ],
      "env": {
        "DISPLAY": ":0",
        "PYTHONPATH": "/home/zsss/zsss_useful_tools/aggr_force"
      }
    }
  }
}
```

## 常见问题（WSL特定）

### 问题1：cannot open display

**错误信息：**
```
Error: cannot open display: :0
```

**解决方案：**
1. 确认VcXsrv正在Windows上运行
2. 检查DISPLAY变量：`echo $DISPLAY`
3. 重新设置：`export DISPLAY=:0`
4. 检查Windows防火墙设置

### 问题2：X服务器连接被拒绝

**错误信息：**
```
X11 connection rejected because of wrong authentication
```

**解决方案：**
1. 在VcXsrv启动时勾选 "Disable access control"
2. 或者配置.Xauthority文件

### 问题3：找不到窗口

**原因：** WSL只能管理通过X服务器显示的窗口，无法管理Windows原生窗口

**解决方案：**
- 只能管理在WSL中启动并通过X服务器显示的GUI应用
- 无法管理Windows原生应用（如Chrome、VSCode等）
- 如需管理Windows窗口，需要使用Windows原生的窗口管理工具

### 问题4：性能问题

**现象：** 窗口操作响应慢

**解决方案：**
1. 使用有线网络而非WiFi
2. 确保VcXsrv使用硬件加速
3. 考虑使用WSL2而非WSL1

## WSL环境限制

### 可以做的：
- ✅ 获取屏幕尺寸
- ✅ 管理通过X服务器显示的Linux GUI应用
- ✅ 对X11应用进行分屏操作

### 不能做的：
- ❌ 管理Windows原生窗口
- ❌ 管理Windows桌面应用
- ❌ 直接操作Windows任务栏

## 替代方案

如果需要管理Windows原生窗口，建议：

1. **使用Windows原生工具**
   - PowerToys FancyZones
   - Windows 11内置分屏功能
   - AutoHotkey脚本

2. **创建Windows版本的MCP工具**
   - 使用PowerShell或Python的win32api
   - 直接调用Windows API

3. **混合方案**
   - WSL管理Linux应用
   - Windows工具管理Windows应用

## 测试WSL配置

运行以下命令测试配置：

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/window_split_mcp

# 测试1：基础功能
python3 -c "
from window_split_tools import WindowSplitTool
tool = WindowSplitTool()
print('屏幕尺寸:', tool.get_screen_size())
print('wmctrl可用:', tool.has_wmctrl)
print('xdotool可用:', tool.has_xdotool)
"

# 测试2：启动一个X11应用测试
# 例如：xeyes &
# 然后列出窗口
python3 -c "
from window_split_tools import WindowSplitTool
tool = WindowSplitTool()
result = tool.list_windows()
print('窗口列表:', result)
"
```

## 启动X11应用示例

```bash
# 启动一些测试应用
xterm &
xclock &
xeyes &

# 等待应用启动
sleep 2

# 列出窗口
python3 -c "
from window_split_tools import WindowSplitTool
tool = WindowSplitTool()
windows = tool.list_windows()
if windows['success']:
    for w in windows['windows']:
        print(f'{w[\"title\"]}: {w[\"id\"]}')
"

# 测试分屏
python3 -c "
from window_split_tools import WindowSplitTool
tool = WindowSplitTool()
windows = tool.list_windows()
if windows['success'] and len(windows['windows']) >= 2:
    ids = [w['id'] for w in windows['windows'][:2]]
    result = tool.split_windows_horizontal(ids)
    print('分屏结果:', result['success'])
"
```

## 推荐工作流程

### 方案1：纯WSL环境
1. 启动VcXsrv
2. 在WSL中启动GUI应用
3. 使用Window Split MCP管理这些应用

### 方案2：混合环境
1. Windows应用使用Windows工具管理
2. WSL应用使用Window Split MCP管理
3. 分别配置和使用

### 方案3：远程开发
1. 使用VSCode Remote-WSL
2. 在WSL中开发和测试
3. 通过X服务器显示GUI

## 性能优化建议

1. **使用WSL2**
   ```bash
   wsl --set-version Ubuntu 2
   ```

2. **配置.wslconfig**
   在Windows用户目录创建 `.wslconfig`：
   ```ini
   [wsl2]
   memory=4GB
   processors=2
   ```

3. **使用本地X服务器**
   - 避免网络延迟
   - 使用localhost而非IP地址

## 获取帮助

如果遇到WSL特定问题：
1. 检查VcXsrv是否运行：在Windows任务管理器中查看
2. 检查DISPLAY变量：`echo $DISPLAY`
3. 测试X连接：`xdpyinfo | head`
4. 查看错误日志：`dmesg | tail`

## 相关资源

- [WSL官方文档](https://docs.microsoft.com/en-us/windows/wsl/)
- [VcXsrv配置指南](https://sourceforge.net/projects/vcxsrv/)
- [WSL GUI应用支持](https://docs.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)

---

**最后更新：** 2025-12-29  
**环境：** WSL (Linux 6.6)
