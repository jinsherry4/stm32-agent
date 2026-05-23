"""I2C - STM32 HAL Library Skill Module"""

__skill_name__ = "i2c"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
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
    printf("OLED SSD1306 found!\\n");
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
'''

def get_skill_info() -> dict:
    """Return the skill data as a Python dict."""
    return eval(SKILL_DATA)
