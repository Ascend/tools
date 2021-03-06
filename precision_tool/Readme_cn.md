# 精度问题分析工具

## 功能介绍
### 简介
该工具包提供了精度比对常用的功能，当前该工具主要适配Tensorflow训练场景

对于常用功能基本可以做到一键操作，同时提供Dump数据/图信息的交互式查询和操作入口

推理场景可直接使用[推理一键式全流程精度比对](https://github.com/Ascend/tools/tree/master/msquickcmp) 工具
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
   将https://github.com/Ascend/tools 以压缩包形式下载
2. 使用git命令方式获取
3. 移动 tools/precision_tool 子目录至训练工作目录
### 安装python3三方依赖
```shell
pip3 install rich gnureadline pexpect scipy graphviz
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
```注意：NPU的Dump数据和计算图存在一定的对应关系，需要同时获取```
* 【推荐】方法一：使用precision_tool中提供的辅助命令行执行训练脚本，将自动配置以上环境变量并执行训练任务
   ```shell
   # 注意：避免在自定义的训练脚本中unset上述DUMP GRAPH相关的环境变量
   python3.7.5 precision_tool/cli.py npu_dump "sh run_train.sh param1 param2"
   ```
* 【不推荐】方法二：参考迁移指导中的修改配置，执行NPU脚本，并将获取到的图转存至precision_data图目录
   ```shell
   export DUMP_GE_GRAPH=2
   export DUMP_GRAPH_LEVEL=3
   export DUMP_GRAPH_PATH=./precision_data/graph/all
   # 未配置DUMP_GRAPH_PATH时，图文件将保存在脚本执行目录，可以直接转存至precision_data目录
   mkdir -p ./precision_data/graph/all && mv ge_proto_*.txt ./precision_data/graph/all/
   ```
#### 2. NPU的DUMP数据获取
* 【推荐】方法一：在训练脚本中**import precision_tool.tf_config**，并使用precision_tool中提供的辅助命令行执行训练脚本 
    ``` python
    # 引用 precision_tool/tf_config.py
    import precision_tool.tf_config as npu_tf_config
    
    # 如果使用的是Estimator
    dump_config=npu_tf_config.estimator_dump_config()
    npu_config = NPURunConfig(dump_config=dump_config)
    
    # 如果使用的是session.run方式，输入config可选，填入可以在原先的config上新增Dump配置项
    config = npu_tf_config.session_dump_config(config)
    sess = tf.Session(config)
    ```
    ```shell
    python3.7.5 precision_tool/cli.py npu_dump "sh run_train.sh param1 param2"
    ```
* 【不推荐】方法二：参考[精度比对工具使用指南](https://support.huaweicloud.com/developmenttg-cann330alphaXtraining/atlasacctrain_16_0004.html) 修改训练脚本。
   执行训练脚本，并将dump的数据拷贝到【precision_data/dump/npu/】目录
#### 3. NPU的溢出检测数据的获取（缺少该数据将无法展示溢出检测结果）
* 【推荐】方法一：在训练脚本中**import precision_tool.tf_config**，并按【2. NPU的DUMP数据获取】中修改训练代码，使用precision_tool中提供的辅助命令行执行训练脚本
    ```shell
    python3.7.5 precision_tool/cli.py npu_overflow "sh run_train.sh param1 param2"
    ```
* 【不推荐】方法二：参考[使用溢出检测工具分析算子溢出](https://support.huaweicloud.com/tensorflowdevg-cann330alphaXtraining/atlasmprtg_13_0037.html) 修改训练脚本，
   并将溢出数据拷贝至【precision_tool/dump/overflow/】目录

#### 4. TF的DUMP数据获取（缺少该数据无法使用数据比对功能）
* 【推荐】方法一：在CPU/GPU训练脚本中添加tf_debug代码，并使用precision_tool中提供的辅助命令行工具生成标杆DUMP数据
   ```python
    import precision_tool.tf_config as npu_tf_config
    
    # 如果使用的是Estimator,EstimatorSpec加入training_hooks
    estim_specs = tf.estimator.EstimatorSpec(training_hooks=[npu_tf_config.estimator_dump()])    
    
    # 如果使用的session.run，以下代码在为sess加上了tf_debug的wrapper
    sess = npu_tf_config.sess_dump(sess=sess)
   ```
   ```shell
   # 注意：TF dump数据的原理是使用tf_debug的print_tensor(pt)命令实现的，由于训练代码提供了非常灵活的run()接口，
   #      脚本无法感知用户需要dump的tensor在哪个run阶段，因此需要用户修改训练代码，在执行完正确的run后，立即退出。
   #      例如，修改代码只执行一个step的训练，根据代码中run的次数，会获取到1~N个离线tf_debug的dump目录
   #      precision_tool脚本会自动提取最后一个run阶段中出现的所有tensor作为标杆数据。
   python3.7.5 precision_tool/cli.py tf_dump "sh cpu_train.sh param1 param2"
   
   # 在precision_data/dump/cpu/ 目录会存放提取的tensor
   # 如果获取tensor不符合预期，可以检查下precision_data/dump/cpu_debug/目录, 只保留预期run阶段的tf_debug离线数据
   # 执行以下命令重新生成
   rm -rf precision_data/dump/cpu/* && python3.7.5 precision_tool/cli.py tf_dump
   ```
* 【不推荐】方法二：参考[准备基于GPU/CPU运行生成的npy数据](https://support.huaweicloud.com/developmenttg-cann330alphaXtraining/atlasacctrain_16_0005.html)
   获取CPU/GPU的TF数据，并拷贝至【precision/dump/cpu/】目录
#### 5. TF计算图Meta文件的获取（可选）
* 通过saver保存ckpt获取
    ```python
    # 修改CPU/NPU脚本
    with tf.Session() as sess:
       # do session.run()
       saver = tf.train.Saver()
       # 保存ckpt
       saver.save(sess, saver_dir)
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
    # 需要配合上述tf_debug修改使用，能够Dump出所有Tensor数据
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
   ╭──────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ [TransData][327] trans_TransData_1170                                                            │
   │  - [AI Core][Status:32][TaskId:327] ['浮点计算有溢出']                                           │
   │  - First overflow file timestamp [1619347786532995] -                                            │
   │  |- TransData.trans_TransData_1170.327.1619347786532995.input.0.npy                              │
   │   |- [Shape: (32, 8, 8, 320)] [Dtype: bool] [Max: True] [Min: False] [Mean: 0.11950836181640626] │
   │  |- TransData.trans_TransData_1170.327.1619347786532995.output.0.npy                             │
   │   |- [Shape: (32, 20, 8, 8, 16)] [Dtype: bool] [Max: True] [Min: False] [Mean: 0.07781982421875] │
   ╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
   ```
   
### 交互模式命令
1. ac (-c)
    ```shell
    # auto check. 自动化检测命令
    # 列出Fusion信息;解析算子溢出信息;(-c)进行全网比对
    PrecisionTool > ac -c
    ```
2. run [command]
    ```shell
    # 不退出交互命令环境执行shell命令，与内置命令不冲突的可以直接执行，否则需要加run前缀
    PrecisionTool > run vim cli.py
    PrecisionTool > vim cli.py
    ```

3. ls -n [op_name] -t [op_type]
    ```shell
    # 通过[算子名]/[算子类型]查询网络里的算子，模糊匹配
    PrecisionTool > ls -t Mul -n mul_3 -f TbeMulti
   [Mul][TbeMultiOutputFusionPass] InceptionV3/InceptionV3/Mixed_5b/Branch_1/mul_3
   [Mul][TbeMultiOutputFusionPass] InceptionV3/InceptionV3/Mixed_5c/Branch_1/mul_3
   [Mul][TbeMultiOutputFusionPass] InceptionV3/InceptionV3/Mixed_5d/Branch_1/mul_3
   [Mul][TbeMultiOutputFusionPass] InceptionV3/InceptionV3/Mixed_6b/Branch_1/mul_3
    ```

4. ni (-n) [op_name] -d -s [save sub graph deep]
    ```shell
    # 通过[算子名]查询算子节点信息
    # -d 显示相应的dump数据信息
    # -s 保存一个以当前算子节点为根，深度为参数值的子图
   PrecisionTool >  ni gradients/InceptionV3/InceptionV3/Mixed_7a/Branch_0/Maximum_1_grad/GreaterEqual -d -s 3
   ╭─────────────────── [GreaterEqual]gradients/InceptionV3/InceptionV3/Mixed_7a/Branch_0/Maximum_1_grad/GreaterEqual ────────────────────╮
   │ [GreaterEqual] gradients/InceptionV3/InceptionV3/Mixed_7a/Branch_0/Maximum_1_grad/GreaterEqual                                       │
   │ Input:                                                                                                                               │
   │  -[0][DT_FLOAT][NHWC][32, 8, 8, 320] InceptionV3/InceptionV3/Mixed_7a/Branch_0/add_3:0                                               │
   │  -[1][DT_FLOAT][NHWC][1, 8, 1, 1] InceptionV3/Mixed_7a/Branch_0/Conv2d_1a_3x3tau:0                                                   │
   │  -[2][][[]][] atomic_addr_clean0_21:-1                                                                                               │
   │ Output:                                                                                                                              │
   │  -[0][DT_BOOL][NHWC][32, 8, 8, 320] ['trans_TransData_1170']                                                                         │
   │ NpuDumpInput:                                                                                                                        │
   │  -[0] GreaterEqual.gradients_InceptionV3_InceptionV3_Mixed_7a_Branch_0_Maximum_1_grad_GreaterEqual.325.1619494134722860.input.0.npy  │
   │   |- [Shape: (32, 8, 8, 320)] [Dtype: float32] [Max: 5.846897] [Min: -8.368301] [Mean: -0.72565556]                                  │
   │  -[1] GreaterEqual.gradients_InceptionV3_InceptionV3_Mixed_7a_Branch_0_Maximum_1_grad_GreaterEqual.325.1619494134722860.input.1.npy  │
   │   |- [Shape: (1, 8, 1, 1)] [Dtype: float32] [Max: 0.0] [Min: 0.0] [Mean: 0.0]                                                        │
   │ NpuDumpOutput:                                                                                                                       │
   │  -[0] GreaterEqual.gradients_InceptionV3_InceptionV3_Mixed_7a_Branch_0_Maximum_1_grad_GreaterEqual.325.1619494134722860.output.0.npy │
   │   |- [Shape: (32, 8, 8, 320)] [Dtype: bool] [Max: True] [Min: False] [Mean: 0.1176300048828125]                                      │
   │ CpuDumpOutput:                                                                                                                       │
   │  -[0] gradients_InceptionV3_InceptionV3_Mixed_7a_Branch_0_Maximum_1_grad_GreaterEqual.0.1619492699305998.npy                         │
   │   |- [Shape: (32, 8, 8, 320)] [Dtype: bool] [Max: True] [Min: False] [Mean: 0.11764373779296874]                                     │
   ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
   2021-04-27 14:39:55 (15178) -[DEBUG]write 14953 bytes to './precision_data/dump/temp/op_graph/GreaterEqual.gradients_InceptionV3_InceptionV3_Mixed_7a_Branch_0_Maximum_1_grad_GreaterEqual.3.gv'
   2021-04-27 14:39:55 (15178) -[INFO]Sub graph saved to /root/sym/inception/precision_data/dump/temp/op_graph
   ```
   
5. pt (-n) [*.npy] (-c)
    ```shell
    # 查看某个dump数据块的数据信息
    # -c : save data to txt
    PrecisionTool > pt TransData.trans_TransData_1170.327.1619347786532995.input.0.npy -c
   ╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ Shape: (32, 8, 8, 320)                                                                                                  │
   │ Dtype: bool                                                                                                             │
   │ Max: True                                                                                                               │
   │ Min: False                                                                                                              │
   │ Mean: 0.11950836181640626                                                                                               │
   │ Path: ./precision_data/dump/temp/overflow_decode/TransData.trans_TransData_1170.327.1619347786532995.input.0.npy        │
   │ TxtFile: ./precision_data/dump/temp/overflow_decode/TransData.trans_TransData_1170.327.1619347786532995.input.0.npy.txt │
   ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ```

6. cp (-n) [left *.npy] [right *.npy] -p [print num] -al [atol] -rl [rtol]
    ```shell
    # 对比两个tensor的数据
    # -p 指定输出的错误数据的个数及前多少个数据
    # -al/rl 指定相对误差的参数,在两个场景中用到
    #   1. np.allclose(left, right, atol=al, rtol=rl)
    #   2. err_cnt += 1 if abs(data_left[i] - data_right[i]) > (al + rl * abs(data_right[i]))
    PrecisionTool > cp Add.InceptionV3_InceptionV3_Mixed_7a_Branch_0_add_3.323.1619494134703053.output.0.npy InceptionV3_InceptionV3_Mixed_7a_Branch_0_add_3.0.1619492699305998.npy -p 10 -s -al 0.002 -rl 0.005
                      Error Item Table                                        Top Item Table
   ┏━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓ ┏━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
   ┃ Index ┃ Left          ┃ Right        ┃ Diff         ┃ ┃ Index ┃ Left        ┃ Right       ┃ Diff          ┃
   ┡━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩ ┡━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
   │ 155   │ 0.024600908   │ 0.022271132  │ 0.002329776  │ │ 0     │ -0.9206961  │ -0.9222216  │ 0.0015255213  │
   │ 247   │ 0.015752593   │ 0.017937578  │ 0.0021849852 │ │ 1     │ -0.6416973  │ -0.64051837 │ 0.0011789203  │
   │ 282   │ -0.0101207765 │ -0.007852031 │ 0.0022687456 │ │ 2     │ -0.35383835 │ -0.35433492 │ 0.0004965663  │
   │ 292   │ 0.019581757   │ 0.02240482   │ 0.0028230622 │ │ 3     │ -0.18851271 │ -0.18883198 │ 0.00031927228 │
   │ 640   │ -0.06593232   │ -0.06874806  │ 0.0028157383 │ │ 4     │ -0.43508735 │ -0.43534422 │ 0.00025686622 │
   │ 1420  │ 0.09293677    │ 0.09586689   │ 0.0029301196 │ │ 5     │ 1.4447614   │ 1.4466647   │ 0.0019032955  │
   │ 1462  │ -0.085207745  │ -0.088047795 │ 0.0028400496 │ │ 6     │ -0.3455438  │ -0.3444429  │ 0.0011008978  │
   │ 1891  │ -0.03433288   │ -0.036525503 │ 0.002192624  │ │ 7     │ -0.6560242  │ -0.6564579  │ 0.0004336834  │
   │ 2033  │ 0.06828873    │ 0.07139922   │ 0.0031104907 │ │ 8     │ -2.6964858  │ -2.6975214  │ 0.0010356903  │
   │ 2246  │ -0.06376442   │ -0.06121233  │ 0.002552092  │ │ 9     │ -0.73746175 │ -0.73650354 │ 0.00095820427 │
   └───────┴───────────────┴──────────────┴──────────────┘ └───────┴─────────────┴─────────────┴───────────────┘
   ╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ Left:                                                                                                                                    │
   │  |- NpyFile: ./precision_data/dump/temp/decode/Add.InceptionV3_InceptionV3_Mixed_7a_Branch_0_add_3.323.1619494134703053.output.0.npy     │
   │  |- TxtFile: ./precision_data/dump/temp/decode/Add.InceptionV3_InceptionV3_Mixed_7a_Branch_0_add_3.323.1619494134703053.output.0.npy.txt │
   │  |- NpySpec: [Shape: (32, 8, 8, 320)] [Dtype: float32] [Max: 5.846897] [Min: -8.368301] [Mean: -0.72565556]                              │
   │ DstFile:                                                                                                                                 │
   │  |- NpyFile: ./precision_data/dump/cpu/InceptionV3_InceptionV3_Mixed_7a_Branch_0_add_3.0.1619492699305998.npy                            │
   │  |- TxtFile: ./precision_data/dump/cpu/InceptionV3_InceptionV3_Mixed_7a_Branch_0_add_3.0.1619492699305998.npy.txt                        │
   │  |- NpySpec: [Shape: (32, 8, 8, 320)] [Dtype: float32] [Max: 5.8425903] [Min: -8.374472] [Mean: -0.7256237]                              │
   │ NumCnt:   655360                                                                                                                         │
   │ AllClose: False                                                                                                                          │
   │ CosSim:   0.99999493                                                                                                                     │
   │ ErrorPer: 0.023504638671875  (rl= 0.005, al= 0.002)                                                                                      │
   ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
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

### F&Q
1. 安装gnureadline报错找不到lncurses
   ```shell
   /usr/bin/ld: cannot find -lncurses
   collect2: error: ld returned 1 exit status
   error: command 'gcc' failed with exit status 1
   ```
   ```shell
   # 先尝试在本地查找libncurses.so*
   find / -name libncurses.so*
   # 如果能找到以下文件，直接创建一个libncurses.so指向libncurses.so.5即可，否则需要用包管理工具安装ncurses
   /usr/lib64/libncurses.so.5
   /usr/lib64/libncurses.so.5.9
   /usr/lib64/libncursesw.so.5
   # 创建软连接
   ln -s /usr/lib64/libncurses.so.5.9 /usr/lib64/libncurses.so
   ```
#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request