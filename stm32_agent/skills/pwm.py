"""PWM - STM32 HAL Library Skill Module"""

__skill_name__ = "pwm"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "pwm": {
        "description": "PWM 脉宽调制输出，基于定时器 PWM 模式实现。用于电机调速、LED调光、舵机控制、DAC 输出等",
        "parameters": [
            ("Prescaler (PSC)", "预分频器 - 决定计数频率: fcnt=fclk/(PSC+1)"),
            ("Period (ARR)", "自动重载值 - 决定 PWM 频率: fpwm=fcnt/(ARR+1)"),
            ("Pulse (CCR)", "比较值 - 决定占空比: Duty%=CCR/(ARR+1)*100%"),
        ],
        "pwm_frequency_formula": "fpwm = fTIM_clk / [(PSC+1) * (ARR+1)]",
        "common_frequencies": {
            "LED PWM (人眼不可感知)": ">= 1000 Hz",
            "舵机 SG90 (50Hz)": "20ms 周期, 0.5~2.5ms 高电平",
            "直流电机": "10~20 kHz",
            "蜂鸣器音调": "262Hz(C4)~2093Hz(C7)",
        },
        "hal_apis": [
            "__HAL_RCC_TIMx_CLK_ENABLE()",
            "HAL_TIM_PWM_Init()",
            "HAL_TIM_PWM_ConfigChannel()",
            "HAL_TIM_PWM_Start()",
            "HAL_TIM_PWM_Stop()",
            "__HAL_TIM_SET_COMPARE()",
        ],
        "code_example": '''
// CubeMX 配置: Timers → TIM4 → Channel1 PWM Generation CH1
//   Prescaler (PSC) = 83    → 84MHz/84 = 1MHz 计数频率
//   Counter Period (ARR) = 999 → fpwm = 1MHz/1000 = 1000Hz (1kHz)
//   Pulse (CCR1) = 500     → 占空比 = 500/1000 = 50%

// 启动 PWM
HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_1);

// 动态调节亮度 (0~100%)
void LED_SetBrightness(uint8_t percent) {
    __HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_1, percent * 10);  // ARR=999
}

// 舵机控制 SG90 (PA0/TIM2_CH1, 50Hz)
// PSC=8399, ARR=19999 → 84MHz/8400/20000 = 0.5Hz? 不对
// 正确: 84MHz/(83+1)/(19999+1) = 50Hz ✓
// 0°: Pulse=500 (0.5ms), 90°: Pulse=1500 (1.5ms), 180°: Pulse=2500 (2.5ms)
void Servo_SetAngle(uint8_t angle) {
    uint16_t pulse = 500 + (angle * 2000 / 180);  // 500~2500
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pulse);
}
''',
        "references": [
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https://github.com/engineer-ae3o/stm32-hal-library", "note": "PWM + 定时器 HAL 实现"},
        ]
    },

    # ---- 7. DMA (直接存储器访问) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
