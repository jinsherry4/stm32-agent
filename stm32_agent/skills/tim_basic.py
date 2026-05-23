"""TIM_BASIC - STM32 HAL Library Skill Module"""

__skill_name__ = "tim_basic"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "tim_basic": {
        "description": "TIM 定时器模块，支持基本定时(TIM6/TIM7无PWM/Capture)、通用定时(TIM2-TIM5含PWM/InputCapture/OutputCompare)。用于精确定时中断、PWM输出、输入捕获、输出比较等",
        "timer_types": [
            ("TIM6/TIM7 (基本定时)", "仅向上计数, 无GPIO, 用于驱动DAC/定时中断"),
            ("TIM2-TIM5 (通用定时)", "16/32位, 4通道, PWM+IC+OC+编码器, 最常用!"),
            ("TIM1/TIM8 (高级定时)", "通用定时功能 + 死区互补输出(电机驱动)"),
        ],
        "modes": [
            ("Timer Mode (向上/向下/中央对齐)", "定时中断、延时、周期任务调度"),
            ("PWM Generation", "脉宽调制输出(电机/LED/舵机)"),
            ("Input Capture", "测量脉宽/频率(超声波HC-SR04/红外解码)"),
            ("Output Compare", "精确时刻翻转电平/单次脉冲"),
            ("Encoder Interface", "正交编码器读取(电机测速/旋钮)"),
        ],
        "hal_apis": [
            "__HAL_RCC_TIMx_CLK_ENABLE()",
            "HAL_TIM_Base_Init()",
            "HAL_TIM_Base_Start()",
            "HAL_TIM_Base_Start_IT()",
            "HAL_TIM_Base_Stop_IT()",
            "HAL_TIM_PeriodElapsedCallback()",       // 定时溢出回调
            "HAL_TIM_Base_GetState()",
            "__HAL_TIM_SET_COUNTER()",               // 设置计数值
            "__HAL_TIM_GET_COUNTER()",               // 读取计数值
        ],
        "timing_formula": """
定时时间计算公式:
  T_overflow = (PSC + 1) * (ARR + 1) / f_TIM_clk
  频率: f = f_TIM_clk / [(PSC+1) * (ARR+1)]

常用配置速查表 (f_TIM_clk = 72MHz for STM32F103):

| 目标频率 | PSC | ARR(CNT) | 用途           |
|---------|-----|----------|---------------|
| 1 Hz    | 7199| 9999     | 1秒定时(时钟) |
| 100 Hz  | 7199| 99       | 10ms定时       |
| 1 kHz   | 71  | 999      | 1ms定时        |
| 10 kHz  | 71  | 99       | 0.1ms定时      |
| 20 kHz  | 0   | 3599     | 舵机50Hz基频   |

注意: TIM2/TIM3/TIM4/TIM5挂载在APB1(36MHz), 但内部自动x2=72MHz!
""",
        "code_example": '''
// ===== 场景1: 基本定时器中断 (1秒闪烁LED) =====
// CubeMX: Timers → TIM6 → Activated
//   Prescaler (PSC) = 7199   → 72MHz / 7200 = 10KHz
//   Counter Period (ARR) = 9999 → 10KHz / 10000 = 1Hz (每秒1次溢出)
//   NVIC: Enable TIM6 global interrupt

// 启动定时器
HAL_TIM_Base_Start_IT(&htim6);

// 定时溢出回调函数
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM6) {
        static uint32_t seconds = 0;
        seconds++;
        printf("Uptime: %lu s\\\\n", seconds);

        // 每1秒翻转一次LED
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_8);
    }
}

// ===== 场景2: 输入捕获 (测量PWM脉宽) =====
// CubeMX: TIM3 → Channel1 → Input Capture direct mode → Rising
//   Prescaler = 71 (1MHz计数频率)
//   NVIC: Enable TIM3 global interrupt

uint32_t IC_Value1 = 0, IC_Value2 = 0;
uint8_t capture_flag = 0;

HAL_TIM_IC_Start_IT(&htim3, TIM_CHANNEL_1);

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim, uint32_t channel) {
    if (htim->Instance == TIM3 && channel == TIM_CHANNEL_1) {
        if (capture_flag == 0) {
            IC_Value1 = HAL_TIM_ReadCapturedValue(htim, channel);  // 上升沿1
            __HAL_TIM_SET_CAPTUREPOLARITY(htim, TIM_CHANNEL_1, TIM_INPUTCHANNELPOLARITY_FALLING);
            capture_flag = 1;
        } else {
            IC_Value2 = HAL_TIM_ReadCapturedValue(htim, channel);  // 下降沿
            __HAL_TIM_SET_CAPTUREPOLARITY(htim, TIM_CHANNEL_1, TIM_INPUTCHANNELPOLARITY_RISING);

            uint32_t pulse_us = IC_Value2 - IC_Value1;  // 高电平时间(us)
            printf("Pulse width: %lu us (%.2f Hz)\\\\n", pulse_us, 1000000.0f/pulse_us);
            capture_flag = 0;
        }
    }
}

// ===== 场景3: 输出比较 (精确时刻产生脉冲) =====
// CubeMX: TIM4 → Channel1 → Output Compare CH1 → Toggle (PWM Generation禁用!)
//   PSC = 83 (1MHz), ARR = 99999 (10Hz, 100ms周期)
//   Pulse (CCR1) = 具体翻转点位置

HAL_TIM_OC_Start_IT(&htim4, TIM_CHANNEL_1);

void HAL_TIM_OC_DelayElapsedCallback(TIM_HandleTypeDef *htim, uint32_t channel) {
    if (htim->Instance == TIM4 && channel == TIM_CHANNEL_1) {
        // 每100ms触发一次
        printf("OC event at %lu us\\\\n", __HAL_TIM_GET_COUNTER(htim));
    }
}
''',
        "references": [
            {"source": "DeepBlueEmbedded", "url": "https://deepbluembedded.com/stm32-timer-interrupt-hal-example-timer-mode-lab/", "note": "定时器中断完整教程"},
            {"source": "aticleworld", "url": "https://aticleworld.com/stm32-timer-interrupt-tutorial-using-hal-code-example/", "note": "HAL定时器中断代码示例"},
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https://github.com/engineer-ae3o/stm32-hal-library", "note": "TIM HAL 完整实现"},
        ]
    },

    # ---- 15. TIM Encoder (编码器接口) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
