"""IAP - STM32 HAL Library Skill Module"""

__skill_name__ = "iap"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "iap": {
        "description": "IAP In-Application Programming 在线应用编程，实现通过串口/USB/CAN等接口远程升级固件。由Bootloader负责接收新固件并写入Flash，然后跳转到App执行。适用于产品发布后的OTA升级、远程维护",
        "architecture": """
┌─────────────────────────────────────┐
│         Flash 地址布局 (STM32F103C8)  │
├──────────┬──────────────────────────┤
│ 0x08000000│ Bootloader (8~16KB)     │ ← 上电首先执行
│          │   - 检查升级标志位        │
│          │   - 接收固件数据          │
│          │   - 写入Flash             │
│          │   - 跳转到App             │
├──────────┼──────────────────────────┤
│ 0x08002000│ App程序区 (48~56KB)      │ ← 用户应用程序
│          │   - VECTOR_TABLE偏移     │
│          │   - 正常业务逻辑          │
│          │   - 触发升级请求          │
├──────────┼──────────────────────────┤
│ 0x0800E000│ 备份区 / 新固件缓存      │ ← 存放待写入的新固件
│ 0x0800FFFF│ (64KB total)            │
└──────────┴──────────────────────────┘

升级流程:
  App请求升级 → 设置标志位+复位 → Bootloader检测标志
  → 通过Ymodem/Xmodem接收新固件 → 写入备份区/App区
  → 清除标志 → 跳转到App执行
""",
        "transport_protocols": [
            ("Ymodem", "串口IAP最常用的协议, 带CRC校验, 支持断点续传(部分终端)"),
            ("Xmodem", "简化版Ymodem, 协议更简单, 128字节/包"),
            ("自定义协议", "自己定义帧头+长度+数据+CRC, 灵活但需自行实现"),
            ("USB DFU", "通过USB进行固件升级, 速度快, 需要USB Device库"),
            ("CAN Bootloader", "汽车电子常用, 工业现场CAN网络升级"),
        ],
        "key_techniques": [
            ("VECTOR_TABLE 重映射", "App的向量表不在0x08000000, 必须用 SCB->VTOR 重映射"),
            ("Bootloader/App 分离编译", "两个工程独立编译, 各自有自己的链接脚本(.ld)"),
            ("中断向量表正确性", "App的向量表第一项必须是新栈指针, 第二项是Reset_Handler地址"),
            ("跳转前清理", "关闭所有外设中断, 禁用SysTick, 恢复默认主堆栈指针"),
            ("标志位约定", "RAM特定地址或Backup Register作为'需要升级'的标志"),
        ],
        "hal_apis": [
            "HAL_FLASH_Unlock() / HAL_FLASH_Lock()",
            "HAL_FLASHEx_Erase()",
            "HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD/HALFWORD, ...)",
            "__disable_irq() / __enable_irq()",
            "__set_MSP()",                    // 设置主栈指针
            "__set_CONTROL(0)",               // 切换到线程模式
            "((void(*)())(*((uint32_t*)(APP_ADDR + 4)))())",  // 函数指针跳转
            "SCB->VTOR = FLASH_BASE | VECT_OFFSET;",          // 向量表重映射
        ],
        "code_example": '''
// ============================================================
// Bootloader 部分 (独立工程, 编译地址从 0x08000000 开始)
// 链接脚本: FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 16K
// ============================================================

#define APP_ADDR         0x08002000    // App起始地址
#define UPGRADE_FLAG_ADDR 0x20004FFC   // RAM中的标志位(SRAM末尾)
#define UPGRADE_MAGIC     0xDEADBEEF   // 升级魔术字

// Bootloader main函数
int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();       // LED指示状态
    MX_USART1_UART_Init(); // Ymodem传输通道

    // 检查是否有升级请求
    uint32_t flag = *((volatile uint32_t*)UPGRADE_FLAG_ADDR);

    if (flag == UPGRADE_MAGIC) {
        // 进入升级模式
        printf("=== Upgrade Mode ===\\\\n");
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_8, GPIO_PIN_SET);  // LED常亮=升级模式

        // Ymodem 接收固件 (使用STM32CubeIDE自带Ymodem组件)
        // 或自己实现简单Xmodem协议
        uint8_t rx_buffer[1024];
        Ymodem_Receive(APP_ADDR, rx_buffer, sizeof(rx_buffer));

        // 接收完成后清除标志
        *((volatile uint32_t*)UPGRADE_FLAG_ADDR) = 0;
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_8, GPIO_PIN_RESET);
    }

    // 跳转到App执行
    Jump_To_App(APP_ADDR);
}

// 跳转到App的关键函数
void Jump_To_App(uint32_t app_addr) {
    typedef  void (*pFunction)(void);
    pFunction JumpToApplication;

    // 1. 检查App地址的栈顶指针是否合法 (应在SRAM范围内)
    uint32_t stack_ptr = *(volatile uint32_t*)app_addr;
    if ((stack_ptr & 0x2FFE0000) == 0x20000000) {
        printf("Jumping to App at 0x%X\\\\n", app_addr);

        // 2. 关闭所有中断
        __disable_irq();

        // 3. 关闭SysTick
        SysTick->CTRL = 0;

        // 4. 关闭所有外设时钟 (可选, 更彻底)
        __HAL_RCC_GPIOA_CLK_DISABLE();
        __HAL_RCC_GPIOB_CLK_DISABLE();
        __HAL_RCC_USART1_CLK_DISABLE();

        // 5. 设置主栈指针(App的栈顶)
        __set_MSP(stack_ptr);

        // 6. 跳转到App的 Reset_Handler
        JumpToApplication = (pFunction)(*(__IO uint32_t*)(app_addr + 4));
        JumpToApplication();

        // 如果返回了说明跳转失败
        while (1) { HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_8); HAL_Delay(200); }
    } else {
        printf("Invalid App! Stack ptr=0x%X\\\\n", stack_ptr);
        while (1) { /* LED闪烁提示 */ }
    }
}


// ============================================================
// App 部分 (独立工程, 编译地址从 0x08002000 开始)
// 链接脚本: FLASH (rx)  : ORIGIN = 0x08002000, LENGTH = 48K
// SRAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 16K (避开末尾4B给Bootloader用)
// ============================================================

// system_stm32f1xx.c 中修改 VECTOR_ADDRESS (或在main开头):
int main(void) {
    HAL_Init();
    SystemClock_Config();

    // ★★★ 关键! 重映射中断向量表到App的实际地址 ★★★
    SCB->VTOR = FLASH_BASE | 0x20000;  // APP_ADDR - 0x08000000 = 0x20000

    MX_GPIO_Init();
    MX_USART1_UART_Init();
    // ...

    // 触发升级 (例如收到"UPDATE"命令时)
    void Trigger_Upgrade(void) {
        *((volatile uint32_t*)UPGRADE_FLAG_ADDR) = UPGRADE_MAGIC;
        HAL_Delay(100);
        NVIC_SystemReset();  // 复位 → Bootloader接管
    }
}
''',
        "references": [
            {"source": "CSDN: 串口IAP实现bootloader + app + qt上位机", "url": "https://blog.csdn.net/qq_39328844/article/details/153266790", "note": "完整的IAP方案(2026年最新)"},
            {"source": "腾讯云: 详解STM32在线IAP升级", "url": "https://cloud.tencent.com/developer/article/2224688", "note": "IAP原理+分区+流程图详解"},
            {"source": "博客园: STM32 IAP BootLoader", "url": "https://www.cnblogs.com/Wangzx000/p/18583065", "note": "BootLoader实现指南"},
            {"source": "技术站: HAL库实现自己的BootLoader", "url": "https://jishuzhan.net/article/1819327870636396546", "note": "BootLoader从入门到实践"},
            {"source": "STMicroelectronics: Open Bootloader", "url": "https://github.com/STMicroelectronics/stm32-mw-openbl", "note": "官方开源IAP Bootloader"},
        ]
    },
}


