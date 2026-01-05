# Overleaf Workflow 使用指南

## 快速开始

### 方法1: 使用启动脚本（推荐）

```bash
cd overleaf_workflow
./run_overleaf.sh
```

### 方法2: 直接运行Python脚本

```bash
cd overleaf_workflow
python3 overleaf_login.py
```

## 工作流程说明

### 自动化步骤

脚本会自动完成以下操作：

1. **启动浏览器** (2秒)
   - 打开Chromium浏览器
   - 最大化窗口

2. **导航到登录页** (3秒)
   - 访问 https://www.overleaf.com/login
   - 等待页面加载完成

3. **填充登录信息** (3秒)
   - 自动填入邮箱: 1094569708@qq.com
   - 自动填入密码: aggr_force123
   - 自动点击登录按钮

4. **等待验证** (60秒)
   - 如果出现验证码，请手动完成
   - 如果需要二次验证，请手动完成
   - 脚本会等待60秒后自动继续

5. **查找项目** (5秒)
   - 自动查找"resume-master-260105"项目
   - 自动点击进入项目

6. **打开文件** (2秒)
   - 自动查找resume-zh_CN.tex文件
   - 自动打开文件进行编辑

7. **保持打开** (180秒)
   - 浏览器保持打开3分钟
   - 您可以在此期间编辑文件
   - 查看实时PDF预览

### 人工操作步骤

在以下情况需要人工介入：

1. **验证码识别**
   - 如果Overleaf显示验证码，请手动完成
   - 完成后脚本会自动继续

2. **二次验证**
   - 如果需要邮箱验证或其他验证
   - 请在60秒内完成

3. **文件编辑**
   - 脚本打开文件后，您有3分钟时间编辑
   - 可以修改resume-zh_CN.tex的内容
   - Overleaf会自动保存更改

## 时间安排

| 步骤 | 自动/手动 | 时间 |
|------|----------|------|
| 启动浏览器 | 自动 | 2秒 |
| 导航到登录页 | 自动 | 3秒 |
| 填充登录信息 | 自动 | 3秒 |
| 等待验证 | 手动 | 60秒 |
| 查找项目 | 自动 | 5秒 |
| 打开文件 | 自动 | 2秒 |
| 编辑文件 | 手动 | 180秒 |
| **总计** | - | **约4分钟** |

## 配置修改

如需修改配置，编辑[`overleaf_login.py`](overleaf_login.py:17)：

```python
# Overleaf登录信息
OVERLEAF_EMAIL = "1094569708@qq.com"
OVERLEAF_PASSWORD = "aggr_force123"
PROJECT_TITLE = "resume-master-260105"
```

## 常见问题

### Q1: 脚本找不到登录输入框怎么办？

**A:** Overleaf可能更新了页面结构。您可以：
- 手动完成登录
- 脚本会在后续步骤继续执行

### Q2: 60秒不够完成验证怎么办？

**A:** 修改[`overleaf_login.py`](overleaf_login.py:89)中的等待时间：

```python
for i in range(120, 0, -10):  # 改为120秒
    print(f"  剩余 {i} 秒...")
    time.sleep(10)
```

### Q3: 找不到项目怎么办？

**A:** 检查项目名称是否正确：
- 登录Overleaf查看实际项目名称
- 修改`PROJECT_TITLE`变量

### Q4: 3分钟编辑时间不够怎么办？

**A:** 修改[`overleaf_login.py`](overleaf_login.py:151)中的等待时间：

```python
for i in range(300, 0, -30):  # 改为300秒（5分钟）
    print(f"  剩余 {i} 秒...")
    time.sleep(30)
```

### Q5: 如何让浏览器一直保持打开？

**A:** 修改脚本，注释掉关闭浏览器的代码：

```python
# finally:
#     print("\n关闭浏览器...")
#     browser.close()
#     print("完成！")
```

然后手动关闭浏览器窗口。

## Hybrid模式优势

此工作流采用**Hybrid模式**（混合模式），结合了：

### 自动化优势
- ✅ 快速启动和导航
- ✅ 准确填充表单
- ✅ 自动查找和打开文件
- ✅ 减少重复操作

### 人工优势
- ✅ 灵活处理验证码
- ✅ 应对各种验证方式
- ✅ 精确编辑文件内容
- ✅ 实时查看效果

## 扩展功能

### 添加更多项目

可以修改脚本支持多个项目：

```python
PROJECTS = [
    "resume-master-260105",
    "paper-draft-2024",
    "thesis-final"
]

# 让用户选择项目
for i, proj in enumerate(PROJECTS):
    print(f"{i+1}. {proj}")
```

### 自动编辑文件

可以添加自动编辑功能：

```python
# 在编辑器中查找特定文本并替换
editor = page.locator('.ace_editor')
# 使用Playwright的键盘操作进行编辑
```

### 批量处理

可以扩展为批量处理多个文件：

```python
FILES = ["resume-zh_CN.tex", "resume-en_US.tex"]
for file in FILES:
    # 打开并编辑每个文件
    pass
```

## 技术细节

### 使用的技术栈

- **Playwright**: 浏览器自动化框架
- **Python 3**: 脚本语言
- **Chromium**: 浏览器引擎

### 选择器策略

脚本使用多种选择器策略确保兼容性：

```python
# 邮箱输入框
email_input = page.locator('input[name="email"], input[type="email"], input#email')

# 密码输入框
password_input = page.locator('input[name="password"], input[type="password"], input#password')

# 登录按钮
login_button = page.locator('button[type="submit"], button:has-text("Login")')
```

### 错误处理

脚本包含完善的错误处理：

- 超时错误处理
- 元素未找到处理
- 网络错误处理
- 通用异常处理

## 下一步

完成基本工作流后，您可以：

1. 根据需求调整等待时间
2. 添加更多自动化步骤
3. 集成到CI/CD流程
4. 创建定时任务自动运行

## 支持

如有问题，请查看：
- [`README.md`](README.md) - 基本说明
- [`overleaf_login.py`](overleaf_login.py) - 源代码
- Playwright文档: https://playwright.dev/python/
