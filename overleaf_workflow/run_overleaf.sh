#!/bin/bash
# Overleaf自动化登录启动脚本

echo "============================================================"
echo "Overleaf自动化登录 - Hybrid模式"
echo "============================================================"
echo ""
echo "此脚本将："
echo "  1. 打开浏览器并导航到Overleaf"
echo "  2. 自动填充登录信息"
echo "  3. 等待您完成验证"
echo "  4. 自动进入项目并打开文件"
echo ""
echo "按Ctrl+C可随时退出"
echo "============================================================"
echo ""

# 检查依赖
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
    playwright install chromium
fi

# 运行脚本
python3 overleaf_login.py

echo ""
echo "脚本执行完成！"
