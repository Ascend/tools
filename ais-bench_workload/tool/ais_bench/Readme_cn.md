# ais_bench推理工具使用指南

## 简介
本文介绍ais_bench推理工具，用来针对指定的推理模型运行推理程序，并能够测试推理模型的性能（包括吞吐率、时延）。

## 工具安装

### 环境和依赖

- 请参见《[CANN开发工具指南](https://www.hiascend.com/document/detail/zh/canncommercial/60RC1/envdeployment/instg/instg_000002.html)》安装昇腾设备开发或运行环境，即toolkit或nnrt软件包。
- 安装Python3。

### 工具安装方式

ais_bench推理工具的安装包括**aclruntime包**和**ais_bench推理程序包**的安装。
安装方式包括：下载whl包安装、一键式编译安装和源代码编译安装。

**说明**：

- 安装环境要求网络畅通。
- centos平台默认为gcc 4.8编译器，可能无法安装本工具，建议更新gcc编译器后再安装。
- 本工具安装时需要获取CANN版本，用户可通过设置CANN_PATH环境变量，指定安装的CANN版本路径，例如：export CANN_PATH=/xxx/nnrt/latest/。若不设置，工具默认会从/usr/local/Ascend/nnrt/latest/和/usr/local/Ascend/ascend-toolkit/latest路径分别尝试获取CANN版本。

#### 下载whl包安装

1. 下载如下aclruntime和ais_bench推理程序的whl包。

   0.0.2版本（aclruntime包请根据当前环境选择适配版本）：

   - [aclruntime-0.0.2-cp37-cp37m-linux_x86_64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp37-cp37m-linux_x86_64.whl)
   - [aclruntime-0.0.2-cp37-cp37m-linux_aarch64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp37-cp37m-linux_aarch64.whl)
   - [aclruntime-0.0.2-cp38-cp38-linux_x86_64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp38-cp38-linux_x86_64.whl)
   - [aclruntime-0.0.2-cp38-cp38-linux_aarch64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp38-cp38-linux_aarch64.whl)
   - [aclruntime-0.0.2-cp39-cp39-linux_x86_64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp39-cp39-linux_x86_64.whl)
   - [aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl)
   - [ais_bench-0.0.2-py3-none-any.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/ais_bench-0.0.2-py3-none-any.whl)

2. 执行如下命令，进行安装。

   ```bash
   # 安装aclruntime
   pip3 install ./aclruntime-{version}-{python_version}-linux_{arch}.whl
   # 安装ais_bench推理程序
   pip3 install ./ais_bench-{version}-py3-none-any.whl
   ```

   {version}表示软件版本号，{python_version}表示Python版本号，{arch}表示CPU架构。

   说明：若为覆盖安装，请增加“--force-reinstall”参数强制安装，例如：

   ```bash
   pip3 install ./aclruntime-{version}-{python_version}-linux_{arch}.whl --force-reinstall
   pip3 install ./ais_bench-{version}-py3-none-any.whl --force-reinstall
   ```

   分别提示如下信息则表示安装成功：

   ```bash
   # 成功安装aclruntime
   Successfully installed aclruntime-{version}
   # 成功安装ais_bench推理程序
   Successfully installed ais_bench-{version}
   ```

   

#### 一键式编译安装

1. **安装aclruntime包**

   在安装环境执行如下命令安装aclruntime包：

   ```bash
   pip3 install -v 'git+https://github.com/Ascend/tools.git#egg=aclruntime&subdirectory=ais-bench_workload/tool/ais_bench/backend'
   ```

   说明：若为覆盖安装，请增加“--force-reinstall”参数强制安装，例如：

   ```bash
   pip3 install -v --force-reinstall 'git+https://github.com/Ascend/tools.git#egg=aclruntime&subdirectory=ais-bench_workload/tool/ais_bench/backend'
   ```

   提示如下示例信息则表示安装成功：

   ```bash
   Successfully installed aclruntime-{version}
   ```

2. **安装ais_bench推理程序包**

   在安装环境执行如下命令安装ais_bench推理程序包：

   ```bash
   pip3 install -v 'git+https://github.com/Ascend/tools.git#egg=ais_bench&subdirectory=ais-bench_workload/tool/ais_bench'
   ```

   说明：若为覆盖安装，请增加“--force-reinstall”参数强制安装，例如：

   ```bash
   pip3 install -v --force-reinstall 'git+https://github.com/Ascend/tools.git#egg=ais_bench&subdirectory=ais-bench_workload/tool/ais_bench'
   ```
   
   提示如下示例信息则表示安装成功：
   
   ```bash
   Successfully installed ais_bench-{version}
   ```



#### 源代码编译安装
1. 从代码开源仓[Gitee](https://github.com/Ascend/tools)克隆/下载工具压缩包“tools-xxx.zip”。

2. 将工具压缩包上传并解压至安装环境。

3. 从工具解压目录下进入ais-bench_workload/tool/ais_bench目录下，执行如下命令进行编译：

   ```bash
   # 进入工具解压目录
   cd ${HOME}/ais-bench_workload/tool/ais_bench/
   # 构建aclruntime包
   pip3 wheel ./backend/ -v
   # 构建ais_bench推理程序包
   pip3 wheel ./ -v
   ```

   其中，${HOME}为ais_bench推理工具包所在目录。

   分别提示如下信息则表示编译成功：

   ```bash
   # 成功编译aclruntime包
   Successfully built aclruntime
   # 成功编译ais_bench推理程序包
   Successfully built ais-bench
   ```

4. 执行如下命令，进行安装。

   ```bash
   # 安装aclruntime
   pip3 install ./aclruntime-{version}-{python_version}-linux_{arch}.whl
   # 安装ais_bench推理程序
   pip3 install ./ais_bench-{version}-py3-none-any.whl
   ```

   {version}表示软件版本号，{python_version}表示Python版本号，{arch}表示CPU架构。

   说明：若为覆盖安装，请增加“--force-reinstall”参数强制安装，例如：

   ```bash
   pip3 install ./aclruntime-{version}-{python_version}-linux_{arch}.whl --force-reinstall
   pip3 install ./ais_bench-{version}-py3-none-any.whl --force-reinstall
   ```
   
   分别提示如下信息则表示安装成功：

   ```bash
   # 成功安装aclruntime
   Successfully installed aclruntime-{version}
   # 成功安装ais_bench推理程序
   Successfully installed ais_bench-{version}
   ```
   
   

### 运行准备
完成ais_bench推理工具安装后，需要执行如下操作，确保工具能够正确运行：
1. 执行requirements.txt文件中的依赖安装，执行如下命令：

   ```bash
   cd ${HOME}/ais-bench_workload/tool/ais_bench/
   pip3 install -r ./requirements.txt
   ```

   其中，${HOME}为ais_bench推理工具包所在目录。

   说明：若依赖已安装，忽略此步骤。
2. 设置CANN包的环境变量，执行如下命令：

   ```bash
   source ${INSTALL_PATH}/Ascend/ascend-toolkit/set_env.sh
   ```

   其中，${INSTALL_PATH}为CANN包安装路径。

   说明：若环境变量已配置，忽略此步骤。

完成以上设置后，可以使用ais_bench推理工具进行推理模型的性能测试。

## 使用方法

### 工具介绍

 #### 使用入口

ais_bench推理工具可以通过ais_bench可执行文件方式启动模型测试。启动方式如下：

```bash
python3 -m ais_bench --model *.om
```
其中，*为OM离线模型文件名。

#### 参数说明

ais_bench推理工具可以通过配置不同的参数，来应对各种测试场景以及实现其他辅助功能。

参数按照功能类别分为**基础功能参数**和**高级功能参数**：

- **基础功能参数**：主要包括输入输入文件及格式、debug、推理次数、预热次数、指定运行设备以及帮助信息等。
- **高级功能参数**：主要包括动态分档场景和动态Shape场景的ais_bench推理测试参数以及profiler或dump数据获取等。

**说明**：以下参数中，参数和取值之间可以用“ ”空格分隔也可以用“=”等号分隔。例如：--debug 1或--debug=0。

##### 基础功能参数

| 参数名                | 说明                                                         | 是否必选 |
| --------------------- | ------------------------------------------------------------ | -------- |
| --model               | 需要进行推理的OM离线模型文件。                               | 是       |
| --input               | 模型需要的输入。可指定输入文件所在目录或直接指定输入文件。支持输入文件格式为“NPY”、“BIN”。可输入多个文件或目录，文件或目录之间用“,”隔开。具体输入文件请根据模型要求准备。  若不配置该参数，会自动构造输入数据，输入数据类型由--pure_data_type参数决定。 | 否       |
| --pure_data_type      | 纯推理数据类型。取值为：“zero”、“random”，默认值为"zero"。 未配置模型输入文件时，工具自动构造输入数据。设置为zero时，构造全为0的纯推理数据；设置为random时，为每一个输入生成一组随机数据。 | 否       |
| --output              | 推理结果保存目录。配置后会创建“日期+时间”的子目录，保存输出结果。如果指定output_dirname参数，输出结果将保存到子目录output_dirname下。不配置输出目录时，仅打印输出结果，不保存输出结果。 | 否       |
| --output_dirname      | 推理结果保存子目录。设置该值时输出结果将保存到*output/output_dirname*目录下。  配合output参数使用，单独使用无效。 例如：--output */output* --output_dirname *output_dirname* | 否       |
| --outfmt              | 输出数据的格式。取值为：“NPY”、“BIN”、“TXT”，默认为”BIN“。  配合output参数使用，单独使用无效。 例如：--output */output* --outfmt NPY。 | 否       |
| --debug               | 调试开关。可打印model的desc信息和其他详细执行信息。1或true（开启）、0或false（关闭），默认关闭。 | 否       |
| --display_all_summary | 是否显示所有的汇总信息，包含h2d和d2h信息。1或true（开启）、0或false（关闭），默认关闭。 | 否       |
| --loop                | 推理次数。默认值为1，取值范围为大于0的正整数。  profiler参数配置为true时，推荐配置为1。 | 否       |
| --warmup_count        | 推理预热次数。默认值为1，取值范围为大于等于0的整数。配置为0则表示不预热。 | 否       |
| --device              | 指定运行设备。根据设备实际的Device ID指定，默认值为0。多Device场景下，可以同时指定多个Device进行推理测试，例如：--device 0,1,2,3。 | 否       |
| --help                | 工具使用帮助信息。                                           | 否       |

##### 高级功能参数

| 参数名                   | 说明                                                         | 是否必选 |
| ------------------------ | ------------------------------------------------------------ | -------- |
| --dymBatch               | 动态Batch参数，指定模型输入的实际Batch。 <br>如ATC模型转换时，设置--input_shape="data:-1,600,600,3;img_info:-1,3" --dynamic_batch_size="1,2,4,8"，dymBatch参数可设置为：--dymBatch 2。 | 否       |
| --dymHW                  | 动态分辨率参数，指定模型输入的实际H、W。 <br>如ATC模型转换时，设置--input_shape="data:8,3,-1,-1;img_info:8,4,-1,-1" --dynamic_image_size="300,500;600,800"，dymHW参数可设置为：--dymHW 300,500。 | 否       |
| --dymDims                | 动态维度参数，指定模型输入的实际Shape。 <br>如ATC模型转换时，设置 --input_shape="data:1,-1;img_info:1,-1" --dynamic_dims="224,224;600,600"，dymDims参数可设置为：--dymDims "data:1,600;img_info:1,600"。 | 否       |
| --dymShape               | 动态Shape参数，指定模型输入的实际Shape。 <br>如ATC模型转换时，设置--input_shape_range="input1:\[8\~20,3,5,-1\];input2:\[5,3\~9,10,-1\]"，dymShape参数可设置为：--dymShape "input1:8,3,5,10;input2:5,3,10,10"。<br>动态Shape场景下，获取模型的输出size通常为0（即输出数据占内存大小未知），建议设置--outputSize参数。<br/>例如：--dymShape "input1:8,3,5,10;input2:5,3,10,10" --outputSize "10000,10000"。 | 否       |
| --dymShape_range         | 动态Shape的阈值范围。如果设置该参数，那么将根据参数中所有的Shape列表进行依次推理，得到汇总推理信息。<br/>配置格式为：name1:1,3,200\~224,224-230;name2:1,300。其中，name为模型输入名，“\~”表示范围，“-”表示某一位的取值。<br/>也可以指定动态Shape的阈值范围配置文件*.info，该文件中记录动态Shape的阈值范围，文件中可同时设置多组Shape，一组Shape占用一行。 | 否       |
| --outputSize             | 指定模型的输出数据所占内存大小，多个输出时，需要为每个输出设置一个值，多个值之间用“,”隔开。<br>动态Shape场景下，获取模型的输出size通常为0（即输出数据占内存大小未知），需要根据输入的Shape，预估一个较合适的大小，配置输出数据占内存大小。<br>例如：--dymShape "input1:8,3,5,10;input2:5,3,10,10" --outputSize "10000,10000" | 否       |
| --auto_set_dymdims_mode  | 自动设置动态Dims模式。1或true（开启）、0或false（关闭），默认关闭。<br/>针对动态档位Dims模型，根据输入的文件的信息，自动设置Shape参数，注意输入数据只能为npy文件，因为bin文件不能读取Shape信息。<br/>配合input参数使用，单独使用无效。<br/>例如：--input 1.npy --auto_set_dymdims_mode 1 | 否       |
| --auto_set_dymshape_mode | 自动设置动态Shape模式。取值为：1或true（开启）、0或false（关闭），默认关闭。<br>针对动态Shape模型，根据输入的文件的信息，自动设置Shape参数，注意输入数据只能为npy文件，因为bin文件不能读取Shape信息。<br>配合input参数使用，单独使用无效。<br/>例如：--input 1.npy --auto_set_dymshape_mode 1 | 否       |
| --profiler               | profiler开关。1或true（开启）、0或false（关闭），默认关闭。<br>profiler数据在--output参数指定的目录下的profiler文件夹内。配合--output参数使用，单独使用无效。不能与--dump同时开启。<br/>若环境配置了GE_PROFILING_TO_STD_OUT=1，则--profiler参数采集性能数据时使用的是acl.json配置文件方式。 | 否       |
| --dump                   | dump开关。1或true（开启）、0或false（关闭），默认关闭。<br>dump数据在--output参数指定的目录下的dump文件夹内。配合--output参数使用，单独使用无效。不能与--profiler同时开启。 | 否       |
| --acl_json_path          | acl.json配置文件路径，须指定一个有效的json文件。该文件内可配置profiler或者dump。当配置该参数时，--dump和--profiler参数无效。 | 否       |
| --batchsize              | 模型batchsize。不输入该值将自动推导。参数传递的batchszie有且只用于结果吞吐率计算。自动推导逻辑为尝试获取模型的batchsize时，首先获取第一个参数的最高维作为batchsize； 如果是动态Batch的话，更新为动态Batch的值；如果是动态dims和动态Shape更新为设置的第一个参数的最高维。如果自动推导逻辑不满足要求，请务必传入准确的batchsize值，以计算出正确的吞吐率。 | 否       |
| --output_batchsize_axis  | 输出tensor的batchsize轴。输出结果保存文件时，根据哪个轴进行切割推理结果，那输出结果的batch维度就在哪个轴。默认按照0轴进行切割，但是部分模型的输出batch为1轴，所以要设置该值为1。 | 否       |



### 使用场景

**说明**：对于ais_bench推理工具的输入输出，工具会根据模型的实际输入size对输入文件进行组合，输入文件不足则自动补全，输入文件过多则分批次；完成推理测试后根据模型batchsize对输出文件进行切割。

 #### 纯推理场景

默认情况下，构造全为0的数据送入模型推理。

示例命令如下：

```bash
python3 -m ais_bench --model /home/model/resnet50_v1.om --output ./ --outfmt BIN --loop 5
```

#### 调试模式
开启debug调试模式。

示例命令如下：

```bash
python3 -m ais_bench --model /home/model/resnet50_v1.om --output ./ --debug 1
```

调试模式开启后会增加更多的打印信息，包括：
- 模型的输入输出参数信息

  ```bash
  input:
    #0    input_ids  (1, 384)  int32  1536  1536
    #1    input_mask  (1, 384)  int32  1536  1536
    #2    segment_ids  (1, 384)  int32  1536  1536
  output:
    #0    logits:0  (1, 384, 2)  float32  3072  3072
  ```

- 详细的推理耗时信息

  ```bash
  [DEBUG] model aclExec cost : 2.336000
  ```
- 模型输入输出等具体操作信息

 #### 文件输入场景

使用--input参数指定模型输入文件，多个文件之间通过“,”进行分隔。

示例命令如下：

```bash
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --input "./1.bin,./2.bin,./3.bin,./4.bin,./5.bin"
```

 #### 文件夹输入场景

使用input参数指定模型输入文件所在目录，多个目录之间通过“,”进行分隔。

```bash
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --input "./"
```

传入文件夹的个数需要与模型实际输入一致。

例如，bert模型有三个输入，则必须传入3个文件夹，且三个文件夹分别对应模型的三个输入，顺序要对应。
模型输入参数的信息可以通过开启调试模式查看，bert模型的三个输入依次为input_ids、 input_mask、 segment_ids，所以依次传入三个文件夹：

- 第一个文件夹“./data/SQuAD1.1/input_ids"，对应模型第一个参数"input_ids"的输入
- 第二个文件夹"./data/SQuAD1.1/input_mask"，对应第二个输入"input_mask"的输入
- 第三个文件夹"./data/SQuAD1.1/segment_ids"，对应第三个输入"segment_ids"的输入

```bash
python3 -m ais_bench --model ./save/model/BERT_Base_SQuAD_BatchSize_1.om --input ./data/SQuAD1.1/input_ids,./data/SQuAD1.1/input_mask,./data/SQuAD1.1/segment_ids
```



#### 多Device场景

多Device场景下，可以同时指定多个Device进行推理测试。

示例命令如下：

```bash
python3 -m ais_bench --model ./pth_resnet50_bs1.om --input ./data/ --device 1,2
```

输出结果依次展示每个Device的推理测试结果，示例如下：

```bash
[INFO] -----------------Performance Summary------------------
[INFO] NPU_compute_time (ms): min = 2.4769999980926514, max = 3.937000036239624, mean = 3.5538000106811523, median = 3.7230000495910645, percentile(99%) = 3.936680030822754
[INFO] throughput 1000*batchsize.mean(1)/NPU_compute_time.mean(3.5538000106811523): 281.38893494131406
[INFO] ------------------------------------------------------
[INFO] -----------------Performance Summary------------------
[INFO] NPU_compute_time (ms): min = 3.3889999389648438, max = 3.9230000972747803, mean = 3.616000032424927, median = 3.555000066757202, percentile(99%) = 3.9134000968933105
[INFO] throughput 1000*batchsize.mean(1)/NPU_compute_time.mean(3.616000032424927): 276.54867008654026
[INFO] ------------------------------------------------------
[INFO] unload model success, model Id is 1
[INFO] unload model success, model Id is 1
[INFO] end to destroy context
[INFO] end to destroy context
[INFO] end to reset device is 2
[INFO] end to reset device is 2
[INFO] end to finalize acl
[INFO] end to finalize acl
[INFO] multidevice run end qsize:4 result:1
i:0 device_1 throughput:281.38893494131406 start_time:1676875630.804429 end_time:1676875630.8303885
i:1 device_2 throughput:276.54867008654026 start_time:1676875630.8043878 end_time:1676875630.8326817
[INFO] summary throughput:557.9376050278543
```

其中结果最后展示每个Device推理测试的throughput（吞吐率）、start_time（测试启动时间）、end_time（测试结束时间）以及summary throughput（吞吐率汇总）。其他详细字段解释请参见本手册的“输出结果”章节。

 #### 动态分档场景

主要包含动态Batch、动态HW（宽高）、动态Dims三种场景，需要分别传入dymBatch、dymHW、dymDims指定实际档位信息。

##### 动态Batch

以档位1 2 4 8档为例，设置档位为2。

```bash
python3 -m ais_bench --model ./resnet50_v1_dynamicbatchsize_fp32.om --input=./data/ --dymBatch 2
```

##### 动态HW宽高

以档位224,224;448,448档为例，设置档位为224,224。

```bash
python3 -m ais_bench --model ./resnet50_v1_dynamichw_fp32.om --input=./data/ --dymHW 224,224
```

##### 动态Dims

以设置档位1,3,224,224为例。

```bash
python3 -m ais_bench --model resnet50_v1_dynamicshape_fp32.om --input=./data/ --dymDims actual_input_1:1,3,224,224
```

##### 自动设置Dims模式（动态Dims模型）

动态Dims模型输入数据的Shape可能是不固定的，比如一个输入文件Shape为1,3,224,224，另一个输入文件Shape为 1,3,300,300。若两个文件同时推理，则需要设置两次动态Shape参数，当前不支持该操作。针对该场景，增加auto_set_dymdims_mode模式，可以根据输入文件的Shape信息，自动设置模型的Shape参数。

```bash
python3 -m ais_bench --model resnet50_v1_dynamicshape_fp32.om --input=./data/ --auto_set_dymdims_mode 1
```



#### 动态Shape场景

##### 动态Shape

以ATC设置[1\~8,3,200\~300,200\~300]，设置档位1,3,224,224为例。

动态Shape的输出大小通常为0，建议通过outputSize参数设置对应输出的内存大小。

```bash
python3 -m ais_bench --model resnet50_v1_dynamicshape_fp32.om --dymShape actual_input_1:1,3,224,224 --outputSize 10000
```

##### 自动设置Shape模式（动态Shape模型）

动态Shape模型输入数据的Shape可能是不固定的，比如一个输入文件Shape为1,3,224,224 另一个输入文件Shape为 1,3,300,300。若两个文件同时推理，则需要设置两次动态Shape参数，当前不支持该操作。针对该场景，增加auto_set_dymshape_mode模式，可以根据输入文件的Shape信息，自动设置模型的Shape参数。

```bash
python3 -m ais_bench --model ./pth_resnet50_dymshape.om  --outputSize 100000 --auto_set_dymshape_mode 1  --input ./dymdata
```

**注意该场景下的输入文件必须为npy格式，如果是bin文件将获取不到真实的Shape信息。**

##### 动态Shape模型range测试模式

输入动态Shape的range范围。对于该范围内的Shape分别进行推理，得出各自的性能指标。

以对1,3,224,224 1,3,224,225 1,3,224,226进行分别推理为例，命令如下：

```bash
python3 -m ais_bench --model ./pth_resnet50_dymshape.om  --outputSize 100000 --dymShape_range actual_input_1:1,3,224,224~226
```



#### profiler或dump场景

支持以--acl_json_path、--profiler、--dump参数形式实现：
+ acl_json_path参数指定acl.json配置文件，可以在该文件中对应的profiler或dump参数。示例代码如下：

  + profiler

    ```bash
    {
    "profiler": {
                  "switch": "on",
                  "output": "./result/profiler"
                }
    }
    ```

    更多性能参数配置请参见《[CANN 开发工具指南](https://www.hiascend.com/document/detail/zh/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)》中的“性能分析工具>高级功能>性能数据采集（acl.json配置文件方式）”章节。

  + dump

    ```bash
    {
        "dump": {
            "dump_list": [
                {
                    "model_name": "{model_name}"
                }
            ],
            "dump_mode": "output",
            "dump_path": "./result/dump"
        }
    }
    ```

    更多dump配置请参见《[CANN 开发工具指南](https://www.hiascend.com/document/detail/zh/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)》中的“精度比对工具>比对数据准备>推理场景数据准备>准备离线模型dump数据文件”章节。

  通过该方式进行Profiler采集时，输出的性能数据文件需要参见《[CANN 开发工具指南](https://www.hiascend.com/document/detail/zh/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)》中的“性能分析工具>高级功能>数据解析与导出”章节，将性能数据解析并导出为可视化的timeline和summary文件。

+ profiler为固化到程序中的一组性能数据采集配置，生成的性能数据保存在--output参数指定的目录下的profiler文件夹内。

  该参数是通过调用ais_bench/infer/__main__.py中的msprof_run_profiling函数来拉起msprof命令进行性能数据采集的。若需要修改性能数据采集参数，可根据实际情况修改msprof_run_profiling函数中的msprof_cmd参数。示例如下：

  ```bash
  msprof_cmd="{} --output={}/profiler --application=\"{}\" --model-execution=on --sys-hardware-mem=on --sys-cpu-profiling=off --sys-profiling=off --sys-pid-profiling=off --dvpp-profiling=on --runtime-api=on --task-time=on --aicpu=on".format(
          msprof_bin, args.output, cmd)
  ```

  该方式进行性能数据采集时，首先检查是否存在msprof命令：

  - 若命令存在，则使用该命令进行性能数据采集、解析并导出为可视化的timeline和summary文件。
  - 若命令不存在，则调用acl.json配置文件进行性能数据采集。采集的性能数据文件未自动解析，需要参见《[CANN 开发工具指南](https://www.hiascend.com/document/detail/zh/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)》中的“性能分析工具>高级功能>数据解析与导出”章节，将性能数据解析并导出为可视化的timeline和summary文件。
  - 若环境配置了GE_PROFILING_TO_STD_OUT=1，则--profiler参数采集性能数据时使用的是acl.json配置文件方式。采集的性能数据文件未自动解析，需要参见《[解析profiling文件](https://github.com/Ascend/tools/blob/master/ada/doc/ada_pa.md)》对性能数据进行解析。

  更多性能数据采集参数介绍请参见《[CANN 开发工具指南](https://www.hiascend.com/document/detail/zh/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)》中的“性能分析工具>高级功能>性能数据采集（msprof命令行方式）”章节。

+ acl_json_path优先级高于profiler和dump，同时设置时以acl_json_path为准。

+ profiler参数和dump参数，必须要增加output参数，指示输出路径。

+ profiler和dump可以分别使用，但不能同时启用。

示例命令如下：

```bash
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --acl_json_path ./acl.json
python3 -m ais_bench  --model /home/model/resnet50_v1.om --output ./ --dump 1
python3 -m ais_bench  --model /home/model/resnet50_v1.om --output ./ --profiler 1
```

 #### 输出结果文件保存场景

默认情况下，ais_bench推理工具执行后不保存输出结果数据文件，配置相关参数后，可生成的结果数据如下：

| 文件/目录                                | 说明                                                         |
| ---------------------------------------- | ------------------------------------------------------------ |
| {文件名}.bin、{文件名}.npy或{文件名}.txt | 模型推理输出结果文件。<br/>文件命名格式：名称_输出序号.后缀。不指定input时（纯推理），名称固定为“pure_infer_data”；指定input时，名称以第一个输入的第一个名称命名；输出的序号从0开始按输出先后顺序排列；文件名后缀由--outfmt参数控制。<br/>默认情况下，会在--output参数指定的目录下创建“日期+时间”的目录，并将结果文件保存在该目录下；当指定了--output_dirname时，结果文件将直接保存在--output_dirname参数指定的目录下。<br/>指定--output_dirname参数时，多次执行工具推理会导致结果文件因同名而覆盖。 |
| xx_summary.json                          | 工具输出模型性能结果数据。默认情况下，“xx”以“日期+时间”命名；当指定了--output_dirname时，“xx”以--output_dirname指定的目录名称命名。<br/>指定--output_dirname参数时，多次执行工具推理会导致结果文件因同名而覆盖。 |
| dump                                     | dump数据文件目录。使用--dump开启dump时，在--output参数指定的目录下创建dump目录，保存dump数据文件。 |
| profiler                                 | Profiler采集性能数据文件目录。使用--profiler开启性能数据采集时，在--output参数指定的目录下创建profiler目录，保存性能数据文件。 |

- 仅设置--output参数。示例命令及结果如下：

  ```bash
  python3 -m ais_bench --model ./pth_resnet50_bs1.om --output ./result
  ```

  ```bash
  result
  |-- 2022_12_17-07_37_18
  │   `-- pure_infer_data_0.bin
  `-- 2022_12_17-07_37_18_summary.json
  ```

- 设置--input和--output参数。示例命令及结果如下：

  ```bash
  # 输入的input文件夹内容如下
  ls ./data
  196608-0.bin  196608-1.bin  196608-2.bin  196608-3.bin  196608-4.bin  196608-5.bin  196608-6.bin  196608-7.bin  196608-8.bin  196608-9.bin
  ```

  ```bash
  python3 -m ais_bench --model ./pth_resnet50_bs1.om --input ./data --output ./result
  ```

  ```bash
  result/
  |-- 2023_01_03-06_35_53
  |   |-- 196608-0_0.bin
  |   |-- 196608-1_0.bin
  |   |-- 196608-2_0.bin
  |   |-- 196608-3_0.bin
  |   |-- 196608-4_0.bin
  |   |-- 196608-5_0.bin
  |   |-- 196608-6_0.bin
  |   |-- 196608-7_0.bin
  |   |-- 196608-8_0.bin
  |   `-- 196608-9_0.bin
  `-- 2023_01_03-06_35_53_summary.json
  ```

- 设置--output_dirname参数。示例命令及结果如下：

  ```bash
  python3 -m ais_bench --model ./pth_resnet50_bs1.om --output ./result --output_dirname subdir
  ```

  ```bash
  result
  |-- subdir
  │   `-- pure_infer_data_0.bin
  `-- subdir_summary.json
  ```

- 设置--dump参数。示例命令及结果如下：

  ```bash
  python3 -m ais_bench --model ./pth_resnet50_bs1.om --output ./result --dump 1
  ```
  
  ```bash
  result
  |-- 2022_12_17-07_37_18
  │   `-- pure_infer_data_0.bin
  |-- dump
  `-- 2022_12_17-07_37_18_summary.json
  ```
  
- 设置--profiler参数。示例命令及结果如下：

  ```bash
  python3 -m ais_bench --model ./pth_resnet50_bs1.om --output ./result --profiler 1
  ```

  ```bash
  result
  |-- 2022_12_17-07_56_10
  │   `-- pure_infer_data_0.bin
  |-- profiler
  │   `-- PROF_000001_20221217075609326_GLKQJOGROQGOLIIB
  `-- 2022_12_17-07_56_10_summary.json
  ```



### 输出结果

ais_bench推理工具执行后，打屏输出结果示例如下：

- display_all_summary=False时，打印如下：

  ```bash
  [INFO] -----------------Performance Summary------------------
  [INFO] NPU_compute_time (ms): min = 0.6610000133514404, max = 0.6610000133514404, mean = 0.6610000133514404, median = 0.6610000133514404, percentile(99%) = 0.6610000133514404
  [INFO] throughput 1000*batchsize.mean(1)/NPU_compute_time.mean(0.6610000133514404): 1512.8592735267011
  [INFO] ------------------------------------------------------
  ```

- display_all_summary=True时，打印如下：

  ```bash
  [INFO] -----------------Performance Summary------------------
  [INFO] H2D_latency (ms): min = 0.05700000002980232, max = 0.05700000002980232, mean = 0.05700000002980232, median = 0.05700000002980232, percentile(99%) = 0.05700000002980232
  [INFO] NPU_compute_time (ms): min = 0.6650000214576721, max = 0.6650000214576721, mean = 0.6650000214576721, median = 0.6650000214576721, percentile(99%) = 0.6650000214576721
  [INFO] D2H_latency (ms): min = 0.014999999664723873, max = 0.014999999664723873, mean = 0.014999999664723873, median = 0.014999999664723873, percentile(99%) = 0.014999999664723873
  [INFO] throughput 1000*batchsize.mean(1)/NPU_compute_time.mean(0.6650000214576721): 1503.759349974173
  ```

通过输出结果可以查看模型执行耗时、吞吐率。耗时越小、吞吐率越高，则表示该模型性能越高。

**字段说明**

| 字段                  | 说明                                                         |
| --------------------- | ------------------------------------------------------------ |
| H2D_latency (ms)      | Host to Device的内存拷贝耗时。单位为ms。                     |
| min                   | 推理执行时间最小值。                                         |
| max                   | 推理执行时间最大值。                                         |
| mean                  | 推理执行时间平均值。                                         |
| median                | 推理执行时间取中位数。                                       |
| percentile(99%)       | 推理执行时间中的百分位数。                                   |
| NPU_compute_time (ms) | NPU推理计算的时间。单位为ms。                                |
| D2H_latency (ms)      | Device to Host的内存拷贝耗时。单位为ms。                     |
| throughput            | 吞吐率。吞吐率计算公式：1000 *batchsize/npu_compute_time.mean |
| batchsize             | 批大小。本工具不一定能准确识别当前样本的batchsize，建议通过--batchsize参数进行设置。 |

## 扩展功能

### 接口开放

开放ais_bench推理工具推理Python接口。

代码示例参考https://github.com/Ascend/tools/blob/master/ais-bench_workload/tool/ais_bench/test/interface_sample.py

可以通过如下示例代码完成ais_bench推理工具推理操作：

```python
def infer_simple():
  device_id = 0
  session = InferSession(device_id, model_path)

  *# create new numpy data according inputs info*
  barray = bytearray(session.get_inputs()[0].realsize)
  ndata = np.frombuffer(barray)

  outputs = session.infer([ndata])
  print("outputs:{} type:{}".format(outputs, type(outputs)))
    
  print("static infer avg:{} ms".format(np.mean(session.sumary().exec_time_list)))
```

动态Shape推理：

```bash
def infer_dymshape():
  device_id = 0
  session = InferSession(device_id, model_path)
  ndata = np.zeros([1,3,224,224], dtype=np.float32)

  mode = "dymshape"
  outputs = session.infer([ndata], mode, custom_sizes=100000)
  print("outputs:{} type:{}".format(outputs, type(outputs)))
  print("dymshape infer avg:{} ms".format(np.mean(session.sumary().exec_time_list)))
```



### 推理异常保存文件功能

当出现推理异常时，会写入算子执行失败的输入输出文件到**当前目录**下。同时会打印出当前的算子执行信息。利于定位分析。示例如下：

```bash
python3 -m ais_bench --model ./test/testdata/bert/model/pth_bert_bs1.om --input ./random_in0.bin,random_in1.bin,random_in2.bin
```

```bash
[INFO] acl init success
[INFO] open device 0 success
[INFO] load model ./test/testdata/bert/model/pth_bert_bs1.om success
[INFO] create model description success
[INFO] get filesperbatch files0 size:1536 tensor0size:1536 filesperbatch:1 runcount:1
[INFO] exception_cb streamId:103 taskId:10 deviceId: 0 opName:bert/embeddings/GatherV2 inputCnt:3 outputCnt:1
[INFO] exception_cb hostaddr:0x124040800000 devaddr:0x12400ac48800 len:46881792 write to filename:exception_cb_index_0_input_0_format_2_dtype_1_shape_30522x768.bin
[INFO] exception_cb hostaddr:0x124040751000 devaddr:0x1240801f6000 len:1536 write to filename:exception_cb_index_0_input_1_format_2_dtype_3_shape_384.bin
[INFO] exception_cb hostaddr:0x124040752000 devaddr:0x12400d98e400 len:4 write to filename:exception_cb_index_0_input_2_format_2_dtype_3_shape_.bin
[INFO] exception_cb hostaddr:0x124040753000 devaddr:0x12400db20400 len:589824 write to filename:exception_cb_index_0_output_0_format_2_dtype_1_shape_384x768.bin
EZ9999: Inner Error!
EZ9999  The error from device(2), serial number is 17, there is an aicore error, core id is 0, error code = 0x800000, dump info: pc start: 0x800124080041000, current: 0x124080041100, vec error info: 0x1ff1d3ae, mte error info: 0x3022733, ifu error info: 0x7d1f3266f700, ccu error info: 0xd510fef0003608cf, cube error info: 0xfc, biu error info: 0, aic error mask: 0x65000200d000288, para base: 0x124080017040, errorStr: The DDR address of the MTE instruction is out of range.[FUNC:PrintCoreErrorInfo]
      
# ls exception_cb_index_0_* -lh
-rw-r--r-- 1 root root  45M Jan  7 08:17 exception_cb_index_0_input_0_format_2_dtype_1_shape_30522x768.bin
-rw-r--r-- 1 root root 1.5K Jan  7 08:17 exception_cb_index_0_input_1_format_2_dtype_3_shape_384.bin
-rw-r--r-- 1 root root    4 Jan  7 08:17 exception_cb_index_0_input_2_format_2_dtype_3_shape_.bin
-rw-r--r-- 1 root root 576K Jan  7 08:17 exception_cb_index_0_output_0_format_2_dtype_1_shape_384x768.bin
```
如果有需要将生成的异常bin文件转换为npy文件，请使用[转换脚本convert_exception_cb_bin_to_npy.py](https://github.com/Ascend/tools/tree/master/ais-bench_workload/tool/ais_bench/test/convert_exception_cb_bin_to_npy.py).  
使用方法：python3 convert_exception_cb_bin_to_npy.py --input {bin_file_path}。支持输入bin文件或文件夹。


## FAQ
[FAQ](FAQ.md) 
