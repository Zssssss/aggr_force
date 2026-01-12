#!/usr/bin/env python3
"""列出所有可用的技能及其详细信息"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from get_skills_mcp.get_skills_mcp_server import (
    handle_call_tool,
    _ensure_loader,
)


async def main():
    print("=" * 80)
    print("GET SKILLS MCP - 所有可用技能列表")
    print("=" * 80)
    
    # 确保loader已初始化
    loader = _ensure_loader()
    
    print(f"\n📊 统计信息:")
    print(f"   总技能数: {len(loader.skills)}")
    print(f"   自定义技能: {len(loader.get_skills_by_source('custom'))}")
    print(f"   开源技能 (vendor): {len(loader.get_skills_by_source('vendor'))}")
    
    # 获取所有技能列表
    print("\n" + "=" * 80)
    print("📋 技能列表")
    print("=" * 80)
    
    result = await handle_call_tool("list_skills", {"source": "all"})
    for item in result:
        lines = item.text.split("\n")
        # 跳过第一行统计信息
        for line in lines[1:]:
            if line.strip():
                print(f"  • {line}")
    
    # 获取每个技能的详细信息
    print("\n" + "=" * 80)
    print("📖 技能详细信息")
    print("=" * 80)
    
    for key, skill in sorted(loader.skills.items()):
        print(f"\n{'─' * 80}")
        print(f"📦 技能名称: {skill.name}")
        print(f"   🔑 键名: {key}")
        print(f"   🏷️  来源: {skill.source}")
        print(f"   📁 路径: {skill.skill_md_path}")
        
        # 读取SKILL.md内容
        try:
            content = skill.read_text()
            print(f"   📏 内容长度: {len(content)} 字符")
            
            # 显示内容的前几行
            content_lines = content.split('\n')
            preview_lines = content_lines[:5]
            print(f"   📄 内容预览:")
            for line in preview_lines:
                if line.strip():
                    print(f"      {line[:70]}..." if len(line) > 70 else f"      {line}")
        except Exception as e:
            print(f"   ⚠️  读取失败: {e}")
    
    # 测试搜索功能
    print("\n" + "=" * 80)
    print("🔍 搜索功能测试 (关键词: 'design')")
    print("=" * 80)
    
    search_result = await handle_call_tool("search_skills", {"keyword": "design"})
    for item in search_result:
        print(item.text)
    
    # 测试获取单个技能
    if loader.skills:
        first_skill_name = list(loader.skills.keys())[0]
        print("\n" + "=" * 80)
        print(f"📄 获取单个技能示例: {first_skill_name}")
        print("=" * 80)
        
        skill_result = await handle_call_tool("get_skill", {"name": first_skill_name})
        for item in skill_result:
            lines = item.text.split('\n')
            # 只显示前20行
            for line in lines[:20]:
                print(line)
            if len(lines) > 20:
                print(f"\n... (还有 {len(lines) - 20} 行)")


if __name__ == "__main__":
    asyncio.run(main())
