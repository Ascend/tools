## 1. 背景

### 1.1 resnet模型基准来源：  

https://github.com/tensorflow/models/tree/r1.13.0/official/resnet

### 1.2 训练指标计算说明

- accuracy 训练结果中accuracy的值
- throughput_ratio 计算公式--imagenet数据集图片数目 * epoch_size / 训练时间（包括训练结果评估时间）

-- imagenet数据集图片数目 全部数据集  1280000个

## 2.训练过程

### 2.1 训练准备

#### 2.1.1 环境要求
+ python3.7.5、tensorflow 1.13(gpu版)、anconda3
+ 执行nvidia-smi，检查当前设备是否使用。若使用请终止相关进程
#### 2.1.2 imagenet tensorflow数据集下载
到resnete官网下载imagenet tensorflow类型的数据集

### 2.2 修改预训练执行配置
执行`vim Ais-Bench-Stubs-aarch64/code/config/config_imagenet2012.sh`, 修改配置。
+ TRAIN_DATA_PATH 修改为resnet训练数据集目录
+ EPOCH_SIZE epoch 数目
+ RESNET_SIZE resnet层数
+ CUDA_VISIBLE_DEVICES  指定设备进行训练。"1"表示仅使用设备1训练。"0,1"，表示同时设备0和1进行训练。

### 2.3. 执行训练测试
进入工作目录, 执行以下指令进行本地训练：
```
cd Ais-Bench-Stubs-aarch64

./ais-bench-stubs test
```

### 2.4 本地训练结果

训练过程，屏幕会有日志输出。训练结束会打印train_result_info信息，包括了精度accuracy和吞吐率throughput_ratio。

```
[2021-8-3 14:35:39][INFO]train_result_info: {
"accruacy" : "0.11714",
"throughput_ratio" : "76.54648206089946",
...
}
```
说明：当前结果是基于 P100 单卡的 1个epoch的训练结果


### 4.5.训练执行注意事项
+ 训练环境需要能联网，方便在线下载代码和resnet数据集
+ 中断训练时，需要执行nvidia-smi，查到当前执行的进程ID，强行杀死该进程，避免影响下一次训练
