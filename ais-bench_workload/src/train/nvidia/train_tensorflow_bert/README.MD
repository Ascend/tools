## 1. 背景

### 1.1 bert模型基准来源：  

https://github.com/google-research/bert/tree/master  

### 1.2 训练指标计算说明

- accuracy 训练结果评估中masked_lm_accuracy的值
- throughput_ratio 计算公式--train_batch_size * num_train_steps / （end - real_step_start_time）。
  公式说明：
  + train_batch_size 训练批数
  + num_train_steps 训练步数
  + real_step_start_time 训练开始时间。该时间是单纯训练时间，不包括训练数据加载内存、加载device、训练热身等辅助时间，因此忽略了训练前2步耗费的时间
  + end 训练结束时间


## 2.训练过程

### 2.1 训练准备

#### 2.1.1 环境要求
+ python3.7.5、tensorflow 1.13(gpu版)、anconda3。建议在conda环境训练
+ 可以在线拉取github.com的代码
+ 执行nvidia-smi，检查当前设备是否使用。若使用请终止相关进程
#### 2.1.2 bert模型下载
到bert[官网](https://github.com/google-research/bert) "Pre-trained models"小节选择合适的bert模型下载到本地并解压使用。

bert large配置包信息： 
+ 配置包规格：BERT-Large, Uncased: 24-layer, 1024-hidden, 16-heads, 340M 
+ 压缩包名称：uncased-L-24_H-1024_A-16.zip
+ 下载地址：https://storage.googleapis.com/bert_models/2018_10_18/uncased_L-24_H-1024_A-16.zip

说明：本训练用到该配置包中的bert_config.json、vocab.txt文档。其它暂不涉及。


### 2.2 修改预训练执行配置
#### 2.2.1 修改配置文件
执行`vim Ais-Bench-Stubs-aarch64/code/config/config_bert.sh`,修改配置。

+ BERT_CONFIG_DIR 修改为bert 配置目录
+ TRAIN_STEPS    训练步数
+ CUDA_VISIBLE_DEVICES 修改为指定设备ID。只有一位数字时为单卡训练。多卡同时使用时，逗号间隔，比如“0,1"

#### 2.2.2 修改run.sh
执行`vim Ais-Bench-Stubs-aarch64/code/run.sh`, 适当修改train_run_cmd变量中预训练参数。
### 2.3. 执行训练测试
进入工作目录Ais-Bench-Stubs-aarch64, 执行以下指令进行本地训练：
```
cd Ais-Bench-Stubs-aarch64
rm -rf output

./ais-bench-stubs test
```


### 2.4 本地训练结果

训练过程，屏幕会有日志输出。训练结束会打印如下2个信息：
#### 2.4.1 train_result_info信息
该信息包括了精度accuracy和吞吐率throughput_retio。

```
[2021-8-4 12:35:39][INFO]train_result_info: {
"accruacy" : "0.05533597",
"throughput_ratio" : "2.456748253218857",
...
}
```
#### 2.4.1 tensorflow回调函数打印的吞吐率
```
actual callback_throught_rate: 2.7236
```


### 2.5.训练执行注意事项
+ 训练环境需要能联网，方便在线下载代码和bert模型
+ 预训练参数max_seq_length越大，越容易造成预训练过程的资源耗尽问题。请选择合适参数
+ 中断训练时，需要执行nvidia-smi，查到当前执行的进程ID，强行杀死该进程，避免影响下一次训练
+ 每次训练前清空run_pretrain.py执行的output目录（ais-bench-stubs同级目录），会确保预训练时tensorflow日志sample/sec打印出来
