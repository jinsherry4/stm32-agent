"""EXTI - STM32 HAL Library Skill Module"""

__skill_name__ = "exti"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SILL_DATA = {
"exti": {
        "description": "EXTI 外部中断/事件控制器，用于检测 GPIO 引脚的电平变化(上升沿/下降沿/双边沿)并触发中断。适用于按键检测、传感器触发、外部信号捕获等场景",
        "features": [
            ("支持多达16个外部中断线", "EXTI0~EXTI15 对应 PA0~PA15 (或其他端口的Pin0~Pin15)"),
            ("边沿检测电路", "可配置上升沿/下降沿/双边沿触发"),
            ("软件中断事件寄存器", "支持软件触发中断(用于调试)"),
            ("事件与中断双模式", "事件模式可唤醒其他外设/CPU, 中断模式执行ISR"),
            ("掩码机制", "中断掩码(IMR)和事件掩码(EMR)独立控制"),
        ],
        "hal_apis": [
            "__HAL_RCC_GPIOx_CLK_ENABLE()",
            "HAL_GPIO_Init()",
            "__HAL_GPIO_EXTI_CLEAR_IT()",
            "HAL_NVIC_SetPriority()",
            "HAL_NVIC_EnableIRQ()",
            "HAL_GPIO_EXTI_Callback()",
        ],
        "exti_line_mapping": {
            "EXTI0": "PA0/PB0/PC0/PD0/PE0 (引脚0)",
            "EXTI1": "PA1/PB1/PC1/PD1/PE1 (引脚1)",
            "EXTI2": "PA2/PB2/PC2/PD2/PE2 (引脚2)",
            "EXTI3": "PA3/PB3/PC3/PD3/PE3 (引脚3)",
            "EXTI4": "PA4/PB4/PC4/PD4/PE4 (引脚4)",
            "EXTI5_9": "PA5~PA9/PB5~PB9 (引脚5-9共用IRQ)",
            "EXTI10_15": "PA10~PA15/PB10~PB15 (引脚10-15共用IRQ)",
        },
        "nvic_irq_mapping": {
            "EXTI0": "EXTI0_IRQn",
            "EXTI1": "EXTI1_IRQn",
            "EXTI2": "EXTI2_IRQn",
            "EXTI3": "EXTI3_IRQn",
            "EXTI4": "EXTI4_IRQn",
            "EXTI5_9": "EXTI9_5_IRQn",
            "EXTI10_15": "EXTI15_10_IRQn",
        },
        "code_example": '''
# CubeMX 配置: GPIO -> PA0 -> GPIO模式=External Interrupt Mode
#   Rising/Falling Trigger: Rising edge (或Falling/Rising+ Falling)
#   GPIO Pull-up/Pull-down: Pull-down (按键接VCC时选下拉)
#   NVIC: Enable EXTI line0 interrupt

# 初始化代码 (CubeMX自动生成)
# void MX_GPIO_Init(void) {
#     GPIO_InitTypeDef GPIO_InitStruct = {0};
#     __HAL_RCC_GPIOA_CLK_ENABLE();
#     GPIO_InitStruct.Pin = GPIO_PIN_0;
#     GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;    # 上升沿触发
#     GPIO_InitStruct.Pull = GPIO_PULLDOWN;           # 下拉
#     GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
#     HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
#
#     HAL_NVIC_SetPriority(EXTI0_IRQn, 2, 0);        # 设置优先级
#     HAL_NVIC_EnableIRQ(EXTI0_IRQn);                 # 使能中断
# }

# 外部中断回调函数 (用户实现)
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_0) {
        # 按键按下! 执行相应动作
        printf("Button pressed!\\\\n");

        # 翻转LED
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_8);
    }
}

# 注意: EXTI0~4 有独立的 IRQ Handler, EXTI5~9 共用, EXTI10~15 共用
void EXTI0_IRQHandler(void) {
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_0);  # 内部会清除标志并调用Callback
}

void EXTI9_5_IRQHandler(void) {
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_5))  { HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_5); }
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_6))  { HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_6); }
    # ... 检查 Pin5~9
}

void EXTI15_10_IRQHandler(void) {
    if (__HAL_GPIO_EXTI_GET_IT(GPIO_PIN_10)) { HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_10); }
    # ... 检查 Pin10~15
}
''',
        "references": [
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https:#github.com/engineer-ae3o/stm32-hal-library", "note": "EXTI HAL 实现"},
            {"source": "野火STM32教程 - EXTI章节", "url": "https:#doc.embedfire.com/mcu/stm32/h743prov/hal/zh/latest/book/EXTI.html", "note": "EXTI 原理详解"},
            {"source": "CSDN: STM32F103HAL库EXTI使用", "url": "https:#blog.csdn.net/weixin_44457715/article/details/142819502", "note": "HAL库EXTI完整教程"},
        ]
    },

    # ---- 14. TIM (基本定时器/通用定时器) ----
}

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SILL_DATA
