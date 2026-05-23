"""DAC - STM32 HAL Library Skill Module"""

__skill_name__ = "dac"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SILL_DATA = {
"dac": {
        "description": "DAC 数模转换器，将数字值(0~4095)转换为模拟电压输出(0~3.3V)。用于波形发生(正弦/三角/方波)、音频输出、可控电压源、校准参考电压等",
        "specs": {
            "分辨率": "12 bit (0~4095 -> 0~VDD, 通常3.3V)",
            "输出通道": "DAC_OUT1(PA4), DAC_OUT2(PA5) -- STM32F103仅2个通道",
            "输出缓冲": "可选Enable(带负载能力)/Disable(更快响应)",
            "触发源": "软件触发/TIM2/TRGO/TIM4/TRGO/TIM5/TRGO/TIM6/TRGO/TIM7/TRGO/EXTI9",
            "DMA支持": "是! 可配合DMA生成连续波形(无需CPU干预)",
            "对齐方式": "12bit右对齐(默认), 12bit左对齐, 8bit右对齐",
        },
        "voltage_formula": "Vout = (Digital_Value / 4095) × VDD_AREF  (通常VDD=3.3V)",
        "hal_apis": [
            "__HAL_RCC_DAC_CLK_ENABLE()",
            "HAL_DAC_Init()",
            "HAL_DAC_ConfigChannel()",
            "HAL_DAC_Start()",
            "HAL_DAC_Start_DMA()",              # DMA波形输出(关键API!)
            "HAL_DAC_Stop()",
            "HAL_DAC_Stop_DMA()",
            "HAL_DAC_SetValue()",               # 软件触发写入DAC
            "HAL_DACGetValue()",                # 读取当前DAC值
            "HAL_DACEx_TriangleWaveGenerate()", # 三角波
            "HAL_DACEx_NoiseGenerate()",         # 噪声波(白噪声)
            "HAL_DAC_ConvCpltCallbackCh1()",     # DMA转换完成回调
        ],
        "code_example": '''
# CubeMX 配置: Analog -> DAC1 -> OUT1 (或 OUT2)
#   Trigger: None (软件触发) 或 Timer 6 Event Out (定时触发/DMA)
#   Output Buffer: Enable (推荐, 增加驱动能力)
#   如用DMA: System Core -> DMA -> 添加 DAC1 Channel1
#     Direction: Memory To Peripheral
#     Data Width: Half Word (16bit, 匹配DAC 12bit右对齐)

# ===== 方法1: 软件触发输出固定电压 =====
HAL_DAC_Start(&hdac, DAC_CHANNEL_1);
HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_12B_R, 2048);  # 1.65V (中间值)
# 或者: HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_8B_R, 128);  # 8bit模式

# ===== 方法2: DMA + 定时器 -> 生成正弦波 =====
# 生成正弦波查找表 (360个采样点)
#define WAVE_POINTS 360
uint16_t sine_table[WAVE_SAMPLES];
for (int i = 0; i < WAVE_POINTS; i++) {
    sine_table[i] = (uint16_t)((2047.0 * sin(i * 2 * M_PI / WAVE_POINTS)) + 2048.0);
    # 范围 1~4094 (避免DAC输出边界失真)
}

# TIM6 配置为DAC触发源 (决定采样频率)
#   PSC=0, ARR=11 -> 72MHz/12 = 6MHz? 太快了
#   正确: 需要 f_sample = desired_freq * points
#   例: 1kHz正弦波 -> f_sample = 1kHz * 360 = 360kHz -> PSC=0, ARR=199 (72M/200=360kHz)
#   但DAC最大1Msps, 所以实际最大约 1kHz/2000points=500kHz采样

# 更实际的例子: 100Hz正弦波, 360点 -> 36kHz采样率
#   PSC=0, ARR=1999 (72MHz/2000=36kHz)

# 启动 DAC + DMA 连续循环输出
HAL_TIM_Base_Start(&htim6);                          # 启动触发定时器
HAL_DAC_Start_DMA(&hdac, DAC_CHANNEL_1,
                   (uint32_t*)sine_table, WAVE_SAMPLES,
                   DAC_ALIGN_12B_R,                   # 12bit右对齐
                   DMA_MODE_CIRCULAR);                # 循环模式!

# DMA完成回调 (Normal模式下触发, Circular模式下持续运行)
void HAL_DAC_ConvCpltCallbackCh1(DAC_HandleTypeDef* hdac) {
    # 仅在 DMA_MODE_NORMAL 时调用
    printf("One wave cycle completed\\\\n");
}

# ===== 方法3: 三角波 (硬件自动生成, 无需查表!) =====
HAL_DACEx_TriangleWaveGenerate(&hdac, DAC_TRIANGLEAMPLITUDE_4095);
HAL_DAC_Start(&hdac, DAC_CHANNEL_1);
# 三角波频率 = f_TRIGGER / (4096 × 2)  (每个三角周期=上升+下降共8192步)

# ===== 音频输出示例 (蜂鸣器/小喇叭接PA4) =====
void Play_Tone(uint16_t frequency_ms, uint16_t duration_ms) {
    # 简单方波通过快速切换高低电平
    uint32_t start = HAL_GetTick();
    while (HAL_GetTick() - start < duration_ms) {
        HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_12B_R, 4095);
        HAL_Delay_us(500000 / frequency_ms);  # 半周期
        HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_12B_R, 0);
        HAL_Delay_us(500000 / frequency_ms);
    }
}
''',
        "references": [
            {"source": "DeepBlueEmbedded", "url": "https:#deepbluembedded.com/stm32-dac-tutorial-example-hal-code-analog-signal-genreation/", "note": "DAC完整教程(原理+代码+波形)" },
            {"source": "技术站", "url": "https:#jishuzhan.net/article/1960056220135501825", "note": "HAL库DAC数模转换详解"},
            {"source": "腾讯云开发者社区", "url": "https:#cloud.tencent.com/developer/article/2070317", "note": "CubeMX+HAL DAC波形输出教程"},
            {"source": "CSDN", "url": "https:#blog.csdn.net/as480133937/article/details/102309242", "note": "HAL库DAC十(建...)"},  # 标题被截断
        ]
    },

    # ---- 20. 内部 Flash / EEPROM 模拟 ----
}

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SILL_DATA
