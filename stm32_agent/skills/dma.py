"""DMA - STM32 HAL Library Skill Module"""

__skill_name__ = "dma"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "dma": {
        "description": "DMA 直接存储器访问，无需 CPU 参与即可在外设与内存间搬运数据。用于 ADC 多通道采集、UART 高速收发、SPI/I2C 批量传输",
        "key_concepts": [
            ("Stream/Channel", "DMA 流和通道 - 不同外设使用固定通道(查手册!)"),
            ("Mode Circular", "循环模式 - 自动重装，适合持续采样"),
            ("Mode Normal", "普通模式 - 传完即停"),
            ("Data Width", "数据宽度 - Byte/HalfWord/Word 必须两端一致"),
            ("Increment", "地址递增 - Memory可增, Peripheral通常不增"),
        ],
        "dma_request_mapping": {
            "ADC1": "DMA1 Channel1",
            "USART1_TX": "DMA1 Channel4",
            "USART1_RX": "DMA1 Channel5",
            "SPI1_TX": "DMA1 Channel2",
            "SPI1_RX": "DMA1 Channel3",
            "I2C1_TX": "DMA1 Channel6",
            "I2C1_RX": "DMA1 Channel7",
            "TIM2_UP": "DMA1 Channel2",
            "TIM4_CH1": "DMA1 Channel1",
        },
        "hal_apis": [
            "__HAL_RCC_DMAx_CLK_ENABLE()",
            "HAL_DMA_Init()",
            "HAL_DMA_Start()",
            "HAL_DMA_PollForTransfer()",
            "HAL_DMA_Start_IT()",
            "HAL_DMA_IRQHandler()",
            "HAL_ADC_Start_DMA()",
            "HAL_UART_Receive_DMA()",
            "HAL_SPI_Transmit_DMA()",
        ],
        "code_example": '''
// CubeMX 配置: System Core → DMA → 添加 ADC1
//   Channel: DMA1 Channel1
//   Direction: Peripheral To Memory
//   Priority: High
//   Mode: Circular (循环)
//   Data Width: Half Word (16bit, 匹配ADC)
//   Increment Address: Memory=Yes, Peripheral=No

uint16_t adc_dma_buffer[3];  // 3通道ADC DMA缓冲区

// 启动 ADC + DMA (自动连续采集到缓冲区)
HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_dma_buffer, 3);

// main循环中直接读取 buffer 即可(无需调用任何API!)
while(1) {
    float ch0_volt = (adc_dma_buffer[0]/4095.0f)*3.3f;
    float ch1_volt = (adc_dma_buffer[1]/4095.0f)*3.3f;
    float ch2_volt = (adc_dma_buffer[2]/4095.0f)*3.3f;
    HAL_Delay(100);
}

// DMA 传输完成回调 (Normal模式下触发)
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc) {}
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {}
''',
        "references": [
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https://github.com/engineer-ae3o/stm32-hal-library", "note": "DMA HAL 实现"},
            {"source": "DeepBlueEmbedded", "url": "https://deepbluembedded.com/", "note": "STM32 HAL DMA 完整教程"},
        ]
    },

    # ---- 8. RTC (实时时钟) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
