# bert推理样例程序
本程序为ais-bench针对bert任务的推理python语言样例实现。对应的软件包为inference_language_bert-Ais-Benchmark-Stubs-aarch64-1.0-.tar

## 依赖与安装
1. 调用如下命令安装依赖包，主要包括transformers, tensorflow, tokenization等.请确保能连接公开网络
```
pip3 install -r requirements.txt
```
2. 安装loadgenerator模块，即负载生成器。该部分以whl包方式提供，需要通过如下命令安装，要注意python版本与包的对应关系
```
pip3 install loadgen-0.0.1-cp36-cp36m-linux_aarch64.whl
或
pip3 install loadgen-0.0.1-cp37-cp37m-linux_aarch64.whl
```
3. 安装aclruntime模块。
```
pip3 install aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
```
4. 设置ascend-toolkit环境变量。对于不同的设备，请设置对应的路径的set_env.sh
```
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```
对于A500环境，请执行
```
source /opt/ascend/nnrt/set_env.sh
```

## 运行
1. 修改配置文件
+ 修改config/config.sh

```
PYTHON_COMMAND  设置运行的python命令
PROFILE         支持的场景
MODEL_PATH      om模型路径
BATCH_SIZE      om模型对应的batchsize
DATASET_PATH    数据集路径
VOCAB_FILE      vocab.txt文件路径
DEVICE_ID       推理执行卡序号
```
说明：PROFILE目前支持的场景有：defaults、bert_large_squad、bert_large_masked_lm

+ 修改code/config.json
将“Mode”字段为“inference"

2. ais-bench-stubs运行有两种方式。 实际测试中执行离线测试即可

+ 联机测试：直接执行，不带参数，会连接远程服务器
+ 离线测试：增加test参数，执行 ./ais-bench-stubs test命令，本地运行, 不联机

3. 动态分档和动态shape配置
针对动态分档类模型和动态shape类模型，需要在配置文件中config/config.sh中修改
注意BATCH_SIZE必须要设置的，默认为1
+ 动态batch
增加 export DYM_BATCH=1 设置指定的batchsize
+ 动态宽高
增加 export DYM_HW="224,224" 设置指定的宽高
+ 动态Dims
增加 export DYM_DIMS="actual_input_1:1,3,224,224" 设置指定的dims 该设置格式跟atc命令转换一致

## 模型获取与转换指南
本样例使用的bert原始模型路径如下：
https://github.com/google-research/bert

ATC转换工具，参考文档：
https://support.huaweicloud.com/adevg-A800_3000_3010/atlasdevelopment_01_0034.html
