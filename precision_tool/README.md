# 精度问题分析工具

## 功能介绍
### 简介
该工具包提供了精度比对常用的功能，当前该工具主要适配Tensorflow训练场景

对于常用功能基本可以做到一键操作，同时提供Dump数据/图信息的交互式查询和操作入口

推理场景可直接使用[推理一键式全流程精度比对](https://gitee.com/ascend/tools/tree/master/msquickcmp) 工具
### 主要功能
#### 已完成功能
1. 简化脚本修改【手动/半自动】
2. TF标杆数据生成【自动/半自动】
3. 算子溢出检测分析【自动】
4. 开启GE图Dump和图解析【自动】
5. 开启数据Dump并进行全网比对【自动】
6. 查询算子列表/节点信息【手动】
7. 查询/解析Dump数据信息【手动】
8. 数据比对【手动】
#### TODO
1. NPU单算子自验证【自动/手动】
2. UB融合/图融合开启关闭分析【自动/手动】
### 工具获取
1. 下载压缩包的方式获取
   将https://gitee.com/ascend/tools 以压缩包形式下载
2. 使用git命令方式获取
3. 移动 tools/precision_tool 子目录至训练工作目录
### 安装python3三方依赖
```shell
pip3 install rich readline pexpect scipy graphviz
# ubuntu/Debian
sudo apt-get install graphviz
# fedora/Centos
sudo yum install graphviz
```
### 工具执行依赖
* 一般直接在NPU训练环境上部署该脚本，环境上能够正常执行CPU和NPU训练脚本
* 该工具基于**NPU的计算图**，**NPU的DUMP数据**，**NPU的溢出检测数据**，**TF的计算图meta文件**，**TF的DUMP数据**进行数据解析和分析。
这几类依赖数据可以通过以下方式获取：
#### 1. NPU的计算图获取
```注意：NPU的Dump数据和计算图存在一定的对应关系，最好同时获取（不修改代码和环境版本的情况下分开获取也可以）```
1. 参考迁移指导中的修改配置，执行NPU脚本，并将获取到的图转存至precision_data图目录
   ```shell
   export DUMP_GE_GRAPH=2
   export DUMP_GRAPH_LEVEL=3
   export DUMP_GRAPH_PATH=./precision_data/graph/all
   # 未配置DUMP_GRAPH_PATH时，图文件将保存在脚本执行目录，可以直接转存至precision_data目录
   mkdir -p ./precision_data/graph/all && mv ge_proto_*.txt ./precision_data/graph/all/
   ```
2. 使用precision_tool中提供的辅助命令行执行训练脚本，将自动配置以上环境变量并执行训练任务
   ```shell
   # 注意：避免在自定义的训练脚本中unset上述DUMP GRAPH相关的环境变量
   python3.7.5 precision_tool/cli.py npu_dump "sh run_train.sh param1 param2"
   ```
#### 2. NPU的DUMP数据获取
1. 参考[精度比对工具使用指南](https://support.huaweicloud.com/developmenttg-cann330alphaXtraining/atlasacctrain_16_0004.html) 修改训练脚本。
   执行训练脚本，并将dump的数据拷贝到【precision_data/dump/npu/】目录
2. 在训练脚本中**import precision_tool.tf_config**，并使用precision_tool中提供的辅助命令行执行训练脚本 
    ``` python
    # 引用 precision_tool/tf_config.py
    import precision_tool.tf_config as npu_tf_config
    
    # 如果使用的是Estimator
    npu_config = NPURunConfig(dump_config=npu_tf_config.estimator_dump_config)
    
    # 如果使用的是session.run方式，输入config可选，填入可以在原先的config上新增Dump配置项
    sess = tf.Session(config=npu_tf_config.session_dump_config(config))
    ```
    ```shell
    python3.7.5 precision_tool/cli.py npu_dump "sh run_train.sh param1 param2"
    ```
#### 3. NPU的溢出检测数据的获取
1. 参考[使用溢出检测工具分析算子溢出](https://support.huaweicloud.com/tensorflowdevg-cann330alphaXtraining/atlasmprtg_13_0037.html) 修改训练脚本，
   并将溢出数据拷贝至【precision_tool/dump/overflow/】目录
2. 在训练脚本中**import precision_tool.tf_config**，并按【2. NPU的DUMP数据获取】中修改训练代码，使用precision_tool中提供的辅助命令行执行训练脚本
    ```shell
    python3.7.5 precision_tool/cli.py npu_overflow "sh run_train.sh param1 param2"
    ```
#### 4. TF计算图Meta文件的获取
* 通过saver保存ckpt获取
    ```python
    # 修改CPU/NPU脚本
    with tf.Session() as sess:
       # do session.run()
       saver = tf.train.Saver()
       # 保存ckpt
       saver.save(sess, saver_dir)
    ```
#### 5. TF的DUMP数据获取
1. 参考[准备基于GPU/CPU运行生成的npy数据](https://support.huaweicloud.com/developmenttg-cann330alphaXtraining/atlasacctrain_16_0005.html) 
   获取CPU/GPU的TF数据，并拷贝至【precision/dump/cpu/】目录
2. 在CPU/GPU训练脚本中添加tf_debug代码，并使用precision_tool中提供的辅助命令行工具生成标杆DUMP数据
   ```python
    from tensorflow.python import debug as tf_debug
    
    # 如果使用的是Estimator,EstimatorSpec加入training_hooks
    estim_specs = tf.estimator.EstimatorSpec(training_hooks=[tf_debug.LocalCLIDebugHook()])    
    
    # 如果使用的session.run，则需要在session初始化后加入tf_debug代码
    sess = tf_debug.LocalCLIDebugWrapperSession(sess, ui_type="readline")
   ```
   ```shell
   python3.7.5 precision_tool/cli.py tf_dump "sh cpu_train.sh param1 param2"
   ```
## 使用说明
1.  配置文件precision_tool/config.py（正常默认即可）
    ```python
    # 如果需要dump特定曾的数据，则可以修改以下配置项
    # 一般对比分析dump首层即可
    # Dump config '0|5|10'
    TF_DUMP_STEP = '0'
    
    # 融合开关配置，可以再该配置文件中配置融合开关的开启和关闭，使用方法参考以下文档：
    # https://support.huaweicloud.com/tensorflowdevg-cann330alphaXtraining/atlastfadapi_07_0005.html
    FUSION_SWITCH_FILE = './precision_tool/fusion_switch.cfg'
    
    # 依赖run包中的atc和msaccucmp.pyc工具，一般在run包安装目录，配置到父目录即可
    # 默认run包安装在/usr/local/Ascend，可以不用修改。指定目录安装则需要修改
    # parent dir path of msaccucmp.pyc and atc, usually run package dir
    CMD_ROOT_PATH = '/usr/local/'
    
    # ASCEND Log Path
    ASCEND_LOG_PATH = '/root/ascend/log/plog/'
    
    # 日志级别及数据分析目录设置
    # TOOL CONFIG
    LOG_LEVEL = "NOTSET"
    DATA_ROOT_DIR = './precision_data'
    ```
2. 启动脚本（交互命令行）
    ```shell
    python3 ./precision_tool/cli.py 
    ```
### 非交互模式命令
1. tf_dump [start tf cpu script command]
    ```shell
    # 启动tf训练脚本，Dump CPU标杆数据
    # 需要配合上述tf_debug修改使用，能够Dump出第一个step的所有Tensor数据
    # 也可以在GPU/CPU环境上单独部署脚本执行该命令，将数据目录precision_data/dump/cpu 拷贝到NPU环境分析
    python3.7.5 precision_tool/cli.py tf_dump 'python3 LeNet_cpu.py'
    ```
2. npu_dump [start npu script command]
    ```shell
    # 启动npu训练脚本，图dump及数据dump
    # 需要配合上述precision_tool/tf_config.py 使用
    python3.7.5 precision_tool/cli.py npu_dump 'python3 LeNet_npu.py'
    ```
   
3. npu_overflow [start npu script command]
    ```shell
    # 启动npu训练脚本，进行溢出检测
    # 需要配合上述precision_tool/tf_config.py 使用
    python3.7.5 precision_tool/cli.py npu_overflow 'python3 LeNet_npu.py'
    ```
   
### 交互模式命令
3. ac (-c)
    ```shell
    # auto check. 自动化检测命令
    # 列出Fusion信息;解析算子溢出信息;(-c)进行全网比对
    PrecisionTool > ac -c
    ```
4. run [command]
    ```shell
    # 不退出交互命令环境执行shell命令，与内置命令不冲突的可以直接执行，否则需要加run前缀
    PrecisionTool > run vim cli.py
    PrecisionTool > vim cli.py
    ```

5. ls -n [op_name] -t [op_type]
    ```shell
    # 通过[算子名]/[算子类型]查询网络里的算子，模糊匹配
    PrecisionTool > ls -n conv1 -t Mul
    [MatMulV2] LeNet/conv1/Matmul
    ```

6. ni (-n) [op_name]
    ```shell
    # 通过[算子名]查询算子节点信息
    PrecisionTool > ni LeNet/conv1/Matmul
    ```
   
7. pt (-n) [*.npy]
    ```shell
    # 查看某个dump数据块的数据信息
    PrecisionTool > pt MatMulV2.LeNet_conv1_Matmul.17.6.16160712863169.output.npy
    Array: [[xxx][xxx]
    =============
    Shape: (2, 3)
    Dtype: float32
    Max:  214.3
    Min: -200.3
    Mean: 100.4
    Path: ./precision_data/dump/decode/MatMulV2.LeNet_conv1_Matmul.17.6.16160712863169.output.npy
    TxtFile:./precision_data/dump/decode/MatMulV2.LeNet_conv1_Matmul.17.6.16160712863169.output.npy.txt
    ```

8. cp (-n) [left *.npy] [right *.npy] -p [print num] -al [atol] -rl [rtol]
    ```shell
    # 对比两个tensor的数据
    # -p 指定输出的错误数据的个数及前多少个数据
    # -al/rl 指定相对误差的参数,在两个场景中用到
    #   1. np.allclose(left, right, atol=al, rtol=rl)
    #   2. err_cnt += 1 if abs(data_left[i] - data_right[i]) > (al + rl * abs(data_right[i]))
    PrecisionTool > cp left.npy right.npy -p 20 -al 0.001 -rl 0.001
    Error Item Table                Top Item Table
    -----------------------    -----------------------
    |_____________________|    |_____________________|
    SrcFile: ./precision_data/dump/decode/left.npy
    DstFile: ./precision_data/dump/cpu/right.npy
    NumCnt: 4000
    AllClose: True
    ConSim: 0.9999
    ErrorPer: 0.01 (rl= 0.001, al= 0.001)
    ```
### TF脚本修改参考

```python
# 打印动态Scale的Loss值
loss_scale_manager = ExponentialUpdateLossScaleManager()
scale_v = sess.run([loss_scale_manager.get_loss_scale()])
print(">>> Current Loss Scale >>> ", scale_v)


with tf.Session() as sess:
   # do session.run()
   saver = tf.train.Saver()
   # 保存ckpt
   saver.save(sess, saver_dir)
   # ...
   # 从ckpt恢复
   saver.restore(sess, saver_dir)
   # ...
   # 保存Tensorboard
   summary_writer = tf.summary.FileWriter(logdir=log_dir, graph=sess.graph)

```
#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request