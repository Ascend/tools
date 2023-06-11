# AIS-Bench Inference Tool User Guide

## Introduction
This document describes the AIS-Bench inference tool, which is used to run an inference program on a specified inference model and test the model's performance (including the throughput and latency).

## Tool Installation

### Environment and Dependency

- Set up the development or operating environment on an Ascend device, that is, install the Toolkit or NNRT software package. For details, see the *[CANN Development Tool User Guide](https://www.hiascend.com/document/detail/en/canncommercial/60RC1/envdeployment/instg/instg_000002.html)*.
- Install Python 3.

### Tool Installation Modes

Installation of the AIS-Bench inference tool requires the installation of the **aclruntime package** and **AIS-Bench inference program package**. The installation modes include .whl package installation, installation through one-click compilation, and installation through source code compilation.

**Description**:

- The network in the installation environment must be properly connected.  
- The CentOS platform uses the GCC 4.8 by default, and this tool may fail to be installed. You are advised to update the GCC before installing this tool.  
- The CANN version is required during installation of this tool. You can specify the CANN version path by setting the **CANN_PATH** environment variable, for example, **export CANN_PATH=/xxx/nnrt/latest/**. If the environment variable is not set, the tool attempts to obtain the CANN version from **/usr/local/Ascend/nnrt/latest/** and **/usr/local/Ascend/ascend-toolkit/latest** by default.

#### .whl Package Download and Installation

1. Download the following .whl packages of the aclruntime and AIS_Bench inference program:

   Version 0.0.2 (Select an appropriate version for the aclruntime package based on the current environment.)

   - [aclruntime-0.0.2-cp37-cp37m-linux_x86_64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp37-cp37m-linux_x86_64.whl)
   - [aclruntime-0.0.2-cp37-cp37m-linux_aarch64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp37-cp37m-linux_aarch64.whl)
   - [aclruntime-0.0.2-cp38-cp38-linux_x86_64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp38-cp38-linux_x86_64.whl)
   - [aclruntime-0.0.2-cp38-cp38-linux_aarch64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp38-cp38-linux_aarch64.whl)
   - [aclruntime-0.0.2-cp39-cp39-linux_x86_64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp39-cp39-linux_x86_64.whl)
   - [aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl)
   - [ais_bench-0.0.2-py3-none-any.whl](https://aisbench.obs.myhuaweicloud.com/packet/ais_bench_infer/0.0.2/ais_bench-0.0.2-py3-none-any.whl)

2. Run the following installation commands:

   ```bash
   # Install aclruntime.
   pip3 install ./aclruntime-{version}-{python_version}-linux_{arch}.whl
   # Install the AIS_Bench inference program.
   pip3 install ./ais_bench-{version}-py3-none-any.whl
   ```

   *{version}* indicates the software version, *{python_version}* indicates the Python version, and *{arch}* indicates the CPU architecture.  

   Note: If overwrite installation is adopted, add the **--force-reinstall** option to enable forcible installation, for example:

   ```bash
   pip3 install ./aclruntime-{version}-{python_version}-linux_{arch}.whl --force-reinstall
   pip3 install ./ais_bench-{version}-py3-none-any.whl --force-reinstall
   ```

   If the following information is displayed, the installation is successful:

   ```bash
   # aclruntime is successfully installed.
   Successfully installed aclruntime-{version}
   # The AIS_Bench inference program is successfully installed.
   Successfully installed ais_bench-{version}
   ```

   

#### Installation Through One-Click Compilation

1. **Install the aclruntime package.**

   Run the following command in the installation environment to install the aclruntime package:


   ```bash
   pip3 install -v 'git+https://github.com/Ascend/tools.git#egg=aclruntime&subdirectory=ais-bench_workload/tool/ais_bench/backend'
   ```

   Note: If overwrite installation is adopted, add the **--force-reinstall** option to enable forcible installation, for example:

   ```bash
   pip3 install -v --force-reinstall 'git+https://github.com/Ascend/tools.git#egg=aclruntime&subdirectory=ais-bench_workload/tool/ais_bench/backend'
   ```

   If the following information is displayed, the installation is successful:

   ```bash
   Successfully installed aclruntime-{version}
   ```

2. **Install the AIS_Bench inference program package.**

   Run the following command in the installation environment to install the AIS_Bench inference program package:

   ```bash
   pip3 install -v 'git+https://github.com/Ascend/tools.git#egg=ais_bench&subdirectory=ais-bench_workload/tool/ais_bench'
   ```

   Note: If overwrite installation is adopted, add the **--force-reinstall** option to enable forcible installation, for example:

   ```bash
   pip3 install -v --force-reinstall 'git+https://github.com/Ascend/tools.git#egg=ais_bench&subdirectory=ais-bench_workload/tool/ais_bench'
   ```
   
   If the following information is displayed, the installation is successful:
   
   ```bash
   Successfully installed ais_bench-{version}
   ```



#### Installation Through Source Code Compilation
1. Clone or download tool package **tools-xxx.zip** from the open-source code repository at [Gitee](https://github.com/Ascend/tools).

2. Upload the tool package to the installation environment and decompress it.

3. Go to the **ais-bench_workload/tool/ais_bench** directory from the directory where the tool is decompressed and run the following commands to perform compilation:

   ```bash
   # Go to the directory where the tool is decompressed.
   cd ${HOME}/ais-bench_workload/tool/ais_bench/
   # Build the aclruntime package.
   pip3 wheel ./backend/ -v
   # Build the AIS_Bench inference program package.
   pip3 wheel ./ -v
   ```

   *${HOME}* indicates the directory where the AIS_Bench inference tool package is located.

   If the following information is displayed, the compilation is successful:

   ```bash
   # The aclruntime package is successfully compiled.
   Successfully built aclruntime
   # The AIS_Bench inference program package is successfully compiled.
   Successfully built ais-bench
   ```

4. Run the following installation commands:

   ```bash
   # Install aclruntime.
   pip3 install ./aclruntime-{version}-{python_version}-linux_{arch}.whl
   # Install the AIS_Bench inference program.
   pip3 install ./ais_bench-{version}-py3-none-any.whl
   ```

   *{version}* indicates the software version, *{python_version}* indicates the Python version, and *{arch}* indicates the CPU architecture.

   Note: If overwrite installation is adopted, add the **--force-reinstall** option to enable forcible installation, for example:

   ```bash
   pip3 install ./aclruntime-{version}-{python_version}-linux_{arch}.whl --force-reinstall
   pip3 install ./ais_bench-{version}-py3-none-any.whl --force-reinstall
   ```
   
   If the following information is displayed, the installation is successful:

   ```bash
   # aclruntime is successfully installed.
   Successfully installed aclruntime-{version}
   # The AIS_Bench inference program is successfully installed.
   Successfully installed ais_bench-{version}
   ```
   
   

### Preparations for Tool Running
After the AIS_Bench inference tool is installed, perform the following operations to ensure that it can run properly:  
1. Run the following command to install the dependency in the **requirements.txt** file:

   ```bash
   cd ${HOME}/ais-bench_workload/tool/ais_bench/
   pip3 install -r ./requirements.txt
   ```

   *${HOME}* indicates the directory where the AIS_Bench inference tool package is located.

   Note: If the dependency has been installed, skip this step.
2. Run the following command to set the environment variable of the CANN package:

   ```bash
   source ${INSTALL_PATH}/Ascend/ascend-toolkit/set_env.sh
   ```

   *${INSTALL_PATH}* indicates the CANN package installation path.

   Note: If the environment variable has been set, skip this step.

After the preceding settings are complete, you can use the AIS_Bench inference tool to test the performance of an inference model.

## Tool Usage

### Tool Introduction

 #### How to Use

The AIS_Bench inference tool can start a model test using the **ais_bench** executable file. The startup mode is as follows:

```bash
python3 -m ais_bench --model *.om
```
(*) indicates the name of the OM offline model file.

#### Command-Line Options

You can configure different options for the AIS_Bench inference tool to cope with different test scenarios and implement other auxiliary functions.

The options are classified into **basic options** and **advanced options** by function type.

- **Basic options**: include the input and output files and formats, debug switch, inference times, warm-up times, specified running devices, and help information.
- **Advanced options**: include AIS_Bench inference test options in dynamic profile and dynamic shape scenarios, and profiler or dump data obtaining options.

**Note**: Each of the following options and its value can be separated by a space or an equal sign (=), for example, **--debug 1** or **--debug=0**.

##### Basic Options

| Option                | Description                                                          | Mandatory (Yes/No) |
| --------------------- | ------------------------------------------------------------ | -------- |
| --model               | OM offline model file to be used for inference.                               | Yes       |
| --input               | Model input. You can specify the directory where the input file is located or directly specify the input file. The input file format can be NPY or BIN. Multiple files or directories are allowed. Separate them with commas (,). Prepare the actual input files based on model requirements. If this option is not set, the tool automatically constructs the input data, whose type is determined by **--pure_data_type**.  | No       |
| --pure_data_type      | Pure inference data type. The value can be **zero** or **random**. The default value is **zero**. If the model input file is not configured, the tool automatically constructs the input data. If this option is set to **zero**, pure inference data with all 0s is constructed. If this option is set to **random**, a group of random data is generated for each input.   | No       |
| --output              | Directory for saving the inference results. After this option is set, subdirectories in the format of "date+time" are created to save the outputs. If the **output_dirname** option is set, the outputs are saved in the subdirectory specified by **output_dirname**. If the output directory is not set, the output results are only printed but not saved.  | No       |
| --output_dirname      | Subdirectory for saving the inference results. If this option is set, the outputs are saved in the **output/output_dirname** directory. This option is used together with **--output**, and is invalid when being used independently, for example, **--output */output* --output_dirname *output_dirname***. | No       |
| --outfmt              | Output data format. The value can be "NPY", "BIN", or "TXT". The default value is "BIN". This option is used together with **--output**, and is invalid when being used independently, for example, **--output */output* --outfmt NPY**.  | No       |
| --debug               | Debug switch. The model description and other detailed execution information can be printed. The value can be **1** or **true** (enabled), or **0** or **false** (disabled). By default, this option is disabled. | No       |
| --display_all_summary | Whether to display all summary information, including h2d and d2h information. The value can be **1** or **true** (enabled), or **0** or **false** (disabled). By default, this option is disabled. | No       |
| --loop                | Number of inference times. The value must be a positive integer greater than 0, and the default value is **1**. If **profiler** is set to **true**, you are advised to set this option to **1**. | No       |
| --warmup_count        | Number of inference warm-up times. The value is an integer greater than or equal to 0, and the default value is **1**. The value **0** indicates that warm-up is not performed. | No       |
| --device              | Specified running device. Set this option based on the actual device ID. The default value is **0**. In multi-device scenarios, you can specify multiple devices for the inference test, for example, **--device 0,1,2,3**.  | No       |
| --help                | Help information about tool usage.                                         | No       |

##### Advanced Options

| Option                    | Description                                                         | Mandatory (Yes/No) |
| ------------------------ | ------------------------------------------------------------ | -------- |
| --dymBatch               | Dynamic batch option, which specifies the actual batch of the model input. <br>For example, if **--input_shape="data:-1,600,600,3;img_info:-1,3" --dynamic_batch_size="1,2,4,8"** is set during ATC-based model conversion, **dymBatch** can be set to **--dymBatch 2**.| No       |
| --dymHW                  | Dynamic image size option, which specifies the actual H (height) and W (width) of the model input. <br>For example, if **--input_shape="data:8,3,-1,-1;img_info:8,4,-1,-1" --dynamic_image_size="300,500;600,800"** is set during ATC-based model conversion, **dymHW** can be set to **--dymHW 300,500**.  | No       |
| --dymDims                | Dynamic dimension option, which specifies the actual shape of the model input.<br>For example, if **--input_shape="data:1,-1;img_info:1,-1" --dynamic_dims="224,224;600,600"** is set during ATC-based model conversion, **dymDims** can be set to **--dymDims "data:1,600;img_info:1,600"**.   | No       |
| --dymShape               | Dynamic shape option, which specifies the actual shape of the model input. <br>For example, if **--input_shape_range="input1:\[8\~20,3,5,-1\];input2:\[5,3\~9,10,-1\]"** is set during ATC-based model conversion, **dymShape** can be set to **--dymShape "input1:8,3,5,10;input2:5,3,10,10"**.<br>In dynamic shape scenarios, the obtained model output size is usually 0 (that is, the memory occupied by the output data is unknown). You are advised to set the **--outputSize** option. <br/>Example: --dymShape "input1:8,3,5,10;input2:5,3,10,10" --outputSize "10000,10000" | No       |
| --dymShape_range         | Threshold range of dynamic shapes. If this option is set, inference is performed based on all shape lists in the option in sequence to obtain the summary inference information.<br/>The configuration format is **name1:1,3,200\~224,224-230;name2:1,300**. **name** indicates the model input name, **\~** indicates the range, and **-** indicates the values of a position. <br/>You can also specify the threshold range configuration file *.info of dynamic shapes. This file records the threshold range of dynamic shapes, in which multiple shape groups can be set, and one shape group occupies one line.  | No       |
| --outputSize             | Memory size occupied by the output data of a model. If there are multiple outputs, set a value for each output and separate the values with commas (,). <br>In dynamic shape scenarios, the obtained model output size is usually 0 (that is, the memory occupied by the output data is unknown). You need to estimate a proper size based on the input shape to configure the memory occupied by the output data. <br>Example: --dymShape "input1:8,3,5,10;input2:5,3,10,10" --outputSize "10000,10000" | No      |
| --auto_set_dymdims_mode  | Automatic setting of the dynamic dims mode. The value can be **1** or **true** (enabled), or **0** or **false** (disabled). By default, this option is disabled. <br/>For dynamic-profile dims models, the **shape** parameter is automatically set based on the input file information. Note that the input data can only be an NPY file because the BIN file cannot read the shape information. <br/>This option is used together with **--input**, and is invalid when being used independently. <br/>Example: --input 1.npy --auto_set_dymdims_mode 1| No       |
| --auto_set_dymshape_mode | Automatic setting of the dynamic shape mode. The value can be **1** or **true** (enabled), or **0** or **false** (disabled). By default, this option is disabled. <br>For dynamic-shape models, the **shape** parameter is automatically set based on the input file information. Note that the input data can only be an NPY file because the BIN file cannot read the shape information. <br>This option is used together with **--input**, and is invalid when being used independently. <br/>Example: --input 1.npy --auto_set_dymshape_mode 1 | No       |
| --profiler               | Profiler switch. The value can be **1** or **true** (enabled), or **0** or **false** (disabled). By default, this option is disabled. <br>The profiler data is stored in the **profiler** folder under the directory specified by the **--output** option. This option is used together with **--output**, and is invalid when being used independently. It cannot be enabled together with **--dump**. <br/>If **GE_PROFILING_TO_STD_OUT** is set to **1** in the environment, the **acl.json** configuration file is used by the **--profiler** option to collect profile data. | No       |
| --dump                   | Dump switch. The value can be **1** or **true** (enabled), or **0** or **false** (disabled). By default, this option is disabled. <br>The dump data is stored in the **dump** folder under the directory specified by the **--output** option. This option is used together with **--output**, and is invalid when being used independently. It cannot be enabled together with **--profiler**.  | No       |
| --acl_json_path          | **acl.json** configuration file path. A valid JSON file must be specified. You can configure profiler or dump in this file. When this option is set, the **--dump** and **--profiler** options are invalid.  | No      |
| --batchsize              | Model batch size. If this option is not specified, the batch size value is automatically deduced. The batch size passed by this option is used only for calculating the result throughput. <br>Automatic deduction logic: try to obtain the highest dimension of the first option as the batch size of a model. In dynamic batch scenarios, update the value to the dynamic batch value. In dynamic dims and dynamic shape scenarios, update the value to the highest dimension of the first set option. If the automatic deduction logic does not meet the requirements, pass the correct batch size value to calculate the correct throughput.  | No       |
| --output_batchsize_axis  | Batch size axis of the output tensor. This option specifies the axis based on which the inference result is split when being saved as files, and the batch dimension of the result is on this axis. By default, the inference result is split based on axis 0. However, the output batch of some models is on axis 1. In this case, you need to set this option to **1**.  | No       |



### Application Scenarios

**Note**: The AIS_Bench inference tool combines input files of a model based on the actual input size. It automatically supplements data if the input files are insufficient, and split data into batches if there are too many input files. After the inference test is complete, the tool splits the output files based on the batch size of the model.

 #### Pure Inference Scenarios

By default, data with all 0s is constructed and fed to the model for inference.

The following is an example command:

```bash
python3 -m ais_bench --model /home/model/resnet50_v1.om --output ./ --outfmt BIN --loop 5
```

#### Debug Mode
Enable the debug mode.

The following is an example command:

```bash
python3 -m ais_bench --model /home/model/resnet50_v1.om --output ./ --debug 1
```

After the debug mode is enabled, more information is printed, including:  
- Input and output parameters of the model

  ```bash
  input:
    #0    input_ids  (1, 384)  int32  1536  1536
    #1    input_mask  (1, 384)  int32  1536  1536
    #2    segment_ids  (1, 384)  int32  1536  1536
  output:
    #0    logits:0  (1, 384, 2)  float32  3072  3072
  ```

- Detailed inference duration information

  ```bash
  [DEBUG] model aclExec cost : 2.336000
  ```
- Detailed operations such as model input and output

 #### File Input Scenarios

Use the **--input** option to specify the model input files. Separate multiple files with commas (,).

The following is an example command:

```bash
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --input "./1.bin,./2.bin,./3.bin,./4.bin,./5.bin"
```

 #### Folder Input Scenarios

Use the **--input** option to specify the directories where the model input files are located. Separate multiple directories with commas (,).

```bash
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --input "./"
```

The number of input folders must be the same as the actual number of model inputs.

For example, if the BERT model has three inputs, they must be transferred to three folders. Each input corresponds to a folder and the sequence must be correct. You can view information about the model input options by enabling the debug mode. The three inputs of the BERT model are **input_ids**, **input_mask**, and **segment_ids**, and are transferred to three folders in sequence.

- The first folder **./data/SQuAD1.1/input_ids** corresponds to the first model input **input_ids**.
- The second folder **./data/SQuAD1.1/input_mask** corresponds to the second model input **input_mask**.
- The third folder **./data/SQuAD1.1/segment_ids** corresponds to the third model input **segment_ids**.

```bash
python3 -m ais_bench --model ./save/model/BERT_Base_SQuAD_BatchSize_1.om --input ./data/SQuAD1.1/input_ids,./data/SQuAD1.1/input_mask,./data/SQuAD1.1/segment_ids
```



#### Multi-Device Scenarios

In multi-device scenarios, you can specify multiple devices for the inference test.

The following is an example command:

```bash
python3 -m ais_bench --model ./pth_resnet50_bs1.om --input ./data/ --device 1,2
```

The output displays the inference test result of each device in sequence. The following is an example:

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

The throughput, test start time (**start_time**), test end time (**end_time**), and summary throughput in the inference test of each device are displayed at the bottom. For details about other fields, see the "Outputs" section in this document.

 #### Dynamic Profile Scenarios

There are three sub-scenarios, dynamic batch, dynamic H & W, and dynamic dims, in which **dymBatch**, **dymHW**, and **dymDims** need to be transferred to specify the actual profiles.

##### Dynamic Batch

Take profiles "1 2 4 8" as an example and set the profile to "2".

```bash
python3 -m ais_bench --model ./resnet50_v1_dynamicbatchsize_fp32.om --input=./data/ --dymBatch 2
```

##### Dynamic H & W

Take profiles "224,224;448,448" as an example and set the profile to "224,224".

```bash
python3 -m ais_bench --model ./resnet50_v1_dynamichw_fp32.om --input=./data/ --dymHW 224,224
```

##### Dynamic Dims

Take profiles "1,3,224,224" as an example.

```bash
python3 -m ais_bench --model resnet50_v1_dynamicshape_fp32.om --input=./data/ --dymDims actual_input_1:1,3,224,224
```

##### Automatic Setting of the Dims Mode (Dynamic Dims Models)

Shapes of the input data of a dynamic dims model may not be fixed. For example, the shape of an input file is "1,3,224,224", and that of another input file is "1,3,300,300". If the two files are used for inference at the same time, you need to set the dynamic shape option twice, but this operation is not supported currently. To cope with this scenario, **auto_set_dymdims_mode** is added, which automatically sets the shape option based on shape information of the input files.

```bash
python3 -m ais_bench --model resnet50_v1_dynamicshape_fp32.om --input=./data/ --auto_set_dymdims_mode 1
```



#### Dynamic Shape Scenarios

##### Dynamic Shape

Assume that ATC sets [1\~8,3,200\~300,200\~300] and profile "1,3,224,224".

Generally, the output size of dynamic shapes is 0. You are advised to set the output memory size by using the **outputSize** option.

```bash
python3 -m ais_bench --model resnet50_v1_dynamicshape_fp32.om --dymShape actual_input_1:1,3,224,224 --outputSize 10000
```

##### Automatic Setting of the Shape Mode (Dynamic Shape Models)

Shapes of the input data of a dynamic shape model may not be fixed. For example, the shape of an input file is "1,3,224,224", and that of another input file is "1,3,300,300". If the two files are used for inference at the same time, you need to set the dynamic shape option twice, but this operation is not supported currently. To cope with this scenario, **auto_set_dymshape_mode** is added, which automatically sets the shape option based on shape information of the input files.

```bash
python3 -m ais_bench --model ./pth_resnet50_dymshape.om  --outputSize 100000 --auto_set_dymshape_mode 1  --input ./dymdata
```

**Note that the input files in this scenario must be in NPY format. If the input files are in BIN format, the actual shape information cannot be obtained.**

##### Range Test Mode of Dynamic Shape Models


Input the range of dynamic shapes. Perform inference for shapes within the range to obtain their performance indicators.

For example, to perform separate inference on "1,3,224,224", "1,3,224,225", and "1,3,224,226", run the following command:

```bash
python3 -m ais_bench --model ./pth_resnet50_dymshape.om  --outputSize 100000 --dymShape_range actual_input_1:1,3,224,224~226
```



#### Profiler or Dump Scenarios

The functions can be implemented by the **--acl_json_path**, **--profiler**, and **--dump** options.
+ **acl_json_path** specifies the **acl.json** configuration file, in which you can set the corresponding profiler or dump parameter. The sample code is as follows:

  + Profiler

    ```bash
    {
    "profiler": {
                  "switch": "on",
                  "output": "./result/profiler"
                }
    }
    ```

    For details about more performance configurations, see "Profiling > Advanced Features > Profile Data Collection with the acl.json Configuration file" in the *[CANN Development Tool Guide](https://www.hiascend.com/document/detail/en/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)*.

  + Dump

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

    For details about more dump configurations, see "Model Accuracy Analyzer > Data Preparation > Inference Scenarios > Preparing Dump Data of an Offline Model" in the *[CANN Development Tool Guide](https://www.hiascend.com/document/detail/en/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)*.

  Profile data collected in this mode needs to be parsed and exported as visualized timeline and summary files. For details, see "Profiling > Advanced Features > Data Parsing and Export" in the *[CANN Development Tool Guide](https://www.hiascend.com/document/detail/en/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)*.

+ Profiler is a group of profile data collection configurations fixed in the program. The generated profile data is saved in the **profiler** folder under the directory specified by the **--output** option.

  It calls the **msprof_run_profiling** function in **ais_bench/infer/__main__.py** to start the msprof command to collect profile data. To modify the profile data collection parameters, modify **msprof_cmd** in the **msprof_run_profiling** function based on the actual requirements. The following is an example:

  ```bash
  msprof_cmd="{} --output={}/profiler --application=\"{}\" --model-execution=on --sys-hardware-mem=on --sys-cpu-profiling=off --sys-profiling=off --sys-pid-profiling=off --dvpp-profiling=on --runtime-api=on --task-time=on --aicpu=on".format(
          msprof_bin, args.output, cmd)
  ```

  Before collecting profile data in this mode, check whether the msprof command exists:

  - If the command exists, run it to collect profile data and parse and export the result data as visualized timeline and summary files.
  - If the command does not exist, call the **acl.json** configuration file to collect profile data.   If the collected profile data file is not automatically parsed, you need to parse and export it as visualized timeline and summary files. For details, see "Profiling > Advanced Features > Data Parsing and Export" in the *[CANN Development Tool Guide](https://www.hiascend.com/document/detail/en/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)*.
  - If **GE_PROFILING_TO_STD_OUT** is set to **1** in the environment, the **acl.json** configuration file is used by the **--profiler** option to collect profile data. If the collected profile data file is not automatically parsed, you need to parse it according to [Parsing the Profiling File](https://github.com/Ascend/tools/blob/master/ada/doc/ada_pa.md).

  For details about more profile data collection parameters, see "Profiling > Advanced Features > Profile Data Collection with the msprof Command Line" in the *[CANN Development Tool Guide](https://www.hiascend.com/document/detail/en/canncommercial/60RC1/devtools/auxiliarydevtool/auxiliarydevtool_0002.html)*.

+ **acl_json_path** has a higher priority than profiler or dump. If both of them are set, **acl_json_path** takes effect.

+ For profiler or dump, the **output** option must be added to specify the output path.

+ Profiler and dump can be used separately, but they cannot be enabled at the same time.

The following are example commands:

```bash
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --acl_json_path ./acl.json
python3 -m ais_bench  --model /home/model/resnet50_v1.om --output ./ --dump 1
python3 -m ais_bench  --model /home/model/resnet50_v1.om --output ./ --profiler 1
```

 #### Saving Output Result Files

After AIS_Bench execution, the output result data is not saved by default. After related parameters are configured, the following result data can be generated:

| File/Directory                                | Description                                                         |
| ---------------------------------------- | ------------------------------------------------------------ |
| {file_name}.bin, {file_name}.npy, or {file_name}.txt  | Output result file of model inference. <br/>The file name format is "name_output sequence number.suffix". If inputs are not specified (pure inference), the file name is fixed to **pure_infer_data**. If inputs are specified, the file name is the first name of the first input. The output sequence number starts from 0 and is sorted in the output sequence. The file name suffix is controlled by **--outfmt**. <br/>By default, subdirectories named in the format of "date+time" are created in the directory specified by **--output** to save the result files. If **--output_dirname** is specified, the result files are directly saved in the directory specified by **--output_dirname**. <br/>If **--output_dirname** is specified and the inference tool is executed for multiple times, the earlier result file will be overwritten by the latest one due to the same name.  |
| xx_summary.json                          | Model performance result data generated by the tool. By default, *xx* is named in the format of "date+time". If **--output_dirname** is specified, *xx* is named after the directory name specified by **--output_dirname**. <br/>If **--output_dirname** is specified and the inference tool is executed for multiple times, the earlier result file will be overwritten by the latest one due to the same name. |
| dump                                     | Dump data file directory. When using **--dump** to enable dump, create a **dump** folder in the directory specified by **--output** to save dump data files. |
| profiler                                 | Directory for saving profile data files collected by profiler. When using **--profiler** to enable profile data collection, create a **profiler** folder in the directory specified by **--output** to save profile data files.  |

- Set only the **--output** option. The example command and result are as follows:

  ```bash
  python3 -m ais_bench --model ./pth_resnet50_bs1.om --output ./result
  ```

  ```bash
  result
  |-- 2022_12_17-07_37_18
  │   `-- pure_infer_data_0.bin
  `-- 2022_12_17-07_37_18_summary.json
  ```

- Set both the **--input** and **--output** options. The example command and result are as follows:

  ```bash
  # The content of the **input** folder is as follows:
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

- Set the **--output_dirname** option. The example command and result are as follows:

  ```bash
  python3 -m ais_bench --model ./pth_resnet50_bs1.om --output ./result --output_dirname subdir
  ```

  ```bash
  result
  |-- subdir
  │   `-- pure_infer_data_0.bin
  `-- subdir_summary.json
  ```

- Set the **--dump** option. The example command and result are as follows:

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
  
- Set the **--profiler** option. The example command and result are as follows:

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



### Outputs

After the AIS_Bench inference tool is executed, the following information is displayed:

- When **display_all_summary** is **False**, the following information is displayed:

  ```bash
  [INFO] -----------------Performance Summary------------------
  [INFO] NPU_compute_time (ms): min = 0.6610000133514404, max = 0.6610000133514404, mean = 0.6610000133514404, median = 0.6610000133514404, percentile(99%) = 0.6610000133514404
  [INFO] throughput 1000*batchsize.mean(1)/NPU_compute_time.mean(0.6610000133514404): 1512.8592735267011
  [INFO] ------------------------------------------------------
  ```

- When **display_all_summary** is **True**, the following information is displayed:

  ```bash
  [INFO] -----------------Performance Summary------------------
  [INFO] H2D_latency (ms): min = 0.05700000002980232, max = 0.05700000002980232, mean = 0.05700000002980232, median = 0.05700000002980232, percentile(99%) = 0.05700000002980232
  [INFO] NPU_compute_time (ms): min = 0.6650000214576721, max = 0.6650000214576721, mean = 0.6650000214576721, median = 0.6650000214576721, percentile(99%) = 0.6650000214576721
  [INFO] D2H_latency (ms): min = 0.014999999664723873, max = 0.014999999664723873, mean = 0.014999999664723873, median = 0.014999999664723873, percentile(99%) = 0.014999999664723873
  [INFO] throughput 1000*batchsize.mean(1)/NPU_compute_time.mean(0.6650000214576721): 1503.759349974173
  ```

You can view the model execution duration and throughput in the output result. A smaller duration and a higher throughput indicate higher model performance.

**Field Description**

| Field                  | Description                                                         |
| --------------------- | ------------------------------------------------------------ |
| H2D_latency (ms)      | Time consumed by host-to-device memory copying, in ms.                      |
| min                   | Minimum inference execution time.                                          |
| max                   | Minimum inference execution time.                                          |
| mean                  | Mean value of the inference execution time.                                          |
| median                | Median of the inference execution time.                                        |
| percentile(99%)       | Percentile in the inference execution time.                                   |
| NPU_compute_time (ms) | NPU inference computation time, in ms.                                 |
| D2H_latency (ms)      | Time consumed by device-to-host memory copying, in ms.                     |
| throughput            | Throughput. Throughput calculation formula: 1000 x batchsize/npu_compute_time.mean |
| batchsize             | Batch size. This tool may not accurately identify the batch size of the current sample. You are advised to set the batch size using **--batchsize**. |

## Extended Functions

### Interface Openness

Open the inference Python interfaces of the AIS_Bench inference tool.

For details about the code sample, see [https://github.com/Ascend/tools/blob/master/ais-bench_workload/tool/ais_bench/test/interface_sample.py](https://github.com/Ascend/tools/blob/master/ais-bench_workload/tool/ais_bench/test/interface_sample.py).

You can use the following sample code to perform inference with the AIS_Bench inference tool:

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

Dynamic shape inference:

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



### File Saving upon Inference Exceptions

When an inference exception occurs, the input and output files of the operators that fail to be executed are written to the **current directory**. In addition, the current operator execution information is printed for fault locating and analysis. The following is an example:

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
To convert an abnormal BIN file to an NPY file, use the conversion script **[convert_exception_cb_bin_to_npy.py](https://github.com/Ascend/tools/tree/master/ais-bench_workload/tool/ais_bench/test/convert_exception_cb_bin_to_npy.py)**.  
Usage: **python3 convert_exception_cb_bin_to_npy.py --input {bin_file_path}**  
 You can enter a BIN file or folder.


## FAQs
[FAQs](FAQ.md) 
