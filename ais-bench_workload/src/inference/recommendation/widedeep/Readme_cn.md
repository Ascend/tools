# Widedeep推理样例程序

本程序为ais-bench针对widedeep任务的推理python语言样例实现。对应的软件包为inference_recommendation_widedeep-Ais-Benchmark-Stubs-aarch64-1.0-.tar或inference_recommendation_widedeep-Ais-Benchmark-Stubs-x86_64-1.0-.tar

以下以aarch64平台操作为例说明。

## 依赖与安装

1. 调用如下命令安装依赖包，主要包括numpy, Pillow等

```
pip3 install -r requirements.txt
```

2. 另外还依赖tensorflow 1.15.0版本. 请确保能连接公开网络

   其安装方法，请参照《CANN 5.0.4 软件安装指南 01》， 网址：https://support.huawei.com/enterprise/zh/doc/EDOC1100234042/5d4f9eec

CANN驱动包版本>=5.0.3

3. 安装loadgenerator模块，即负载生成器。该部分以whl包方式提供，需要通过如下命令安装，要注意python版本与包的对应关系

```
pip3 install loadgen-0.0.1-cp36-cp36m-linux_aarch64.whl
或
pip3 install loadgen-0.0.1-cp37-cp37m-linux_aarch64.whl
```

4. 安装aclruntime模块。

```
pip3 install aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
```

5. 设置ascend-toolkit环境变量。对于不同的设备，请设置对应的路径的set_env.sh

```
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```

 对于A500环境，请执行

```
source /opt/ascend/nnrt/set_env.sh
```

6. 编译获取benchmark二进制工具

根据 [benchmark推理](https://github.com/Ascend/cann-benchmark/tree/master/infer) 页面构建benchmark工具二进制。在测试目录创建work目录，并将benchmark二进制拷贝到work目录下。

## 运行

1. 修改配置文件

+ 修改config/config.sh

```
PYTHON_COMMAND  设置运行的python命令
PROFILE         支持的场景
MODEL_PATH      om模型路径
CACHE_PATH      本地缓存路径
BATCH_SIZE      om模型对应的batchsize。默认1
DATASET_PATH    数据集路径
DEVICE_ID       推理执行卡序号。默认0卡
DEBUG           调试开关是否开启，默认不开启
```

说明：PROFILE目前支持的场景有：defaults、deeplabv3-tf_voc2012

+ 修改code/config.json
  将“Mode”字段为“inference"

2. ais-bench-stubs运行有两种方式。 实际测试中执行离线测试即可

+ 联机测试：直接执行，不带参数，会连接远程服务器
+ 离线测试：增加test参数，执行 ./ais-bench-stubs test命令，本地运行, 不联机
说明： 程序运行过程中会出现类似 “WARNING: tensorflow ......is deprecated and will be removed in a futrue version.”，此提示是tensorflow软件提示的API兼容的告警。该告警是对您使用的tensorflow软件API兼容性问题的正常提示，不影响本工具的正常使用
## 模型获取与转换指南

本样例使用的widedeep原始模型路径如下：
https://github.com/Ascend/ModelZoo-TensorFlow/tree/master/ACL_TensorFlow/contrib/recommendation/WideDeep_for_ACL
