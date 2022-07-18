# ais_infer 推理工具使用文档

## 介绍
本文介绍AisBench推理工具，该工具包含前端和后端两部分。
后端基于c+开发，实现通用推理功能；
前端基于python开发，实现用户界面功能。

## 使用环境与依赖
已安装开发运行环境的昇腾AI推理设备。

## 源代码构建与安装
1. 本推理工具编译需要安装好CANN环境。用户可以设置CANN_PATH环境变量指定安装的CANN版本路径，比如export CANN_PATH=/xxx/nnae/latest/.
如果不设置，本推理工具默认会从
CANN_PATH
/usr/local/Ascend/nnae/latest/
/usr/local/Ascend/ascend-toolkit/latest
分别尝试去获取

1. 进入ais-bench/tool/ais_infer目录下执行如下命令进行编译，即可生成推理后端whl包

```Bash
root@root:/home/ais-bench# cd tool/ais_infer/backend/
root@root:/home/ais-bench/tool/ais_infer/backend# pip3.7 wheel ./
root@root:/home/ais-bench/tool/ais_infer/backend# ls
aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl  aisbench.egg-info  base  build  doc  frontend  pyproject.toml  python  setup.py  test

```
2. 在运行设备上执行如下命令，进行安装
```
pip3 install ./aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
```
如果安装提示已经安装了相同版本的whl，请执行命令请添加参数"--force-reinstall"

```
root@root:/home/ais-bench/tool/ais_infer# pip3  install ./aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
Looking in indexes: https://mirrors.aliyun.com/pypi/simple/
Processing ./aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
Installing collected packages: aclruntime
Successfully installed aclruntime-0.0.1
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

 ### 纯推理场景 会构造全为0的假数据送入模型推理
```
python3.7.5 ais_infer.py  --model /home/model/resnet50_v1.om --output ./ --outfmt BIN --loop 5
```


 ### 文件输入场景 input传入文件列表 通过,进行分隔
 本场景会根据文件输入和模型实际输入进行组batch

```
python3.7.5 ais_infer.py --model ./resnet50_v1_bs1_fp32.om --input "./1.bin,./2.bin,./3.bin,./4.bin,./5.bin"

```

注意针对于动态分档或动态shape场景，会根据实际模型实际需要size与输入size判断进行组batch操作
```
python3.7.5 ais_infer.py --model ./resnet50_v1_dynamicbatchsize_fp32.om --input "./1.bin,./2.bin,./3.bin,./4.bin,./5.bin" --dymBatch 2
```

 ### 文件夹输入场景 input传入文件夹列表 通过,进行分隔
 本场景会根据文件输入和模型输入进行组batch 根据 模型输入size与文件输入size进行对比得出

```
python3.7.5 ais_infer.py --model ./resnet50_v1_bs1_fp32.om --input "./"

```

如下样例，模型输入需与传入文件夹的个数一致，比如bert有三个输入 则必须传入3个文件夹
```
python3 ais_infer.py --model ./save/model/BERT_Base_SQuAD_BatchSize_1.om  --input ./data/SQuAD1.1/input_ids,./data/SQuAD1.1/input_mask,./data/SQuAD1.1/segment_ids
```

 ### 动态分档场景 主要包含动态batch 动态宽高 动态Dims三种场景，需要分别传入dymBatch dymHW dymDims指定实际档位信息

#### 动态batch场景 档位为1 2 4 8档，设置档位为2 本程序将获取实际模型输入组batch 每2个输入来组一组batch进行推理
```
python3 ais_infer.py --model ./resnet50_v1_dynamicbatchsize_fp32.om --input=./data/ --dymBatch 2

```

#### 动态HW宽高场景 档位为224,224;448,448档，设置档位为224,224 本程序将获取实际模型输入组batch
```
python3 ais_infer.py --model ./resnet50_v1_dynamichw_fp32.om --input=./data/ --dymHW 224,224

