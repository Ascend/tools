## 基于ModelArts的集群训练Ais-Bench接入

### 训练背景
训练执行人需要提前熟悉云环境modelarts训练相关流程，包括云环境用户注册登录、obs配置、modelarts训练作业执行流程及相关操作。
本文假设读者已经熟悉云环境modelarts操作。
### 整体流程

```sequence
本地侧->>ModelArts侧: 传递训练参数，拉起训练
ModelArts侧->>OBS侧: 请求下载训练代码
OBS侧->>ModelArts侧: 下载代码
ModelArts侧->>OBS侧: 请求下载数据集
OBS侧->>ModelArts侧: 下载数据集
ModelArts侧->>ModelArts侧: 执行训练
ModelArts侧->>OBS侧: 上传throughput/accuracy数据
ModelArts侧->>本地侧: 训练完成
本地侧->>OBS侧: 请求下载throughput/accuracy数据
OBS侧->>本地侧: 下载数据
本地侧->>Tester: 上报数据及运行结果
```

整体流程如上图所示，大致可分为3个步骤：

1. 用户在本地配置训练任务信息
2. 用户在本地拉起ais-bench-stubs二进制，整个训练过程和数据统计过程在ModelArts侧完成并上传OBS
3. ais-bench-stubs从OBS上获取统计数据，并上报给Tester

### 训练代码来源

本例中训练代码来自于mindspore的model_zoo：

https://gitee.com/mindspore/models.git   目录： models/official/nlp/bert
同时进行了一定的适配修改，主要适配点是适配ModelArts、数据统计上传

### 环境依赖

