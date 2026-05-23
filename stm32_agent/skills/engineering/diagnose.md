---
name: diagnose
description: >
  系统性调试循环 - 专门针对 STM32 嵌入式开发中的疑难 bug。
  流程：重现 → 最小化 → 假设 → 检测 → 修复 → 回归测试。
  适用场景：代码不工作、外设无响应、中断异常、数据错乱。
  触发词：'调试', 'diagnose', 'bug', '不工作', '排查', '为什么不对'
---

## `<what-to-do>`

引导用户按照以下 **6 步诊断循环** 排查 STM32 项目问题。

**不要跳步。** 每一步完成后才进入下一步。

## `</what-to-do>`

## `<supporting-info>`

## 诊断循环（STM32 专用）

### Step 1: 重现 (Reproduce)
- 问题能稳定复现吗？还是随机出现？
- 复现条件是什么？（上电后立即 / 运行一段时间后 / 特定操作后）
- 记录：现象 → 预期 → 实际

### Step 2: 最小化 (Minimize)
- 去掉所有无关代码，保留最小可复现案例
- 注释掉其他外设初始化，只保留问题相关的
- 用最简单的 GPIO 翻转或 USART 打印验证 MCU 本身正常
- **目标：用 < 20 行代码复现问题**

### Step 3: 假设 (Hypothesize)
基于 STM32 常见故障模式列出假设：

| 故障现象 | 常见原因 | 检查方法 |
|----------|----------|----------|
| 外设完全无响应 | 时钟未使能 | 检查 `__HAL_RCC_xxx_CLK_ENABLE()` |
| 中断不触发 | NVIC 未配置 | 检查 NVIC 优先级 + 中断使能 |
| 数据全是 0xFF | 引脚浮空/未配置 | 检查 GPIO 模式 + 上拉/下拉 |
| 串口乱码 | 波特率不匹配 | 双方波特率必须一致 |
| SPI/I2C 通信失败 | 时序模式错误 | CPOL/CPHA 必须与从机匹配 |
| ADC 读数跳动 | 采样时间不足 | 增大 Sample Time 或加滤波 |
| 定时器不准 | 时钟源选错 | 检查时钟树 APB1/APB2 预分频 |
| HardFault | 空指针/数组越界/除零 | 查看 Fault Handler 的 PC+LR 寄存器 |
| 程序卡死 | 死循环/看门狗复位 | 检查 while 循环退出条件 |
| DMA 不工作 | 源/地址不对齐 | STM32F1 DMA 需要 4 字节对齐 |

### Step 4: 检测 (Detect)
- **不要用 printf 猜测！** 设计有针对性的检测实验：
  - 用 GPIO 翻转 + 示波器测量时序
  - 用 USART 逐步打印关键变量
  - 用 Keil/IAR 断点观察寄存器值
- 每个检测只验证一个假设

### Step 5: 修复 (Fix)
- 只改一处！
- 改完后立即测试

### Step 6: 回归 (Regression)
- 修复是否引入了新问题？
- 其他外设还正常吗？
- 长时间运行是否稳定？

## 常用检测代码模板

### GPIO 快速调试（替代 printf）
```c
// 定义调试引脚（如 PA0，接 LED 或示波器）
#define DEBUG_PIN()     HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_0)
#define DEBUG_HIGH()    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_SET)
#define DEBUG_LOW()     HAL_GPIO_WritePin(GPIOA, GPIO_PIN_0, GPIO_PIN_RESET)

// 在可疑位置插入
DEBUG_HIGH();   // 标记进入某段代码
/* ... 可疑代码 ... */
DEBUG_LOW();    // 标记离开某段代码
```

### 寄存器状态快照
```c
// 打印关键寄存器（通过 USART）
printf("SPI1->CR1=0x%04lX\r\n", SPI1->CR1);
printf("SPI1->SR =0x%04lX\r\n", SPI1->SR);
printf("GPIOA->ODR=0x%04lX\r\n", GPIOA->ODR);
```

### HardFault 诊断
```c
void HardFault_Handler(void) {
    __disable_irq();
    printf("HardFault! PC=0x%08lX LR=0x%08lX\r\n",
           (unsigned long)(*((volatile unsigned long *)(0x08))),
           (unsigned long)(*((volatile unsigned long *)(0x0C))));
    while(1);  // 停住，方便连接 debugger
}
```

## `</supporting-info>`
