"""USB - STM32 HAL Library Skill Module"""

__skill_name__ = "usb"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "usb": {
        "description": "USB Device 模式，实现 CDC (Communication Device Class) 虚拟串口(VCP)、HID设备(鼠标/键盘)、MSC大容量存储等。STM32F103C8T6需使用USB Device库(非USB OTG)",
        "usb_classes": [
            ("CDC (VCP)", "虚拟串口 — 替代USART, 电脑无需额外硬件, 速度可达115200+" ),
            ("HID", "人机接口设备 — 键盘/鼠标/游戏手柄, 即插即用免驱动" ),
            ("MSC", "大容量存储 — 模拟U盘" ),
            ("Audio", "音频设备 — USB声卡/MIC" ),
            ("DFU", "固件升级 — Device Firmware Upgrade模式" ),
        ],
        "hardware_requirement": "STM32F103: PA11(DM), PA12(DP) + DP上1.5K电阻到3.3V (多数Blue Pill已集成)",
        "hal_apis": [
            "USBD_Init()",
            "USBD_RegisterClass()",
            "USBD_Start()",
            "USBD_Stop()",
            "CDC_Transmit_FS()",
            "CDC_Receive_FS()",
            "USBD_CDC_SetTxBuffer()",
            "USBD_CDC_ReceivePacket()",
        ],
        "middleware_files": [
            "usbd_core.c/h — USB核心协议栈",
            "usbd_cdc.c/h — CDC类实现",
            "usbd_cdc_if.c/h — 用户回调接口(必须修改此文件!)",
            "usbd_desc.c/h — 设备描述符(VID/PID/字符串)",
            "stm32f1xx_hal_pcd.c/h — PCD底层驱动",
        ],
        "code_example": '''
// CubeMX 配置:
//   Connectivity → USB → DEVICE (FS) → Class For FS IP: Communication Device Class (Virtual Port Com)
//   Clock Configuration: USB必须48MHz! (PLL设置: HSE→PLL→USBCLK=48MHz)
//   Middleware → USB_DEVICE → Enabled
//   NVIC: Enable USB low priority interrupt / USB high priority interrupt

// === 关键修改文件: USB_DEVICE/App/usbd_cdc_if.c ===

// 1. 数据接收回调 (电脑发数据给STM32时自动调用)
static int8_t CDC_Receive_FS(uint8_t* Buf, uint32_t *Len) {
    // Buf = 收到的数据指针, *Len = 数据长度
    USER_BUFFER[0] = '\\\\0';
    memcpy(USER_BUFFER, Buf, (*Len < 64) ? *Len : 63);
    cmd_ready = 1;
    return USBD_OK;
}

// 2. 发送数据到电脑 (自定义封装函数)
void USB_SendString(char *str) {
    USBD_CDC_SetTxBuffer(&hUsbDeviceFS, (uint8_t*)str, strlen(str));
    USBD_CDC_TransmitPacket(&hUsbDeviceFS);
}

// main.c 中的用法 (与USART几乎一致!)
uint8_t USER_BUFFER[128];
volatile uint8_t cmd_ready = 0;

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USB_DEVICE_Init();  // USB初始化(自动)

    while (1) {
        if (cmd_ready) {
            printf("USB RX: %s\\\\n", USER_BUFFER);  // 通过USB-CDC发送回显
            cmd_ready = 0;
        }

        // 定期上报数据
        static uint32_t last_report = 0;
        if (HAL_GetTick() - last_report >= 1000) {
            char msg[64];
            sprintf(msg, "Temp: %.1f C, Uptime: %lu\\\\n", read_temp(), HAL_GetTick());
            USB_SendString(msg);
            last_report = HAL_GetTick();
        }
    }
}
''',
        "references": [
            {"source": "controllerstech/STM32-HAL (USB CDC)", "url": "https://github.com/controllerstech/STM32-HAL/blob/master/usb/cdc_vcp/README.md", "note": "USB CDC VCP 完整教程系列"},
            {"source": "DeepBlueEmbedded", "url": "https://deepbluembedded.com/stm32-usb-cdc-virtual-com-port-vcp-examples/", "note": "USB VCP 配置步骤详解"},
            {"source": "CSDN: STM32F103 USB CDC虚拟串口移植", "url": "https://blog.csdn.net/qq_54543879/article/details/145930958", "note": "Blue Pill USB CDC 移植实战"},
            {"source": "STMicroelectronics", "url": "https://github.com/STMicroelectronics/stm32-mw-openbl", "note": "官方Open Bootloader(IAP over USB)"},
        ]
    },

    # ---- 17. CAN 总线 ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
