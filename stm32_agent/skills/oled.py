"""OLED - STM32 HAL Library Skill Module"""

__skill_name__ = "oled"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "oled": {
        "description": "SSD1306 OLED 显示屏驱动 (128×64像素)。支持 I2C/SPI 两种接口。用于显示文字、图像、波形、状态信息",
        "specs": {
            "分辨率": "128×64 像素 (默认), 也支持 128×32",
            "颜色": "单色(黄蓝双色可选)",
            "驱动IC": "SSD1306",
            "I2C 地址": "0x78 (SA0=GND) 或 0x7A (SA0=VCC)",
            "显存": "1024 字节 (128×64/8)",
            "视角": ">160度",
        },
        "libraries": [
            {"name": "4ilo/ssd1306-stm32HAL", "interface": "I2C", "url": "https://github.com/4ilo/ssd1306-stm32HAL"},
            {"name": "afiskon/stm32-ssd1306", "interface": "SPI+I2C", "url": "https://github.com/afiskon/stm32-ssd1306"},
            {"name": "stm32-ssd1306 (Gitee)", "interface": "SPI+I2C", "note": "支持 SH1106/SH1107/SSD1309 兼容"},
        ],
        "api_functions": [
            "ssd1306_Init(I2C/SPI handle) - 初始化显示屏",
            "ssd1306_Fill(Black/White) - 全屏填充颜色",
            "ssd1306_UpdateScreen() - 将缓冲区刷新到屏幕(关键!)",
            "ssd1306_SetCursor(x, y) - 设置绘制位置",
            "ssd1306_WriteString(str, font, color) - 绘制字符串",
            "ssd1306_DrawPixel(x, y, color) - 绘制像素点",
            "ssd1306_DrawLine(x0,y0,x1,y1,color) - 绘制直线",
            "ssd1306_DrawRectangle(x,y,w,h,color) - 绘制矩形",
            "ssd1306_SetContrast(level) - 设置对比度(0-255)",
        ],
        "code_example": '''
// === 方案A: 使用 4ilo/ssd1306-stm32HAL 库 (I2C) ===
#include "ssd1306.h"
#include "fonts.h"

// 初始化 (只需调用一次)
ssd1306_Init(&hi2c1);

// 绘制操作 (都在本地缓冲区进行)
ssd1306_Fill(Black);                              // 清屏
ssd1306_SetCursor(0, 0);
ssd1306_WriteString("Hello STM32!", Font_11x18, White);  // 标题
ssd1306_SetCursor(0, 28);
ssd1306_WriteString("Temp: 25.6 C", Font_7x10, White);    // 数据行

// 刷新到屏幕 (必须调用!)
ssd1306_UpdateScreen(&hi2c1);

// 数码管倒计时显示 (参考 HW7 项目)
void Display_CountDown(uint8_t seconds) {
    static const uint8_t seg_codes[] = {
        0xC0,0xF9,0xA4,0xB0,0x99,0x92,0x82,0xF8,
        0x80,0x90,0x88,0x83,0xC6,0xA1,0x86,0x8E
    };  // 共阳段码 0-F
    // ... 段选 + 位选动态扫描
}

// === 方案B: 直接用 HAL_I2C 操作 SSD1306 寄存器 ===
// 写命令
void OLED_WriteCmd(uint8_t cmd) {
    uint8_t buf[2] = {0x00, cmd};  // Control Byte=0x00(命令)
    HAL_I2C_Master_Transmit(&hi2c1, 0x78, buf, 2, 100);
}
// 写数据
void OLED_WriteData(uint8_t data) {
    uint8_t buf[2] = {0x40, data};  // Control Byte=0x40(数据)
    HAL_I2C_Master_Transmit(&hi2c1, 0x78, buf, 2, 100);
}
// 设置坐标
void OLED_SetCursor(uint8_t x, uint8_t page) {
    OLED_WriteCmd(0xB0 | page);         // Page 地址
    OLED_WriteCmd(0x10 | (x >> 4));     // 列地址高4位
    OLED_WriteCmd(0x0F & x);            // 列地址低4位
}
''',
        "references": [
            {"source": "4ilo/ssd1306-stm32HAL", "url": "https://github.com/4ilo/ssd1306-stm32HAL", "note": "MIT开源, I2C SSD1306 驱动库"},
            {"source": "IoTWord: STM32 I2C/SPI+DMA驱动SSD1306", "url": "https://www.iotword.com/17744.html", "note": "DMA加速 OLED 驱动方案"},
        ]
    },

    # ---- 10. W25Q64 (SPI Flash 存储) ----
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

    # ---- 11. PWR (电源管理) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