1. 本程序运行需依赖联网的linux环境。

    如无linux设备环境，可以在windows上开启wsl linux子系统。安装说明请参考[官网链接](https://docs.microsoft.com/zh-cn/windows/wsl/install)，

    同时本程序也可以选择modelarts中的notebook作为运行系统来运行程序。  请参考官网链接  [创建Notebook实例](https://support.huaweicloud.com/devtool-modelarts/devtool-modelarts_0004.html ) 和 [打开Notebook实例](https://support.huaweicloud.com/devtool-modelarts/devtool-modelarts_0005.html  )

2. windows10以上环境WSL2中运行modelarts时，请更新config.sh中环境变量PYTHON_COMMAND为WSL2中的实际python版本

3. 本程序需要安装 easydict程序包
    ```
    pip3 install easydict
    ```

4. 安装modelarts sdk程序包,参考如下网页
https://support.huaweicloud.com/sdkreference-modelarts/modelarts_04_0004.html#modelarts_04_0004__section16657165520146


5. 如果当前测试需要更新cann包，需要在训练主程序py文件同级目录（code/code）增加ma-pre-start.sh脚本，并增加对应的run包文件。

   ma-pre-start.sh内容类似以下内容：
   ```BASH
    #!/bin/bash
    set -x
    echo "Start to intall the run package"
    LOCAL_DIR=$(cd "$(dirname "$0")";pwd)
    echo $LOCAL_DIR

    TRAIN_PY_PATH=$(readlink -f `find ./ -name run_pretrain.py`)
    BASE_PATH=`dirname $TRAIN_PY_PATH`

    pip install $BASE_PATH/run/protobuf*.whl
    pip install $BASE_PATH/run/mindspore_ascend*.whl
    echo "replace origin mindspore packet!!! done ret:$? !!!"

    sudo chmod +x $BASE_PATH/run/*.run
    CANN_RUN_PACKET=`find $BASE_PATH/run/ -name Ascend-cann-nnae*.run`
    sudo $CANN_RUN_PACKET --upgrade
    echo "replace origin CANN_RUN_PACKET!!!: $CANN_RUN_PACKET done ret:$? !!!"

    # env set
    export GLOG_v=3
    export ASCEND_GLOBAL_LOG_LEVEL=3
    export ASCEND_GLOBAL_EVENT_ENABLE=0
    export ASCEND_SLOG_PRINT_TO_STDOUT=0

    set +x

   ```

   备注：
   通过修改ma-pre-start.sh文件中“GLOG_v”和“ASCEND_GLOBAL_LOG_LEVEL”的变量值，可以更新日志的级别。
   + GLOG日志级别 INFO、 WARNING、 ERROR、FATAL对应的值分别为0、1、2、3.
   + ASCEND_GLOBAL_LOG_LEVEL日志级别DEBUG、INFO、WARNING、ERROR、NULL对应的值分别为0、1、2、3、4.

5. 请咨询modelarts所在云环境的运维，获取该云相关服务（obs、modelarts、swr）域名和IP的映射关系并写入/etc/hosts, 
   
   比如武汉云相关服务obs、modelarts、swr域名映射关系如下：
   
   ```bash
   58.48.42.19 obs.cn-central-221.ovaijisuan.com
   58.48.42.193 modelarts.cn-central-221.ovaijisuan.com
   58.48.42.198 swr.cn-central-221.ovaijisuan.com
   ```
   
   注意： 如果在notebook中运行，不需要设置该项 

### 配置文件详解

配置文件用于配置该次训练任务所需的信息，

#### config.sh配置文件

位于 程序包路径/code/config/config.sh 

**	PYTHON_COMMAND**需设置为为实际运行python版本

**	SINGLESERVER_MODE** 单服务器模式指运行n个设备。但是运行是各自设备进行单设备8卡进行业务训练，默认不开启。

如果需要打开该模式 请增加如下命令 export SINGLESERVER_MODE=True

#### modelarts配置文件

位于Ais-Benchmark-Stubs-x86_64/code/config/modelarts_config.py，填写指导如下：

​		**access_config访问配置：**

​		主要包含 ak sk、obs等配置信息，需联系运维同事获取，详细参数强参考配置文件中描述信息。

​		**session_config节点配置**

​		超参配置参考

resnet 1.3
```BASH
    'hyperparameters': [
        {'label': 'enable_modelarts', 'value': 'True'},
        {'label': 'distribute', 'value': 'true'},
        {'label': 'epoch_size', 'value': '2'},      # 训练的epoch数 优先级低于train_steps，如果存在train_steps以此为准，否则以epoch_size为准
        {'label': 'enable_save_ckpt', 'value': 'true'},
        {'label': 'enable_lossscale', 'value': 'true'},
        {'label': 'do_shuffle', 'value': 'true'},
        {'label': 'enable_data_sink', 'value': 'true'},
        {'label': 'data_sink_steps', 'value': '100'},
        {'label': 'accumulation_steps', 'value': '1'},
        {'label': 'save_checkpoint_steps', 'value': '100'}, #表示训练的保存ckpt的step数 建议与train_steps保持一致
        {'label': 'save_checkpoint_num', 'value': '1'},
        {'label': 'train_steps', 'value': '100'},       # 表示训练的step数
        {'label': 'bert_network', 'value': 'large_acc'},
    ],
```


resnet 1.5以上

```BASH
    'hyperparameters': [
        {'label': 'config_path', 'value': 'pretrain_config_Ascend_Boost.yaml'},
        {'label': 'enable_modelarts', 'value': 'True'},
        {'label': 'distribute', 'value': 'true'},
        {'label': 'epoch_size', 'value': '2'},
        {'label': 'enable_save_ckpt', 'value': 'true'},
        {'label': 'enable_lossscale', 'value': 'true'},
        {'label': 'do_shuffle', 'value': 'true'},
        {'label': 'enable_data_sink', 'value': 'true'},
        {'label': 'data_sink_steps', 'value': '100'},
        {'label': 'accumulation_steps', 'value': '1'},
        {'label': 'save_checkpoint_steps', 'value': '99'},
        {'label': 'save_checkpoint_num', 'value': '1'},
        {'label': 'train_steps', 'value': '100'},
    ],
```


### 训练流程
解压modelarts训练测试包，进入解压文件夹，配置好相关配置文件后，执行`./ais-bench-stubs test`，进行训练。整个训练过程，需要保持网络通畅。WSL2和linux环境执行命令一致。


### 中断和停止训练
+ 云上modelarts界面操作  
在云环境modelarts服务“训练管理”->“训练作业”界面，点击正在运行的job链接并进入。在执行job界面，点击“更多操作”按钮，激活下拉菜单，在上下文菜单中点击“停止”，即可终止运行的job。
+ 本地停止方法，如下操作即可。该操作可以停止掉配置文件中job_name指示的最新一个作业版本
```
[root@node66 ]# ls
ais-bench-stubs  code  log  result
[root@node66 code]# python3  ./code/common/train_modelarts.py  --action stop
jobname:aisbench-debug jobid:3043 preversionid:13231 jobstatus:JOBSTAT_RUNNING stop status:{'is_success': True}
```