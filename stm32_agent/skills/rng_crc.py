"""RNG_CRC - STM32 HAL Library Skill Module"""

__skill_name__ = "rng_crc"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "rng_crc": {
        "description": "RNG 真随机数发生器 + CRC 硬件循环冗余校验单元。RNG用于加密密钥生成、安全令牌、随机延迟(防侧信道); CRC用于数据完整性校验、通信协议帧校验、Flash数据验证",
        "rng_specs": {
            "类型": "硬件真随机数 (基于模拟噪声)",
            "输出": "32位随机数每次",
            "速率": "≤ 24个时钟周期/32bit",
            "时钟": "AHB总线时钟(通常72MHz)",
            "错误检测": "种子错误检测 + 连续一致性检查",
        },
        "crc_specs": {
            "多项式": "CRC-32 (IEEE 802.3标准): 0x4C11DB7 (不可改)",
            "初始值": "0xFFFFFFFF (可自定义)",
            "输入/输出反转": "支持 (可配置)",
            "计算宽度": "8/16/32 bit",
            "用途": "数据校验、通信帧完整性、固件完整性验证",
        },
        "hal_apis": [
            // RNG APIs
            "__HAL_RCC_RNG_CLK_ENABLE()",
            "HAL_RNG_Init()",
            "HAL_RNG_GenerateRandomNumber()",
            "HAL_RNG_GenerateRandomNumber_IT()",  // 中断方式
            "HAL_RNG_ReadyCallback()",
            "HAL_RngReadyDataCallback()",
            // CRC APIs
            "__HAL_RCC_CRC_CLK_ENABLE()",
            "HAL_CRC_Init()",
            "HAL_CRC_Accumulate()",              // 累加计算(不断重置)
            "HAL_CRC_Calculate()",                // 单次计算
            "HAL_CRC_State(),
        ],
        "code_example": '''
// ===== RNG 真随机数 =====
// CubeMX 配置: Computing → RNG → Activated
//   NVIC: Enable RNG global interrupt (如用中断模式)

HAL_RNG_Init(&hrng);

// 方法1: 阻塞等待获取一个32位随机数
uint32_t random_num;
if (HAL_RNG_GenerateRandomNumber(&hrng, &random_num) == HAL_OK) {
    printf("Random: 0x%08X (%u)\\\\n", random_num, random_num);
}

// 方法2: 获取指定范围的随机数
uint32_t RandomRange(uint32_t min, uint32_t max) {
    uint32_t val;
    HAL_RNG_GenerateRandomNumber(&hrng, &val);
    return min + (val % (max - min + 1));
}

// 应用: 加密Token生成
uint8_t auth_token[16];
for (int i = 0; i < 4; i++) {
    uint32_t r;
    HAL_RNG_GenerateRandomNumber(&hrng, &r);
    auth_token[i*4+0] = (r >> 0) & 0xFF;
    auth_token[i*4+1] = (r >> 8) & 0xFF;
    auth_token[i*4+2] = (r >> 16) & 0xFF;
    auth_token[i*4+3] = (r >> 24) & 0xFF;
}
printf("Auth Token: ");
for (int i = 0; i < 16; i++) printf("%02X", auth_token[i]);
printf("\\\\n");

// ===== CRC 校验 =====
// CubeMX 配置: Computing → CRC → Activated
//   Polynomial Size: 32bit (CRC-32 IEEE标准)

// 单次计算: 计算一段数据的CRC32
uint8_t firmware_data[256];
// ... 填充数据 ...
uint32_t crc_result = HAL_CRC_Calculate(&hcrc, (uint32_t*)firmware_data, 256 / 4);
printf("CRC32 of firmware block: 0x%08X\\\\n", crc_result);

// 累加计算: 多段数据连续计算 (适合流式处理)
HAL_CRC_Calculate(&hcrc, (uint32_t*)data_part1, part1_size / 4);
uint32_t final_crc = HAL_CRC_Calculate(&hcrc, (uint32_t*)data_part2, part2_size / 4);

// 实际应用: 固件完整性验证
typedef struct {
    uint32_t version;
    uint32_t size;
    uint32_t crc32;       // 固件编译时预计算的CRC
} FirmwareHeader_t;

// Bootloader中验证App固件
int Verify_Firmware(uint32_t app_addr) {
    FirmwareHeader_t *header = (FirmwareHeader_t*)app_addr;
    uint32_t *firmware_start = (uint32_t*)(app_addr + sizeof(FirmwareHeader_t));
    uint32_t calc_crc = HAL_CRC_Calculate(&hcrc, firmware_start, header->size / 4);
    return (calc_crc == header->crc32) ? 0 : -1;  // 0=OK, -1=CRC不匹配
}
''',
        "references": [
            {"source": "CSDN: STM32 HAL硬件CRC校验与RNG真随机数", "url": "https://blog.csdn.net/Eyderoe/article/details/139967630", "note": "RNG+CRC完整示例"},
            {"source": "丢石头百科: STM32CubeMX教程16-RNG和CRC", "url": "https://wiki.diustou.com/cn/STM32CubeMX%E7%B3%BB%E5%88%97%E6%95%99%E7%A8%8B16:RNG%E5%92%8CCRC", "note": "CubeMX配置步骤详解"},
            {"source": "waveShare", "url": "https://www.waveshare.net/study/portal.php?mod=view&aid=655&_dsign=a61de21", "note": "RNG+CRC教程(中文版)"},
        ]
    },

    # ---- 22. IAP (在线应用编程 / OTA固件升级) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
