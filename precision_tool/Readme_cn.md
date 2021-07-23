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
### 工具获取
1. 下载压缩包的方式获取
   将https://github.com/Ascend/tools 以压缩包形式下载
2. 使用git命令方式获取
3. 移动 tools/precision_tool 子目录至训练工作目录
### 安装python3三方依赖
```shell
pip3 install rich gnureadline pexpect graphviz
# ubuntu/Debian
sudo apt-get install graphviz
# fedora/Centos
sudo yum install graphviz
```
### 工具执行依赖
* 一般直接在NPU训练环境上部署该脚本，环境上能够正常执行CPU和NPU训练脚本
* 如果需要进行数据Dump比对，则需要先检查并去除训练脚本内部使用到的随机处理，避免由于输入数据不一致导致数据比对结果不可用
    ```python
    # 对于使用tf.random / np.random / (python) random的可以通过固定随机种子的方式固定输入
    # import tf_config.py 默认会设置上述三种random的seed，但由于import位置关系，可能不一定能作用到所有的关联代码，建议在代码确认合适位置手动嵌入
    random.seed(cfg.DUMP_SEED)
    tf.random.set_random_seed(cfg.DUMP_SEED)
    np.random.seed(cfg.DUMP_SEED)
    
    # 此处给出一些典型示例，需要根据自己的脚本进行排查

    # 1. 参数初始化中的随机操作
    #    加载checkpoint的方式能够固定大多数初始参数
    saver.restore(sess, saver_dir)
    
    # 2. 输入数据的随机操作（例如对输入数据做shuffle操作）
    dataset = tf.data.TFRecordDataset(tf_data)
    dataset = dataset.shuffle(batch_size*10)    # 直接注释掉该行
    
    # 3. 模型中的随机操作（例如使用dropout）
    net = slim.dropout(net, keep_prob=dropout_keep_prob, scope='Dropout_1b') # 建议注释该行
    
    # 4. 图像预处理使用的随机操作(根据实际情况固定随机种子，或者替换成其他固定的预处理操作)
    # 4.1 Random rotate
    random_angle = tf.random_uniform([], - self.degree * 3.141592 / 180, self.degree * 3.141592 / 180)
    image = tf.contrib.image.rotate(image, random_angle, interpolation='BILINEAR')
    depth_gt = tf.contrib.image.rotate(depth_gt, random_angle, interpolation='NEAREST')
  
    # 4.2 Random flipping
    do_flip = tf.random_uniform([], 0, 1)
    image = tf.cond(do_flip > 0.5, lambda: tf.image.flip_left_right(image), lambda: image)
    depth_gt = tf.cond(do_flip > 0.5, lambda: tf.image.flip_left_right(depth_gt), lambda: depth_gt)
    
    # 4.3 Random crop
    mage_depth = tf.concat([image, depth_gt], 2)
    image_depth_cropped = tf.random_crop(image_depth, [self.params.height, self.params.width, 4])
    
    # 5. RunConfig/NPURunConfig中设置tf_random_seed固定网络随机因子
    run_config = tf.estimator.RunConfig(tf_random_seed=1, ...)
    run_config = NPURunConfig(tf_random_seed=1, ...)
  
    # 其他......
    ```
* 该工具基于**NPU的计算图**，**NPU的DUMP数据**，**NPU的溢出检测数据**，**TF的计算图meta文件**，**TF的DUMP数据**进行数据解析和分析。
这几类依赖数据可以通过以下方式获取（只使用部分工具功能并不需要提前获取所有依赖数据）：
#### 1. NPU的计算图获取
   ```
     注意：NPU的Dump数据和计算图存在一定的对应关系，需要同时获取 
          避免在自定义的训练脚本中unset DUMP GRAPH相关的环境变量
   ```
* 【推荐】方法一：配置2、3依赖中的NPU数据Dump或者overflow检测功能，将自动配置上Dump GE图的环境变量

* 【不推荐】方法二：参考迁移指导中的修改配置，执行NPU脚本，并将获取到的图转存至precision_data图目录
   ```shell
   export DUMP_GE_GRAPH=2
   export DUMP_GRAPH_LEVEL=3
   export DUMP_GRAPH_PATH=./precision_data/npu/debug_0/graph
   # 未配置DUMP_GRAPH_PATH时，图文件将保存在脚本执行目录，可以直接转存至precision_data目录
   mkdir -p ./precision_data/npu/debug_0/graph && mv ge_proto_*.txt ./precision_data/npu/debug_0/graph
   ```
