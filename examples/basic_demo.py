"""
STM32 Agent Usage Demo - 基础查询示例
=====================================

演示如何使用 STM32Agent 进行外设查询、
CubeMX 配置向导调用、以及知识库浏览。
"""

from stm32_agent import STM32Agent


def main():
    # 初始化 Agent (自动加载 skills/ 目录下所有模块)
    agent = STM32Agent()
    print(agent.show_all_knowledge())
    print()

    # ── 示例1: 单模块查询 ──
    print("=" * 60)
    print("  示例1: GPIO LED 控制")
    print("=" * 60)
    result = agent.query("如何用GPIO控制LED灯")
    print(result)
    print()

    # ── 示例2: 串口通信查询 ──
    print("=" * 60)
    print("  示例2: USART 串口中断接收")
    print("=" * 60)
    result = agent.query("USART串口怎么接收数据")
    print(result)
    print()

    # ── 示例3: CubeMX 配置向导 ──
    print("=" * 60)
    print("  示例3: PWM 的 CubeMX 配置步骤")
    print("=" * 60)
    guide = agent.get_cube_mx_guide("pwm")
    print(guide)
    print()

    # ── 示例4: 组合查询 (多模块) ──
    print("=" * 60)
    print("  示例4: ADC + DMA 多通道采样")
    print("=" * 60)
    result = agent.query("ADC配合DMA做多通道数据采集")
    print(result)


if __name__ == "__main__":
    main()
