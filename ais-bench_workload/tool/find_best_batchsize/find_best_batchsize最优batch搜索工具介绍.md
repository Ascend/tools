# find_best_batchsize推理介绍

## 介绍
本文介绍AisBench推理工具中find_best_batchsize专项功能

输入：原始模型文件，支持onnx、pb、prototx格式

输出：最优的吞吐率，最优的batchsize序号

## 使用环境与依赖
已安装开发运行环境的昇腾AI推理设备。

## 构建与安装
本专项功能包含在推理工具中，构建和安装遵从推理工具的构建和安装。详细过程请参见推理工具的README.md

## 运行说明
在安装好推理whl包后，即可按照如下流程进行搜索命令执行
1. 确定requirement中依赖是否执行，如果没有安装，则执行如下命令进行安装
    ```
    root@root:/home/aclruntime-aarch64# pip3 install -r ./requirements.txt
    ```

2. 确定是否设置了CANN包的环境变量，如果没有设置，请执行如下命令进行设置，注意CANN包路径如果安装在其他目录,需手动替换
    ```
    root@root:/home/aclruntime-aarch64# source  /usr/local/Ascend/ascend-toolkit/set_env.sh
    ```

3. 运行find_best_batchsize.sh 执行最优batch搜索命令操作

## 使用方法

 ### 运行指令
 onnx模型
```
bash  ./find_best_batchsize.sh --model_path /home/model/resnet50/resnet50.onnx --input_shape_str actual_input_1:batchsize,3,224,224 --soc_version Ascend310 --max_batch_num 10
```
pb模型
```
bash  ./find_best_batch.sh --model_path /home/lcm/tool/atc_bert_base_squad/save/model/BERT_Base_SQuAD1_1_BatchSize_None.pb --input_shape_str "input_ids:batchsize,384;input_mask:batchsize,384;segment_ids:batchsize,384" --soc_version "Ascend310" --max_batch_num 4
```
prototxt模型
```
bash  ./find_best_batchsize.sh --model_path /home/lhb/model/resnet50.prototxt --weight_path /home/lhb/model/resnet50.caffemodel --input_shape_str data:batchsize,3,224,224 --soc_version Ascend310 --max_batch_num 4
```

### 运行参数说明

| 参数名   | 说明                            |
| -------- | ------------------------------- |
| --model_path  | 推理模型路径，支持onnx、pb、prototx格式           |
| --weight_path  | 推理模型权因子文件路径。可选。只针对 caffe模型           |
| --max_batch_num | 最大搜索batch范围。值越大，搜索时间越长。默认值64      |
| --input_shape_str  | 推理模型输入节点 用于传入atc模型转换工具input_shape参数，格式为 name:shape;name1:shape1，同时需要将bath维度修改为 batchsize常量，以便用于工具进行遍历搜寻最佳batch。举例  输入节点信息为 actual_input_1:1,3,224,224  那么需要设置为 actual_input_1:batchsize,3,224,224        |
| --soc_version | 推理卡类型。支持昇腾310卡和710卡，可取值“Ascend310”、“Ascend710”                |
| --python_command | 搜索支持的python版本。默认取值python3.7      |
| --loop_count   | 推理次数。可选参数。默认1000 |
| --device_id   | 指定运行设备 [0,255]，可选参数，默认0 |
| --help| 工具使用帮助信息                  |

### 执行结果

以resnet50.onnx最优搜索结果为例：

```
best_batchsize:8 best_throughput:3716.05793807153
```