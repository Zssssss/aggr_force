#!/usr/bin/env python3
"""
测试 MCP 服务器连接和工具调用
"""
import asyncio
import json
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

async def test_mcp_server():
    """测试MCP服务器"""
    print("=" * 60)
    print("测试 smart_mouse_move_mcp 服务器")
    print("=" * 60)
    
    try:
        # 导入服务器模块
        print("\n1. 测试导入模块...")
        from smart_mouse_move_mcp_server import app, list_tools, call_tool
        print("✓ 模块导入成功")
        
        # 测试列出工具
        print("\n2. 测试列出工具...")
        tools = await list_tools()
        print(f"✓ 找到 {len(tools)} 个工具:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:60]}...")
        
        # 测试调用 smart_move_to_target
        print("\n3. 测试调用 smart_move_to_target...")
        try:
            result = await call_tool(
                name="smart_move_to_target",
                arguments={
                    "target_description": "测试目标",
                    "max_attempts": 3,
                    "tolerance": 10
                }
            )
            print(f"✓ 工具调用成功，返回 {len(result)} 个内容项")
            for i, item in enumerate(result):
                if hasattr(item, 'type'):
                    print(f"  [{i}] 类型: {item.type}")
                    if item.type == "text":
                        text_preview = item.text[:100] if len(item.text) > 100 else item.text
                        print(f"      内容预览: {text_preview}")
                    elif item.type == "image":
                        print(f"      图片数据长度: {len(item.data) if hasattr(item, 'data') else 'N/A'}")
        except Exception as e:
            print(f"✗ 工具调用失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
