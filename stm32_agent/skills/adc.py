"""ADC - STM32 HAL Library Skill Module"""

__skill_name__ = "adc"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "adc": {
        "description": "ADC 模数转换器，将模拟信号(电压)转换为数字值。支持单通道/多通道扫描、轮询/中断/DMA 触发",
        "resolution": {
            "12bit": "0~4095 (STM32F103 默认)",
            "10bit": "0~1023",
            "8bit":  "0~255",
            "6bit":  "0~63",
        },
        "trigger_sources": [
            ("Software Trigger", "软件触发 - 手动调用开始转换"),
            ("Timer TRGO", "定时器触发 - 固定频率采样(推荐!)"),
        ],
        "hal_apis": [
            "__HAL_RCC_ADCx_CLK_ENABLE()",
            "HAL_ADC_Init()",
            "HAL_ADC_ConfigChannel()",
            "HAL_ADC_Start()",
            "HAL_ADC_PollForConversion()",
            "HAL_ADC_GetValue()",
            "HAL_ADC_Start_IT()",
            "HAL_ADC_ConvCpltCallback()",
        ],
        "voltage_calculation": """
电压计算公式:
  voltage = (ADC_Value / 4095.0) * Vref    // Vref 通常 = 3.3V
  示例: ADC读数=2048 => voltage = (2048/4095)*3.3 = 1.65V

温度传感器(STM32内部):
  Vsense = (ADC_Value / 4095.0) * 3.3
  Temperature = ((1.43 - Vsense) / 0.0043) + 25  // 近似公式
""",
        "code_example": '''
// CubeMX 配置: ADC1 → IN0(PA0) → Rank1 → SamplingTime=55.5Cycles
// 如果用定时器触发: Timer4 → Trigger Source Selection → Event Out/TRGO

// 方法1: 轮询模式 (简单场景)
HAL_ADC_Start(&hadc1);
HAL_ADC_PollForConversion(&hadc1, 100);
uint16_t adc_val = HAL_ADC_GetValue(&hadc1);
float voltage = (adc_val / 4095.0f) * 3.3f;

// 方法2: 定时器触发 + 中断 (精确周期采样)
// 在 CubeMX 中:
//   ADC1 → External Trigger Conversion Source → Timer 4 Event Out
//   TIM4 → Prescaler=8399, Period=999 → 1Hz 触发频率
//   NVIC → ADC1&EXTI interrupt → Enable
HAL_ADC_Start_IT(&hadc1);

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {
    if (hadc->Instance == ADC1) {
        uint16_t val = HAL_ADC_GetValue(&hadc);
        float temp = ((1.43f - (val/4095.0f*3.3f)) / 0.0043f) + 25.0f;
        printf("Temp: %.1f C\\\\n", temp);
    }
}
''',
        "references": [
            {"source": "bhupender0415/STM32_Driver_Development", "url": "https://github.com/bhupender0415/STM32_Driver_Development", "note": "ADC 轮询/中断/多通道完整教程"},
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https://github.com/engineer-ae3o/stm32-hal-library", "note": "ADC HAL 实现"},
        ]
    },

    # ---- 6. PWM (脉冲宽度调制) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
