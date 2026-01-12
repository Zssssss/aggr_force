#!/usr/bin/env python3
"""get_skills_mcp.skill_loader

按用户给定的最小规范加载 skills：

- 技能根目录：`./skills`（相对项目根目录）
- 一个 skill = `skills/<skill_name>/SKILL.md`
- 列表仅扫描 `skills/` 的**一级子目录**（不递归），且必须存在 `SKILL.md`

同时为了兼容 vendor/anthropics-skills，本 loader 还会从：
- `vendor/anthropics-skills/skills`
以同样规则加载（同样只扫描一级子目录，且必须有 `SKILL.md`）。

注意：不再加载 `skills/custom/*.md|*.json|*.txt` 这类 legacy 文件；避免把“文档/规范类”误当 skill。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Skill:
    """只保留最小字段：name + SKILL.md 路径 + 来源。"""

    name: str
    skill_md_path: Path
    source: str  # custom | vendor

    def read_text(self) -> str:
        return self.skill_md_path.read_text(encoding="utf-8")


class SkillLoader:
    """加载 skills/<name>/SKILL.md（以及 vendor/anthropics-skills/skills/<name>/SKILL.md）。"""

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent

        self.base_dir = Path(base_dir)

        # 对齐用户示例：主 skills 根目录
        self.custom_skills_root = self.base_dir / "skills"
        # 兼容 vendor：只加载 vendor repo 的 skills 子目录（不碰 spec/template 等）
        self.vendor_skills_root = self.base_dir / "vendor" / "anthropics-skills" / "skills"

        self.roots: List[Tuple[str, Path]] = [
            ("custom", self.custom_skills_root),
            ("vendor", self.vendor_skills_root),
        ]

        # key: skill_key（通常等于目录名；冲突时 vendor_ 前缀）
        self.skills: Dict[str, Skill] = {}

    def load_all_skills(self) -> Dict[str, Skill]:
        self.skills.clear()

        for source, root in self.roots:
            if not root.exists():
                logger.info("Skills root not found: %s", root)
                continue

            for d in root.iterdir():
                if not d.is_dir():
                    continue
                skill_md = d / "SKILL.md"
                if not skill_md.is_file():
                    continue

                name = d.name
                key = name

                # 冲突策略：custom 优先，vendor 加前缀
                if key in self.skills and source == "vendor":
                    key = f"vendor_{name}"

                # 极端情况：仍冲突则追加序号
                if key in self.skills:
                    i = 2
                    while f"{key}_{i}" in self.skills:
                        i += 1
                    key = f"{key}_{i}"

                self.skills[key] = Skill(name=name, skill_md_path=skill_md, source=source)

        return self.skills

    def reload_skills(self) -> Dict[str, Skill]:
        return self.load_all_skills()

    def list_skills(self) -> List[str]:
        return sorted(self.skills.keys())

    def get_skill(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)

    def get_skills_by_source(self, source: str) -> Dict[str, Skill]:
        return {k: v for k, v in self.skills.items() if v.source == source}
