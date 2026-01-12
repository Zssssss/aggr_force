#!/bin/bash
# 钉钉文档下载工具 - 快速启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "钉钉文档下载工具"
echo "========================================"
echo ""
echo "目标文档: 2026-0105-0111"
echo ""
echo "请选择操作:"
echo "  1. 首次登录（Hybrid模式 - 显示浏览器窗口）"
echo "  2. 自动下载文档（Headless模式 - 后台运行）"
echo "  3. 查看已下载的文档"
echo "  4. 退出"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "========================================"
        echo "步骤1: 首次登录"
        echo "========================================"
        echo ""
        python3 step1_hybrid_login.py
        ;;
    2)
        echo ""
        echo "========================================"
        echo "步骤2: 自动下载文档"
        echo "========================================"
        echo ""
        python3 step2_download_docs.py
        ;;
    3)
        echo ""
        echo "========================================"
        echo "已下载的文档"
        echo "========================================"
        echo ""
        if [ -d "downloaded_docs" ]; then
            ls -lh downloaded_docs/
            echo ""
            echo "文档位置: $SCRIPT_DIR/downloaded_docs/"
        else
            echo "还没有下载任何文档"
            echo "请先运行选项1和2"
        fi
        ;;
    4)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac
