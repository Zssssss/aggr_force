#!/usr/bin/env python3
"""
Overleaf Hybrid模式登录脚本
用于首次登录Overleaf并保存session，支持人工完成reCAPTCHA验证

使用browser_use_mcp的hybrid_login工具
"""

import asyncio
import sys
import os

# 添加browser_use_mcp到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'browser_use_mcp'))

from browser_tools import get_browser_manager

async def overleaf_hybrid_login():
    """使用hybrid模式登录Overleaf"""
    manager = get_browser_manager()
    
    print("=" * 60)
    print("Overleaf Hybrid模式登录")
    print("=" * 60)
    print("\n使用browser_use_mcp的hybrid_login工具")
    print("这将打开浏览器窗口，等待你手动完成登录和reCAPTCHA验证")
    print("=" * 60)
    
    try:
        # 使用hybrid_login工具
        result = await manager.hybrid_login(
            session_id="overleaf_session",
            login_url="https://www.overleaf.com/login",
            wait_seconds=120  # 等待2分钟供用户完成登录
        )
        
        if result.get('success'):
            print("\n" + "=" * 60)
            print("✓ Hybrid模式登录完成!")
            print("=" * 60)
            print("📋 会话信息:")
            print(f"  - 会话ID: {result['session_id']}")
            print(f"  - 存储文件: {result['storage_state_file']}")
            print("\n💡 后续使用:")
            print("  - 运行 step2_headless_edit.py 进行自动化编辑")
            print("  - 会话将自动恢复登录状态，无需重新登录")
            print("=" * 60)
            return True
        else:
            print(f"\n❌ 登录失败: {result.get('error')}")
            return False
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    success = asyncio.run(overleaf_hybrid_login())
    
    if success:
        print("\n下一步: 运行 step2_headless_edit.py 进行自动化编辑")
        sys.exit(0)
    else:
        print("\n登录失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
