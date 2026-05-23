"""SPI - STM32 HAL Library Skill Module"""

__skill_name__ = "spi"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "spi": {
        "description": "SPI 高速同步串行总线，用于连接 Flash 存储器(W25Q64)、TFT 屏幕、SD 卡等高速外设",
        "modes": [
            ("SPI_MODE_MASTER", "主模式 - MCU 控制 SCK 时钟"),
            ("SPI_MODE_SLAVE", "从模式 - 外部设备提供时钟"),
            ("SPI_POLARITY_LOW", "CPOL=0 空闲时SCK低电平"),
            ("SPI_POLARITY_HIGH", "CPOL=1 空闲时SCK高电平"),
            ("SPI_PHASE_1EDGE", "CPHA=0 第一个边沿采样"),
            ("SPI_PHASE_2EDGE", "CPHA=1 第二个边沿采样"),
        ],
        "hal_apis": [
            "__HAL_RCC_SPIx_CLK_ENABLE()",
            "HAL_SPI_Init()",
            "HAL_SPI_Transmit()",
            "HAL_SPI_Receive()",
            "HAL_SPI_TransmitReceive()",
            "HAL_SPI_Transmit_IT()",
            "HAL_SPI_Transmit_DMA()",
        ],
        "wiring": "MOSI(PA7/PB5) MISO(PA6/PB4) SCK(PA5/PB3) CS(NSS-任意GPIO)",
        "code_example": '''
// CubeMX 配置: Connectivity → SPI1 → Full-Duplex Master
// 参数: Prescaler=256(281.25KBps), MSB First, CPOL=Low, CPHA=1Edge
// CS 引脚配置为 GPIO Output (手动控制片选)

#define W25Q64_CS_GPIO  GPIOB
#define W25Q64_CS_PIN   GPIO_PIN_6

void SPI_Select(void) { HAL_GPIO_WritePin(W25Q64_CS_GPIO, W25Q64_CS_PIN, GPIO_PIN_RESET); }
void SPI_Unselect(void) { HAL_GPIO_WritePin(W25Q64_CS_GPIO, W25Q64_CS_PIN, GPIO_PIN_SET); }

uint8_t SPI_RW(uint8_t data) {
    uint8_t rx_data;
    HAL_SPI_TransmitReceive(&hspi1, &data, &rx_data, 1, 100);
    return rx_data;
}

// 读取 W25Q64 JEDEC ID
void W25Q64_ReadID(uint8_t *id) {
    SPI_Select();
    SPI_RW(0x9F);              // Read JEDEC ID 指令
    id[0] = SPI_RW(0xFF);     // Manufacturer ID
    id[1] = SPI_RW(0xFF);     // Memory Type
    id[2] = SPI_RW(0xFF);     // Capacity
    SPI_Unselect();
}
''',
        "references": [
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https://github.com/engineer-ae3o/stm32-hal-library", "note": "SPI HAL 实现"},
            {"source": "CSDN: STM32CubeMX+HAL+硬件SPI读写W25Q64", "url": "https://blog.csdn.net/weixin_71894495/article/details/149944069"},
        ]
    },

    # ---- 4. I2C (Inter-Integrated Circuit) ----
    "i2c": {
        "description": "I2C 双线串行总线，用于连接 OLED 显示屏(SSD1306)、温湿度传感器(AHT20)、EEPROM、MPU6050 等",
        "modes": [
            ("I2C_MODE_I2C", "标准 I2C 模式"),
            ("SMBUSMODE", "SMBus 总线模式(电池管理)"),
        ],
        "hal_apis": [
            "__HAL_RCC_I2Cx_CLK_ENABLE()",
            "HAL_I2C_Init()",
            "HAL_I2C_Master_Transmit()",
            "HAL_I2C_Master_Receive()",
            "HAL_I2C_Mem_Read()",
            "HAL_I2C_Mem_Write()",
            "HAL_I2C_IsDeviceReady()",
            "HAL_I2C_Mem_Read_IT()",
            "HAL_I2C_Mem_Write_DMA()",
        ],
        "wiring": "SCL(PB6/PB8) SDA(PB7/PB9) + 上拉电阻(4.7K~10K)",
        "common_addresses": {
            "SSD1306 OLED": "0x78 (或 0x7A)",
            "AHT20 温湿度": "0x38",
            "MPU6050": "0xD0 (AD0=GND)",
            "EEPROM AT24C02": "0xA0",
            "BH1750 光照": "0x46",
        },
        "code_example": '''
// CubeMX 配置: Connectivity → I2C1 → I2C → Speed=Fast Mode (400kHz)
// 注意: 必须在 I2C Configuration → Timing 中选择正确参数

// 检测 I2C 设备是否在线
HAL_StatusTypeDef status = HAL_I2C_IsDeviceReady(&hi2c1, 0x78, 3, 100);
if (status == HAL_OK) {
    printf("OLED SSD1306 found!\\\\n");
}

// 写入 OLED 寄存器 (SSD1306 初始化序列)
uint8_t init_cmds[] = {0xAE, 0x20, 0x10, ...};  // 关闭显示, 寻址模式...
HAL_I2C_Mem_Write(&hi2c1, 0x78, 0x00, I2C_MEMADD_SIZE_8BIT,
                  init_cmds, sizeof(init_cmds), 100);

// 从 MPU6050 读取加速度数据
uint8_t data[6];
HAL_I2C_Mem_Read(&hi2c1, 0xD0, 0x3B, I2C_MEMADD_SIZE_8BIT,
                 data, 6, 100);
// data[0..2]=AccX/Y/Z high+low bytes
''',
        "references": [
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https://github.com/engineer-ae3o/stm32-hal-library", "note": "I2C HAL 实现"},
            {"source": "DeepBlueEmbedded", "url": "https://deepbluembedded.com/stm32-i2c-tutorial-hal-examples-slave-dma/", "note": "I2C Master/Slave + DMA 完整教程"},
        ]
    },

    # ---- 5. ADC (模数转换器) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
