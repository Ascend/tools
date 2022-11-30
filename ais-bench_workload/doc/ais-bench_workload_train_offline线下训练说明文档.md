# ais-bench_workload_train_offline线下训练说明文档



[TOC]

## 简介

ais-bench标准化性能测试软件，又称AI Server Benchmark软件，是根据AI标准（IEEE 2937及 T/CESA 1169-2021）对AI服务器进行性能测试的工具软件。

本文主要介绍基于ais-bench软件，在离线环境对模型进行训练性能测试。离线环境是指非modelarts云上训练场景，当前主要适配单卡、单机、线下集群、容器集群场景。

## 使用前准备

### 环境

1. Atals训练设备（搭载Ascend NPU以及Ascend 910芯片等昇腾硬件环境），可以搭建单卡、单机、线下集群、容器集群场景，相关硬件产品文档请参见[昇腾硬件产品文档](https://www.hiascend.com/document?data=hardware)。
2. 根据需要测试的模型类型安装MindSpore或TensorFlow框架；参见《[CANN 软件安装指南](https://www.hiascend.com/document/detail/zh/canncommercial/51RC1/envdeployment/instg/instg_000002.html)》安装CANN软件包。MindSpore或TensorFlow框架需要根据《ais-bench_workload构建教程》所选择的模型版本来安装对应版本的框架。
3. 集群测试时需要安装依赖软件--sshpass，版本无要求。
4. 容器环境测试时，容器制作请参照《制作可ssh登录镜像ascend-mindspore-arm的方法》

### 数据集

下载相关模型数据集到运行设备任意目录下。例如resnet模型需要imagenet数据集，bert模型需要enwiki数据集。具体下载方式请至相关模型官网，本文不作详述。

### 软件包

请参见 《ais-bench_workload构建教程》，完成需要测试的模型对应的性能测试软件包构建。

#### 选择软件包

注意性能测试软件包会包含不同系统架构，请根据运行设备的系统架构进行选择。

- 比如运行设备的系统架构为x86_64架构，那么请选择xxxx_x86_64.tar.gz软件包。
- 比如运行设备的系统架构为aarch64架构，那么请选择xxxx_aarch64_xxx.tar.gz软件包。

本文以mindspore框架r1.3版本的resnet模型运行设备aarch64环境进行举例，选择train_huawei_train_mindspore_resnet-Ais-Benchmark-Stubs-aarch64-1.0-r1.3.tar.gz软件包。

#### 解压软件包

登录运行设备，将性能测试软件包拷贝到任意目录下，执行解压操作。

```
tar xvf train_huawei_train_mindspore_resnet-Ais-Benchmark-Stubs-aarch64-1.0-r1.3_modelarts.tar.gz
```

软件包解压后目录结构如下：

```
.
├── ais-bench-stubs  // 性能测试命令行工具，用于执行性能测试操作
├── code  // 性能测试代码包
│   ├── config  // 配置目录
│   │   ├── config.sh  // 离线训练性能测试配置文件
│   │   ├── mindspore_env.sh  // Mindspore框架模型测试时的环境变量，可根据实际需求补充环境变量
│   │   ├── modelarts_config.py  // 线上训练性能测试时配置
│   │   └── tensorflow_env.sh  // TensorFlow框架模型测试时的环境变量，可根据实际需求补充环境变量
│   ├── config.json  // tester服务器信息配置文件，配置后可自动将测试结果上报到tester服务器上。本地离线测试模式下不需要填写
│   ├── doc  // 指导文档存放目录
│   └── system.json  // 性能测试系统信息配置文件，仅当需要将测试结果上报到tester服务器时需要配置。本地离线测试模式下不需要填写
├── log  // 日志输出目录
├── README.md  // 离线性能测试指导
└── result  // 测试结果输出目录
```



## 离线训练性能测试操作

### 文件配置

#### 配置config.sh

config.sh通用负载配置文件，位于性能测试软件包解压路径/code/config/config.sh，主要包括离线训练性能测试操作的基本配置信息。

请在配置文件中根据注释说明填写.


**注意**

1. 非单卡环境下，必须要生成rank_table文件并配置RANK_TABLE_FILE变量。rank_table文件生成请参见“rank_table文件生成与实例”。
2. 集群环境下，必须要生成节点ssh信息文件并配置NODEINFO_FILE变量。节点ssh信息文件生成请参见“节点ssh信息文件”。
3. 集群环境下，直接使用ssh信息文件进行节点间的登录交互可能存在安全风险，可以设置集群节点的秘钥认证，提高安全性。请参见“集群节点免密设置”。

#### 配置config.json

config.json tester服务器信息配置文件，位于性能测试软件包解压路径/code/config.json，主要填写ais-bench测试的tester服务器具体信息，用于在完成性能测试后将测试结果上报到tester服务器上。若无须上报测试结果，可不配置。

#### 配置system.json

system.json 性能测试系统信息配置文件，位于性能测试软件包解压路径/code/system.json，主要填写ais-bench测试的运行环境系统信息，用于在完成性能测试后将运行环境系统信息作为测试结果的内容上报到tester服务器上。若无须上报测试结果，可不配置。

### 运行测试

完成配置文件配置后执行性能测试操作，本地测试命令如下：

```
./ais-bench-stubs test
```

连接tester服务器测试时，无需test参数。

## 附录

### **日志级别设置**

性能测试启动后，默认在性能测试软件包解压路径/log目录下输出日志。

如果需要设置日志级别，请在性能测试软件包解压路径/config目录下的mindspore_env.sh或tensorflow_env.sh文件中添加如下环境变量。

```
export GLOG_v=3
```

GLOG日志级别取值为：0（INFO）、1（WARNING）、2（ERROR）、3（FATAL）。

### rank_table文件生成与实例

单机或集群rank_table文件生成方法，请单击[芯片资源信息配置文件参考](https://support.huawei.com/enterprise/zh/doc/EDOC1100192402/a1885ca4)访问相关文档。

生成双机16卡的rank_table文件示例：rank_table_16p_64_66.json

```bash
{
    "version": "1.0",
    "server_count": "2",
    "server_list": [
        {
            "server_id": "90.90.66.64",
            "device": [
                {"device_id": "0", "device_ip": "192.100.61.14", "rank_id": "0"},
                {"device_id": "1", "device_ip": "192.100.62.14", "rank_id": "1"},
                {"device_id": "2", "device_ip": "192.100.63.14", "rank_id": "2"},
                {"device_id": "3", "device_ip": "192.100.64.14", "rank_id": "3"},
                {"device_id": "4", "device_ip": "192.100.61.15", "rank_id": "4"},
                {"device_id": "5", "device_ip": "192.100.62.15", "rank_id": "5"},
                {"device_id": "6", "device_ip": "192.100.63.15", "rank_id": "6"},
                {"device_id": "7", "device_ip": "192.100.64.15", "rank_id": "7"}
            ],
            "host_nic_ip": "reserve"
        },
        {
            "server_id": "90.90.66.66",
            "device": [
                {"device_id": "0", "device_ip": "192.100.61.16", "rank_id": "8"},
                {"device_id": "1", "device_ip": "192.100.62.16", "rank_id": "9"},
                {"device_id": "2", "device_ip": "192.100.63.16", "rank_id": "10"},
                {"device_id": "3", "device_ip": "192.100.64.16", "rank_id": "11"},
                {"device_id": "4", "device_ip": "192.100.61.17", "rank_id": "12"},
                {"device_id": "5", "device_ip": "192.100.62.17", "rank_id": "13"},
                {"device_id": "6", "device_ip": "192.100.63.17", "rank_id": "14"},
                {"device_id": "7", "device_ip": "192.100.64.17", "rank_id": "15"}
            ],
            "host_nic_ip": "reserve"
        }
    ],
    "status": "completed"
}
```

### 节点ssh信息文件

集群场景下执行性能测试时，需要设置节点ssh信息文件，用于在测试过程中节点之间的登录验证。

节点ssh信息文件由用户自行创建文件名格式类似于ssh64_66.json，按照如下示例格式进行配置。

示例：ssh64_66.json

```bash
{
  "cluster": {
    "90.90.66.64": {    # 节点IP，必须与rank_table文件中的server_id一一对应
      "user": "root",   # 节点登录用户名，完成集群节点免密设置可不配置
      "pd": "xxxx",     # 节点登录密码，完成集群节点免密设置可不配置
      "port":0          # 容器端口，默认22。可不设置。删除本参数或配置为22时，表示性能测试在默认22端口通信；设置具体端口号时，表示在容器或者设备中运行并提供指定端口访问能力

    },
    "90.90.66.66": {
      "user": "root",
      "pd": "xxxx",
      "port":1
    }
  }
}
```

**注意：该文件中的节点数目应与rank_table文件中的节点数目一致。**

### 集群节点免密设置

集群节点免密设置的参考操作如下：

1. 登录集群管理节点并生成SSH Key。

   ```
   ssh-keygen -t rsa -b 2048
   ```

   安全起见，建议用户到“Enter passphrase”步骤时输入密钥密码，且符合密码复杂度要求。建议执行该命令前先将umask设置为0077，测试完成后再恢复原来umask值。

2. 将管理节点的公钥拷贝到所有节点的机器上。

   ```
   ssh-copy-id -i ~/.ssh/id_rsa.pub <user>@<ip>
   ```

   <user>@<ip>替换成要拷贝到的对应节点的用户名和IP。

3. 设置ssh代理管理ssh密钥。

   ```
   ssh-agent bash   # 开启ssh-agent的bash进程
   ssh-add   # 向ssh-agent添加私钥
   ```

   避免工具批量安装操作过程中输入密钥密码和节点密码。



