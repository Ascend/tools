EN|[中文](README.md)

# Model Inference Tool: msame

### Function

The msame tool takes the offline model (.om) and the .bin file required by the model as the inputs, and outputs the model output data. Inferring on the same input data for multiple times is supported.

The model must be an offline model converted with the C7x version of ATC. The input .bin file must meet the input requirements of the model (multiple inputs are supported).

### Environment

Install the C7x environments by referring to *Driver and Development Environment Setup Guide*.

### Acquisition

1. By downloading the package
   
   Download the script from the **tools** repository at https://gitee.com/ascend/tools to any directory on the server.
   
   For example, the path can be **$HOME/AscendProjects/tools**.

2. By running the **git** command
   
   Run the following command in the **$HOME/AscendProjects** directory to download code:
   
   **git clone https://gitee.com/ascend/tools.git**

### Instructions

#### a. Run the built tool.

**Environment requirements: The architecture is Arm and the C7x operating environment has been installed. If the preceding requirements are not meet, use method b to build the source code.**

Go to the **msame** directory.
```
cd $HOME/AscendProjects/tools/msame/
```

Go to the **out** directory.
```
cd out
```

The msame tool is in the **out** directory.


Run the tool in the command line.
```
./msame --model /home/HwHiAiUser/ljj/colorization.om --input /home/HwHiAiUser/ljj/colorization_input.bin --output /home/HwHiAiUser/ljj/MSAME/out/output1 --outfmt TXT --loop 2
```

If there are multiple inputs, separate them by commas (,). Note that no space is allowed on either side of the commas.   
For details about other parameters, run the **--help** command.

#### b. Build and run the source code.

**Environment requirements: The C7x operating development has been installed (both co-deployment and separate deployment are available).**   
Source code build is supported. If you need to modify the code, the code needs to be rebuilt. Run the following command to go to the **msame** directory:
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
Currently, dumping and dynamic batch are not supported.

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
| --device  | Device for inference (optional). The value ranges from 0 to 255. Defaults to **0**.
| --help    | Help information about the tool

