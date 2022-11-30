# ais_bench 推理工具使用文档

## 介绍
本文介绍ais_bench推理工具，该工具包含前端和后端两部分。
后端基于c++开发，实现通用推理功能；
前端基于python开发，实现用户界面功能。

## 使用环境与依赖
已安装开发运行环境的昇腾AI推理设备。需要安装python3,  不支持python2

## 一键安装
安装aclruntime包
pip3  install -v --force-reinstall 'git+https://github.com/Ascend/tools.git#egg=aclruntime&subdirectory=ais-bench_workload/tool/ais_infer/backend'

安装ais_bench推理程序包
pip3  install -v --force-reinstall 'git+https://github.com/Ascend/tools.git#egg=ais_bench&subdirectory=ais-bench_workload/tool/ais_infer'

## 源代码构建与安装
1. 本推理工具编译需要安装好CANN环境。用户可以设置CANN_PATH环境变量指定安装的CANN版本路径，比如export CANN_PATH=/xxx/nnae/latest/.
如果不设置，本推理工具默认会从
CANN_PATH
/usr/local/Ascend/nnae/latest/
/usr/local/Ascend/ascend-toolkit/latest
分别尝试去获取

1. 进入ais-bench/tool/ais_infer目录下执行如下命令进行编译，即可生成推理后端whl包

   为了提高易用性。增加ais_bench的python包。可以通过如下命令进行安装。

```Bash
root@root: /home/tools# cd ais-bench_workload/tool/ais_infer/
# 构建ais_bench推理后端包aclruntime
root@root: /home/tools/ais-bench_workload/tool/ais_infer# pip3  wheel ./backend/ -v
# 构建ais_bench推理前端包ais_bench
root@root: /home/tools/ais-bench_workload/tool/ais_infer# pip3  wheel ./ -v
```
2. 在运行设备上执行如下命令，进行安装。

   注意： 如果提示已安装 请增加--force-reinstall参数强制安装
```
# 安装ais_bench推理后端包aclruntime
pip3 install ./aclruntime-0.0.2-cp37-cp37m-linux_aarch64.whl --force-reinstall
# 安装ais_bench推理前端包ais_bench
pip3 install ./ais_bench-0.0.2-py3-none-any.whl --force-reinstall
```
## 压缩包安装

如果拿到的是压缩包，可以按照如下流程执行
1. 执行如下命令 执行解压操作
```
root@root:/home/# tar xvf aclruntime-aarch64.tar.gz
```
2. 执行如下命令，安装aisbench后端whl包
```
root@root:/home/tool# cd aclruntime-aarch64/
root@root:/home/aclruntime-aarch64# pip3 install ./aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
```
如果安装提示已经安装了相同版本的whl，请执行命令请添加参数"--force-reinstall"

## 运行说明
在安装好whl包后，即可按照如下流程进行推理命令执行
1. 确定requirement中依赖是否执行，如果没有安装，则执行如下命令进行安装
```
root@root:/home/aclruntime-aarch64# pip3 install -r ./requirements.txt
```

2. 确定是否设置了CANN包的环境变量，如果没有设置，请执行如下命令进行设置，注意CANN包路径如果安装在其他目录,需手动替换
```
root@root:/home/aclruntime-aarch64# source  /usr/local/Ascend/ascend-toolkit/set_env.sh
```

3. 运行ais_infer.py 执行相关推理命令操作

## 使用方法

 ### 使用入口
当前入口程序有两个，可以使用原有的ais_infer.py作为入口。如下调用

```
python3 ais_infer.py --model /home/model/resnet50_v1.om
```

也可以使用ais_bench的python包作为入口进行调用

```
python3 -m ais_bench --model /home/model/resnet50_v1.om
```

**为了便利使用。推荐大家使用第二种方式进行调用。这样不需要依赖具体文件夹内容，直接使用系统中的whl包。**

 ### 纯推理场景 会构造全为0的假数据送入模型推理
```
python3 -m ais_bench --model /home/model/resnet50_v1.om --output ./ --outfmt BIN --loop 5
```

### 调试模式开启
debug调试模式 默认不使能。 设置为true 或1时可以开启调试模式。设置命令如下。
```
python3 -m ais_bench --model /home/model/resnet50_v1.om --output ./ --debug=1
```

