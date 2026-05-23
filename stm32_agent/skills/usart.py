"""USART - STM32 HAL Library Skill Module"""

__skill_name__ = "usart"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "usart": {
        "description": "USART/UART 串口通信，支持轮询发送/接收、中断接收、DMA传输，常用于调试打印和设备间通信",
        "baud_rates": ["9600", "19200", "38400", "57600", "115200"],
        "modes": [
            ("Polling", "轮询模式 - 简单场景，阻塞等待完成"),
            ("Interrupt", "中断模式 - 非阻塞，适合不定长数据接收"),
            ("DMA", "DMA模式 - 大数据量高速传输，不占用CPU"),
        ],
        "hal_apis": [
            "__HAL_RCC_USARTx_CLK_ENABLE()",
            "HAL_UART_Init()",
            "HAL_UART_Transmit()",
            "HAL_UART_Receive()",
            "HAL_UART_Transmit_IT()",
            "HAL_UART_Receive_IT()",
            "HAL_UARTEx_ReceiveToIdle_IT()",
            "HAL_UART_RxCpltCallback()",
        ],
        "code_example": '''
// CubeMX 配置: Connectivity → USART1 → Mode=Asynchronous → Baud Rate=9600
// NVIC 中断使能: Settings → NVIC → USART1 global interrupt → Enabled

uint8_t rx_buffer[128];          // 接收缓冲区
volatile uint8_t cmd_ready = 0;  // 命令就绪标志

// 初始化接收
HAL_UARTEx_ReceiveToIdle_IT(&huart1, rx_buffer, sizeof(rx_buffer));

// 回调函数 - 数据接收完成时自动调用
void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t size) {
    if (huart->Instance == USART1) {
        rx_buffer[size] = '\\\\0';       // 字符串终止符
        cmd_ready = 1;                   // 标记命令就绪
        // 重新启动接收（防死锁关键步骤！）
        HAL_UARTEx_ReceiveToIdle_IT(huart, rx_buffer, sizeof(rx_buffer));
    }
}

// main 循环中处理
if (cmd_ready) {
    printf("Received: %s\\\\n", rx_buffer);
    cmd_ready = 0;
}

// Printf 重定向 (需要包含 stdio.h)
int fputc(int ch, FILE *f) {
    HAL_UART_Transmit(&huart1, (uint8_t*)&ch, 1, 10);
    return ch;
}
''',
        "references": [
            {"source": "bhupender0415/STM32_Driver_Development", "url": "https://github.com/bhupender0415/STM32_Driver_Development", "note": "UART Tx/Rx/Printf 完整教程"},
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https://github.com/engineer-ae3o/stm32-hal-library", "note": "UART HAL 实现"},
        ]
    },

    # ---- 3. SPI (串行外设接口) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
