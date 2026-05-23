"""FLASH_EEPROM - STM32 HAL Library Skill Module"""

__skill_name__ = "flash_eeprom"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "flash_eeprom": {
        "description": "利用 STM32 内部 Flash 模拟 EEPROM 存储，用于掉电保存参数配置(如WiFi密码、设备ID、校准数据)。无需额外硬件，但擦写次数有限(约1万次)，适合少量数据低频更新场景",
        "stm32f103_flash_layout": {
            "总大小": "64 KB (STM32F103C8) / 128 KB (STM32F103ZE)",
            "页大小": "1 KB (每页1024字节, 共64/128页)",
            "起始地址": "0x08000000 (从这开始存放程序代码)",
            "EEPROM建议地址": "0x0800F000 (最后4KB, 页60~63, 不与程序空间冲突)",
        },
        "constraints": [
            ("擦除粒度", "只能按整页擦除(1KB), 不能单字节擦除"),
            ("先擦后写", "Flash位只能1→0, 要写新值必须先擦除整页(全1)"),
            ("擦写寿命", "~10,000 次 (不同温度有差异)"),
            ("写入要求", "必须是半字(16bit)对齐写入"),
            ("不能运行时读取正在写入的同一地址", "会导致CPU暂停(stall)"),
        ],
        "hal_apis": [
            "HAL_FLASH_Unlock()",                // 解锁Flash (写操作前必调!)
            "HAL_FLASH_Lock()",                  // 锁定Flash (写完后必调!)
            "HAL_FLASHEx_Erase()",               // 按页/按块擦除
            "HAL_FLASH_Program(FLASH_TYPEPROGRAM_HALFWORD, ...)",  // 半字编程(16bit)
            "HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, ...)",      // 字编程(32bit, F4以上)",
            "HAL_FLASH_OB_Launch()",             // 选项字节编程后重载",
        ],
        "code_example": '''
// ============================================================
// STM32 内部Flash模拟EEPROM — 封装好的读写函数
// 使用方法: Save_Params() 保存, Load_Params() 读取
// ============================================================

// 定义EEPROM区域 (STM32F103C8 最后4KB)
#define FLASH_EEPROM_ADDR    0x0800F000
#define FLASH_EEPROM_SIZE    (4 * 1024)  // 4KB
#define FLASH_PAGE_SIZE      1024        // F103每页1KB

// 要保存的参数结构体
typedef struct {
    uint32_t magic;           // 魔术字(验证数据有效性)
    float   voltage_offset;   // ADC电压偏移校准
    uint16_t device_id;       // 设备ID
    char    wifi_ssid[32];    // WiFi名称
    char    wifi_pass[32];    // WiFi密码
    uint8_t brightness;       // OLED亮度
    uint8_t alarm_threshold;  // 温度报警阈值
} DeviceParams_t;

static DeviceParams_t g_params;

// 写入参数到Flash
int Save_Params(void) {
    HAL_FLASH_Unlock();

    FLASH_EraseInitTypeDef erase_init;
    uint32_t page_error = 0;
    erase_init.TypeErase = FLASH_TYPEERASE_PAGES;
    erase_init.PageAddress = FLASH_EEPROM_ADDR;
    erase_init.NbPages = (FLASH_EEPROM_SIZE + FLASH_PAGE_SIZE - 1) / FLASH_PAGE_SIZE;

    if (HAL_FLASHEx_Erase(&erase_init, &page_error) != HAL_OK) {
        HAL_FLASH_Lock();
        return -1;  // 擦除失败
    }

    // 按半字(16bit)写入
    uint16_t *src = (uint16_t*)&g_params;
    uint32_t addr = FLASH_EEPROM_ADDR;
    uint32_t len = sizeof(DeviceParams_t);
    for (uint32_t i = 0; i < (len + 1) / 2; i++) {
        if (HAL_FLASH_Program(FLASH_TYPEPROGRAM_HALFWORD, addr, src[i]) != HAL_OK) {
            HAL_FLASH_Lock();
            return -2;  // 写入失败
        }
        addr += 2;
    }

    HAL_FLASH_Lock();
    return 0;  // 成功!
}

// 从Flash读取参数
int Load_Params(void) {
    DeviceParams_t *flash_data = (DeviceParams_t*)FLASH_EEPROM_ADDR;

    if (flash_data->magic != 0xDEADBEEF) {
        // 未找到有效数据 → 使用默认值
        memset(&g_params, 0, sizeof(g_params));
        g_params.magic = 0xDEADBEEF;
        g_params.voltage_offset = 0.0f;
        g_params.device_id = 1;
        strcpy(g_params.wifi_ssid, "Default");
        strcpy(g_params.wifi_pass, "password");
        g_params.brightness = 128;
        g_params.alarm_threshold = 30;
        Save_Params();  // 写入默认值
        return 1;  // 使用默认值
    }

    memcpy(&g_params, flash_data, sizeof(DeviceParams_t));
    return 0;  // 成功读取
}

// main()中使用
int main(void) {
    HAL_Init();
    Load_Params();  // 上电加载参数

    while (1) {
        // 正常运行...
        // 参数变更时调用 Save_Params()
        if (params_modified) {
            Save_Params();
            params_modified = 0;
        }
    }
}
''',
        "references": [
            {"source": "lamik/EEPROM-emulation-STM32F4-HAL", "url": "https://github.com/lamik/EEPROM-emulation-STM32F4-HAL", "note": "EEPROM模拟完整工程(F4系列)"},
            {"source": "CSDN: 基于HAL库的Flash模拟EEPROM", "url": "https://blog.csdn.net/qiezhihuai/article/details/52100798", "note": "Flash EEPROM模拟原理与代码"},
        ]
    },

    # ---- 21. RNG/CRC (随机数与循环冗余校验) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