调试模式开启后会增加更多的打印信息，包括
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
```
[DEBUG] model aclExec cost : 2.336000
```
- 模型输入输出等具体操作信息


 ### 文件输入场景 input传入文件列表 通过,进行分隔
 本场景会根据文件输入和模型实际输入进行组batch

```
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --input "./1.bin,./2.bin,./3.bin,./4.bin,./5.bin"

```

注意针对于动态分档或动态shape场景，会根据实际模型实际需要size与输入size判断进行组batch操作
```
python3 -m ais_bench --model ./resnet50_v1_dynamicbatchsize_fp32.om --input "./1.bin,./2.bin,./3.bin,./4.bin,./5.bin" --dymBatch 2
```

 ### 文件夹输入场景 input传入文件夹列表 通过,进行分隔
 本场景会根据文件输入和模型输入进行组batch 根据 模型输入size与文件输入size进行对比得出

```
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --input "./"

```

如下指令示例，模型输入需与传入文件夹的个数一致。bert模型有三个输入 则必须传入3个文件夹，且三个文件夹分别对应模型的三个输入，顺序要对应。
模型输入参数的信息可以通过开启调试模式查看，bert模型的三个输入依次为input_ids、 input_mask、 segment_ids，所以依次传入三个文件夹，
第一个文件夹“./data/SQuAD1.1/input_ids",  对应模型第一个参数"input_ids"的输入 
第二文件夹"./data/SQuAD1.1/input_mask",  对应第二个输入"input_mask"的输入
第三个文件夹"./data/SQuAD1.1/segment_ids",  对应第三个输入"segment_ids"的输入

```
python3 -m ais_bench --model ./save/model/BERT_Base_SQuAD_BatchSize_1.om  --input ./data/SQuAD1.1/input_ids,./data/SQuAD1.1/input_mask,./data/SQuAD1.1/segment_ids
```

 ### 输出结果保存场景
 默认推理结果数据不保存文件。

如果设置了output参数。则保存到output目录下。默认会建立日期+时间的子文件夹保存推理输出结果 而summary文件和profiling文件将保存到output目录下

 ```
# python3 -m ais_bench --model  ./pth_resnet50_bs1.om  --output ./
# ls ./2022_11_29-03_11_35
pure_infer_data_0.bin
# ls ./2022_11_29-03_11_35_summary.json
./2022_11_29-03_11_35_summary.json
 ```

```
python3 -m ais_bench --model  ./pth_resnet50_bs1.om  --output ./ --profiler 1
# profiler文件保存在output目录下
# ls profiler/PROF_000001_20221129060140649_HGPIAQEDEDPMFGAC/
device_0
```

 如果指定output_dirname 将保存到output_dirname的子文件夹下
```
 # python3 -m ais_bench --model ./pth_resnet50_bs1.om  --output ./ --output_dirname subdir
# ls ./subdir/pure_infer_data_0.bin
./subdir/pure_infer_data_0.bin
# ls ./subdir_summary.json
./subdir_summary.json
```

 ### 动态分档场景 主要包含动态batch 动态宽高 动态Dims三种场景，需要分别传入dymBatch dymHW dymDims指定实际档位信息

#### 动态batch场景 档位为1 2 4 8档，设置档位为2 本程序将获取实际模型输入组batch 每2个输入来组一组batch进行推理
```
python3 -m ais_bench --model ./resnet50_v1_dynamicbatchsize_fp32.om --input=./data/ --dymBatch 2
```

#### 动态HW宽高场景 档位为224,224;448,448档，设置档位为224,224 本程序将获取实际模型输入组batch
```
python3 -m ais_bench --model ./resnet50_v1_dynamichw_fp32.om --input=./data/ --dymHW 224,224

```

#### 动态Dims场景 设置档位为1,3,224,224 本程序将获取实际模型输入组batch
```
python3 -m ais_bench --model resnet50_v1_dynamicshape_fp32.om --input=./data/ --dymDims actual_input_1:1,3,224,224
```

#### 自动设置dims模式（动态dims模型）

针对动态dims模型，增加auto_set_dymdims_mode参数，根据输入文件的shape信息自动设置模型的shape参数。

针对动态dims模型。输入数据的shape可能是不固定的，比如一个输入文件shape为1,3,224,224 另一个输入文件shape为 1,3,300,300。如果两个文件要一起推理的话，需要设置两次动态shape参数，那正常的话是不支持的。针对该种场景，增加auto_set_dymdims_mode模式，根据输入文件的shape信息自动设置模型的shape参数，

