[中文](https://github.com/Ascend/tools/blob/master/ais-bench_workload/tool/ais_infer/Readme_cn.md)|EN

# AIS-bench referencing tool usage document

## Overview
This document introduces ais-bench referencing tool, which includes front-end and back-end parts.
The back-end is developed based on C++ to realize the general referencing function.
The front end is developed based on Python to realize the function of user interface.

## Environment Setup
Ascend AI referencing equipment of development and operation environment should be installed.Python3 needs to be installed. Python2 is not supported.

## Tool Preparation
The cann environment needs to be installed for the compilation of this referencing tool. Users can set CANN_PATH environment variable specifies the path of the installed cann version, such as export CANN_PATH=/xxx/nnae/latest/.
If not set, the referencing tool will get the information from the following path by default.
+ CANN_PATH
+ /usr/local/Ascend/nnae/latest/
+ /usr/local/Ascend/ascend-toolkit/latest

### Install by source codes
1. clone source codes
```Bash
git clone https://github.com/Ascend/ais-bench.git
```
2. compile and generate the referencing back-end WHL package

```Bash
root@root:/home/ais-bench# cd tool/ais_infer/backend/
root@root:/home/ais-bench/tool/ais_infer/backend# pip3.7 wheel ./
root@root:/home/ais-bench/tool/ais_infer/backend# ls
aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl  aisbench.egg-info  base  build  doc  frontend  pyproject.toml  python  setup.py  test

```
3. install
```
pip3 install ./aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
```
If the installation prompt indicates that the same version of WHL has been installed, execute the command and add the  parameter of "--force-reinstall"

```
root@root:/home/ais-bench/tool/ais_infer# pip3  install ./aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
Looking in indexes: https://mirrors.aliyun.com/pypi/simple/
Processing ./aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
Installing collected packages: aclruntime
Successfully installed aclruntime-0.0.1
```

### Install by package
With a compressed installing package, you can follow the following process.
1. unzip the compressed file
```
root@root:/home/# tar xvf aclruntime-aarch64.tar.gz
```
2. install the ais-bench backend WHL package
```
root@root:/home/tool# cd aclruntime-aarch64/
root@root:/home/aclruntime-aarch64# pip3 install ./aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
```
If the installation prompt indicates that the same version of WHL has been installed, execute the command and add the  parameter of "--force-reinstall"

## Tool Instructions
After installing the WHL package, execute the referencing command according to the following process.

1. determine whether the dependency in the requirement is executed. If it is not installed, execute the following command to install it.
```
root@root:/home/aclruntime-aarch64# pip3 install -r ./requirements.txt
```

2. determine whether the environment variable of the cann package is set. If not, please execute the following command to set it. Note that if the cann package path is installed in another directory, it needs to be replaced manually.
```
root@root:/home/aclruntime-aarch64# source  /usr/local/Ascend/ascend-toolkit/set_env.sh
```

3. run ais_infer.py and executes related referencing commands

## Usage Examples

 ### Pure inference scenario. Fake data (all 0s) is constructed and fed to the model for inference.
```
python3 ais_infer.py  --model /home/model/resnet50_v1.om --output ./ --outfmt BIN --loop 5
```

### Debug mode on
Set the debug parameter to 1, true, and true to enable debugging mode.，The setting command is as follows:
```
python3 ais_infer.py  --model /home/model/resnet50_v1.om --output ./ --debug=1
```

After the debugging mode is enabled, more printing information will be added as follows:
- Input and output parameter information of the model
```bash
input:
  #0    input_ids  (1, 384)  int32  1536  1536
  #1    input_mask  (1, 384)  int32  1536  1536
  #2    segment_ids  (1, 384)  int32  1536  1536
output:
  #0    logits:0  (1, 384, 2)  float32  3072  3072
```
- Detailed reasoning time-consuming information
```
[DEBUG] model aclExec cost : 2.336000
```
- Specific operation information such as model input and output

 ### File input scenario. Input is passed into the file list, separated by commas.

 In this scenario, group batch will be performed according to the file input and the actual input of the model.

```
python3 ais_infer.py --model ./resnet50_v1_bs1_fp32.om --input "./1.bin,./2.bin,./3.bin,./4.bin,./5.bin"

```

Note that for dynamic grading or dynamic shape scenes, the group batch operation will be judged according to the actual size and input size of the actual model.
```
python3 ais_infer.py --model ./resnet50_v1_dynamicbatchsize_fp32.om --input "./1.bin,./2.bin,./3.bin,./4.bin,./5.bin" --dymBatch 2
```

 ### Folder input scenario. Input is passed into the folder list, separated by commas.
 This scenario will be grouped according to file input and model input. Batch is obtained by comparing the model input size with the file input size.

```
python3 ais_infer.py --model ./resnet50_v1_bs1_fp32.om --input "./"

```

In the following example, the model input must be consistent with the number of incoming folders. For example, if Bert has three inputs, three folders must be imported.
```
python3 ais_infer.py --model ./save/model/BERT_Base_SQuAD_BatchSize_1.om  --input ./data/SQuAD1.1/input_ids,./data/SQuAD1.1/input_mask,./data/SQuAD1.1/segment_ids
```

 ### Dynamic grading scene. Includes three scenes: dynamic batch, dynamic width and height and dynamic dims. And need to input dymbatch, dymhw and dymdims respectively to specify the actual gear information.

+ Dynamic batch scene. The gears are 1, 2, 4 and 8,and setting gear is 2. This program will obtain the actual model input group batch and group a group of batch for referencing every two inputs.
```
python3 ais_infer.py --model ./resnet50_v1_dynamicbatchsize_fp32.om --input=./data/ --dymBatch 2

```

+ Dynamic HW width height scene. The gears are 224,224;448,448. Setting gear is 224,224. This program will get the actual model input group batch.
```
python3 ais_infer.py --model ./resnet50_v1_dynamichw_fp32.om --input=./data/ --dymHW 224,224

```

+ Dynamic dims scene. The gears are 1,3,224,224. This program will get the actual model input group batch.
```
python3 ais_infer.py --model resnet50_v1_dynamicshape_fp32.om --input=./data/ --dymShape actual_input_1:1,3,224,224 --outputSize 10000
```

### Dynamic shape scene. atc is set to [1~8,3,200~300,200~300]. Setting gears are 1,3,224,224. This program will get the actual model input group batch. Note that the output size of a dynamic shape is often 0, you need to set the memory size of the corresponding parameter through the outputsize parameter.
Note that the dynamic shape scene cannot obtain the shape of the tensor at present. One dimension is filled in by default. So please pay attention to the following when outputting numpy file.
```
python3 ais_infer.py --model resnet50_v1_dynamicshape_fp32.om --input=./data/ --dymShape actual_input_1:1,3,224,224 --outputSize 10000
```

### Profiler or dump scenarios
- acl_ json_path is the JSON file with the specified path, and the corresponding parameter information can be modified in this file
- profiler is a set of acl_json configuration solidified into the program, and the generated profiling data is saved in the profiler folder of the output path
- dump is a group of acl_json configuration solidified into the program, and the generated dump data is saved in the profiler folder of the output path
- acl_ json_path has a higher priority than profiler and dump. when set together,  with acl_ json_path shall prevail
- the output parameter must be used with the profiler parameter or dump parameter. It indicates the output path
- profiler and dump can be used separately, but cannot be enabled at the same time

```bash
python3 ais_infer.py --model ./resnet50_v1_bs1_fp32.om --acl_json_path ./acl.json
python3 ais_infer.py  --model /home/model/resnet50_v1.om --output ./ --dump
python3 ais_infer.py  --model /home/model/resnet50_v1.om --output ./ --profiler
```
### Result summary function
For the result output, this program adds summary JSON file prints parameter values to facilitate summary statistics.
The specific results are as follows:
NPU_compute_time: total referencing call time
H2D_latency: delay time from host to device during referencing
D2H_latency: delay time from device to host during referencing
throughput: throughput. Calculation formula：1000 * batchsize/npu_compute_time.mean


Print as follows:
summary:{'NPU_compute_time': {'min': 2.4385452270507812, 'max': 2.587556838989258, 'mean': 2.5239520602756076, 'median': 2.529621124267578, 'percentile(99%)': 2.585916519165039}, 'H2D_latency': {'min': 0.5118846893310547, 'max': 1.0373592376708984, 'mean': 0.6650818718804253, 'median': 0.6296634674072266, 'percentile(99%)': 1.0063838958740234}, 'D2H_latency': {'min': 0.027894973754882812, 'max': 0.05745887756347656, 'mean': 0.04508760240342882, 'median': 0.04744529724121094, 'percentile(99%)': 0.05671501159667969}, 'throughput': 396.2040387925606}

## Command Line Options

| Option   | Description                            |
| -------- | ------------------------------- |
| --model  | Offline model.            |
| --input  | Model input, either binary files or directories. If this option is not included, all-0s data is generated as the model input.                  |
| --output | Inference result output path. By default, a date + time subfolder will be created to save the output results. If output_dirname is specified, inference result will be save to the subfolder of output_dirname.                |
| --output_dirname | (Optional) Inference result output subfolder. Used with parameter output, it is invalid to use it alone. When this value is set, the output result is saved to output/output_ dirname folder.              |
| --outfmt | Inference output format. Default BIN. can be set to "NPY", "BIN" or "TXT" |
| --loop   | (Optional) Number of inferences. Must be in the range of \[1, 255]. Defaults to 1. When profiler is set to true, you are advised to set this option to 1. |
| --debug  | (Optional) Debug switch for printing the model description, either true or false. Defaults to false. |
| --device --device_id   | (Optional)Specify operating equipment. Value range is [0,255]. Default 0 |
| --dymBatch  | (Optional) Dynamic batch parameter， specifies the actual batch of the model input. <br>If ATC model conversion settings --input_shape="data:-1,600,600,3;img_info:-1,3" --dynamic_batch_size="1,2,4,8" , the dymBatch parameter can be set to --dymBatch 2.|
| --dymHW  | (Optional) Dynamic image size parameter， specifies the actual image size of the model input. <br>If ATC model conversion settings --input_shape="data:8,3,-1,-1;img_info:8,4,-1,-1"  --dynamic_image_size="300,500;600,800" , the dymBatch parameter can be set to --dymHW 300,500.|
| --dymDims| (Optional) Dynamic dimension parameter， specifies the actual shape of the model input. <br>If ATC model conversion settings --input_shape="data:1,-1;img_info:1,-1" --dynamic_dims="224,224;600,600" , the dymDims parameter can be set to --dymDims "data:1,600;img_info:1,600".|
| --dymShape| (Optional) Dynamic shape parameter， specifies the actual shape of the model input. <br>If ATC model conversion settings --input_shape_range="input1:\[8\~20,3,5,-1\];input2:\[5,3\~9,10,-1\]" , the dymShape parameter can be set to --dymShape "input1:8,3,5,10;input2:5,3,10,10". <br>This parameter must be used with --input and --outputSize. |
| --auto_set_dymshape_mode| (Optional)Automatically set shape mode, default false。<br>For the dynamic shape model, automatically set the shape parameters according to the information of the input file<br> --auto_set_dymshape_mode true"|
| --outputSize| (Optional)Specify the output size of the model. If there are several outputs, set several values. <br>In the dynamic shape scenario, the output size of the acquired model may be 0. The user needs to estimate an appropriate value according to the input shape to apply for memory.<br>Example： --outputSize "10000,10000,10000".|
| --batchsize | model batch size.            |
| --pure_data_type | (Optional)Pure inference data type。Default "zero", can be set to "zero" or "random"。<br>When set to zero, all pure reasoning data are 0; When set to random, each legend data is a random integer between [0, 255]      |
| --profiler | (Optional)profiler switch。either true or false. Defaults to false.<br>--Output parameter must be provided. The profiler data is in the profiler folder under the directory specified by the --output parameter. Cannot be true at the same time as --dump      |
| --dump | (Optional)dump switch。either true or false. Defaults to false.<br>--Output parameter must be provided. Dump data is in the dump folder under the directory specified by the --output parameter. Cannot be true at the same time as --profiler      |
| --acl_json_path | Acl json file. For profiling or dump scenarios.When this parameter is set, -dump and --profiler parameters are invalid. |
| --output_batchsize_axis | The batchsize axis of the output tensor，default 0. When saving the output result file, the cutting inference result is based on which axis. For example, if the batchsize is 2, it means that two input files are grouped to batch inference, and the batch dimension of the output result is on which axis. The default value is 0 axis, and 2 copies are cut according to 0 axis, but the output batch of some models is 1 axis, so this value should be set to 1. |
| --help| Help information.                  |