#### 2. NPU的DUMP数据获取
* 【推荐】方法一：在训练脚本中**import precision_tool.tf_config**，并使用precision_tool中提供的辅助命令行执行训练脚本 
    ``` python
    # NPU的DUMP获取和溢出检测数据的获取，均可按如下方式修改代码
    # 注意：参数action可以设置为'dump'或'overflow'
    # 引用 precision_tool/tf_config.py
    import precision_tool.tf_config as npu_tf_config
    
    # 如果使用的是Estimator的NPURunConfig配置使能NPU，则可以参考以下修改
    dump_config = npu_tf_config.estimator_dump_config(action='dump') # 新增行
    npu_config = NPURunConfig(dump_config=dump_config)
  
    # 如果使用的是session.run或者使用tf.ConfigProto创建session_config传入tf.estimator.RunConfig的方式使能npu
    # 可以参考如下修改
    session_config = npu_tf_config.session_dump_config(session_config, action='dump') # 新增行
    # tf.estimator
    run_config = tf.estimator.RunConfig(session_config=session_config,...)
    # tf.keras
    npu_keras_sess = set_keras_session_npu_config(config=session_config)
    # session run
    with tf.Session(config=npu_config_proto(session_config)):
        ......
    
    # 如果使用的是custom_op方式，则可以参考以下修改
    config = tf.ConfigProto()
    custom_op =  config.graph_options.rewrite_options.custom_optimizers.add()
    custom_op.name =  "NpuOptimizer"
    custom_op.parameter_map["use_off_line"].b = True
    custom_op = npu_tf_config.update_custom_op(custom_op, action='dump')   # 新增行
    ```

