"""RNG_CRC - STM32 HAL Library Skill Module"""

__skill_name__ = "rng_crc"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SKILL_DATA = {
    "rng_crc": {
        "description": "RNG 真随机数发生器 + CRC 硬件循环冗余校验单元。RNG用于加密密钥生成、安全令牌、随机延迟(防侧信道); CRC用于数据完整性校验、通信协议帧校验、Flash数据验证",
        "rng_specs": {
            "类型": "硬件真随机数 (基于模拟噪声)",
            "输出": "32位随机数每次",
            "速率": "<= 24个时钟周期/32bit",
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
            "__HAL_RCC_RNG_CLK_ENABLE()",
            "HAL_RNG_Init()",
            "HAL_RNG_GenerateRandomNumber()",
            "HAL_RNG_GenerateRandomNumber_IT()",
            "HAL_RNG_ReadyCallback()",
            "HAL_RngReadyDataCallback()",
            "__HAL_RCC_CRC_CLK_ENABLE()",
            "HAL_CRC_Init()",
            "HAL_CRC_Accumulate()",
            "HAL_CRC_Calculate()",
            "HAL_CRC_State()",
        ],
        "code_example": """
# ===== RNG 真随机数 =====
# CubeMX 配置: Computing -> RNG -> Activated

HAL_RNG_Init(&hrng);

# 方法1: 阻塞等待获取一个32位随机数
uint32_t random_num;
if (HAL_RNG_GenerateRandomNumber(&hrng, &random_num) == HAL_OK) {
    printf("Random: 0x%08X (%u)\\n", random_num, random_num);
}

# 方法2: 获取指定范围的随机数
uint32_t RandomRange(uint32_t min, uint32_t max) {
    uint32_t val;
    HAL_RNG_GenerateRandomNumber(&hrng, &val);
    return min + (val % (max - min + 1));
}
""",
        "references": [
            {"source": "STM32 Reference Manual", "url": "", "note": "RNG/CRC 寄存器说明"},
        ]
    }
}


def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SKILL_DATA
