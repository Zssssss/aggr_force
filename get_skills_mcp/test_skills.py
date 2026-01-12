#!/usr/bin/env python3
"""get_skills_mcp.test_skills

回归测试：确保仅按目录扫描并且只读取每个 skill 的 SKILL.md。

规则（与服务端一致）：
- custom: ./skills/<skill_name>/SKILL.md
- vendor: ./vendor/anthropics-skills/skills/<skill_name>/SKILL.md
- 仅扫描一级子目录，不递归
- 不再把 *.md/*.json/*.txt 文件当 skill
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from get_skills_mcp.skill_loader import SkillLoader


def test_skill_loader() -> None:
    loader = SkillLoader()

    print("=" * 60)
    print("测试 SkillLoader（仅 SKILL.md）")
    print("=" * 60)
    print(f"base_dir={loader.base_dir}")
    print(f"custom_root={loader.custom_skills_root}")
    print(f"vendor_root={loader.vendor_skills_root}")

    skills = loader.load_all_skills()
    print(f"loaded={len(skills)}")

    # 基本断言：所有 skill 都应有 SKILL.md
    for key, skill in skills.items():
        assert skill.skill_md_path.name == "SKILL.md", f"{key} not SKILL.md"
        assert skill.skill_md_path.is_file(), f"{key} SKILL.md not exists"

    # smoke：读第一条
    if skills:
        first_key = sorted(skills.keys())[0]
        s = loader.get_skill(first_key)
        assert s is not None
        text = s.read_text()
        assert isinstance(text, str) and len(text) > 0
        print(f"smoke_read={first_key} chars={len(text)} source={s.source}")

    # 来源统计
    custom = loader.get_skills_by_source("custom")
    vendor = loader.get_skills_by_source("vendor")
    print(f"custom={len(custom)} vendor={len(vendor)} total={len(skills)}")


def main() -> None:
    try:
        test_skill_loader()
        print("\n✅ 测试通过")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
