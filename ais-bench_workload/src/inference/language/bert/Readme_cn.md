# bert推理样例程序
本程序为ais-bench针对bert任务的推理python语言样例实现。对应的软件包为inference_language_bert-Ais-Benchmark-Stubs-aarch64-1.0-.tar

## 依赖与安装
1. 调用如下命令安装依赖包，主要包括transformers, tensorflow, tokenization等
```
pip3 install -r requirements.txt 
```
2. 安装loadgenerator模块，即负载生成器。该部分以whl包方式提供，需要通过如下命令安装，要注意python版本与包的对应关系
```
pip3 install loadgen-0.0.1-cp36-cp36m-linux_x86_64.whl
或
pip3 install loadgen-0.0.1-cp37-cp37m-linux_x86_64.whl
```
3. 安装aclruntime模块。
```
pip3 install aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
```
4. 设置ascend-toolkit环境变量。
```
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```
## 运行  
1. 修改配置文件 config/config.sh

```
PYTHON_COMMAND  设置运行的python命令  
PROFILE         支持的场景  
MODEL_PATH      om模型路径  
BATCH_SIZE      om模型对应的batchsize  
DATASET_PATH    数据集路径  
VOCAB_FILE      vocab.txt文件路径  
```

2. 执行 ./ais-bench-stubs test命令用于离线测试。  
3. 如果需要联机Tester测试，请配置好config.json后，然后运行 ./ais-bench-stubs  

## 模型获取与转换指南
本样例使用的bert原始模型路径如下：
https://github.com/google-research/bert

更改原始模型的输入batchsize，需要使用ATC转换工具，参考文档：
https://support.huaweicloud.com/adevg-A800_3000_3010/atlasdevelopment_01_0034.html