* 【不推荐】方法二：参考[精度比对工具使用指南](https://www.hiascend.com/document?tag=community-developer) 修改训练脚本。
   执行训练脚本，并将dump的数据拷贝到【precision_data/dump/npu/】目录
#### 3. NPU的溢出检测数据的获取（缺少该数据将无法展示溢出检测结果）
* 【推荐】方法一：在训练脚本中**import precision_tool.tf_config**，并按【2. NPU的DUMP数据获取】中修改训练代码，使用precision_tool中提供的辅助命令行执行训练脚本
    ```python
    # 需要将action设置成'overflow'
    # 引用 precision_tool/tf_config.py
    import precision_tool.tf_config as npu_tf_config
    dump_config = npu_tf_config.estimator_dump_config(action='overflow') # 新增行
    ```
* 【不推荐】方法二：参考[使用溢出检测工具分析算子溢出](https://www.hiascend.com/document?tag=community-developer) 修改训练脚本，
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
   # 1. 执行脚本
   # 2. 解析tf debug dump文件，生成算子输出tensor文件
   # 注意：TF dump数据的原理是使用tf_debug的print_tensor(pt)命令实现的，由于训练代码提供了非常灵活的run()接口，
   #      脚本无法感知用户需要dump的tensor在哪个run阶段，因此需要用户修改训练代码，在执行完正确的run后，立即退出。
   #      例如，修改代码只执行一个step的训练，根据代码中run的次数，会获取到1~N个离线tf_debug的dump目录
   #      precision_tool脚本会自动提取最后一个run阶段中出现的所有tensor作为标杆数据。
   python3.7.5 precision_tool/cli.py tf_dump
   
   # 在precision_data/tf/dump/ 目录会存放提取的tensor
   # 如果获取tensor不符合预期，可以检查下precision_data/dump/cpu_debug/目录, 只保留预期run阶段的tf_debug离线数据
   # 执行以下命令重新生成
   rm -rf precision_data/tf/dump/* && python3.7.5 precision_tool/cli.py tf_dump
   ```
* 【不推荐】方法二：参考[准备基于GPU/CPU运行生成的npy数据](https://www.hiascend.com/document?tag=community-developer)
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
#### 6. 关闭NPU的融合功能（根据情况启用）
* NPU会对计算图中的算子进行融合，以提高网络性能，由于大多数融合是自动识别的，可能存在未考虑到的场景，导致精度问题，
  因此，可以尝试关闭融合定界网络问题是否是由于融合导致。
  ```python
    # 关闭融合可以和溢出检测/数据Dump同时进行，启用方法也类似
    # 引用 precision_tool/tf_config.py
    import precision_tool.tf_config as npu_tf_config
    
    # 如果使用的是Estimator的NPURunConfig配置使能NPU，则可以参考以下修改
    npu_config = NPURunConfig(fusion_switch_file=npu_tf_config.FUSION_OFF_FILE) # 修改行
    # 如果需要关闭指定的融合规则，则可以修改precision_tool/fusion_switch.cfg, 并参考如下修改
    npu_config = NPURunConfig(fusion_switch_file=npu_tf_config.FUSION_SWITCH_FILE) # 关闭特定融合修改行
  
    # 如果使用的是session.run或者使用tf.ConfigProto创建session_config传入tf.estimator.RunConfig的方式使能npu
    # 可以参考如下修改(数据Dump和关闭融合同时使能)
    session_config = npu_tf_config.session_dump_config(session_config, action='dump|fusion_off') # 新增行
    session_config = npu_tf_config.session_dump_config(session_config, action='dump|fusion_switch') # 关闭特定融合新增行
    # tf.estimator
    run_config = tf.estimator.RunConfig(session_config=session_config,...)
    # tf.keras
    npu_keras_sess = set_keras_session_npu_config(config=session_config)
    # session run
    with tf.Session(config=npu_config_proto(session_config)):
        ......
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
    # ModelArts场景下，可以根据情况将数据跟目录修改成自定义目录，并在完成后完整下载该目录
    ROOT_DIR = './'
    ```
2. 启动脚本（交互命令行）
    ```shell
    python3 ./precision_tool/cli.py 
    ```
   
### 交互模式命令
1. ac -l [limit_num] -c
    ```shell
    # auto check. 自动化检测命令
    # 列出Fusion信息;解析算子溢出信息;
    # -c 可选，进行全网比对
    # -l 可选，限制输出结果的条数（overflow解析的条数等）
    PrecisionTool > ac -c
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

7. vc -lt [left_path] -rt [right_path] -g [graph]
   ```python
    # 用于手动指定两个目录进行整网对比
    # -lt 必选，其中一个文件目录
    # -rt 必选，另一个目录，一般是标杆目录 
    # -g 可选，指定-g将尝试解析graph内的映射关系比对（一般用于NPU和TF之间的数据比对， NPU与NPU之间比对不需要，直接按照算子name对比）
   ```
8. vcs -f [file_name] -c [cos_sim_threshold] -l [limit]
   ```python
    # 查看精度比对结果的概要信息，可以更加预先相似的阈值过滤出低于阈值的算子/信息
    # -f (--file) 可选，指定csv文件，不设置则默认遍历precision_data/temp/vector_compare/目录下最近产生的对比目录内的所有csv
    # -c (--cos_sim) 可选，指定筛选所使用的预先相似度阈值，默认0.98
    # -l (--limit) 可选，指定输出前多少个结果，默认值3
    PrecisionTool > vcs -c 0.98 -l 2
    2021-05-31 14:48:56 (2344298) -[INFO]Sub path num:[1]. Dirs[['20210529145750']], choose[20210529145750]
    2021-05-31 14:48:56 (2344298) -[DEBUG]Find ['result_20210529145751.csv', 'result_20210529145836.csv', 'result_20210529145837.csv', 'result_20210529145849.csv', 'result_20210529150404.csv', 'result_20210529151102.csv'] result files in dir precision_data/temp/vector_compare/20210529145750
    2021-05-31 14:48:56 (2344298) -[INFO]Find 0 ops less then 0.98 in precision_data/temp/vector_compare/20210529145750/result_20210529145751.csv
    2021-05-31 14:48:56 (2344298) -[INFO]Find 0 ops less then 0.98 in precision_data/temp/vector_compare/20210529145750/result_20210529145836.csv
    2021-05-31 14:48:56 (2344298) -[INFO]Find 1 ops less then 0.98 in precision_data/temp/vector_compare/20210529145750/result_20210529145837.csv
    2021-05-31 14:48:56 (2344298) -[INFO]Find 2 ops less then 0.98 in precision_data/temp/vector_compare/20210529145750/result_20210529145849.csv
    2021-05-31 14:48:56 (2344298) -[INFO]Find 2 ops less then 0.98 in precision_data/temp/vector_compare/20210529145750/result_20210529150404.csv
    2021-05-31 14:48:56 (2344298) -[INFO]Find 0 ops less then 0.98 in precision_data/temp/vector_compare/20210529145750/result_20210529151102.csv
    ╭── [578] pixel_cls_loss/cond_1/TopKV2 ───╮
    │ Left:  ['pixel_cls_loss/cond_1/TopKV2'] │
    │ Right: ['pixel_cls_loss/cond_1/TopKV2'] │
    │ Input:                                  │
    │  - [0]1.0        - [1]nan               │
    │ Output:                                 │
    │  - [0]0.999999   - [1]0.978459          │
    ╰─────────────────────────────────────────╯
    ╭── [490] gradients/AddN_5 ───╮
    │ Left:  ['gradients/AddN_5'] │
    │ Right: ['gradients/AddN_5'] │
    │ Input:                      │
    │  - [0]nan        - [1]1.0   │
    │ Output:                     │
    │  - [0]0.05469               │
    ╰─────────────────────────────╯
   ```
### Precision_data目录结构
```
precision_data/
├── npu
│   ├── debug_0
|   |   ├── dump
|   |       └── 20210510101133
|   │   └── graph
|   |       └── ge_proto_00000179_PreRunAfterBuild.txt
│   └── debug_1
├── tf
|   ├── tf_debug
|   └── dump
├── overflow
├── fusion
└── temp
    ├── op_graph
    ├── decode
    |   ├── dump_decode
    |   ├── overflow_decode
    |   └── dump_convert
    └── vector_compare
        ├── 20210510101133
        |   ├── result_123456.csv
        |   └── result_123455.csv
        └── 20210510101134
            └── result_123458.csv
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