```
python3 -m ais_bench --model resnet50_v1_dynamicshape_fp32.om --input=./data/ --auto_set_dymdims_mode 1
```

**注意该场景下输入必须为npy文件，如果是bin文件将获取不到真实的shape信息。**

### 动态shape场景 atc设置为[1~8,3,200~300,200~300]，设置档位为1,3,224,224 本程序将获取实际模型输入组batch 注意动态shape的输出大小经常为0需要通过outputSize参数设置对应参数的内存大小

```
python3 -m ais_bench --model resnet50_v1_dynamicshape_fp32.om --dymShape actual_input_1:1,3,224,224 --outputSize 10000
```

#### 自动设置shape模式（动态shape模型）

针对动态shape模型。输入数据的shape可能是不固定的，比如一个输入文件shape为1,3,224,224 另一个输入文件shape为 1,3,300,300。如果两个文件要一起推理的话，需要设置两次动态shape参数，那正常的话是不支持的。针对该种场景，增加auto_set_dymshape_mode模式，根据输入文件的shape信息自动设置模型的shape参数，

```
python3 -m ais_bench --model ./pth_resnet50_dymshape.om  --outputSize 100000 --auto_set_dymshape_mode 1  --input ./dymdata
```

**注意该场景下输入必须为npy文件，如果是bin文件将获取不到真实的shape信息。**

#### 动态shape模型range测试模式

输入动态shape range范围。对于该范围内的shape分别进行推理。得出各自的性能指标

```shell
# 对1,3,224,224 1,3,224,225 1,3,224,226进行分别推理
# python3 -m ais_bench --model ./pth_resnet50_dymshape.om  --outputSize 100000 --dymShape_range actual_input_1:1,3,224,224~226
[INFO] -----------------dyshape_range Performance Summary------------------
[INFO] run_count:3 success_count:3 avg_throughput:246.77165024828034
[INFO] 0 dymshape:actual_input_1:1,3,224,225 bs:1 result:OK throughput:269.54177620425804
[INFO] 1 dymshape:actual_input_1:1,3,224,226 bs:1 result:OK throughput:239.29170225734876
[INFO] 2 dymshape:actual_input_1:1,3,224,224 bs:1 result:OK throughput:231.48147228323418


# python3 -m ais_bench --model ./pth_resnet50_dymshape.om  --outputSize 100000 --dymShape_range actual_input_1:1~2,3,224-300,224-300
[INFO] -----------------dyshape_range Performance Summary------------------
[INFO] run_count:8 success_count:8 avg_throughput:398.7681101272126
[INFO] 0 dymshape:actual_input_1:2,3,224,224 bs:2 result:OK throughput:633.5128156214085
[INFO] 1 dymshape:actual_input_1:2,3,300,224 bs:2 result:OK throughput:534.7593569251704
[INFO] 2 dymshape:actual_input_1:2,3,224,300 bs:2 result:OK throughput:513.2152840194153
[INFO] 3 dymshape:actual_input_1:2,3,300,300 bs:2 result:OK throughput:448.63165496928906
[INFO] 4 dymshape:actual_input_1:1,3,224,300 bs:1 result:OK throughput:311.42946455686143
[INFO] 5 dymshape:actual_input_1:1,3,300,224 bs:1 result:OK throughput:292.9115377690921
[INFO] 6 dymshape:actual_input_1:1,3,300,300 bs:1 result:OK throughput:227.94620033507945
[INFO] 7 dymshape:actual_input_1:1,3,224,224 bs:1 result:OK throughput:227.73856682138447


# cat dym.info
actual_input_1:1,3,224-300,224-225
actual_input_1:8-9,3,224-300,260-300
# python3 -m ais_bench --model ./pth_resnet50_dymshape.om  --outputSize 100000 --dymShape_range ./dym.info
[INFO] -----------------dyshape_range Performance Summary------------------
[INFO] run_count:12 success_count:12 avg_throughput:701.4533561722105
[INFO] 0 dymshape:actual_input_1:8,3,224,260 bs:8 result:OK throughput:1189.5910949365423
[INFO] 1 dymshape:actual_input_1:8,3,224,300 bs:8 result:OK throughput:1062.4169690698604
[INFO] 2 dymshape:actual_input_1:9,3,224,260 bs:9 result:OK throughput:1009.3080839755332
[INFO] 3 dymshape:actual_input_1:8,3,300,260 bs:8 result:OK throughput:877.9630807069874
[INFO] 4 dymshape:actual_input_1:8,3,300,300 bs:8 result:OK throughput:840.8660974692447
[INFO] 5 dymshape:actual_input_1:9,3,224,300 bs:9 result:OK throughput:836.1981221927723
[INFO] 6 dymshape:actual_input_1:9,3,300,260 bs:9 result:OK throughput:765.8922381333857
[INFO] 7 dymshape:actual_input_1:9,3,300,300 bs:9 result:OK throughput:689.3382481843958
[INFO] 8 dymshape:actual_input_1:1,3,300,225 bs:1 result:OK throughput:317.7629413291059
[INFO] 9 dymshape:actual_input_1:1,3,224,224 bs:1 result:OK throughput:310.6554733134515
[INFO] 10 dymshape:actual_input_1:1,3,224,225 bs:1 result:OK throughput:302.0235479203686
[INFO] 11 dymshape:actual_input_1:1,3,300,224 bs:1 result:OK throughput:215.42437683487793

```

