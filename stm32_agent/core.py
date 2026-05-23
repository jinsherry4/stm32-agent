"""
STM32 Agent Core - 核心引擎
============================
仿 ROSAgent core.py 架构：
  1. Skill          : 技能数据类（类似 ROSAgent.Skill）
  2. SkillRegistry  : 注册中心（类似 ROSAgent.SkillRegistry）
  3. STM32Agent     : Agent 主类（关键词 NLP 路由 + 查询引擎）
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable


# ─────────────────────────────────────────────
# 1. Skill 数据类（仿 ROSAgent.Skill）
# ─────────────────────────────────────────────

@dataclass
class Skill:
    """
    STM32 外设技能单元。
    参考 ROSAgent 的 Skill 定义，适配 STM32 HAL 库开发场景。
    """
    name: str                          # 模块标识符, 如 "gpio", "usart"
    description: str                   # 功能描述（供 NLP 匹配 & 用户阅读）
    category: str                      # 分类: digital/comm/analog/timing/display/storage/power/security/system
    peripheral: str                    # 外设名称: "GPIO", "USART1" 等
    hal_apis: List[str] = field(default_factory=list)   # 核心 HAL API 列表
    cube_mx_config: str = ""           # CubeMX 配置要点
    code_template: str = ""            # 代码模板（初始化+主循环）
    examples: List[str] = field(default_factory=list)  # 使用示例
    references: List[Dict] = field(default_factory=list)  # GitHub 参考资源
    prerequisites: List[str] = field(default_factory=list)  # 前置依赖

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "peripheral": self.peripheral,
        }

    def __repr__(self):
        return f"<Skill '{self.name}' [{self.category}]>"


# ─────────────────────────────────────────────
# 2. SkillRegistry 注册中心（仿 ROSAgent.SkillRegistry）
# ─────────────────────────────────────────────

class SkillRegistry:
    """
    技能注册中心。
    支持：
      - register() / get() / list()
      - 按分类过滤
      - 动态注册新技能
    """

    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> "SkillRegistry":
        """注册技能（支持链式调用）"""
        self._skills[skill.name] = skill
        return self

    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    def list_skills(self, category: str = None) -> List[Skill]:
        if category:
            return [s for s in self._skills.values() if s.category == category]
        return list(self._skills.values())

    def categories(self) -> List[str]:
        return sorted({s.category for s in self._skills.values()})

    def count(self) -> int:
        return len(self._skills)

    def describe_all(self) -> str:
        """生成技能概览文本"""
        lines = ["=" * 60, "  STM32 Skills Registry", "=" * 60, ""]
        for cat in self.categories():
            lines.append(f"[{cat}]")
            for s in self.list_skills(category=cat):
                lines.append(f"  - {s.name}: {s.description[:50]}")
            lines.append("")
        lines.append(f"Total: {self.count()} skills")
        return "\n".join(lines)


# ─────────────────────────────────────────────
# 3. STM32Agent 主类（仿 ROSAgent.ROSAgent）
# ─────────────────────────────────────────────

class STM32Agent:
    """
    STM32 HAL Library 开发助手 Agent。

    功能：
      - 自然语言查询 → 关键词匹配 → 返回外设知识
      - CubeMX 配置向导
      - 22 个外设模块完整覆盖
      - 支持组合查询（多模块联合回答）
    """

    # 分类映射 (module_name → category)
    CATEGORY_MAP = {
        "gpio": "digital",
        "exti": "digital",
        "usart": "comm",
        "spi": "comm",
        "i2c": "comm",
        "usb": "comm",
        "can": "comm",
        "adc": "analog",
        "dac": "analog",
        "pwm": "timing",
        "dma": "timing",
        "rtc": "timing",
        "tim_basic": "timing",
        "encoder": "timing",
        "oled": "display",
        "w25q64": "storage",
        "sdio": "storage",
        "flash_eeprom": "storage",
        "pwr": "power",
        "wdg": "power",
        "rng_crc": "security",
        "iap": "system",
    }

    # 关键词 → Skill 映射（NLP 路由核心）
    KEYWORD_MAP = {
        "gpio":     ["gpio", "led", "引脚", "按键", "输入输出", "output", "input", "toggle"],
        "exti":     ["exti", "外部中断", "中断线", "边沿触发", "上升沿", "下降沿", "按键中断", "irq", "nvic", "事件线"],
        "usart":    ["usart", "uart", "串口", "serial", "printf", "接收", "发送", "rx", "tx", "中断接收"],
        "spi":      ["spi", "flash", "w25q", "w25", "mosi", "miso", "sck"],
        "i2c":      ["i2c", "iic", "oled", "mpu6050", "aht20", "eeprom", "scl", "sda", "传感器"],
        "usb":      ["usb", "cdc", "vcp", "虚拟串口", "usb设备", "枚举", "descriptor", "端点"],
        "can":      ["can", "can总线", "控制器局域网", "报文", "过滤器", "mcp2551", "id", "仲裁"],
        "adc":      ["adc", "模数", "analog", "采样", "电压", "temperature", "温度", "电位器", "pot"],
        "dac":      ["dac", "数模", "波形", "正弦波", "三角波", "音频", "tone", "模拟输出", "sine"],
        "pwm":      ["pwm", "脉宽", "调光", "舵机", "servo", "motor", "电机", "频率", "占空比", "brightness"],
        "dma":      ["dma", "直接存储器", "搬运", "批量", "高速传输", "buffer", "循环"],
        "rtc":      ["rtc", "实时时钟", "clock", "calendar", "闹钟", "alarm", "date", "time", "日期", "时间", "wake"],
        "tim_basic":["tim", "timer", "定时器", "定时", "计数", "中断定时", "输入捕获", "输出比较", "pwm频率", "时基"],
        "encoder":  ["encoder", "编码器", "正交", "电机测速", "旋转方向", "脉冲计数", "quadrature"],
        "oled":     ["oled", "显示屏", "显示", "屏幕", "ssd1306", "lcd", "字体", "汉字"],
        "w25q64":   ["w25q64", "w25q", "flash", "存储", "字库", "擦除", "扇区", "page program"],
        "sdio":     ["sdio", "sd卡", "sdcard", "fatfs", "文件系统", "f_mount", "f_open", "读写文件", "存储卡"],
        "flash_eeprom": ["flash_eeprom", "eeprom", "参数保存", "数据持久化", "页擦除", "写入flash", "掉电保存"],
        "pwr":      ["pwr", "电源", "sleep", "stop", "standby", "低功耗", "shutdown", "wake", "唤醒", "vbat", "backup"],
        "wdg":      ["wdg", "watchdog", "看门狗", "iwdg", "wwdg", "喂狗", "reset", "复位", "死锁"],
        "rng_crc":  ["rng", "随机数", "crc", "校验", "checksum", "数据完整性", "真随机", "硬件随机"],
        "iap":      ["iap", "bootloader", "升级", "ota", "在线编程", "跳转应用", "ymodem", "引导加载", "固件升级"],
    }

    def __init__(self, knowledge_base: Dict[str, dict] = None):
        """
        初始化 Agent。

        Args:
            knowledge_base: 知识库字典。如果为 None 则从 skills/ 目录自动加载。
        """
        if knowledge_base is None:
            from stm32_agent.knowledge_base import load_knowledge_base
            knowledge_base = load_knowledge_base()

        self.knowledge_base = knowledge_base
        self.registry = SkillRegistry()
        self._build_skill_registry()

    def _build_skill_registry(self):
        """从知识库构建技能注册表"""
        for key, info in self.knowledge_base.items():
            skill = Skill(
                name=key,
                description=info.get("description", ""),
                category=self.CATEGORY_MAP.get(key, "other"),
                peripheral=info.get("peripheral", key.upper()),
                hal_apis=info.get("hal_apis", []),
                cube_mx_config=info.get("cube_mx_config", ""),
                code_template=info.get("code_template", ""),
                examples=info.get("examples", []),
                references=info.get("references", []),
                prerequisites=info.get("prerequisites", []),
            )
            self.registry.register(skill)

    def query(self, question: str) -> str:
        """
        自然语言查询 → 关键词匹配 → 返回详细答案。

        Args:
            question: 用户问题，如 "如何配置 GPIO 输出 LED"

        Returns:
            格式化的回答字符串
        """
        q_lower = question.lower()

        # 计算每个技能的匹配得分
        scores = {}
        for skill_name, keywords in self.KEYWORD_MAP.items():
            score = sum(1 for kw in keywords if kw in q_lower)
            if score > 0:
                scores[skill_name] = score

        if not scores:
            return self._format_no_match_response(question)

        # 多模块组合查询
        if len(scores) >= 2 and sum(1 for v in scores.values() if v > 0) >= 2:
            return self._format_combined_response(question, scores)

        best_match = max(scores, key=scores.get)
        return self._format_single_skill_response(best_match)

    # ── 响应格式化方法 ──

    def _format_single_skill_response(self, skill_name: str) -> str:
        info = self.knowledge_base.get(skill_name, {})
        skill = self.registry.get(skill_name)
        if not skill:
            return f"[Error] Skill '{skill_name}' not found"

        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"  STM32 {skill.peripheral} - {info.get('description', '')}")
        lines.append(f"{'='*60}")
        lines.append("")

        if skill.hal_apis:
            lines.append("[核心 HAL API]")
            lines.append("-" * 40)
            for api in skill.hal_apis:
                lines.append(f"  • {api}")
            lines.append("")

        code = info.get("code_example") or info.get("code_template", "")
        if code:
            lines.append("[代码示例]")
            lines.append("-" * 40)
            lines.append(code.strip())
            lines.append("")

        features = info.get("features", [])
        if features:
            lines.append("[功能特性]")
            lines.append("-" * 40)
            for feat, desc in features:
                lines.append(f"  ✓ {feat}: {desc}")
            lines.append("")

        if skill.references:
            lines.append("[参考资源]")
            lines.append("-" * 40)
            for ref in skill.references:
                note = ref.get("note", "")
                url = ref.get("url", "")
                line = f"  • {note}"
                if url:
                    line += f"\n    {url}"
                lines.append(line)
            lines.append("")

        return "\n".join(lines)

    def _format_combined_response(self, question: str, scores: dict) -> str:
        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"  组合查询: {question}")
        lines.append(f"  涉及模块: {', '.join(sorted(scores.keys(), key=lambda k: scores[k], reverse=True))}")
        lines.append(f"{'='*60}")

        for skill_name in sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[:3]:
            info = self.knowledge_base.get(skill_name, {})
            lines.append(f"\n--- {skill_name.upper()} ---")
            lines.append(info.get("description", ""))
            if info.get("code_example"):
                code_lines = info["code_example"].strip().split("\n")[:12]
                lines.append("\n[代码摘要]")
                lines.extend(f"  {line}" for line in code_lines)
                lines.append("  ... (完整代码请单独查询 '{skill_name}')")
            lines.append("")

        return "\n".join(lines)

    def _format_no_match_response(self, question: str) -> str:
        skills_list = ", ".join(s.name for s in self.registry.list_skills())
        return (
            f"[未找到匹配]\n\n"
            f"查询: \"{question}\"\n\n"
            f"支持的技能列表:\n{skills_list}\n\n"
            f"你可以尝试:\n"
            f"  • agent.query('如何配置 GPIO 输出')\n"
            f"  • agent.query('USART 中断接收怎么做')\n"
            f"  • agent.query('ADC + DMA 多通道采样')\n"
            f"  • agent.query('IAP 在线升级')"
        )

    # ── 向导与展示方法 ──

    def show_all_knowledge(self) -> str:
        lines = []
        lines.append("=" * 70)
        lines.append("  STM32 Agent - 完整外设知识库")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"{'模块':<14} {'分类':<10} {'描述'}")
        lines.append("-" * 70)

        for skill in self.registry.list_skills():
            info = self.knowledge_base.get(skill.name, {})
            desc = info.get("description", "")[:50]
            lines.append(f"{skill.name:<14} {skill.category:<10} {desc}")

        lines.append("")
        lines.append("=" * 70)
        lines.append(f"  共 {self.registry.count()} 个外设模块 | {len(self.registry.categories())} 个分类")
        lines.append("=" * 70)
        return "\n".join(lines)

    def get_cube_mx_guide(self, skill_name: str) -> str:
        """获取 CubeMX 配置向导"""
        from stm32_agent.guides import CUBE_MX_GUIDES
        guide = CUBE_MX_GUIDES.get(
            skill_name,
            f"'{skill_name}' 的 CubeMX 配置指南待补充"
        )
        header = f"\n{'='*50}\n  CubeMX 配置向导: {skill_name}\n{'='*50}\n"
        return header + guide
