# Screenshot MCP 快速开始指南

## 📦 安装

### 1. 安装Python依赖

```bash
cd /home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp
pip install -r requirements.txt
```

### 2. 验证安装

```bash
python test_screenshot.py
```

如果看到"总计: 3/3 测试通过"，说明安装成功！

## 🚀 使用方法

### 方法1: 作为MCP服务器使用（推荐）

#### 配置Claude Desktop

编辑配置文件 `~/.config/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "screenshot": {
      "command": "python3",
      "args": [
        "/home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp/screenshot_mcp_server.py"
      ]
    }
  }
}
```

#### 重启Claude Desktop

配置完成后重启Claude Desktop，然后就可以在对话中使用截图功能了：

**示例对话：**
```
你: 请帮我截取当前屏幕
Claude: [调用 take_screenshot 工具并返回截图信息]
```

### 方法2: 作为Python模块使用

```python
from screenshot_mcp.screenshot_tools import ScreenshotTool

# 创建截图工具实例
tool = ScreenshotTool()

# 截图
result = tool.take_screenshot()

if result['success']:
    print(f"截图成功: {result['filepath']}")
    print(f"尺寸: {result['width']} x {result['height']}")
```

### 方法3: 命令行使用

```bash
cd /home/zsss/zsss_useful_tools/aggr_force
python -c "from screenshot_mcp.screenshot_tools import take_screenshot_simple; print(take_screenshot_simple())"
```

## 🎯 MCP工具说明

### take_screenshot

截取当前全屏并保存为PNG图片。

**参数：**
- `filename` (可选): 自定义文件名
- `output_dir` (可选): 保存目录
- `return_base64` (可选): 是否返回base64编码

**示例：**
```json
{
  "name": "take_screenshot",
  "arguments": {
    "filename": "my_screen.png"
  }
}
```

### get_screenshot_info

获取最近一次截图的详细信息。

**参数：** 无

## 📝 测试结果

```
✅ 基本截图: 通过
✅ 自定义文件名: 通过  
✅ Base64编码: 通过

总计: 3/3 测试通过
```

## 🔧 技术细节

- **WSL环境**: 自动调用Windows的PowerShell脚本进行截图
- **截图方法**: powershell_wsl
- **支持格式**: PNG
- **默认保存位置**: `/home/zsss/zsss_useful_tools/aggr_force/screenshot_mcp/`

## ⚠️ 注意事项

1. **WSL环境**: 已自动配置使用Windows截图功能
2. **文件权限**: 确保有写入screenshot_mcp目录的权限
3. **PowerShell**: 确保可以从WSL调用powershell.exe

## 🐛 故障排除

### 问题: 截图失败

**解决方案:**
```bash
# 检查PowerShell是否可用
powershell.exe -Command "Get-Date"

# 检查screen_op目录
ls -la /home/zsss/zsss_useful_tools/aggr_force/screen_op/
```

### 问题: 找不到模块

**解决方案:**
```bash
# 重新安装依赖
pip install -r requirements.txt
```

## 📚 更多文档

- [README.md](README.md) - 完整功能说明
- [CONFIG_GUIDE.md](CONFIG_GUIDE.md) - 详细配置指南
- [test_screenshot.py](test_screenshot.py) - 测试代码示例

## ✅ 项目状态

- ✅ 核心功能已实现
- ✅ WSL环境已测试通过
- ✅ 所有测试用例通过
- ✅ 文档已完善

## 📞 支持

如有问题，请查看：
1. 测试输出: `python test_screenshot.py`
2. 日志信息: 查看命令行输出
3. 配置文件: 检查MCP服务器配置
