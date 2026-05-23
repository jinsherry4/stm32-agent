"""
STM32 Agent - STM32 HAL Library AI Assistant
=============================================
仿 ROSAgent (OpenClaw) 架构的 STM32 外设开发助手。

架构：
  - core.py        : Skill 定义 + Registry + Agent 引擎
  - skills/        : 22 个外设模块（每个独立文件）
  - knowledge_base.py : 知识库自动加载器
  - guides.py       : CubeMX 配置向导
  - cli.py          : 命令行交互入口

使用方式：
    from stm32_agent import STM32Agent
    agent = STM32Agent()
    agent.query("如何配置 GPIO 输出 LED")
"""

from stm32_agent.core import Skill, SkillRegistry, STM32Agent

__version__ = "2.0.0"
__all__ = ["Skill", "SkillRegistry", "STM32Agent"]