```

#### 动态Dims场景 设置档位为1,3,224,224 本程序将获取实际模型输入组batch
```
python3 ais_infer.py --model resnet50_v1_dynamicshape_fp32.om --input=./data/ --dymDims actual_input_1:1,3,224,224
```

### 动态shape场景 atc设置为[1~8,3,200~300,200~300]，设置档位为1,3,224,224 本程序将获取实际模型输入组batch 注意动态shape的输出大小经常为0需要通过outputSize参数设置对应参数的内存大小
```
python3 ais_infer.py --model resnet50_v1_dynamicshape_fp32.om --dymShape actual_input_1:1,3,224,224 --outputSize 10000
```

### profiling或者dump场景
```
python3.7.5 ais_infer.py --model ./resnet50_v1_bs1_fp32.om --acl_json_path ./acl.json

```
### 结果sumary功能
针对结果输出，本程序增加sumary.json文件打印参数值，便于汇总统计
具体结果信息如下
NPU_compute_time: 推理调用总时间
H2D_latency: 推理host到device延迟时间(ms)
D2H_latency: 推理device到host延迟时间(ms)
throughput: 吞吐率。吞吐率计算公式：1000 * batchsize/npu_compute_time.mean

打印如下:
sumary:{'NPU_compute_time': {'min': 2.4385452270507812, 'max': 2.587556838989258, 'mean': 2.5239520602756076, 'median': 2.529621124267578, 'percentile(99%)': 2.585916519165039}, 'H2D_latency': {'min': 0.5118846893310547, 'max': 1.0373592376708984, 'mean': 0.6650818718804253, 'median': 0.6296634674072266, 'percentile(99%)': 1.0063838958740234}, 'D2H_latency': {'min': 0.027894973754882812, 'max': 0.05745887756347656, 'mean': 0.04508760240342882, 'median': 0.04744529724121094, 'percentile(99%)': 0.05671501159667969}, 'throughput': 396.2040387925606}

## 参数说明

| 参数名   | 说明                            |
| -------- | ------------------------------- |
| --model  | 需要进行推理的om模型            |
| --input  | 模型需要的输入，支持bin文件和目录，若不加该参数，会自动生成都为0的数据                  |
| --output | 推理数据输出路径                |
| --outfmt | 输出数据的格式，NPY或者BIN      |
| --loop   | 推理次数，可选参数，默认1，profiler为true时，推荐为1 |
| --debug  | 调试开关，可打印model的desc信息，true或者false，可选参数，默认false |
| --device | 指定运行设备 [0,255]，可选参数，默认0 |
| --dymBatch  | 动态Batch参数，指定模型输入的实际batch，可选参数。 <br>如atc模型转换时设置 --input_shape="data:-1,600,600,3;img_info:-1,3" --dynamic_batch_size="1,2,4,8" , dymBatch参数可设置为：--dymBatch 2|
| --dymHW  | 动态分辨率参数，指定模型输入的实际H、W，可选参数。 <br>如atc模型转换时设置 --input_shape="data:8,3,-1,-1;img_info:8,4,-1,-1"  --dynamic_image_size="300,500;600,800" , dymHW参数可设置为：--dymHW 300,500|
| --dymDims| 动态维度参数，指定模型输入的实际shape，可选参数。 <br>如atc模型转换时设置 --input_shape="data:1,-1;img_info:1,-1" --dynamic_dims="224,224;600,600" , dymDims参数可设置为：--dymDims "data:1,600;img_info:1,600"|
| --dymShape| 动态shape参数，指定模型输入的实际shape，可选参数。 <br>如atc模型转换时设置 --input_shape_range="input1:\[8\~20,3,5,-1\];input2:\[5,3\~9,10,-1\]" , dymShape参数可设置为：--dymShape "input1:8,3,5,10;input2:5,3,10,10"<br>设置此参数时，必须设置 --input 和 --outputSize。 |
| --outputSize| 指定模型的输出size，有几个输出，就设几个值，可选参数。<br>动态shape场景下，获取模型的输出size可能为0，用户需根据输入的shape预估一个较合适的值去申请内存。<br>如 --outputSize "10000,10000,10000"|
| --acl_json_path | acl json文件 profiling或者dump时设置      |
| --batchsize | 模型batch size      |
| --pure_data_type | 纯推理数据类型。可选参数，默认"zero",可取值"zero"或"random"。<br>设置为zero时，纯推理数据全部是0；设置为random时，每一个图例数据是[0,255]之间的随机整数      |
| --help| 工具使用帮助信息                  |