# ============================================================
# STM32 Agent 核心 - 技能匹配与路由
# ============================================================

class STM32Agent:
    """
    STM32 开发智能助手 Agent
    - 维护所有外设模块的知识库(Skill Registry)
    - 根据用户查询匹配相关 Skill
    - 提供 CubeMX 配置指导、代码模板、常见问题排查
    """

    def __init__(self):
        self.knowledge_base = STM32_KNOWLEDGE_BASE
        self.skill_registry: list[Skill] = []
        self._build_skill_registry()

    def _build_skill_registry(self):
        """从知识库构建技能注册表"""
        for key, info in self.knowledge_base.items():
            skill = Skill(
                name=key,
                description=info.get("description", ""),
                category=self._infer_category(key),
                peripheral=key.upper(),
                hal_apis=info.get("hal_apis", []),
                cube_mx_config=info.get("cube_mx_config", {}),
                code_template=info.get("code_example", ""),
                examples=info.get("examples", []),
                references=info.get("references", []),
                prerequisites=info.get("prerequisites", []),
            )
            self.skill_registry.append(skill)

    def _infer_category(self, skill_name: str) -> str:
        mapping = {
            "gpio": "digital",
            "usart": "comm",
            "spi": "comm",
            "i2c": "comm",
            "adc": "analog",
            "pwm": "timing",
            "dma": "timing",
            "rtc": "timing",
            "oled": "display",
            "w25q64": "storage",
            "pwr": "power",
            "wdg": "power",
            # ---- 扩展模块 (v2.0) ----
            "exti": "digital",
            "tim_basic": "timing",
            "encoder": "timing",
            "usb": "comm",
            "can": "comm",
            "sdio": "storage",
            "dac": "analog",
            "flash_eeprom": "storage",
            "rng_crc": "security",
            "iap": "system",
        }
        return mapping.get(skill_name, "other")

    def list_skills(self, category: str | None = None) -> list[Skill]:
        """列出所有可用技能，可按分类过滤"""
        if category:
            return [s for s in self.skill_registry if s.category == category]
        return self.skill_registry

    def get_skill(self, name: str) -> Skill | None:
        """按名称获取单个技能"""
        for s in self.skill_registry:
            if s.name == name:
                return s
        return None

    def query(self, question: str) -> str:
        """
        用户自然语言查询 → 匹配技能 → 返回详细回答

        支持的查询类型:
        - "如何配置 GPIO?" → 返回 GPIO 技能详情
        - "USART 中断接收怎么做" → 匹配 usart + 中断关键词
        - "帮我生成 PWM 代码" → 返回 PWM 代码模板
        - "DMA 和 ADC 怎么配合" → 返回 DMA+ADC 联合用法
        """
        q_lower = question.lower()

        # 关键词 → Skill 映射
        keyword_map = {
            "gpio": ["gpio", "led", "引脚", "按键", "输入输出", "output", "input", "toggle"],
            "usart": ["usart", "uart", "串口", "serial", "printf", "接收", "发送", "rx", "tx", "中断接收"],
            "spi": ["spi", "flash", "w25q", "w25", "mosi", "miso", "sck"],
            "i2c": ["i2c", "iic", "oled", "mpu6050", "aht20", "eeprom", "scl", "sda", "传感器"],
            "adc": ["adc", "模数", "analog", "采样", "电压", "temperature", "温度", "电位器", "pot"],
            "pwm": ["pwm", "脉宽", "调光", "舵机", "servo", "motor", "电机", "频率", "占空比", "brightness"],
            "dma": ["dma", "直接存储器", "搬运", "批量", "高速传输", "buffer", "循环"],
            "rtc": ["rtc", "实时时钟", "clock", "calendar", "闹钟", "alarm", "date", "time", "日期", "时间", "wake"],
            "oled": ["oled", "显示屏", "显示", "屏幕", "ssd1306", "lcd", "字体", "汉字"],
            "w25q64": ["w25q64", "w25q", "flash", "存储", "字库", "擦除", "扇区", "page program"],
            "pwr": ["pwr", "电源", "sleep", "stop", "standby", "低功耗", "shutdown", "wake", "唤醒", "vbat", "backup"],
            "wdg": ["wdg", "watchdog", "看门狗", "iwdg", "wwdg", "喂狗", "reset", "复位", "死锁"],
            # ---- 扩展模块 (v2.0) ----
            "exti": ["exti", "外部中断", "中断线", "边沿触发", "上升沿", "下降沿", "按键中断", "irq", "nvic", "事件线"],
            "tim_basic": ["tim", "timer", "定时器", "定时", "计数", "中断定时", "输入捕获", "输出比较", "pwm频率", "时基"],
            "encoder": ["encoder", "编码器", "正交", "电机测速", "旋转方向", "脉冲计数", "quadrature"],
            "usb": ["usb", "cdc", "vcp", "虚拟串口", "usb设备", "枚举", "descriptor", "端点"],
            "can": ["can", "can总线", "控制器局域网", "报文", "过滤器", "mcp2551", "id", "仲裁"],
            "sdio": ["sdio", "sd卡", "sdcard", "fatfs", "文件系统", "f_mount", "f_open", "读写文件", "存储卡"],
            "dac": ["dac", "数模", "波形", "正弦波", "三角波", "音频", "tone", "模拟输出", "sine"],
            "flash_eeprom": ["flash", "eeprom", "参数保存", "数据持久化", "页擦除", "写入flash", "掉电保存", "扇区"],
            "rng_crc": ["rng", "随机数", "crc", "校验", "checksum", "数据完整性", "真随机", "硬件随机"],
            "iap": ["iap", "bootloader", "升级", "ota", "在线编程", "跳转应用", "ymodem", "引导加载", "固件升级"],
        }

        # 匹配得分
        scores = {}
        for skill_name, keywords in keyword_map.items():
            score = sum(1 for kw in keywords if kw in q_lower)
            if score > 0:
                scores[skill_name] = score

        if not scores:
            return self._format_no_match_response(question)

        # 按得分排序，取最佳匹配
        best_match = max(scores, key=scores.get)

        # 如果涉及多模块组合查询
        if len(scores) > 1 and sum(1 for v in scores.values() if v > 0) >= 2:
            return self._format_combined_response(question, scores)

        return self._format_single_skill_response(best_match)

    def _format_single_skill_response(self, skill_name: str) -> str:
        """格式化单个技能的回答"""
        info = self.knowledge_base.get(skill_name, {})
        skill = self.get_skill(skill_name)
        if not skill:
            return f"[Error] Skill '{skill_name}' not found"

        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"  STM32 {skill.peripheral} - {info.get('description', '')}")
        lines.append(f"{'='*60}")
        lines.append("")

        # HAL APIs
        if skill.hal_apis:
            lines.append("[核心 HAL API]")
            lines.append("-" * 40)
            for api in skill.hal_apis:
                lines.append(f"  • {api}")
            lines.append("")

        # 代码模板
        if skill.code_template:
            lines.append("[代码模板]")
            lines.append("-" * 40)
            lines.append(skill.code_template.strip())
            lines.append("")

        # 参考资料
        if skill.references:
            lines.append("[参考资料 (GitHub)]")
            lines.append("-" * 40)
            for ref in skill.references:
                source = ref.get("source", "")
                url = ref.get("url", "")
                note = ref.get("note", "")
                line = f"  • {source}"
                if note:
                    line += f" — {note}"
                if url:
                    line += f"\n    {url}"
                lines.append(line)
            lines.append("")

        return "\n".join(lines)

    def _format_combined_response(self, question: str, scores: dict) -> str:
        """格式化多技能组合查询的回答"""
        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"  组合查询: {question}")
        lines.append(f"  涉及模块: {', '.join(sorted(scores.keys(), key=lambda k: scores[k], reverse=True))}")
        lines.append(f"{'='*60}")

        for skill_name in sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[:3]:
            info = self.knowledge_base.get(skill_name, {})
            lines.append(f"\n--- {skill_name.upper()} ---")
            lines.append(info.get("description", ""))
            if info.get("code_example"):
                # 只显示代码模板的前15行(摘要)
                code_lines = info["code_example"].strip().split("\n")[:12]
                lines.append("\n[代码摘要]")
                lines.extend(f"  {line}" for line in code_lines)
                lines.append("  ... (完整代码请单独查询 '{skill_name}')")
            lines.append("")

        return "\n".join(lines)

    def _format_no_match_response(self, question: str) -> str:
        skills_list = ", ".join(s.name for s in self.skill_registry)
        return (
            f"[未找到匹配]\n\n"
            f"查询: \"{question}\"\n\n"
            f"支持的技能列表:\n{skills_list}\n\n"
            f"你可以尝试:\n"
            f"  • agent.query('如何配置 GPIO 输出')\n"
            f"  • agent.query('USART 中断接收怎么做')\n"
            f"  • agent.query('ADC + DMA 多通道采样')\n"
            f"  • agent.query('OLED 显示中文')"
        )

    def get_cube_mx_guide(self, skill_name: str) -> str:
        """获取 CubeMX 配置向导"""
        info = self.knowledge_base.get(skill_name, {})
        guides = {
            "gpio": (
                "1. 打开 Pinout & Configuration\n"
                "2. System Core → GPIO → 选择引脚\n"
                "3. 设置:\n"
                "   - GPIO mode: Output Push Pull (LED)\n"
                "   - GPIO Pull-up/Pull-down: No pull-up\n"
                "   - Maximum output speed: Low/Medium/High/Very High\n"
                "4. 生成代码后调用 HAL_GPIO_xxx() 函数\n"
                "提示: 绿色=Output, 黄色=Input, 深绿=Alternate Function"
            ),
            "usart": (
                "1. Connectivity → USART1 → Mode: Asynchronous\n"
                "2. Parameter Settings:\n"
                "   - Baud Rate: 9600 (常用)\n"
                "   - Word Length: 8 Bits\n"
                "   - Parity: None\n"
                "   - Stop Bits: 1\n"
                "3. NVIC Settings → 启用 USART1 global interrupt\n"
                "4. GPIO: TX(PA9) RX(PA10) 自动配置\n"
                "5. 生成代码后在 main.c 的 USER CODE 区域添加回调函数"
            ),
            "adc": (
                "1. Analog → ADC1 → 勾选 IN0-IN15 (根据使用的引脚)\n"
                "2. Parameter Settings:\n"
                "   - Resolution: 12 bits\n"
                "   - Data Alignment: Right alignment\n"
                "   - Scan Conversion Mode: Disable (单通道) / Enable (多通道)\n"
                "3. Rank 配置: 每个通道分配一个 Rank (优先级)\n"
                "4. Sampling Time: 推荐 55.5 Cycles (平衡精度与速度)\n"
                "5. 如需定时触发: Timers → 选定时器 → Trigger Source Selection → Event Out\n"
                "6. NVIC: 启用 ADC1&EXTI interrupt (中断模式)"
            ),
            "pwm": (
                "1. Timers → 选择定时器 (如 TIM4)\n"
                "2. Channel1 → PWM Generation CH1\n"
                "3. Parameter Settings:\n"
                "   - Prescaler (PSC): 83 (84MHz→1MHz)\n"
                "   - Counter Period (ARR): 999 (1MHz→1kHz PWM频率)\n"
                "   - Pulse (CCR): 500 (50%占空比)\n"
                "4. GPIO 自动配置为 AF (复用功能)\n"
                "5. 代码中调用 HAL_TIM_PWM_Start()\n"
                "6. 运行时用 __HAL_TIM_SET_COMPARE() 调节占空比"
            ),
            "rtc": (
                "1. RCC → Low Speed Clock (LSE) → Crystal/Ceramic Resonator (32.768kHz)\n"
                "2. RCC → RTC Clock Sources → Select → LSE\n"
                "3. 勾选 'Activate clock security system' 和 'Activate RTC'\n"
                "4. RTC → Activate Calendar\n"
                "5. Date/Time 初始值 (编译时会写入初始时间)\n"
                "6. Activation → Init/Deinit → Check by default\n"
                "7. NVIC: 启用 RTC global / RTC Alarm interrupt\n"
                "8. ⚠️ 代码中必须先 HAL_RTC_GetTime() 再 HAL_RTC_GetDate()"
            ),
            # ---- 扩展模块 CubeMX 向导 (v2.0) ----
            "exti": (
                "1. System Core → GPIO → 选择引脚 (如 PA0)\n"
                "2. GPIO mode: External Interrupt Mode with Rising edge (上升沿触发)\n"
                "   或 Falling edge / Rising/Falling (双边沿, 用于按键消抖)\n"
                "3. System Core → NVIC → 找到对应 EXTI IRQ:\n"
                "   - PA0~PB0→EXTI0_IRQn | PA5~PB5→EXTI9_5_IRQn(共享) | PA10~PB10→EXTI15_10_IRQn(共享)\n"
                "4. 勾选 Enable + 设置优先级\n"
                "5. 代码中实现 HAL_GPIO_EXTI_Callback() 或 EXTIx_IRQHandler()\n"
                "提示: 同一Pin号(Pin0/Pin1/...)的不同端口共用一条EXTI线"
            ),
            "tim_basic": (
                "1. Timers → 选择定时器 (基本定时器TIM6/TIM7 / 通用TIM2-5):\n"
                "2. 时基参数:\n"
                "   - Prescaler (PSC): 分频系数 (如 83, 84MHz→1MHz)\n"
                "   - Counter Period (ARR): 自动重载值 (如 999, 1MHz→1ms定时)\n"
                "3. 中断模式: NVIC Settings → 启用 TIMx global interrupt\n"
                "4. PWM 模式: Channel → PWM Generation CHx, 设 Pulse(占空比)\n"
                "5. 输入捕获: Channel → Input Capture direct mode/Rising\n"
                "6. 输出比较: Channel → Output Compare CHx / PWM Generation\n"
                "7. 定时公式: T = (PSC+1)*(ARR+1) / f_clk"
            ),
            "encoder": (
                "1. Timers → 选择带编码器接口的定时器 (TIM2/TIM3/TIM4 推荐)\n"
                "2. Combined Channels → Encoder Mode (Encoder Mode TI1 and TI2 为正交编码)\n"
                "3. Counter Settings:\n"
                "   - Counter Period: 设为最大 (如 65535, 16位计数范围)\n"
                "   - Encoder mode: Encoder Mode TI1 and TI2 (双边沿计数×4精度)\n"
                "4. Parameter Settings:\n"
                "   - Counter Mode: Up (正转计数增加, 反转减少)\n"
                "   - Encoder Polarity: Rise / Both Edge (双边沿×4分辨率)\n"
                "5. GPIO: CH1/CH2 引脚自动配置为 AF (如 PA6/PA7 for TIM3)\n"
                "6. 代码: __HAL_TIM_ENABLE_IT(&htimx, TIM_SOURCE_UPDATE); HAL_TIM_Encoder_Start()"
            ),
            "usb": (
                "1. Connectivity → USB → Device (FS) → 勾选 Activate\n"
                "2. Middleware → USB_DEVICE → Class For FS IP: Communication Device Class (Virtual Port Com)\n"
                "3. Clock Configuration: USB 需要精确 48MHz 时钟 (RCC配置48MHz USB时钟源)\n"
                "4. USB 中断: NVIC → 启用 USB_HP_CAN1_TX_IRQn / USB_LP_CAN1_RX0_IRQn\n"
                "5. GPIO: DM(PA11), DP(PA12) 自动配置\n"
                "6. 生成代码后关键文件:\n"
                "   - usbd_cdc_if.c/h: 用户回调 (接收发送数据在这里修改)\n"
                "   - usb_device.c: 初始化函数 MX_USB_DEVICE_Init()\n"
                "7. PC端安装 STM32 Virtual COM Port 驱动 (ST官网下载)"
            ),
            "can": (
                "1. Connectivity → CAN → Master Mode (或 Loopback 测试用回环)\n"
                "2. Parameter Settings:\n"
                "   - Prescaler (for Time Quantum): 如 8 (42MHz/8=5.25MHz tq)\n"
                "   - Time Quanta in Bit Segment 1: 13 (TS1)\n"
                "   - Time Quanta in Bit Segment 2: 2 (TS2)\n"
                "   - ReSynchronization Jump Width: 1 (SJW)\n"
                "   → 波特率 = 42MHz / 8*(13+2+1) = 350Kbps (调整参数改变波特率)\n"
                "3. CAN Filter: 配置 ID 过滤 (标准ID 11位 / 扩展ID 29位)\n"
                "4. NVIC: 启用 USB_HP/CAN_TX / USB_LP/CAN_RX0 中断\n"
                "5. GPIO: TX(PB12), RX(PB11) 自动配置, 外接 MCP2551 收发器\n"
                "6. 代码: HAL_CAN_Start(), HAL_CAN_AddTxMessage(), HAL_CAN_GetRxMessage()"
            ),
            "sdio": (
                "1. Connectivity → SDIO → 勾选 Activate\n"
                "2. Parameter Settings:\n"
                "   - Clock Divide: SDIOCLK divide bypass (尽量高速) 或 SDIO_CK_DIV0~DIV255\n"
                "   - Data Bus Width: 4-bit (推荐, 比1位快4倍)\n"
                "   - Clock Edge: Rising\n"
                "3. Middleware → FATFS → 勾选 Activate:\n"
                "   - User Defined: SD Card (使用SDIO接口的SD卡)\n"
                "   - Code generation setting: 勾选 Use DMA\n"
                "   - API: 勾选 f_mount/f_open/f_read/f_write/f_close 等\n"
                "4. NVIC: 启用 SDIO global interrupt\n"
                "5. GPIO: CMD(PC12), D0-D3(PC8-PC11), CK(PC12) 自动配置\n"
                "6. 代码: f_mount(&SDFatFS, SDPath, 1); f_open/f_read/f_write/f_close"
            ),
            "dac": (
                "1. Analog → DAC → Channel1 (PA4) / Channel2 (PA5) → 勾选 OUT\n"
                "2. Parameter Settings:\n"
                "   - Output Buffer: Disable (高速/低阻负载) 或 Enable (大电流驱动)\n"
                "   - Trigger: None (软件触发, 用 HAL_DAC_SetValue())\n"
                "   - 或选择 Timer Trigger (定时器+DMA连续波形输出)\n"
                "3. DMA 模式 (连续波形):\n"
                "   - DAC → Settings → 勾选 DMA Out\n"
                "   - System Core → DMA → 添加 DACx Channel\n"
                "   - Mode: Circular (循环) 或 Normal\n"
                "   - Timers → 选一个定时器作为触发源 (如 TIM6 TRGO)\n"
                "4. GPIO: DAC_OUT1(PA4) / DAC_OUT2(PA5) 自动配置为模拟\n"
                "5. 代码: HAL_DAC_Start() / HAL_DAC_SetValue() / HAL_DAC_Start_DMA()"
            ),
            "flash_eeprom": (
                "⚠️ 内部Flash不需要CubeMX外设配置, 直接在代码中操作\n"
                "1. 确定保存地址 (避开用户程序区):\n"
                "   - F103C8T6 Flash: 64KB, 页大小 1KB (0x08000000 ~ 0x0800FFFF)\n"
                "   - 推荐起始页: 最后几页 (如 0x0800F800 = 第62页)\n"
                "2. 代码步骤:\n"
                "   a. HAL_FLASH_Unlock() 解锁Flash\n"
                "   b. HAL_FLASHEx_ErasePage(页地址) 擦除一整页 (必须先擦除再写)\n"
                "   c. HAL_FLASH_Program(FLASH_TYPEPROGRAM_HALFWORD, 地址, 数据) 写入半字 (16bit)\n"
                "   d. HAL_FLASH_Lock() 锁定Flash\n"
                "3. 注意事项:\n"
                "   - 擦除以页为单位 (1KB), 写入以半字为单位 (2字节)\n"
                "   - 擦写次数寿命约 1万次, 不适合频繁写入\n"
                "   - 擦除期间 CPU 会暂停 (约20~30ms/页)"
            ),
            "rng_crc": (
                "RNG (真随机数生成器):\n"
                "1. 不需要CubeMX配置 (F103无RNG硬件, 仅F4/H7等有)\n"
                "   - 对于F103可用 ADC噪声+时间种子 软件伪随机替代\n"
                "CRC (循环冗余校验):\n"
                "1. Computing → CRC → 勾选 Activate\n"
                "2. Polynomial size: 32bits (标准CRC-32)\n"
                "3. 代码: \n"
                "   - uint32_t crc = HAL_CRC_Calculate(&hcrc, (uint32_t*)data, len/4);\n"
                "   - 适用场景: 数据包校验、通信协议完整性验证、固件完整性检查\n"
                "提示: CRC是纯硬件计算, 极快且不占用CPU"
            ),
            "iap": (
                "⚠️ IAP 需要创建两个独立项目 (Bootloader + App)\n"
                "【项目1: Bootloader】 (@ 0x08000000)\n"
                "1. 正常配置 USART/USB/CAN (用于接收新固件)\n"
                "2. 实现协议解析 (Ymodem/Xmodem/自定义)\n"
                "3. 接收完整固件后:\n"
                "   a. HAL_FLASH_Unlock()\n"
                "   b. 循环擦除App所在Flash页\n"
                "   c. HAL_FLASH_Program() 逐半字写入\n"
                "   d. HAL_FLASH_Lock()\n"
                "4. 校验通过后调用 Jump_To_App()\n"
                "【项目2: App】 (@ 0x08002000, 偏移量=Bootloader大小)\n"
                "1. CubeMX → Linker Settings:\n"
                "   - ROM offset: 0x08002000 (或设置VECT_TAB_OFFSET=0x2000)\n"
                "   - RAM offset/SIZE: 默认不变\n"
                "2. main() 最开始添加:\n"
                "   SCB->VTOR = FLASH_BASE | 0x2000; // 重定向中断向量表\n"
                "3. 编译生成的 .bin 文件用于传输\n"
                "【跳转函数核心代码】\n"
                "typedef void (*pFunction)(void);\n"
                "pFunction Jump_To_Application;\n"
                "uint32_t JumpAddress = *(uint32_t*)(APP_ADDR + 4);\n"
                "Jump_To_Application = (pFunction)JumpAddress;\n"
                "HAL_DeInit(); __disable_irq(); SysTick->CTRL = 0;\n"
                "Jump_To_Application(); // 跳转到App执行"
            ),
        }
        return guides.get(skill_name, f"{skill_name} 的 CubeMX 配置指南待补充")

    def show_all_knowledge(self) -> str:
        """展示完整知识库概览"""
        lines = []
        lines.append("=" * 70)
        lines.append("  STM32 Agent - 完整外设知识库")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"{'模块':<8} {'分类':<10} {'描述'}")
        lines.append("-" * 70)

        for skill in self.skill_registry:
            info = self.knowledge_base.get(skill.name, {})
            desc = info.get("description", "")[:50]
            lines.append(f"{skill.name:<8} {skill.category:<10} {desc}")

        lines.append("")
        lines.append("=" * 70)
        lines.append(f"  共 {len(self.skill_registry)} 个外设模块")
        lines.append(f"  数据来源: GitHub 开源社区")
        lines.append("=" * 70)
        return "\n".join(lines)


# ============================================================
# CLI 入口
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="STM32 Agent - HAL库开发助手")
    parser.add_argument("--query", "-q", help="查询某个外设模块")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有可用技能")
    parser.add_argument("--guide", "-g", help="获取 CubeMX 配置向导")
    parser.add_argument("--all", "-a", action="store_true", help="展示完整知识库")
    args = parser.parse_args()

    agent = STM32Agent()

    if args.all:
        print(agent.show_all_knowledge())
    elif args.list:
        for skill in agent.list_skills():
            print(f"  [{skill.category:8s}] {skill.name:<10s} - {skill.description[:45]}")
    elif args.guide:
        print(agent.get_cube_mx_guide(args.guide))
    elif args.query:
        result = agent.query(args.query)
        print(result)
    else:
        # 交互模式
        print(agent.show_all_knowledge())
        print("\n输入查询 (或 Ctrl+C 退出):\n")
        while True:
            try:
                q = input("STM32> ").strip()
                if q:
                    print(agent.query(q))
                    print()
            except (KeyboardInterrupt, EOFError):
                print("\nBye!")
                break


if __name__ == "__main__":
    main()
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
