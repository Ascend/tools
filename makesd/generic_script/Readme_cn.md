中文|[English](Readme.md)

# fgeneric_script
**此脚本支持1.0.12.alpha及以上所有版本**

## 配套关系

制卡需要驱动固件包。  
Atlas 200 DK开发者套件包含：  
- 驱动固件包：包含AI软件栈及维测相关软件的驱动、固件及Device侧的文件系统镜像。
- CANN包：AI异构计算架构。CANN是华为公司针对AI场景推出的异构并行计算架构，通过提供多层次的编程接口，支持用户快速构建基于Ascend平台的AI应用和业务。  

Atlas 200 DK的驱动包与CANN包的版本配套关系请参见：[版本配套说明](../Version_Mapping_CN.md)


## 文件介绍

- make_sd_card.py：制卡入口脚本

- make_ubuntu_sd.sh：制作SD卡操作系统脚本

## 制卡步骤

**制卡步骤请参见[硬件产品文档](https://www.hiascend.com/document?tag=hardware)下的【AI开发者套件】文档**