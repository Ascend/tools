# Ais-Bench+Mindspore+widedeep使用说明

## 简介

AI Server Benchmark 是按《信息技术 人工智能 服务器系统性能测试规范》对人工智能服务器系统的性能进行性能评估的测试系统（测试套件），简称Ais-Bench软件。

## 使用前提

本程序包运行需要基于以下前提

1. Atlas 800-9000设备
2. 安装好CANN包和Mindspore对应版本。并可以运行正常mindspore测试程序。
3. 保存数据集和相关预处理文件等到设备中。

## 集群节点配置

如果运行设备大于1个设备，那么需要运行设置ssh节点文件。说明节点信息
{
"cluster": {
"90.90.66.62": {    # 节点ip 必须与ranktable中对应
"user": "root",   # 用户名 免密可以不用设置
"pd": "xx",  # 密码 免密不用设置
"port":0   # 端口 默认22  可以不用设置
},
"90.90.66.64": {
"user": "root",
"pd": "xx",
"port":1
}
}
}

## 集群节点免密设置

设置密钥认证的参考操作如下：
ssh-keygen -t rsa -b 2048   # 登录管理节点并生成SSH Key。安全起见，建议用户到"Enter passphrase"步骤时输入密钥密码，且符合密码复杂度要求。建议执行这条命令前先将umask设置为0077，执行完后再恢复原来umask值。
ssh-copy-id -i ~/.ssh/id_rsa.pub `<user>`@`<ip>`   # 将管理节点的公钥拷贝到所有节点的机器上，`<user>`@`<ip>`替换成要拷贝到的对应节点的账户和ip。

## 配置文件信息

> #python版本设置
> export PYTHON_COMMAND=python3.7
> #训练数据文件路径
> export TRAIN_DATA_FILE=/home/data/criteo/origin_data/mini_demo.txt

> 节点信息
> export RANK_SIZE=8
> export DEVICE_NUM=8

> #need if rank_size > 1
> export RANK_TABLE_FILE=/home/lcm/tool/rank_table_16p_62_64.json

> #cluster need for node info
> export NODEINFO_FILE=/home/lcm/tool/ssh64_66.json

说明：
配置文件默认是8卡训练。
单卡训练时，需要设置RANK_SIZE=1，DEVICE_NUM=1，且不能使用RANK_TABLE_FILE环境变量.
同时还请按需增加指定执行卡序号变量声明export SINGLE_CARD_INDEX。默认 SINGLE_CARD_INDEX=0，可以不显式声明。其它卡时需要显式声明，比如export SINGLE_CARD_INDEX=6
## FAQ

如果程序运行遇到错误--OSError: /lib/aarch64-linux-gnu/libgomp.so.1: cannot allocate memory in static TLS block，请执行以下命令可解决问题：
export LD_PRELOAD=$LD_PRELOAD:/usr/local/python3.7.5/lib/python3.7/site-packages/scikit_learn.libs/libgomp-d22c30c5.so.1.0.0
