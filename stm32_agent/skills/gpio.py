"""GPIO - STM32 HAL Library Skill Module"""

__skill_name__ = "gpio"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SKILL_DATA = {
    "gpio": {
        "description": "GPIO 通用输入输出控制，包括推挽输出、开漏输出、上拉/下拉输入、模拟输入等模式",
        "modes": [
            ("GPIO_MODE_OUTPUT_PP", "推挽输出 - LED驱动、电平控制"),
            ("GPIO_MODE_OUTPUT_OD", "开漏输出 - I2C总线、线与逻辑"),
            ("GPIO_MODE_INPUT", "浮空输入 - 外部信号读取（需外部上拉）"),
            ("GPIO_MODE_IT_RISING", "上升沿触发中断 - 按键检测"),
            ("GPIO_MODE_IT_FALLING", "下降沿触发中断"),
            ("GPIO_MODE_IT_RISING_FALLING", "双边沿触发中断"),
            ("GPIO_MODE_ANALOG", "模拟输入 - ADC通道"),
        ],
        "hal_apis": [
            "__HAL_RCC_GPIOx_CLK_ENABLE()",
            "HAL_GPIO_Init()",
            "HAL_GPIO_WritePin()",
            "HAL_GPIO_ReadPin()",
            "HAL_GPIO_TogglePin()",
            "__HAL_GPIO_EXTI_CLEAR_IT()",
        ],
        "code_example": """
# CubeMX 配置: GPIO -> 选择引脚 -> 设置模式/速度/上下拉
# 推挽输出示例 (LED)
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_8, GPIO_PIN_SET);      # PA8 高电平
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_8, GPIO_PIN_RESET);    # PA8 低电平
HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_8);                   # PA8 翻转

# BSRR 方式 (原子操作，推荐用于多引脚同时控制)
# GPIOA->BSRR = GPIO_PIN_8;     # 置位(高电平)  [C语言]
# GPIOA->BRR = GPIO_PIN_8;      # 复位(低电平)  [C语言]

# 输入读取
GPIO_PinState state = HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0);
""",
        "references": [
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https://github.com/engineer-ae3o/stm32-hal-library", "note": "GPIO HAL 函数实现"},
            {"source": "bhupender0415/STM32_Driver_Development", "url": "https://github.com/bhupender0415/STM32_Driver_Development", "note": "GPIO + EXTI 中断驱动教程"},
        ]
    }
}


def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SKILL_DATA