### profiler或者dump场景

支持以--acl_json_path、--profiler、--dump参数形式实现：
+ acl_json_path 为指定路径的json文件，可以在该文件中修改对应的参数信息。
+ profiler 为固化到程序中的一组acl_json配置，生成的profiling数据保存在 output路径的profiler文件夹中。**注意运行中会首先检查msprof命令是否存在，如果存在，则通过msprof拉起ais_bench推理程序，这样可以采集、解析profiling数据，更为方便。**
+ acl_json_path 优先级高于 profiler dump。 同时设置时以acl_json_path为准
+ profiler参数和dump参数 必须要增加output参数。指示输出路径。
+ profiler和dump可以分别使用，但不能同时启用

指令示例:

```bash
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --acl_json_path ./acl.json
python3 -m ais_bench  --model /home/model/resnet50_v1.om --output ./ --dump 1
python3 -m ais_bench  --model /home/model/resnet50_v1.om --output ./ --profiler 1
```

### 结果summary功能

针对结果输出，本程序会在增加output目录下创建 xxxx_summary.json文件打印参数值，便于汇总统计

其中xxxx为输入创建的子文件夹，比如默认是2022_11_23-06_40_37之类的当前日期时间格式的，如果设置为output_dirname参数的话，就是output_dirname的值。

具体结果信息如下
NPU_compute_time: 推理调用总时间
throughput: 吞吐率。吞吐率计算公式：1000 *batchsize/npu_compute_time.mean

注意batchsize值需要自己进行设置，因为本程序不能准确得到当前样本的batchsize。需要通过batchsize参数进行设置。

打印如下:

```bash
[INFO] -----------------Performance Summary------------------
[INFO] NPU_compute_time (ms): min = 0.6610000133514404, max = 0.6610000133514404, mean = 0.6610000133514404, median = 0.6610000133514404, percentile(99%) = 0.6610000133514404
[INFO] throughput 1000*batchsize(1)/NPU_compute_time.mean(0.6610000133514404): 1512.8592735267011
[INFO] ------------------------------------------------------
```

注意 当前默认不展示h2d和d2h的耗时信息，如果需要打开，请设置display_all_summary=True。设置后的打印信息如下

```
[INFO] -----------------Performance Summary------------------
[INFO] H2D_latency (ms): min = 0.05700000002980232, max = 0.05700000002980232, mean = 0.05700000002980232, median = 0.05700000002980232, percentile(99%) = 0.05700000002980232
[INFO] NPU_compute_time (ms): min = 0.6650000214576721, max = 0.6650000214576721, mean = 0.6650000214576721, median = 0.6650000214576721, percentile(99%) = 0.6650000214576721
[INFO] D2H_latency (ms): min = 0.014999999664723873, max = 0.014999999664723873, mean = 0.014999999664723873, median = 0.014999999664723873, percentile(99%) = 0.014999999664723873
[INFO] throughput 1000*batchsize(1)/NPU_compute_time.mean(0.6650000214576721): 1503.759349974173
```



### 接口开放

