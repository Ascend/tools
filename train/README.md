# 训练benchmark

## 支持的产品
Atlas 800 (Model 9000)

## 操作系统

centos7.6 & ubuntu 18.04


## 训练方法

1. 根据实际情况修改 ./yaml/ 目录下的对应的 yaml 文件，建议备份原文件，且保持 yaml 文件名与模型名称相同。
2. 在当前目录（train）下，执行：`./benchmark.sh --help` 查看帮助信息。
3. 根据 **帮助信息** 或本文件中的 **运行参数说明** 选择配置运行参数后，执行：`./benchmark.sh`

## 示例
- 示例1，docker 环境下启动 MobileNet 多卡（8p）训练：`./benchmark.sh -e MobileNet -hw 8p -y ./yaml/MobileNet.yaml -docker`
- 示例2，host 环境下启动 MobileNet 单卡（1p）训练，yaml 使用默认文件：`./benchmark.sh -e MobileNet`
- 示例3，host 环境下启动 ResNet50 集群（cluster）训练，yaml 使用默认文件：`./benchmark.sh -e ResNet50 -hw ct`
- 示例4，host 环境下启动 pytorch模型DeepMar单卡（1p）训练，yaml 使用默认文件：`./benchmark.sh -e DeepMar -hw 1p -f pytorch`
- 示例5，host 环境下启动 pytorch模型DeepMar多卡（8p）训练，yaml 使用默认文件：`./benchmark.sh -e DeepMar -hw 8p -f pytorch`
- 示例6，docker环境下启动 pytorch模型DeepMar多卡（8p）训练，yaml 使用默认文件：`./benchmark.sh -e DeepMar -hw 8p -f pytorch -docker`

## 运行参数说明

|      参数       | 是否必填 | 参数说明             | 默认值                  |
| --------------- | -------- | -------------------- |------------------------ |
| --execmodel, -e | 选填     | 需要执行的模型名称   | ResNet50                 |
| --hardware, -hw | 选填     | 选择 1p, 2p, 4p, 8p, cluster/ct | 1p                  |
| --yamlpath, -y  | 选填     | yaml 文件的路径      | ./yaml/{execmodel}.yaml |
| --framework, -f | 选填     | 模型训练框架         | tensorflow              |
| -docker, -host  | 选填     | 选择 docker 或 host  | host                    |
| --help, -h      | 选填     | 显示帮助信息         | NA                       |
| --list, -l      | 选填     | 显示当前支持的模型与框架 | NA                    |

## 查看日志

- 可在 train/result/ 目录下查看各个模型最后生成的含性能与精度数据的日志。
- 中间结果ckpt或其他文件存放在 *device id* 下。
- train_x.log 为模型训练过程日志，内容较为详细；以 hw 开头的日志为打点日志，仅记录数据。

## 注意事项

- yaml 文件中的值可以参考注释，根据实际情况自行修改。键不可随意修改，否则可能导致训练失败或训练结果偏离实际。
- 集群（cluster）执行时，请保证各节点环境配置相同，且包括**配置文件、数据集、代码**绝对路径相同。

## Benchmark工具资料参考

https://support.huawei.com/enterprise/zh/ascend-computing/atlas-data-center-solution-pid-251167910/software/251732401?idAbsPath=fixnode01%7C23710424%7C251366513%7C22892968%7C251167910
