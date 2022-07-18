# ais-bench_workload_train_offline线下训练说明文档



[TOC]

## 简介

ais-bench标准化性能测试软件,又称AI Server Benchmark软件，是根据AI标准（IEEE 2937及 T/CESA 1169-2021）对AI服务器进行性能测试的工具软件。

本文主要介绍基于ais-bench软件，适配华为模型负载，实现训练业务性能测试的方法。包含程序包构建、配置、运行等流程。线下训练是指非modelarts云上训练场景，包括单卡、单机、线下集群、容器集群等场景。

## 构建

请参考 《ais-bench_workload负载程序包构建教程》

## 测试

### 环境准备

1. Atals训练设备
2. 安装好CANN软件包和Mindspore框架等软件，并能正常运行测试程序。

### 数据集准备

举例resnet模型需要imagenet数据集，bert模型需要wiki数据集，该数据集需要提前下载到运行设备中。

### 负载测试包准备：

在《构建》章节中会生成对应的负载测试包。

#### 负载包选择

注意负载程序包会包含不同架构的测试包，请根据本地运行设备的架构进行选择。

- 比如如果本地运行环境是x86架构，那么请选择xxxx_x86_64.tar.gz程序包。
- 如果本地运行环境是aarch64的，请选择xxxx_aarch64_xxx.tar.gz程序包。

本文以mindspore框架r1.3版本的resnet模型进行举例，本地运行设备如果是aarch64环境，那么选择train_huawei_train_mindspore_resnet-Ais-Benchmark-Stubs-aarch64-1.0-r1.3.tar.gz。

**拷贝解压**

登录本地运行设备，将负载测试包拷贝到指定的文件夹。

登录本地运行设备控制台，找到对应测试包。执行解压操作。

```
tar xvf train_huawei_train_mindspore_resnet-Ais-Benchmark-Stubs-aarch64-1.0-r1.3_modelarts.tar.gz
```

执行如下命令，会看到解压后包含如下内容

```
root# ls
ais-bench-stubs  code  log  result
```

### 配置

配置信息是比较重要的，需要用户仔细审视。

#### config.json  ais-bench工具配置文件 

位于基准目录/code/config.json 主要填写ais-bench测试的具体参数与tester服务器具体信息，**本地测试模式下不需要填写，只要网络测试模式下才需要填写。**

#### config.sh 通用负载配置文件

位于 基准路径/code/config/config.sh 主要包括基准配置信息。请打开配置文件，仔细填写。

**注意**

1. 如果非单卡操作，必须要生成rank_table文件并配置RANK_TABLE_FILE变量。rank_table文件生成请参考附录
2. 如果是多机操作，必须要生成节点信息文件并配置NODEINFO_FILE变量。请参考附录
3. 如果是多机操作，请务必设置集群节点的秘钥认证，直接使用密码可能有安全风险。请参考附录

### 启动运行

配置好指定配置文件后，执行`./ais-bench-stubs test`，即可启动本地运行模式，执行性能测试。

整个训练过程，需要保持网络通畅。

## 附录

### **日志级别设置：**

如果需要设置日志几倍，请在 基准目录/common/mindspore_env.sh中设置相关变量。

```
export GLOG_v=3
```

备注：

+ GLOG日志级别 INFO、 WARNING、 ERROR、FATAL对应的值分别为0、1、2、3

### rank_table文件生成与实例

单机或集群rank_table文件生成方法，请参照[这里](https://gitee.com/mindspore/models/tree/master/utils/hccl_tools#merge_hccl)。

示例：rank_table_16p_64_66.json

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

### ssh节点文件格式

运行设备大于1个设备，则需要运行设置ssh节点文件。说明节点信息
示例：ssh64_66.json

```bash
{
  "cluster": {
    "90.90.66.64": {    # 节点ip 必须与ranktable中的server_id一一对应
      "user": "root",   # 用户名 免密可以不用设置
      "pd": "xxxx",     # 密码 免密不用设置
      "port":0          # 容器端口，默认22。可以不设置。本行缺失时，表示测试在该节点本地（非容器）运行，设置时表示在容器中运行并提供指定端口访问能力
    },
    "90.90.66.66": {
      "user": "root",
      "pd": "xxxx",
      "port":1
    }
  }
}
```

**注意：该文件中的节点数目应与rank_table中的的节点数目一致。**

## 集群节点免密设置

设置密钥认证的参考操作如下：

+ ssh-keygen -t rsa -b 2048   # 登录管理节点并生成SSH Key。安全起见，建议用户到"Enter passphrase"步骤时输入密钥密码，且符合密码复杂度要求。建议执行这条命令前先将umask设置为0077，执行完后再恢复原来umask值。
+ ssh-copy-id -i ~/.ssh/id_rsa.pub `<user>`@`<ip>`   # 将管理节点的公钥拷贝到所有节点的机器上，`<user>`@`<ip>`替换成要拷贝到的对应节点的账户和ip。
+ 设置ssh代理管理ssh密钥，避免工具批量安装操作过程中输入密钥密码和节点密码
  ssh-agent bash   # 开启ssh-agent的bash进程
  ssh-add                # 向ssh-agent添加私钥

## FAQ