开放推理python接口。

参考https://github.com/Ascend/tools/blob/be75cf413af2238147708c46b6745dd5eee68f09/ais-bench_workload/tool/ais_infer/test/interface_sample.py

可以通过如下几行命令就完成推理操作

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

动态shape推理

```
def infer_dymshape():
  device_id = 0
  session = InferSession(device_id, model_path)
  ndata = np.zeros([1,3,224,224], dtype=np.float32)

  mode = "dymshape"
  outputs = session.infer([ndata], mode, custom_sizes=100000)
  print("outputs:{} type:{}".format(outputs, type(outputs)))
  print("dymshape infer avg:{} ms".format(np.mean(session.sumary().exec_time_list)))
```


### 增加异常写文件功能

当出现推理异常时，会写入算子执行失败的输入输出文件到**当前目录**下。同时会打印出当前的算子执行信息。利于定位分析。

```bash
(lcm) root@4f0ab57f0243:/home/infname77/lcm/code/tools_develop/ais-bench_workload/tool/ais_infer# python3 -m ais_bench --model  ./test/testdata/bert/model/pth_bert_bs1.om --input ./random_in0.bin,random_in1.bin,random_in2.bin
[INFO] acl init success
[INFO] open device 0 success
[INFO] load model ./test/testdata/bert/model/pth_bert_bs1.om success
[INFO] create model description success
[INFO] get filesperbatch files0 size:1536 tensor0size:1536 filesperbatch:1 runcount:1
[INFO] exception_cb streamId:4 taskId:22 deviceId: 0 opName:bert/embeddings/GatherV2 inputCnt:3 outputCnt:1
[INFO] exception_cb format:2 hostaddr:0x124040800000 devaddr:0x12400ac48a00 len:46881792 write to filename:exception_cb_index_0_input_0.bin
[INFO] exception_cb format:2 hostaddr:0x124040751000 devaddr:0x12408020c000 len:1536 write to filename:exception_cb_index_0_input_1.bin
[INFO] exception_cb format:2 hostaddr:0x124040752000 devaddr:0x12400d98e600 len:4 write to filename:exception_cb_index_0_input_2.bin
[INFO] exception_cb format:2 hostaddr:0x124040753000 devaddr:0x12400db20400 len:589824 write to filename:exception_cb_index_0_output_0.bin
EZ9999: Inner Error!
EZ9999  The error from device(2), serial number is 17, there is an aicore error, core id is 0, error code = 0x800000, dump info: pc start: 0x800124080041000, current: 0x124080041100, vec error info: 0x1ff1d3ae, mte error info: 0x3022733, ifu error info: 0x7d1f3266f700, ccu error info: 0xd510fef0003608cf, cube error info: 0xfc, biu error info: 0, aic error mask: 0x65000200d000288, para base: 0x124080017040, errorStr: The DDR address of the MTE instruction is out of range.[FUNC:PrintCoreErrorInfo]
      
(lcm) root@4f0ab57f0243:/home/infname77/lcm/code/tools_develop/ais-bench_workload/tool/ais_infer# ls exception_cb_index_0_* -lh
-rwxrwxrwx 1 root root  45M Nov 28 12:40 exception_cb_index_0_input_0.bin
-rwxrwxrwx 1 root root 1.5K Nov 28 12:40 exception_cb_index_0_input_1.bin
-rwxrwxrwx 1 root root    4 Nov 28 12:40 exception_cb_index_0_input_2.bin
-rwxrwxrwx 1 root root 576K Nov 28 12:40 exception_cb_index_0_output_0.bin
```


## 参数说明

