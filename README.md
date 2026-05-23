# STM32 Agent v2.0

**STM32 HAL Library 智能开发助手** — 22 个外设模块完整覆盖，自然语言查询 + CubeMX 配置向导

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow)
![STM32F103](https://img.shields.io/badge/Chip-STM32F103-blue)
![22 Modules](https://img.shields.io/badge/Modules-22-green)

## ✨ 特性

- **📚 22 个外设模块** — 从 GPIO 到 IAP 全覆盖
- **🔍 自然语言查询** — 关键词 NLP 路由，支持中英文
- **⚙️ CubeMX 向导** — 每个模块都有详细的图形化配置步骤
- **💻 代码模板** — 即拿即用的 HAL 库代码示例
- **🔗 GitHub 资源** — 每个模块附带开源参考链接
- **🏗️ ROSAgent 风格架构** — Skill / Registry / Agent 分层设计

## 📦 外设模块一览

| 分类 | 模块 | 说明 |
|------|------|------|
| **Digital** | GPIO | 通用输入输出 (LED/按键/中断) |
| | EXTI | 外部中断 (边沿触发/NVIC) |
| **Comm** | USART | 串口异步通信 |
| | SPI | SPI 总线主从模式 |
| | I2C | I2C 总线 (OLED/传感器/EEPROM) |
| | USB | USB Device CDC 虚拟串口 |
| | CAN | CAN 总线通信 |
| **Analog** | ADC | 模数转换 (多通道/DMA) |
| | DAC | 数模转换 (波形输出) |
| **Timing** | PWM | 脉宽调制 (舵机/调光/电机) |
| | DMA | 直接存储器访问 |
| | RTC | 实时时钟 (日历/闹钟) |
| | TIM Basic | 定时器 (中断/PWM/捕获/比较) |
| | Encoder | 正交编码器接口 |
| **Display** | OLED | SSD1306 I2C OLED 显示屏 |
| **Storage** | W25Q64 | SPI Flash 存储芯片 |
| | SDIO + FatFs | SD 卡文件系统 |
| | Flash EEPROM | 内部Flash模拟EEPROM |
| **Power** | PWR | 电源管理 (Sleep/Stop/Standby) |
| | WDG | 看门狗 (IWDG/WWDG) |
| **Security** | RNG/CRC | 随机数生成/CRC校验 |
| **System** | IAP | 在线编程/OTA固件升级 |

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/jinsherry4/stm32-agent.git
cd stm32_agent_v2

# 或者直接使用 (无需安装)
python -m stm32_agent --help
```

### 命令行使用

```bash
# 列出所有技能
python -m stm32_agent --list

# 查询某个外设
python -m stm32_agent -q "如何配置GPIO输出"

# 获取CubeMX配置向导
python -m stm32_agent -g pwm

# 展示完整知识库
python -m stm32_agent --all

# 交互模式
python -m stm32_agent
```

### Python API 使用

```python
from stm32_agent import STM32Agent, SkillRegistry

# 初始化 Agent
agent = STM32Agent()

# 自然语言查询
result = agent.query("如何用ADC采集温度")

# CubeMX 配置向导
guide = agent.get_cube_mx_guide("usart")

# 浏览全部知识
print(agent.show_all_knowledge())

# 通过 Registry 访问单个技能
skill = agent.registry.get("gpio")
print(skill.hal_apis)
```

## 📁 项目结构

```
stm32_agent_v2/
├── pyproject.toml              # 项目配置
├── README.md                   # 本文件
├── stm32_agent/                # 主包
│   ├── __init__.py             # 包入口 (导出 Skill/Registry/Agent)
│   ├── core.py                 # 核心引擎 (Skill/SkillRegistry/STM32Agent)
│   ├── knowledge_base.py       # 知识库加载器 (自动扫描 skills/)
│   ├── guides.py               # 22个CubeMX配置向导
│   ├── cli.py                  # 命令行入口 (argparse + 交互循环)
│   └── skills/                 # 22个外设技能模块 (独立文件)
│       ├── __init__.py
│       ├── gpio.py
│       ├── usart.py
│       ├── spi.py
│       ├── i2c.py
│       ├── adc.py
│       ├── pwm.py
│       ├── dma.py
│       ├── rtc.py
│       ├── oled.py
│       ├── w25q64.py
│       ├── pwr.py
│       ├── wdg.py
│       ├── exti.py
│       ├── tim_basic.py
│       ├── encoder.py
│       ├── usb.py
│       ├── can.py
│       ├── sdio.py
│       ├── dac.py
│       ├── flash_eeprom.py
│       ├── rng_crc.py
│       └── iap.py
└── examples/
    └── basic_demo.py           # 基础用法示例
```

## 🏗️ 架构设计

本项目仿照 [ROSAgent](https://github.com/openclaw/rosagent) 的分层架构：

```
┌─────────────────────────────────────┐
│            CLI / API                │  ← cli.py / 用户代码
├─────────────────────────────────────┤
│          STM32Agent                 │  ← 核心引擎 (core.py)
│    ┌───────────┬──────────┐        │
│    │ Keyword   │ Response  │        │     NLP关键词路由 → 格式化输出
│    │ Matching  │ Formatter │        │
│    └─────┬─────┴────┬─────┘        │
│    ┌─────▼──────────▼─────┐        │
│    │   SkillRegistry      │        │     技能注册中心
│    │  (22 Skills loaded)  │        │
│    └──────────┬───────────┘        │
├───────────────┼───────────────────┤
│  knowledge_   │    guides.py       │
│  base.py      │  (CubeMX向导)      │  ← 数据层
│  (自动加载)   │                    │
├───────────────┼───────────────────┤
│     skills/*.py (22 files)         │  ← 技能数据层
│  gpio / usart / spi / ... / iap    │
└─────────────────────────────────────┘
```

## 🔧 开发

### 添加新模块

1. 在 `stm32_agent/skills/` 下创建新文件 `xxx.py`
2. 按照模板格式编写：

```python
"""MODULE_NAME - STM32 HAL Library Skill Module"""

__skill_name__ = "module_name"
__all__ = ["get_skill_info"]

SKILL_DATA = '''
    "module_name": {
        "description": "...",
        "hal_apis": [...],
        "code_example": '''...''',
        "references": [...]
    },
'''

def get_skill_info() -> dict:
    return eval(SKILL_DATA)
```

3. 在 `core.py` 的 `CATEGORY_MAP` 和 `KEYWORD_MAP` 中添加映射
4. 在 `guides.py` 的 `CUBE_MX_GUIDES` 中添加配置向导

### 运行测试

```bash
cd stm32_agent_v2
python examples/basic_demo.py
```

## 📊 对比 v1.0 (单文件版)

| 特性 | v1.0 (单文件) | v2.0 (多文件) |
|------|--------------|---------------|
| 文件结构 | 1个 .py (2379行) | 包 + 26个模块文件 |
| 可维护性 | 低 | 高 (每个模块独立) |
| 可扩展性 | 需改大文件 | 新增 .py 文件即可 |
| 架构参考 | 无 | ROSAgent 分层设计 |
| 知识库加载 | 硬编码字典 | 自动扫描 skills/ |
| CubeMX 向导 | 嵌入方法内 | 独立 guides.py |
| CLI 入口 | 嵌入同一文件 | 独立 cli.py |
| 可安装 | 不行 | `pip install` 就绪 |

## 📄 License

MIT License

## 🙏 致谢

- [STMicroelectronics](https://www.st.com/) — STM32 HAL Library
- [ROSAgent](https://github.com/openclaw/rosagent) — 架构设计灵感来源
- GitHub 开源社区 — 各模块的代码参考和教程资源
