"""
STM32 Agent CLI - 命令行交互入口
=================================
仿 ROSAgent interactive_loop() 风格。

用法:
    python -m stm32_agent.cli --all           # 展示全部知识库
    python -m stm32_agent.cli -l              # 列出技能
    python -m stm32_agent.cli -q "GPIO LED"   # 查询
    python -m stm32_agent.cli -g usart        # CubeMX 向导
    python -m stm32_agent.cli                 # 交互模式
"""

import sys
import argparse

from stm32_agent.core import STM32Agent


def main():
    parser = argparse.ArgumentParser(
        description="STM32 Agent v2.0 - HAL库开发助手 (仿ROSAgent架构)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --all                    展示全部 22 个外设模块
  %(prog)s -l                       列出所有技能(带分类)
  %(prog)s -q "外部中断怎么配置"     自然语言查询
  %(prog)s -g iap                   获取 IAP 的 CubeMX 配置向导
  %(prog)s                          进入交互模式
        """
    )
    parser.add_argument("--query", "-q", help="查询某个外设模块（自然语言）")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有可用技能")
    parser.add_argument("--guide", "-g", help="获取指定外设的 CubeMX 配置向导")
    parser.add_argument("--all", "-a", action="store_true", help="展示完整知识库概览")
    parser.add_argument("--version", "-v", action="version", version=f"STM32 Agent 2.0.0")

    args = parser.parse_args()

    # 初始化 Agent
    print("[STM32 Agent] 正在加载 22 个外设模块...")
    agent = STM32Agent()
    print(f"[STM32 Agent] 就绪! 共 {agent.registry.count()} 个技能, {len(agent.registry.categories())} 个分类\n")

    if args.all:
        print(agent.show_all_knowledge())
    elif args.list:
        for skill in agent.registry.list_skills():
            info = agent.knowledge_base.get(skill.name, {})
            desc = info.get("description", "")[:45]
            print(f"  [{skill.category:10s}] {skill.name:<14s} {desc}")
    elif args.guide:
        print(agent.get_cube_mx_guide(args.guide))
    elif args.query:
        result = agent.query(args.query)
        print(result)
    else:
        _interactive_loop(agent)


def _interactive_loop(agent: STM32Agent):
    """交互模式 (仿 ROSAgent.interactive_loop)"""
    print(agent.show_all_knowledge())
    print("\n输入自然语言查询 (或 Ctrl+C 退出):")
    print("提示: 输入 'skills' 查看列表, 'help' 查看帮助\n")

    while True:
        try:
            q = input("STM32> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not q:
            continue
        if q.lower() in ("exit", "quit", "q"):
            print("Bye!")
            break
        if q.lower() == "skills":
            for s in agent.registry.list_skills():
                print(f"  [{s.category:10s}] {s.name:<14s} {s.description[:45]}")
            print()
            continue
        if q.lower() == "help":
            print(parser.format_help())
            continue

        result = agent.query(q)
        print(result)
        print()


if __name__ == "__main__":
    main()
