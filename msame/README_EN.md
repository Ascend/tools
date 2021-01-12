EN|[中文](README.md)

# Model Inference Tool: msame

### Function

The msame tool takes the offline model (.om) and the .bin file required by the model as the inputs, and outputs the model output data. Inferring on the same input data for multiple times is supported.

The model must be an offline model converted with  ATC. The input .bin file must meet the input requirements of the model (multiple inputs are supported).

### Environment

The development and running environment has been installed on ascend AI reasoning equipment.  
Installation reference documents: https://support.huaweicloud.com/instg-cli-cann/atlascli_03_0001.html

### Acquisition

1. By downloading the package
   
   Download the script from the **tools** repository at https://gitee.com/ascend/tools to any directory on the server.
   
   For example, the path can be **$HOME/AscendProjects/tools**.

2. By running the **git** command
   
   Run the following command in the **$HOME/AscendProjects** directory to download code:
   
   **git clone https://gitee.com/ascend/tools.git**

### Instructions

#### a. Run the built tool.

**Environment requirements:**  
The development and running environment has been installed on shengteng AI reasoning equipment.  
Installation reference documents：https://support.huaweicloud.com/instg-cli-cann/atlascli_03_0001.html

Go to the **msame** directory.
```
cd $HOME/AscendProjects/tools/msame/
```

The msame tool is in the **out** directory. Go to the **out** directory.
```
cd out
```


Run the tool in the command line like this
```
./msame --model /home/HwHiAiUser/ljj/colorization.om --input /home/HwHiAiUser/ljj/colorization_input.bin --output /home/HwHiAiUser/ljj/MSAME/out/output1 --outfmt TXT --loop 2
```

If there are multiple inputs, separate them by commas (,). Note that no space is allowed on either side of the commas.   
For details about other parameters, run the **--help** command.

#### b. Build and run the source code.

**Environment requirements: The  operating development has been installed (both co-deployment and separate deployment are available).**   
Source code build is supported. If you need to modify the code, the code needs to be rebuilt.   

Set environment variables  
(The following example shows how to set environment variables. Replace /home/HwHiAiUser/Ascend/ascend-toolkit/latest/xxx-linux_gccx.x.x with the actual installation path of the ACLlib installation package in /home/HwHiAiUser/Ascend/ascend-toolkit/latest/xxx-linux_gccx.x.x form.)  
**export DDK_PATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest**  
**export NPU_HOST_LIB=/home/HwHiAiUser/Ascend/ascend-toolkit/latest/acllib/lib64/stub** 

Run the following command to go to the **msame** directory:
```
cd $HOME/AscendProjects/tools/msame/
```
Execute the build script.
```
./build.sh g++ $HOME/AscendProjects/tools/msame/out
```
The first parameter specifies the compiler, which is determined by the operating environment.   
The second parameter specifies the directory for msame. To specify a relative directory, ensure that it is relative to the **out** directory.

## Precautions

The msame running user must have the permission to create the directory and execute msame in the directory. Check the permissions in advance.   
Currently, dynamic batch is not supported.

## Parameter Description

| Parameter| Description
|---------- |----------
| --model   | Offline model
| --input   | Input of the model. If no argument is passed, all 0 data is automatically generated.
| --output  | Path of the inference output data
| --outfmt  | Format of the output data, either .txt or .bin
| --loop    | Inference loop count (optional). The value ranges from 1 to 100. Defaults to **1**. When **profiler** is set to **True**, the recommended value is **1**.
| --debug   | Debug enable (optional). The value can be **True** or **False**. Defaults to **False**.
| --profiler| Profiler enable (optional). Defaults to **False**.  
| --dump| dump enable (optional). Defaults to **False**.
| --device  | Device for inference (optional). The value ranges from 0 to 255. Defaults to **0**.
| --help    | Help information about the tool

