"""CAN - STM32 HAL Library Skill Module"""

__skill_name__ = "can"
__all__ = ["get_skill_info"]

# Raw skill data dict (parsed by knowledge_base.py)
SKILL_DATA = '''
    "can": {
        "description": "CAN Controller Area Network 总线通信，工业级高可靠性串行总线。支持多主模式、错误检测、自动重传。用于汽车电子、工业控制、机器人多节点通信",
        "features": [
            ("多主竞争总线", "所有节点平等, 无主从之分"),
            ("差分信号抗干扰", "CAN_H/CAN_L差分传输, 适合恶劣环境"),
            ("硬件CRC校验", "帧级别数据完整性保证"),
            ("错误隔离", "故障节点自动脱离总线, 不影响其他节点"),
            ("标准帧11位/扩展帧29位ID", "标准帧足够大多数应用"),
        ],
        "baud_rates": ["125 kbps (工业常用)", "250 kbps", "500 kbps (汽车常用)", "1000 kbps (高速CAN)"],
        "hardware": "STM32F103内置 bxCAN: CAN1_TX(PB9/PB13) CAN1_RX(PB8/PB12) + MCP2551/MCP2562收发器芯片",
        "hal_apis": [
            "__HAL_RCC_CAN1_CLK_ENABLE()",
            "HAL_CAN_Init()",
            "HAL_CAN_ConfigFilter()",
            "HAL_CAN_Start()",
            "HAL_CAN_ActivateNotification()",
            "HAL_CAN_AddTxMessage()",
            "HAL_CAN_GetTxMailboxesFreeLevel()",
            "HAL_CAN_GetRxFifoFillLevel()",
            "HAL_CAN_GetRxMessage()",
            "CAN_RxFifo0MsgPendingCallback()",  // 接收回调
            "CAN_TxMailboxCompleteCallback()",  // 发送完成回调
        ],
        "code_example": '''
// CubeMX 配置:
//   Connectivity → CAN → Master Mode (Loopback用于自测, Normal用于实际通信)
//   Parameter Settings:
//     Prescaler(for Time Quantum): 9  (APB1=36MHz → TQ=36/(9+1)=3.6MHz? 不对)
//     正确计算: 36M / ((BRP+1) * (TS1+1+TS2+1)) = 波特率
//     500kbps示例: BRP=18, TS1=14(Tq), TS2=5(Tq) → 36M/(18+1)/(14+1+5+1)=500k ✓
//     SJW: 1Tq
//   NVIC: Enable CAN1 RX0 interrupt

// CAN 过滤器配置 (决定接收哪些报文)
CAN_FilterTypeDef canfilterconfig;
canfilterconfig.FilterBank = 0;
canfilterconfig.FilterMode = CAN_FILTERMODE_IDMASK;
canfilterconfig.FilterScale = CAN_FILTERSCALE_32BIT;
canfilterconfig.FilterIdHigh = 0x0000 << 5;    // 标准ID左移5位(高16位)
canfilterconfig.FilterIdLow = 0x0000;
canfilterconfig.FilterMaskIdHigh = 0x0000;    // 掩码0=接收所有ID
canfilterconfig.FilterMaskIdLow = 0x0000;
canfilterconfig.FilterFIFOAssignment = CAN_RX_FIFO0;
canfilterconfig.FilterActivation = ENABLE;
canfilterconfig.SlaveStartFilterBank = 14;
HAL_CAN_ConfigFilter(&hcan1, &canfilterconfig);

// 启动CAN并使能中断
HAL_CAN_Start(&hcan1);
HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING);

// 发送CAN报文
CAN_TxHeaderTypeDef TxHeader;
uint32_t TxMailbox;

TxHeader.StdId = 0x123;              // 标准帧ID (0~0x7FF)
TxHeader.ExtId = 0x01;               // 扩展帧ID(标准帧不关心)
TxHeader.RTR = CAN_RTR_DATA;         // 数据帧 (非远程帧)
TxHeader.IDE = CAN_ID_STD;           // 标准帧格式
TxHeader.DLC = 8;                    // 数据长度 (0~8字节)
TxHeader.TransmitGlobalTime = Disable;

uint8_t data[] = {'H', 'e', 'l', 'l', 'o', 0, 0, 0};

if (HAL_CAN_AddTxMessage(&hcan1, &TxHeader, data, &TxMailbox) != HAL_OK) {
    printf("CAN Tx failed!\\\\n");
}

// 接收回调
void CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan) {
    CAN_RxHeaderTypeDef RxHeader;
    uint8_t RxData[8];

    HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &RxHeader, RxData);

    printf("CAN Rx ID=0x%03X, DLC=%d, Data=", RxHeader.StdId, RxHeader.DLC);
    for (int i = 0; i < RxHeader.DLC; i++) printf("%02X ", RxData[i]);
    printf("\\\\n");
}
''',
        "references": [
            {"source": "controllerstech", "url": "https://controllerstech.com/can-protocol-in-stm32/", "note": "CAN协议+接线+代码完整教程"},
            {"source": "技术站", "url": "https://jishuzhan.net/article/1916748983226191874", "note": "HAL库CAN通信实战(1小时搞定)"},
            {"source": "CSDN", "url": "https://blog.csdn.net/2301_79913420/article/details/147341452", "note": "CUBEMX+HAL CAN收发含代码"},
            {"source": "知乎", "url": "https://zhuanlan.zhihu.com/p/18331910832", "note": "基于HAL库的CAN收发实验"},
        ]
    },

    # ---- 18. SDIO + FatFs (SD卡文件系统) ----
'''

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return eval(SKILL_DATA)
