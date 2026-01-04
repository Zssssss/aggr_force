#!/bin/bash
# Browser Use MCP Server 安装脚本

set -e

echo "=========================================="
echo "Browser Use MCP Server 安装脚本"
echo "基于 browser-use 库的 AI 浏览器自动化"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "1. 安装 Python 依赖..."
pip install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "2. 安装 Playwright 浏览器..."
playwright install chromium

echo ""
echo "3. 检查 WSL 环境并安装系统依赖..."
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "检测到 WSL 环境，安装额外依赖..."
    sudo apt-get update
    sudo apt-get install -y \
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libpango-1.0-0 \
        libcairo2 \
        libatspi2.0-0
else
    echo "非 WSL 环境，跳过系统依赖安装"
fi

echo ""
echo "4. 创建数据目录..."
mkdir -p ~/.browser_use_mcp/sessions
mkdir -p ~/.browser_use_mcp/screenshots

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "请在 mcp_settings.json 中添加以下配置："
echo ""
cat << EOF
{
  "mcpServers": {
    "browser-use": {
      "command": "python3",
      "args": ["$SCRIPT_DIR/browser_use_mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "sk-your-openai-api-key",
        "BROWSER_USE_USERNAME": "your_username",
        "BROWSER_USE_PASSWORD": "your_password"
      },
      "disabled": false,
      "alwaysAllow": [],
      "disabledTools": []
    }
  }
}
EOF
echo ""
echo "⚠️ 重要提示："
echo "1. 必须配置 LLM API 密钥（OPENAI_API_KEY、ANTHROPIC_API_KEY、GOOGLE_API_KEY 或 GROQ_API_KEY）"
echo "2. 敏感数据（用户名、密码等）通过环境变量配置，不会暴露给 AI"
echo ""
