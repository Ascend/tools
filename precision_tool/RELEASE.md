#Release 0.1.7
## Update
* 兼容新平台溢出检测数据解析

#Release 0.1.6
## Update
* 支持获取profiling数据
* 兼容一些溢出监测dump数据的修改 
* 修复溢出检测数据解析问题

# Release 0.1.5
## Update
* 修复PT命令重复打屏的问题
* 模糊匹配溢出检测算子名
* 修复PT Dump的H5文件解析的一些问题

# Release 0.1.4
## Update
* 完善训练随机固定场景


# Release 0.1.3
## Update
* 支持解析Torch Dump的H5数据

# Release 0.1.2
## Update
* 适配部分dump数据格式

# Release 0.1.1
## Features
* 新增NpuPrintLossScaleCallBack，用于TF2.x下打印scale值
* 新增自动查找子图Data节点真实输入节点功能

## Update
* 优化部分推理场景自动对比目录名和graph名不匹配的场景识别逻辑

## Bugfix
* 溢出错误码解析崩溃bugfix


# Release 0.1.0
## Feature
* 新增基于Checkpoint加载执行网络精度对比的能力

## Update
* 优化目录组织结构