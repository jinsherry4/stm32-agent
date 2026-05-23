"""WDG - STM32 HAL Library Skill Module"""

__skill_name__ = "wdg"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SILL_DATA = {
"wdg": {
        "description": "看门狗定时器，防止程序死锁/跑飞。分为独立看门狗(IWDG)和窗口看门狗(WDG)",
        "two_types": [
            ("IWDG (Independent Watchdog)", "独立看门狗 - 使用独立的 40kHz LSI 时钟源, 即使主时钟故障也能工作. 用于防止系统死锁, 超时未喂狗则复位系统."),
            ("WWDG (Window Watchdog)", "窗口看门狗 - 基于 APB1 时钟. 要求在指定时间窗口内喂狗(不能太早也不能太晚). 用于检测软件时序异常."),
        ],
        "iwdg_params": [
            ("Prescaler (/4,/8,/32,/64,/128,/256)", "LSI~40kHz, /256≈156Hz"),
            ("Reload Value (0-4095)", "超时 = (Prescaler/LSI) * Reload * 1000 ms"),
            ("Max Timeout (~26.2秒)", "/4095 @ /256"),
            ("Min Timeout (~98微秒)", "/1 @ /4"),
        ],
        "wwdg_params": [
            ("Prescaler (1/2/4/8)", "APB1分频"),
            ("Window Value", "早于此值喂狗=太早=复位!"),
            ("Counter Value (0x40-0x7F)", "减到0x3F=超时=复位!"),
        ],
        "hal_apis": [
            "HAL_IWDG_Init()",
            "HAL_IWDG_Refresh()",
            "HAL_WWDG_Init()",
            "HAL_WWDG_Refresh()",
            "HAL_WWDG_EARLYWakeupCallback()",
        ],
        "timeout_calculation": """
IWDG 超时计算公式:
  Timeout(ms) = (Prescaler_divisor / LSI_freq) × Reload_value × 1000

常用配置速查表 (LSI ≈ 40 kHz):

| Prescaler | Reload | 超时时间    | 适用场景           |
|-----------|--------|-------------|-------------------|
| /256      | 4095   | ~26.2 s     | 工业监控(慢响应)  |
| /256      | 2047   | ~13.1 s     | 通用              |
| /256      | 635    | ~4.0 s      | 通用              |
| /64       | 4095   | ~6.5 s      | 通用              |
| /64       | 635    | ~1.0 s      | 快速响应          |
| /4        | 4095   | ~102 ms     | 严格时序要求      |

⚠️ 推荐: 1~5 秒超时, 在主循环或 RTOS 任务中每 200~500ms 喂一次狗
""",
        "code_example": ''' ===== IWDG 独立看门狗示例 ===== */
/* CubeMX 配置: System Core -> IWDG -> Enable
 *   Prescaler: IWDG_PRESCALER_256
 *   Reload Counter: 635 (约4秒超时)
 */

void IWDG_Init_Example(void) {
    IWDG_HandleTypeDef hiwdg;
    hiwdg.Instance = IWDG;
    hiwdg.Init.Prescaler = IWDG_PRESCALER_256;
    hiwdg.Init.Reload = 635;  # ~4秒超时
    HAL_IWDG_Init(&hiwdg);
}

# 主循环中定期喂狗 (必须在超时时间内调用!)
while (1) {
    HAL_IWDG_Refresh(&hiwdg);  # 喂狗!

    # ... 业务逻辑 ...

    # 如果代码卡死在某处, 超过4秒没喂狗 -> 系统自动复位!
}

# ===== WWDG 窗口看门狗示例 ===== */
/*
 * CubeMX 配置: System Core -> WWDG -> Enable
 *   Prescaler: APB1/8
 *   Window Value: 64 (0x40)  ← 不能早于此时喂狗
 *   Counter: 127 (0x7F)      ← 不能晚于此时(减到0x3F=复位)
 *   窗口范围: counter从0x7F递减到0x40之间可以喂狗
 */
void HAL_WWDG_EarlyWakeupCallback(WWDG_HandleTypeDef* hwwdg) {
    # 太早喂狗了! 说明程序执行异常地快 -> 处理错误
    Error_Handler();
}
''',

        "references": [
            {"source": "engineer-ae3o/stm32-hal-library", "url": "https:#github.com/engineer-ae3o/stm32-hal-library", "note": "Watchdog HAL 实现"},
        ]
    },

    # ---- 13. EXTI (外部中断/事件控制器) ----
}

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SILL_DATA
