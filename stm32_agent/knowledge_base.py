"""
Knowledge Base Loader - 自动扫描并聚合所有 skill 模块
=========================================================
扫描 stm32_agent/skills/ 目录下的所有 .py 文件，
调用每个模块的 get_skill_info() 函数，合并为完整知识库字典。
"""

import os
import importlib
import sys
from pathlib import Path
from typing import Dict

# 获取 skills 目录的绝对路径
_SKILLS_DIR = Path(__file__).parent / "skills"


def load_knowledge_base() -> Dict[str, dict]:
    """
    扫描 skills/ 目录，加载所有技能模块，返回聚合知识库。

    Returns:
        dict: {module_name: skill_data_dict, ...}
        例如: {"gpio": {...}, "usart": {...}, ...}
    """
    knowledge_base = {}

    # 确保 skills 目录存在
    if not _SKILLS_DIR.exists():
        raise FileNotFoundError(
            f"Skills directory not found: {_SKILLS_DIR}\n"
            "Please ensure the project structure is intact."
        )

    # 扫描所有 .py 文件（排除 __init__.py）
    skill_files = sorted(
        f for f in _SKILLS_DIR.iterdir()
        if f.suffix == ".py" and f.name != "__init__.py"
    )

    for skill_file in skill_files:
        module_name = skill_file.stem  # e.g. "gpio", "usart"

        try:
            # 动态导入 skill 模块
            spec = importlib.util.spec_from_file_location(
                f"stm32_agent.skills.{module_name}",
                str(skill_file)
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules[f"stm32_agent.skills.{module_name}"] = mod
            spec.loader.exec_module(mod)

            # 调用 get_skill_info() 获取数据
            if hasattr(mod, "get_skill_info"):
                skill_data = mod.get_skill_info()
                if isinstance(skill_data, dict):
                    # skill_data 格式: {"module_name": {....}}
                    knowledge_base.update(skill_data)
                    print(f"  ✓ Loaded skill: {module_name}")
                else:
                    print(f"  ⚠ {module_name}: get_skill_info() did not return a dict")
            else:
                print(f"  ⚠ {module_name}: missing get_skill_info() function")

        except Exception as e:
            print(f"  ✗ Failed to load {module_name}: {e}")

    print(f"\n  Total: {len(knowledge_base)} skills loaded")
    return knowledge_base


def list_available_skills() -> list:
    """返回可用的技能名称列表（不加载全部数据）"""
    if not _SKILLS_DIR.exists():
        return []
    return sorted(
        f.stem for f in _SKILLS_DIR.iterdir()
        if f.suffix == ".py" and f.name != "__init__.py"
    )