| 参数名   | 说明                            |
| -------- | ------------------------------- |
| --model  | 需要进行推理的om模型            |
| --input  | 模型需要的输入，支持bin文件和目录，若不加该参数，会自动生成都为0的数据                  |
| --output | 推理结果输出路径。默认会建立日期+时间的子文件夹保存输出结果 如果指定output_dirname 将保存到output_dirname的子文件夹下。|
| --output_dirname | 推理结果输出子文件夹。可选参数。与参数output搭配使用，单独使用无效。设置该值时输出结果将保存到 output/output_dirname文件夹中              |
| --outfmt | 输出数据的格式，默认”BIN“，可取值“NPY”、“BIN”、“TXT” |
| --loop   | 推理次数，可选参数，默认1，profiler为true时，推荐为1 |
| --debug  | 调试开关，可打印model的desc信息和其他详细执行信息，true或者false，可选参数，默认false |
| --device | 指定运行设备 [0,255]，可选参数，默认0 |
| --dymBatch  | 动态Batch参数，指定模型输入的实际batch，可选参数。 <br>如atc模型转换时设置 --input_shape="data:-1,600,600,3;img_info:-1,3" --dynamic_batch_size="1,2,4,8" , dymBatch参数可设置为：--dymBatch 2|
| --dymHW  | 动态分辨率参数，指定模型输入的实际H、W，可选参数。 <br>如atc模型转换时设置 --input_shape="data:8,3,-1,-1;img_info:8,4,-1,-1"  --dynamic_image_size="300,500;600,800" , dymHW参数可设置为：--dymHW 300,500|
| --dymDims| 动态维度参数，指定模型输入的实际shape，可选参数。 <br>如atc模型转换时设置 --input_shape="data:1,-1;img_info:1,-1" --dynamic_dims="224,224;600,600" , dymDims参数可设置为：--dymDims "data:1,600;img_info:1,600"|
| --dymShape| 动态shape参数，指定模型输入的实际shape，可选参数。 <br>如atc模型转换时设置 --input_shape_range="input1:\[8\~20,3,5,-1\];input2:\[5,3\~9,10,-1\]" , dymShape参数可设置为：--dymShape "input1:8,3,5,10;input2:5,3,10,10"<br>设置此参数时，必须设置  --outputSize。 |
| --auto_set_dymshape_mode| 自动设置动态shape模式，可选参数, 默认false。<br>针对动态shape模型，根据输入的文件的信息，自动设置shape参数 注意 输入数据只能为npy文件 因为bin文件不能读取shape信息<br>如 --auto_set_dymshape_mode true" |
| --auto_set_dymdims_mode | 自动设置动态dims模式，可选参数, 默认false。<br/>针对动态档位dims模型，根据输入的文件的信息，自动设置shape参数 注意 输入数据只能为npy文件 因为bin文件不能读取shape信息<br/>如 --auto_set_dymdims_mode true" |
| --outputSize| 指定模型的输出size，有几个输出，就设几个值，可选参数。<br>动态shape场景下，获取模型的输出size可能为0，用户需根据输入的shape预估一个较合适的值去申请内存。<br>如 --outputSize "10000,10000,10000"|
| --batchsize | 模型batch size 默认为1 。当前推理模块根据模型输入和文件输出自动进行组batch。参数传递的batchszie有且只用于结果吞吐率计算。请务必注意需要传入该值，以获取计算正确的吞吐率      |
| --pure_data_type | 纯推理数据类型。可选参数，默认"zero",可取值"zero"或"random"。<br>设置为zero时，纯推理数据全部是0；设置为random时，每一个推理数据是[0,255]之间的随机整数|
| --profiler | profiler开关，true或者false, 可选参数，默认false。<br>--output参数必须提供。profiler数据在--output参数指定的目录下的profiler文件夹内。不能与--dump同时为true。|
| --dump |dump开关，true或者false, 可选参数，默认false。<br>--output参数必须提供。dump数据在--output参数指定的目录下的dump文件夹内。不能与--profiler同时为true。|
| --acl_json_path | acl json文件 profiling或者dump时设置。当该参数设置时，--dump和--profiler参数无效。      |
| --output_batchsize_axis |输出tensor的batchsize轴，默认0。输出结果保存文件时，根据哪个轴进行切割推理结果，比如batchsize为2，表示2个输入文件进行组batch进行推理，那输出结果的batch维度是在哪个轴。默认为0轴，按照0轴进行切割为2份，但是部分模型的输出batch为1轴，所以要设置该值为1。|
| --display_all_summary |是否显示所有的汇总信息包含h2d和d2h。默认为false|
| --warmup_count |推理预热次数。默认为1|
| --dymShape_range |动态shape的阈值范围。如果设置该参数，那么将根据参数中所有的shape列表进行依次推理。得到汇总推理信息。格式为 name1:1:3:200~224:224-230;name2:1,300     name为模型输入名字，~表示范围 -表示某一位的取值|
| --help| 工具使用帮助信息                  |

## FAQ
[FAQ](FAQ.md) 