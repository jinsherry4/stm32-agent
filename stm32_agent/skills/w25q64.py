"""W25Q64 SPI Flash - STM32 HAL Library Skill Module"""

__skill_name__ = "w25q64"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "w25q64": {
        "description": "W25Q64 系列 SPI NOR Flash 芯片 (8MB/16MB容量)。用于存储字库文件、日志数据、固件升级、图片资源等",
        "specs": {
            "W25Q64": "8 MByte (64 Mbit), 128 个扇区",
            "W25Q128": "16 MByte (128 Mbit), 256 个扇区",
            "Sector Size": "4 KB (一个扇区需先擦除再写)",
            "Page Size": "256 Bytes (每次写入不超过一页)",
            "Interface": "SPI Mode 0/3, 最高 104MHz",
            "JEDEC ID": "0xEF4017 (W25Q64), 0xEF4018 (W25Q128)",
        },
        "instruction_set": [
            ("0x9F", "Read JEDEC ID (制造商+类型+容量)"),
            ("0x03", "Read Data (标准读)"),
            ("0x0B", "Fast Read (快速读, 8 dummy cycles)"),
            ("0x02", "Page Program (页编程, 最大256字节)"),
            ("0x20", "Sector Erase (擦除4KB扇区)"),
            ("0xD8", "Block Erase 64KB"),
            ("0xC7", "Chip Erase (全片擦除)"),
            ("0x05", "Read Status Register 1"),
            ("0x06", "Write Enable (写操作前必须调用!)"),
            ("0x04", "Write Disable"),
        ],
        "operation_flow": """
W25Q64 操作流程 (非常重要!):
  读:    CS低 → 发送指令(03/0B) → 发送地址 → 读取数据 → CS高
  写:    写使能(06) → CS低 → 页编程(02)+地址+数据 → CS高 → 等待BUSY清零
  擦除:  写使能(06) → CS低 → 扇区擦除(20)+地址 → CS高 → 等待BUSY清零(~50ms)
  ⚠️ 写之前必须擦除! 擦除只能将1变0!
""",
        "code_example": '''
#define W25Q64_WRITE_ENABLE   0x06
#define W25Q64_READ_ID        0x9F
#define W25Q64_READ_DATA      0x03
#define W25Q64_PAGE_PROGRAM   0x02
#define W25Q64_SECTOR_ERASE   0x20
#define W25Q64_READ_STATUS1   0x05
#define W25Q64_BUSY_FLAG      0x01

void W25Q64_WaitBusy(void) {
    uint8_t status;
    SPI_Select();
    SPI_RW(W25Q64_READ_STATUS1);
    do {
        status = SPI_RW(0xFF);
    } while (status & W25Q64_BUSY_FLAG);
    SPI_Unselect();
}

void W25Q64_WriteEnable(void) {
    SPI_Select(); SPI_RW(W25Q64_WRITE_ENABLE); SPI_Unselect();
}

// 扇区擦除 (4KB)
void W25Q64_SectorErase(uint32_t sector_addr) {
    W25Q64_WaitBusy();
    W25Q64_WriteEnable();
    SPI_Select();
    SPI_RW(W25Q64_SECTOR_ERASE);
    SPI_RW((addr >> 16) & 0xFF);  // 地址3字节(Big-Endian)
    SPI_RW((addr >> 8) & 0xFF);
    SPI_RW(addr & 0xFF);
    SPI_Unselect();
    W25Q64_WaitBusy();  // 等待约 50ms
}

// 页写入 (最大256字节)
void W25Q64_PageWrite(uint32_t addr, uint8_t *data, uint16_t len) {
    W25Q64_WaitBusy();
    W25Q64_WriteEnable();
    SPI_Select();
    SPI_RW(W25Q64_PAGE_PROGRAM);
    SPI_RW((addr >> 16) & 0xFF);
    SPI_RW((addr >> 8) & 0xFF);
    SPI_RW(addr & 0xFF);
    for (uint16_t i = 0; i < len; i++) SPI_RW(data[i]);
    SPI_Unselect();
}

// 从 Flash 读取汉字字库并在 OLED 上显示
void OLED_ShowChinese(uint16_t addr) {
    uint8_t font_buf[32];  // 16×16汉字 = 32字节
    W25Q64_ReadData(addr, font_buf, 32);
    // 将字模数据写入 OLED 显存...
}
''',
        "references": [
            {"source": "GitHub Topics: w25q64", "url": "https://github.com/topics/w25q64", "note": "W25Q64 相关项目合集"},
            {"source": "CSDN: STM32CubeMX+HAL+SPI读写W25Q64", "url": "https://blog.csdn.net/weixin_71894495/article/details/149944069"},
        ]
    },
'''

def get_skill_info() -> dict:
    """Return the skill data as a Python dict."""
    return eval(SKILL_DATA)
