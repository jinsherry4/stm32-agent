# CONTEXT.md - STM32 Embedded Domain Glossary
#
# This file establishes a shared language between the developer and the AI agent.
# All terms are specific to STM32 HAL library development with CubeMX workflow.
# Inspired by Matt Pocock's Ubiquitous Language concept (DDD).
#
# Rule: Pure glossary only. No implementation details, no specs, no scratch pad.

---

## MCU & Hardware

| Term | Meaning |
|------|---------|
| **MCU / 芯片** | Microcontroller unit, e.g., STM32F103C8T6 ("Blue Pill") |
| **Board** | Development board, e.g., Blue Pill, Nucleo-F401RE |
| **Core** | ARM Cortex-M core (M3/M4/M7), determines instruction set and FPU availability |
| **Clock Tree** | System clock distribution: HSE → PLL → SYSCLK → AHB → APB1/APB2 → peripherals |

## Pin & GPIO

| Term | Meaning |
|------|---------|
| **Pin** | Physical pin on the chip package, labeled as PA0-PB15 etc. |
| **AF** | Alternate Function - when a pin is used by a peripheral (USART TX, SPI MOSI) instead of GPIO |
| **BSRR** | Bit Set/Reset Register - atomic way to toggle pins without read-modify-write race condition |
| **Push-Pull** | Output mode: actively drives HIGH or LOW (for LEDs, CS lines) |
| **Open-Drain** | Output mode: only drives LOW, needs pull-up for HIGH (I2C SDA/SCL) |

## Communication Peripherals

| Term | Meaning |
|------|---------|
| **Full-Duplex** | Simultaneous TX and RX on separate lines (SPI MOSI + MISO) |
| **Half-Duplex** | TX and RX share the same line, take turns (USART single-wire, I2C) |
| **CPOL / CPHA** | SPI clock polarity and phase - Mode 0-3, must match slave device datasheet |
| **Baud Rate** | Communication speed in bits/sec (USART 9600/115200; I2C 100kHz/400kHz; SPI depends on prescaler) |
| **CS / NSS / SS** | Chip Select / Slave Select - active-low GPIO to select which slave device is active |
| **MOSI / MISO / SCK** | SPI Master Out/Slave In, Master In/Slave Out, Serial Clock |
| **SDA / SCL** | I2C Serial Data, Serial Clock - require external pull-up resistors (4.7KΩ~10KΩ) |

## Timing

| Term | Meaning |
|------|---------|
| **PSC (Prescaler)** | Timer clock divider: counter_freq = timer_clk / (PSC + 1) |
| **ARR (Auto-Reload)** | Counter reset value: period = (ARR + 1) / counter_freq |
| **CCR (Capture/Compare)** | Compare match value for PWM duty cycle or output compare events |
| **Duty Cycle** | Pulse width ratio = CCR / (ARR + 1), expressed as percentage |
| **Input Capture** | Timer measures external signal frequency/pulse width (encoder, IR receiver) |
| **Output Compare** | Timer generates precise timing edges (PWM, stepper motor step) |

## Interrupts

| Term | Meaning |
|------|---------|
| **NVIC** | Nested Vectorable Interrupt Controller - ARM core interrupt manager |
| **ISR** | Interrupt Service Routine - callback function that runs when interrupt fires |
| **Priority Grouping** | How preempt vs sub-priority bits are split (4-bit group = 4 pre, 0 sub recommended for most cases) |
| **Callback** | HAL weak function you override to handle events (`HAL_UART_RxCpltCallback`, `HAL_TIM_PeriodElapsedCallback`) |
| **Critical Section** | Code where interrupts must be disabled (`__disable_irq()` / `__enable_irq()`) to prevent data corruption |

## Analog

| Term | Meaning |
|------|---------|
| **ADC Resolution** | Number of bits: 12-bit = 0~4095 range on STM32F1/F4 |
| **Sample Time** | How long ADC samples the pin before conversion (longer = more accurate but slower) |
| **DAC** | Digital-to-Analog Converter: generates analog voltage from digital value |
| **VREF** | Reference voltage for ADC/DAC (usually VDDA = 3.3V) |

## Memory & Storage

| Term | Meaning |
|------|---------|
| **Flash** | Non-volatile memory for storing program code and persistent data (EEPROM emulation uses last pages) |
| **SRAM** | Volatile runtime memory (20KB on F103C8, critical resource!) |
| **Sector/Page** | Flash erasure granularity: sector (Flash EEPROM), page (W25Q64 = 256 bytes) |
| **JEDEC ID** | Manufacturer+type+capacity identifier read from SPI Flash via command 0x9F |

## Power

| Term | Meaning |
|------|---------|
| **Sleep Mode** | CPU stops, peripherals run, any interrupt wakes up |
| **Stop Mode** | Most clocks stopped, SRAM retained, EXTI or RTC alarm wakes up |
| **Standby Mode** | Lowest power (~µA), SRAM lost, only WKUP pin, RTC, or NRST wakes up |
| **IWDG** | Independent Watchdog - runs on LSI ~40kHz, cannot be stopped once started |
| **WWDG** | Window Watchdog - runs on APB1 clock, must feed within a time window |
| **Feed Dog / Kick** | Reload watchdog counter to prevent reset (`HAL_IWDG_Refresh()`) |

## Debug & Toolchain

| Term | Meaning |
|------|---------|
| **CubeMX** | ST graphical tool for pin assignment, clock config, peripheral setup - generates initialization code |
| **HAL** | Hardware Abstraction Layer - ST's high-level driver API (`HAL_GPIO_WritePin`, `HAL_SPI_Transmit`) |
| **Proteus** | Circuit simulation software with COMPIM virtual serial port bridge |
| **VSPD** | Virtual Serial Port Driver - pairs COM ports for PC ↔ simulation communication |
| **ST-Link** | In-circuit debugger/programmer for STM32, supports SWD/JTAG |
| **COMPIM** | Proteus component bridging physical COM port to simulated USART |

## Project-Specific Terms (HW7)

| Term | Meaning |
|------|---------|
| **倒计时系统** | HW7 project: 4-digit 7-segment countdown display over USART control |
| **数码管动态扫描** | Multiplexed 7-segment display: one digit lit at a time, cycling fast enough (<5ms) that all appear simultaneously lit |
| **位选 / 段选** | Digit selection (PB0-PB3) / Segment selection (PB4-PB13) for common-anode display |
| **cmd_ready flag** | USART interrupt receive flag indicating a complete command packet has arrived |
| **HUMI command** | UART protocol command requesting humidity data display |
