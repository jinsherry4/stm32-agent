"""ENCODER - STM32 HAL Library Skill Module"""

__skill_name__ = "encoder"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SILL_DATA = {
"encoder": {
        "description": "TIM 编码器接口模式，读取正交编码器(A/B相)的脉冲数和方向。用于直流电机转速测量、旋转编码器角度检测、滑块位置反馈等",
        "encoder_types": [
            ("Incremental Encoder (正交增量)", "A/B两相90度相位差, 输出方向+脉冲"),
            ("Hall Sensor (霍尔传感器)", "三相霍尔信号, 用于BLDC无刷电机换相"),
        ],
        "hal_apis": [
            "__HAL_RCC_TIMx_CLK_ENABLE()",
            "HAL_TIM_Encoder_Init()",
            "HAL_TIM_Encoder_Start()",
            "HAL_TIM_Encoder_Start_IT()",
            "HAL_TIM_Encoder_Stop()",
            "__HAL_TIM_GET_COUNTER()",
            "__HAL_TIM_SET_COUNTER()",
            "__HAL_TIM_IS_TIM_COUNTING_DOWN()",  # 判断旋转方向
        ],
        "wiring": "A相(TIMx_CH1) B相(TIMx_CH2) -- 推荐TIM2(PA0/PA1) 或 TIM3(PA6/PA7) 或 TIM4(PB6/PB7)",
        "code_example": '''
# CubeMX 配置: Timers -> TIM2 (或TIM3/TIM4)
#   Combined Channels -> Encoder Mode -> Encoder Mode TI1 and TI2
#   Counter Period: 65535 (16位最大值, 或设为0xFFFFFFFF用32位TIM2)
#   不需要NVIC中断! 主循环中直接读CNT即可
#   ⚠️ 不要同时开启 Channel1/Channel2 的PWM或Capture!

# 编码器初始化 (CubeMX部分生成, 需手动调整)
TIM_Encoder_InitTypeDef encoder = {
    .EncoderMode = TIM_ENCODERMODE_TI12,          # 双边沿计数(精度4倍增)
    .IC1Filter = 0,                               # 输入滤波
    .IC2Filter = 0,
    .IC1Polarity = TIM_ICPOLARITY_RISING,
    .IC2Polarity = TIM_ICPOLARITY_RISING,
};
TIM_MasterConfigTypeDef master = {0};
master.MasterOutputTrigger = TIM_TRGO_RESET;
master.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;

htim2.Instance = TIM2;
htim2.Init.Prescaler = 0;
htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
htim2.Init.Period = 65535;
htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
HAL_TIM_Encoder_Init(&htim2, &encoder);

# 启动编码器 (非IT方式 -- 轮询读取)
HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);

# 主循环中读取编码器值
while (1) {
    int16_t count = (int16_t)__HAL_TIM_GET_COUNTER(&htim2);

    # 判断方向 (向下计数 = 反转)
    int direction = __HAL_TIM_IS_TIM_COUNTING_DOWN(&htim2) ? -1 : 1;

    printf("Position: %d, Direction: %s\\\\n",
           count, direction > 0 ? "CW" : "CCW");

    # 计算速度 (差分法): 两次采样间位移/时间间隔
    static int16_t prev_count = 0;
    static uint32_t prev_time = 0;
    uint32_t now = HAL_GetTick();
    if (now - prev_time >= 100) {  # 每100ms计算一次
        int16_t delta = count - prev_count;
        float speed_rpm = (delta / (float)(now - prev_time)) * 60000.0f / PPR;  # PPR=每圈脉冲数
        printf("Speed: %.1f RPM\\\\n", speed_rpm);
        prev_count = count;
        prev_time = now;
    }

    HAL_Delay(10);
}

# 归零操作 (设置参考原点)
__HAL_TIM_SET_COUNTER(&htim2, 0);
''',
        "references": [
            {"source": "CSDN: TIM编码器模式读取旋钮编码器", "url": "https:#blog.csdn.net/DIVIDADA/article/details/130192899", "note": "编码器接口详细教程"},
            {"source": "IoTWord: CubeMX TIM编码器踩坑记录", "url": "https:#www.iotword.com/18133.html", "note": "常见问题与解决方案"},
            {"source": "ST Community", "url": "https:#community.st.com/t5/stm32cubemx-mcus/stm32f103-timer-encoder-mode-interrupt-callback-periodelapsed/td-p/298970", "note": "编码器中断回调讨论"},
        ]
    },

    # ---- 16. USB Device (CDC虚拟串口) ----
}

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SILL_DATA
