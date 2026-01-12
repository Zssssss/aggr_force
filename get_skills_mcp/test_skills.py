#!/usr/bin/env python3
"""
测试 Get Skills MCP Server 的功能
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from get_skills_mcp.skill_loader import SkillLoader


def test_skill_loader():
    """测试技能加载器"""
    print("=" * 60)
    print("测试 Skill Loader")
    print("=" * 60)
    
    # 创建加载器
    loader = SkillLoader()
    print(f"\n✓ 创建 SkillLoader 实例")
    print(f"  - 基础目录: {loader.base_dir}")
    print(f"  - 自定义技能目录: {loader.custom_skills_dir}")
    print(f"  - Vendor技能目录: {loader.vendor_skills_dir}")
    
    # 加载所有技能
    print(f"\n正在加载技能...")
    skills = loader.load_all_skills()
    print(f"\n✓ 加载完成，共 {len(skills)} 个技能")
    
    # 按来源分组
    custom_skills = loader.get_skills_by_source('custom')
    vendor_skills = loader.get_skills_by_source('vendor')
    
    print(f"\n技能统计:")
    print(f"  - 自定义技能: {len(custom_skills)} 个")
    print(f"  - Vendor技能: {len(vendor_skills)} 个")
    
    # 列出所有技能
    if skills:
        print(f"\n技能列表:")
        for name, skill in skills.items():
            source = skill.metadata.get('source', 'unknown')
            print(f"  [{source}] {name}")
            print(f"      描述: {skill.description[:50]}..." if len(skill.description) > 50 else f"      描述: {skill.description}")
    
    # 测试获取单个技能
    if skills:
        first_skill_name = list(skills.keys())[0]
        print(f"\n测试获取技能: {first_skill_name}")
        skill = loader.get_skill(first_skill_name)
        if skill:
            print(f"  ✓ 成功获取技能")
            print(f"    - 名称: {skill.name}")
            print(f"    - 描述: {skill.description}")
            print(f"    - 指令长度: {len(skill.instructions)} 字符")
            print(f"    - 来源: {skill.metadata.get('source')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def test_skill_formats():
    """测试不同格式的技能文件"""
    print("\n" + "=" * 60)
    print("测试技能文件格式")
    print("=" * 60)
    
    from get_skills_mcp.skill_loader import Skill
    
    # 测试 Skill 对象
    skill = Skill(
        name="test_skill",
        description="这是一个测试技能",
        instructions="执行测试指令",
        metadata={"source": "test", "version": "1.0.0"}
    )
    
    print(f"\n✓ 创建 Skill 对象")
    print(f"  - 名称: {skill.name}")
    print(f"  - 描述: {skill.description}")
    print(f"  - 指令: {skill.instructions}")
    
    # 转换为字典
    skill_dict = skill.to_dict()
    print(f"\n✓ 转换为字典:")
    for key, value in skill_dict.items():
        if key != 'instructions':
            print(f"  - {key}: {value}")
    
    print("\n" + "=" * 60)


def main():
    """主函数"""
    print("\n🚀 Get Skills MCP Server - 功能测试\n")
    
    try:
        # 测试技能加载器
        test_skill_loader()
        
        # 测试技能格式
        test_skill_formats()
        
        print("\n✅ 所有测试通过！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
