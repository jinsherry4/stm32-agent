"""SDIO - STM32 HAL Library Skill Module"""

__skill_name__ = "sdio"
__all__ = ["get_skill_info"]

# Skill data dict (parsed by knowledge_base.py)
SILL_DATA = {
"sdio": {
        "description": "SDIO SD卡接口 + FatFs 文件系统组合方案，实现大容量数据存储与文件读写。适用于数据日志存储、图片资源保存、固件缓存、音乐播放等需要持久化数据的场景",
        "specs": {
            "SDIO时钟": "最高24MHz (SDSC) / 48MHz (SDHC)",
            "总线宽度": "1-bit或4-bit数据总线",
            "FatFs版本": "FatFS R0.15 (开源, 支持FAT12/16/32/exFAT)",
            "支持格式": "FAT32 (推荐, 最大2TB分区)",
        },
        "hardware": "STM32F103: SDIO_D0(PC8) D1(PC9) D2(PC10) D3(PC11) CK(PC12) CMD(PD2), SD卡座+电平转换(3.3V<->1.8V)",
        "hal_apis": [
            "__HAL_RCC_SDIO_CLK_ENABLE()",
            "HAL_SD_Init()",
            "HAL_SD_ReadBlocks()",             # 读扇区
            "HAL_SD_WriteBlocks()",            # 写扇区
            "HAL_SD_GetCardInfo()",            # 获取卡信息(容量/类型/block size),
            "HAL_SD_GetCardStatus()",
            "# FatFs API:",
            "f_mount()",                       # 挂载文件系统
            "f_open()",                        # 打开文件
            "f_read()",                        # 读文件
            "f_write()",                       # 写文件
            "f_close()",                       # 关闭文件
            "f_sync()",                        # 同步缓冲区到物理介质
            "f_mkdir()",                       # 创建目录
            "f_opendir()/f_readdir()",         # 目录遍历
            "f_getfree()",                     # 获取剩余空间
            "f_unmount()",                     # 卸载
            "f_printf()",                      # 格式化写入(需FF_USE_STRFUNC=1)
        ],
        "code_example": '''
# CubeMX 配置:
#   Connectivity -> SDIO -> Mode: SD 4bits Wide bus
#     Clock Divide Factor: SDIOCLK divide bypass (最快)
#     Wide Bus: 4-bit (性能最优)
#   Middleware -> FATFS -> User Defined -> SD Card
#     USE_LFN: Enabled with static buffer (支持长文件名)
#     FF_FS_EXFAT: Disabled (一般不需要exFAT)
#     Code Page: 936 (简体中文GBK, 如需中文文件名)
#   NVIC: Enable SDIO global interrupt

#include "fatfs.h"
#include "sd.h"

FATFS fs;                    # 文件系统对象
FIL file;                    # 文件对象
FRESULT res;                 # 操作结果
UINT bytes_read, bytes_written;

# 1. 初始化并挂载SD卡
res = f_mount(&fs, "0:", 1);  # 1=立即挂载
if (res != FR_OK) {
    printf("SD mount failed! error=%d\\\\n", res);
} else {
    printf("SD mounted OK!\\\\n");
}

# 2. 写入数据日志
char log_msg[128];
sprintf(log_msg, "[2026-05-23] Temp=25.6C Hum=60%%\\\\r\\\\n");
res = f_open(&file, "0:sensor_log.txt", FA_OPEN_ALWAYS | FA_WRITE);
if (res == FR_OK) {
    f_lseek(&file, f_size(&file));  # 追加到末尾
    f_write(&file, log_msg, strlen(log_msg), &bytes_written);
    f_sync(&file);                  # 立即写入SD卡!
    f_close(&file);
}

# 3. 读取配置文件
char config_buf[256];
res = f_open(&file, "0:config.ini", FA_READ);
if (res == FR_OK) {
    f_read(&file, config_buf, sizeof(config_buf)-1, &bytes_read);
    config_buf[bytes_read] = '\\\\0';
    printf("Config: %s\\\\n", config_buf);
    f_close(&file);
}

# 4. 创建目录并列出文件
f_mkdir("0:data");
DIR dir;
FILINFO finfo;
f_opendir(&dir, "0:");
while (f_readdir(&dir, &finfo) == FR_OK && finfo.fname[0]) {
    printf("  %-20s %10lu bytes\\\\n", finfo.fname, finfo.fsize);
}
f_closedir(&dir);

# 5. 获取SD卡信息
HAL_SD_CardInfoTypeDef card_info;
HAL_SD_GetCardInfo(&hsd, &card_info);
DWORD free_clusters, free_sectors;
FATFS *pfs;
f_getfree("0:", &free_clusters, &pfs);
free_sectors = free_clusters * pfs->csize;
printf("Card: %lu MB total, %lu MB free\\\\n",
       (card_info.LogBlockNbr * card_info.BlockSize) / (1024*1024),
       (free_sectors * 512) / (1024*1024));
''',
        "references": [
            {"source": "野火STM32教程 - FatFs文件系统", "url": "https:#doc.embedfire.com/mcu/stm32/f429tiaozangzhe/hal/zh/latest/doc/chapter36/chapter36.html", "note": "SD卡+FatFs完整教程"},
            {"source": "DeepBlueEmbedded", "url": "https:#deepbluembedded.com/stm32-sdio-sd-card-example-fatfs-tutorial/", "note": "SDIO+FatFs实战指南"},
            {"source": "CSDN: CubeMX FATFS文件系统", "url": "https:#blog.csdn.net/Deheng_Kong/article/details/117820173", "note": "FatFs配置与文件读写示例"},
            {"source": "博客园: SDIO接口SD卡", "url": "https:#www.cnblogs.com/xiaobaibai2021/p/15716892.html", "note": "SDIO底层配置详解"},
        ]
    },

    # ---- 19. DAC (数模转换器) ----
}

def get_skill_info() -> dict:
    """Return this skill's knowledge base entry as a Python dict."""
    return SILL_DATA
