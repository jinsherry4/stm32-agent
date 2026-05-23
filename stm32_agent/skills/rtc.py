"""RTC - STM32 HAL Library Skill Module"""

__skill_name__ = "rtc"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SILL_DATA = {
"rtc": {
        "description": "RTC 实时时钟，由后备域供电(VBAT)，掉电后继续运行。提供日历功能(年月日时分秒)，配合 OLED 可做电子钟",
        "features": [
            ("32.768 kHz LSE", "外部低速晶振作为时钟源(精度高)"),
            ("LSI ~40 kHz", "内部低速振荡器(精度低但省去外部晶振)"),
            ("Alarm A/B", "两个独立闹钟中断源"),
            ("WakeUp Timer", "周期性唤醒定时器"),
            ("Backup Registers", "20个32位备份寄存器(掉电不丢失)"),
            ("Timestamp", "事件时间戳记录"),
        ],
        "hal_apis": [
            "__HAL_RCC_RTC_CLK_ENABLE()",
            "HAL_RTC_Init()",
            "HAL_RTC_SetTime()",
            "HAL_RTC_SetDate()",
            "HAL_RTC_GetTime()",
            "HAL_RTC_GetDate()",
            "HAL_RTC_SetAlarm()",
            "HAL_RTC_AlarmAEventCallback()",
            "HAL_RTCEx_SetWakeUpTimer()",
            "HAL_RTCEx_WakeUpTimerEventCallback()",
            "HAL_RTCEx_BKUPWrite()",
            "HAL_RTCEx_BKUPRead()",
        ],
        "cube_mx_critical_config": """
CubeMX 关键配置步骤:
  1. RCC -> Low Speed Clock(LSE) -> Crystal/Ceramic Resonator (32.768kHz)
  2. RTC Clock Source -> LSE
  3. Enable Clock Activation (激活RTC)
  4. RTC -> Activate Calendar (激活日历)
  5. NVIC -> RTC global interrupt / RTC Alarm interrupt -> Enable
  6. 必须设置 PWR_CR_DBP 位才能写入RTC寄存器!
""",

        "code_example": '''
#include "rtc.h"

RTC_TimeTypeDef sTime = {0};
RTC_DateTypeDef sDate = {0};

# 设置时间: 14:30:00
sTime.Hours = 14; sTime.Minutes = 30; sTime.Seconds = 0;
sTime.DayLightSaving = RTC_DAYLIGHTSAVING_NONE;
sTime.StoreOperation = RTC_STOREOPERATION_RESET;
HAL_RTC_SetTime(&hrtc, &sTime, RTC_FORMAT_BIN);

# 设置日期: 2026-05-23 (周五)
sDate.Year = 26; sDate.Month = RTC_MONTH_MAY; sDate.Date = 23;
sDate.WeekDay = RTC_WEEKDAY_FRIDAY;
HAL_RTC_SetDate(&hrtc, &sDate, RTC_FORMAT_BIN);

# 读取当前时间并显示在 OLED
void Show_Time_On_OLED(void) {
    RTC_TimeTypeDef currentTime;
    RTC_DateTypeDef currentDate;
    HAL_RTC_GetTime(&hrtc, &currentTime, RTC_FORMAT_BIN);  # 必须先GetTime!
    HAL_RTC_GetDate(&hrtc, &currentDate, RTC_FORMAT_BIN);  # 再GetDate!

    char time_str[16];
    sprintf(time_str, "%02d:%02d:%02d",
            currentTime.Hours, currentTime.Minutes, currentTime.Seconds);
    ssd1306_SetCursor(24, 0);
    ssd1306_WriteString(time_str, Font_11x18, White);
    ssd1306_UpdateScreen(&hi2c1);
}

# 闹钟中断回调
void HAL_RTC_AlarmAEventCallback(RTC_HandleTypeDef *hrtc) {
    printf("Alarm triggered! Wake up!\\\\n");
}
''',
        "references": [
            {"source": "野火 STM32 HAL库开发实战", "url": "https:#doc.embedfire.com/mcu/stm32/f103mini/hal/zh/latest/book/RTC.html"},
            {"source": "知乎: STM32 HAL库中的 RTC", "url": "https:#blog.csdn.net/qq_39725309/article/details/149944784"},
        ]
    },

    # ---- 9. OLED (SSD1306 显示屏) ----
}

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SILL_DATA
