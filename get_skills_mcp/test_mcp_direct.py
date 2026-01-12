#!/usr/bin/env python3
"""直接测试MCP服务器返回的资源和工具"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from get_skills_mcp.get_skills_mcp_server import (
    handle_list_resources,
    handle_call_tool,
    _ensure_loader,
)


async def main():
    print("=" * 60)
    print("测试 MCP 服务器直接调用")
    print("=" * 60)
    
    # 确保loader已初始化
    loader = _ensure_loader()
    print(f"\nLoader initialized:")
    print(f"  Base dir: {loader.base_dir}")
    print(f"  Custom root: {loader.custom_skills_root}")
    print(f"  Vendor root: {loader.vendor_skills_root}")
    print(f"  Total skills: {len(loader.skills)}")
    print(f"  Custom: {len(loader.get_skills_by_source('custom'))}")
    print(f"  Vendor: {len(loader.get_skills_by_source('vendor'))}")
    
    # 测试 list_resources
    print("\n" + "=" * 60)
    print("测试 handle_list_resources()")
    print("=" * 60)
    resources = await handle_list_resources()
    print(f"Total resources: {len(resources)}")
    for r in resources[:5]:  # 只显示前5个
        print(f"  - {r.name}: {r.uri}")
    if len(resources) > 5:
        print(f"  ... and {len(resources) - 5} more")
    
    # 测试 list_skills tool
    print("\n" + "=" * 60)
    print("测试 list_skills tool (source=all)")
    print("=" * 60)
    result = await handle_call_tool("list_skills", {"source": "all"})
    for item in result:
        lines = item.text.split("\n")
        print(f"First line: {lines[0]}")
        print(f"Total lines: {len(lines)}")
        if len(lines) <= 20:
            for line in lines[1:]:
                print(f"  {line}")
        else:
            for line in lines[1:6]:
                print(f"  {line}")
            print(f"  ... and {len(lines) - 6} more")
    
    # 测试 list_skills tool (source=vendor)
    print("\n" + "=" * 60)
    print("测试 list_skills tool (source=vendor)")
    print("=" * 60)
    result = await handle_call_tool("list_skills", {"source": "vendor"})
    for item in result:
        print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
