#!/usr/bin/env python3
"""
Skill Loader - 加载和管理技能的核心模块

支持从以下目录加载技能：
1. skills/custom - 用户自定义技能目录
2. vendor/anthropics-skills - Anthropic开源技能目录
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class Skill:
    """技能类，表示一个可执行的技能"""
    
    def __init__(self, name: str, description: str, instructions: str, 
                 metadata: Optional[Dict[str, Any]] = None, 
                 source_path: Optional[Path] = None):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.metadata = metadata or {}
        self.source_path = source_path
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "metadata": self.metadata,
            "source_path": str(self.source_path) if self.source_path else None
        }
    
    def __repr__(self) -> str:
        return f"Skill(name={self.name}, source={self.source_path})"


class SkillLoader:
    """技能加载器，负责从不同目录加载技能"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        初始化技能加载器
        
        Args:
            base_dir: 基础目录，默认为项目根目录
        """
        if base_dir is None:
            # 默认使用当前文件的父目录的父目录作为基础目录
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = Path(base_dir)
        self.custom_skills_dir = self.base_dir / "skills" / "custom"
        self.vendor_skills_dir = self.base_dir / "vendor" / "anthropics-skills"
        
        self.skills: Dict[str, Skill] = {}
        
        logger.info(f"SkillLoader initialized with base_dir: {self.base_dir}")
        logger.info(f"Custom skills directory: {self.custom_skills_dir}")
        logger.info(f"Vendor skills directory: {self.vendor_skills_dir}")
    
    def load_all_skills(self) -> Dict[str, Skill]:
        """
        加载所有技能
        
        Returns:
            技能字典，key为技能名称，value为Skill对象
        """
        self.skills.clear()
        
        # 加载自定义技能
        if self.custom_skills_dir.exists():
            logger.info(f"Loading custom skills from: {self.custom_skills_dir}")
            self._load_skills_from_directory(self.custom_skills_dir, source="custom")
        else:
            logger.warning(f"Custom skills directory not found: {self.custom_skills_dir}")
        
        # 加载vendor技能
        if self.vendor_skills_dir.exists():
            logger.info(f"Loading vendor skills from: {self.vendor_skills_dir}")
            self._load_skills_from_directory(self.vendor_skills_dir, source="vendor")
        else:
            logger.warning(f"Vendor skills directory not found: {self.vendor_skills_dir}")
        
        logger.info(f"Total skills loaded: {len(self.skills)}")
        return self.skills
    
    def _load_skills_from_directory(self, directory: Path, source: str = "unknown"):
        """
        从指定目录加载技能
        
        Args:
            directory: 技能目录
            source: 技能来源标识
        """
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return
        
        # 遍历目录中的所有文件
        for item in directory.rglob("*"):
            if item.is_file():
                # 支持多种格式
                if item.suffix.lower() in ['.md', '.txt', '.json']:
                    try:
                        skill = self._load_skill_from_file(item, source)
                        if skill:
                            # 如果技能名称已存在，添加来源前缀避免冲突
                            skill_key = skill.name
                            if skill_key in self.skills:
                                skill_key = f"{source}_{skill.name}"
                                logger.warning(f"Skill name conflict, renamed to: {skill_key}")
                            
                            self.skills[skill_key] = skill
                            logger.info(f"Loaded skill: {skill_key} from {item}")
                    except Exception as e:
                        logger.error(f"Failed to load skill from {item}: {e}")
    
    def _load_skill_from_file(self, file_path: Path, source: str) -> Optional[Skill]:
        """
        从文件加载单个技能
        
        Args:
            file_path: 技能文件路径
            source: 技能来源
            
        Returns:
            Skill对象或None
        """
        try:
            if file_path.suffix.lower() == '.json':
                return self._load_skill_from_json(file_path, source)
            elif file_path.suffix.lower() in ['.md', '.txt']:
                return self._load_skill_from_markdown(file_path, source)
        except Exception as e:
            logger.error(f"Error loading skill from {file_path}: {e}")
            return None
    
    def _load_skill_from_json(self, file_path: Path, source: str) -> Optional[Skill]:
        """从JSON文件加载技能"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        name = data.get('name', file_path.stem)
        description = data.get('description', '')
        instructions = data.get('instructions', '')
        metadata = data.get('metadata', {})
        metadata['source'] = source
        
        return Skill(
            name=name,
            description=description,
            instructions=instructions,
            metadata=metadata,
            source_path=file_path
        )
    
    def _load_skill_from_markdown(self, file_path: Path, source: str) -> Optional[Skill]:
        """从Markdown文件加载技能"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单解析：使用文件名作为技能名称，内容作为说明和指令
        name = file_path.stem
        
        # 尝试从内容中提取标题和描述
        lines = content.strip().split('\n')
        description = ""
        instructions = content
        
        # 如果第一行是标题（以#开头），使用它作为描述
        if lines and lines[0].startswith('#'):
            description = lines[0].lstrip('#').strip()
            instructions = '\n'.join(lines[1:]).strip()
        
        metadata = {
            'source': source,
            'format': 'markdown'
        }
        
        return Skill(
            name=name,
            description=description or f"Skill from {file_path.name}",
            instructions=instructions,
            metadata=metadata,
            source_path=file_path
        )
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """
        获取指定名称的技能
        
        Args:
            name: 技能名称
            
        Returns:
            Skill对象或None
        """
        return self.skills.get(name)
    
    def list_skills(self) -> List[str]:
        """
        列出所有技能名称
        
        Returns:
            技能名称列表
        """
        return list(self.skills.keys())
    
    def get_skills_by_source(self, source: str) -> Dict[str, Skill]:
        """
        获取指定来源的所有技能
        
        Args:
            source: 技能来源（custom或vendor）
            
        Returns:
            技能字典
        """
        return {
            name: skill 
            for name, skill in self.skills.items() 
            if skill.metadata.get('source') == source
        }
    
    def reload_skills(self) -> Dict[str, Skill]:
        """
        重新加载所有技能
        
        Returns:
            技能字典
        """
        logger.info("Reloading all skills...")
        return self.load_all_skills()
