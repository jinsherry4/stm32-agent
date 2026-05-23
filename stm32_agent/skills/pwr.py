"""PWR - STM32 HAL Library Skill Module"""

__skill_name__ = "pwr"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SILL_DATA = {
"pwr": {
        "description": "STM32 电源管理，支持 Sleep/Stop/Standby 三种低功耗模式。适用于电池供电设备、降低功耗场景",
        "power_modes": [
            ("Sleep Mode", "睡眠模式 - CPU停止, 外设运行, 任意中断唤醒, 功耗~mA级"),
            ("Stop Mode", "停止模式 - 大部分时钟停止, SRAM数据保留, 外部中断/RTC闹钟唤醒, 功耗~μA级"),
            ("Stop0", "正常停止, 主稳压器开启"),
            ("Stop1", "低功耗稳压器开启"),
            ("Stop2", "部分SRAM关闭, 最低功耗停止模式"),
            ("Standby Mode", "待机模式 - 最低功耗(~μA), SRAM丢失, 仅RTC/备份域保留, WKUP引脚/RTC闹钟/NRST唤醒"),
            ("Shutdown Mode", "关断模式 - 最低功耗(~nA), BOR禁用, 仅WKUP/NRST复位唤醒"),
        ],
        "wakeup_sources": {
            "WKUP Pin": "PA0 (WKUP1), PC0/PC13等(视型号) - 上升沿触发",
            "RTC Alarm": "闹钟A/B中断唤醒",
            "RTC WakeUp Timer": "周期唤醒定时器",
            "LSE/CSS": "外部晶振故障检测唤醒",
            "Ethernet (仅Stop)": "以太网MAC帧唤醒",
        },
        "hal_apis": [
            "__HAL_RCC_PWR_CLK_ENABLE()",
            "HAL_PWR_EnableBkUpAccess()",
            "HAL_PWR_EnterSLEEPMode()",
            "HAL_PWR_EnterSTOPMode()",
            "HAL_PWR_EnterSTANDBYMode()",
            "HAL_PWR_DisableWakeUpPin()",
            "HAL_PWREx_EnableBatteryCharging()",
            "HAL_PWREx_EnableUltraLowPower()",
        ],
        "power_consumption_comparison": """
功耗对比 (以 STM32F103C8 为参考):
┌─────────────────┬──────────┬─────────────────────┐
│ 模式            │ 功耗     │ 恢复时间            │
├─────────────────┼──────────┼─────────────────────┤
│ Run (72MHz)     │ ~36 mA   │ -                   │
│ Sleep           │ ~12 mA   │ μs级 (中断直接恢复) │
│ Stop            │ ~20 μA   │ ms级 (HSI重启)      │
│ Standby         │ ~2 μA    │ 相当于 POR 复位     │
│ Shutdown        │ ~100 nA  │ 相当于 POR 复位     │
└─────────────────┴──────────┴─────────────────────┘
""",
        "code_example": '''
#include "main.h"

# ===== Sleep 模式示例 =====
void Enter_Sleep_Mode(void) {
    HAL_SuspendTick();                    # 挂起RTOS Tick(如有)
    HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    HAL_ResumeTick();                     # 恢复Tick
}

# ===== Stop 模式示例 (超低功耗) =====
void Enter_Stop_Mode(void) {
    # 配置唤醒源: PA0 上升沿唤醒
    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef gpio_init = {
        .Pin = GPIO_PIN_0,
        .Mode = GPIO_MODE_IT_RISING,
        .Pull = GPIO_NOPULL,
        .Speed = GPIO_SPEED_FREQ_LOW,
    };
    HAL_GPIO_Init(GPIOA, &gpio_init);

    HAL_PWR_EnterSTOPMode(PWR_REGULATOR_LP, PWR_STOPENTRY_WFI);
    # 唤醒后重新初始化系统时钟(HSI->HSE)
    SystemClock_Config();
}

# ===== Standby 模式示例 (最低功耗) =====
void Enter_Standby_Mode(void) {
    # 使能 WKUP 引脚 (PA0)
    HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);

    # 清除 WakeUp 标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);

    # 进入待机
    HAL_PWR_EnterSTANDBYMode();

    # ⚠️ 下面的代码不会执行! 待机唤醒相当于系统复位
    # 会从 main() 重新开始执行
    if (__HAL_PWR_GET_FLAG(PWR_FLAG_SB)) {
        # 检查是否从待机唤醒
        __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
        printf("Woke from Standby!\\\\n");
    }
}
''',
        "references": [
            {"source": "DeepBlueEmbedded", "url": "https:#deepbluembedded.com/stm32-stop-mode-examples-stop0-stop1-stop2/", "note": "Stop Mode 详细教程"},
            {"source": "ST官方文档", "note": "STM32 Reference Manual - PWR 章节"},
        ]
    },

    # ---- 12. WDG (看门狗) ----
}

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SILL_DATA
