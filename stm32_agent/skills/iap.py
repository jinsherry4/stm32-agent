"""IAP - STM32 HAL Library Skill Module"""

__skill_name__ = "iap"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SKILL_DATA = {
    "iap": {
        "description": "IAP In-Application Programming 在线应用编程，实现通过串口/USB/CAN等接口远程升级固件。由Bootloader负责接收新固件并写入Flash，然后跳转到App执行。适用于产品发布后的OTA升级、远程维护",
        "architecture": """
+-------------------------------------------+
|         Flash 地址布局 (STM32F103C8)       |
+----------+--------------------------------+
| 0x08000000| Bootloader (8~16KB)          |
|           |   - 检查升级标志位             |
|           |   - 接收固件数据               |
|           |   - 写入Flash                  |
|           |   - 跳转到App                  |
+----------+--------------------------------+
| 0x08002000| App程序区 (48~56KB)           |
|           |   - VECTOR_TABLE偏移          |
|           |   - 正常业务逻辑               |
|           |   - 触发升级请求               |
+----------+--------------------------------+
| 0x0800E000| 备份区 / 新固件缓存            |
| 0x0800FFFF| (64KB total)                  |
+----------+--------------------------------+

升级流程:
  App请求升级 => 设置标志位+复位 => Bootloader检测标志
  => 通过Ymodem/Xmodem接收新固件 => 写入备份区/App区
  => 清除标志 => 跳转到App执行
""",
        "transport_protocols": [
            ("Ymodem", "串口IAP最常用的协议, 带CRC校验, 支持断点续传(部分终端)"),
            ("Xmodem", "简化版Ymodem, 协议更简单, 128字节/包"),
            ("自定义协议", "自己定义帧头+长度+数据+CRC"),
            ("USB DFU", "通过USB进行固件升级"),
            ("CAN Bootloader", "汽车电子常用"),
        ],
        "key_techniques": [
            ("VECTOR_TABLE 重映射", "App的向量表不在0x08000000, 必须用 SCB->VTOR 重映射"),
            ("Bootloader/App 分离编译", "两个工程独立编译, 各自有自己的链接脚本(.ld)"),
            ("中断向量表正确性", "App的向量表第一项必须是新栈指针, 第二项是Reset_Handler地址"),
            ("跳转前清理", "关闭所有外设中断, 禁用SysTick"),
            ("标志位约定", "RAM特定地址作为需要升级的标志"),
        ],
        "hal_apis": [
            "HAL_FLASH_Unlock() / HAL_FLASH_Lock()",
            "HAL_FLASHEx_Erase()",
            "HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, ...)",
            "__disable_irq() / __enable_irq()",
            "__set_MSP()",
            "__set_CONTROL(0)",
            "SCB->VTOR = FLASH_BASE | VECT_OFFSET",
        ],
        "code_example": """
// Bootloader main函数 (C代码参考)
int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART1_UART_Init();

    uint32_t flag = *((volatile uint32_t*)UPGRADE_FLAG_ADDR);
    if (flag == UPGRADE_MAGIC) {
        printf("=== Upgrade Mode ===\\n");
        // Ymodem 接收固件
        Ymodem_Receive(APP_ADDR, rx_buffer, sizeof(rx_buffer));
        *((volatile uint32_t*)UPGRADE_FLAG_ADDR) = 0;
    }

    Jump_To_App(APP_ADDR);
}

void Jump_To_App(uint32_t app_addr) {
    typedef void (*pFunction)(void);
    pFunction JumpToApplication;
    uint32_t stack_ptr = *(volatile uint32_t*)app_addr;
    if ((stack_ptr & 0x2FFE0000) == 0x20000000) {
        __disable_irq();
        SysTick->CTRL = 0;
        __HAL_RCC_GPIOA_CLK_DISABLE();
        __set_MSP(stack_ptr);
        JumpToApplication = (pFunction)(*(volatile uint32_t*)(app_addr + 4));
        JumpToApplication();
    }
}
""",
        "references": [
            {"source": "STM32 IAP Tutorial", "note": "Bootloader 跳转与向量表重映射"},
        ]
    }
}


def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SKILL_DATA
