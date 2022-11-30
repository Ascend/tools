# 一键式全流程精度比对（推理）

### 功能介绍

本文介绍一键式全流程精度比对（推理）工具，该工具适用于TensorFlow和ONNX模型，用户只需要输入原始模型，对应的离线模型和输入，就能出整网比对的结果，离线模型必须是通过ATC工具转换的om模型，输入bin文件需要符合模型的输入要求（支持模型多输入）。
该工具使用约束场景说明，参考链接：https://support.huaweicloud.com/tg-cannApplicationDev330/atlasaccuracy_16_0011.html

### 环境准备

1. 已安装开发运行环境的昇腾AI推理设备

2. 安装python3.7.5环境

3. 通过pip3.7.5安装环境依赖onnxruntime、onnx、numpy、skl2onnx、pexpect、gnureadline

   pip安装依赖命令示例：

   ```
   pip3.7.5 install onnxruntime
   ```
4. 安装TensorFlow1.15.0的环境

   安装参考文档：https://bbs.huaweicloud.com/blogs/181055
- 注：若pip安装依赖失败，建议执行命令pip3 install --upgrade pip 进行升级，避免因pip版本过低导致安装失败。
### 获取

- 下载压缩包方式获取。

   将 https://github.com/Ascend/tools 仓中的脚本下载至服务器的任意目录。

   例如存放路径为：$HOME/AscendProjects/tools。

- 命令行使用git命令方式获取。

   在命令行中：$HOME/AscendProjects目录下执行以下命令下载代码。

   **git clone https://github.com/Ascend/tools.git**

### 使用方法

1. 进入msquickcmp目录


```
cd $HOME/AscendProjects/tools/msquickcmp/
```

2. 设置环境变量
    (如下为设置环境变量的示例，请将/home/HwHiAiUser/Ascend/ascend-toolkit/latest替换为Ascend 的ACLlib安装包的实际安装路径。)

```
export install_path=/home/HwHiAiUser/Ascend/ascend-toolkit/latest
export DDK_PATH=${install_path}
export NPU_HOST_LIB=${install_path}/runtime/lib64/stub
```

3. 配置ATC工具环境变量

  （如下环境变量中${install_path}以软件包使用默认安装路径为例进行说明）

  ```
  export PATH=/usr/local/python3.7.5/bin:${install_path}/compiler/ccec_compiler/bin:${install_path}/compiler/bin:$PATH
  export PYTHONPATH=${install_path}/compiler/python/site-packages:$PYTHONPATH
  export LD_LIBRARY_PATH=${install_path}/compiler/lib64:${install_path}/runtime/lib64:$LD_LIBRARY_PATH
  export ASCEND_OPP_PATH=${install_path}/opp
  ```

4. 执行命令
- 用户指定模型输入
   1. 参数准备
      - 昇腾AI处理器的离线模型（.om）路径
      - 模型文件（.pb或.onnx）路径
      - 模型的输入数据（.bin）路径
   2. 执行命令  
      1.示例
         ```
      python3 main.py -m /home/HwHiAiUser/onnx_prouce_data/resnet_offical.onnx -om /home/HwHiAiUser/onnx_prouce_data/model/resnet50.om -i /home/HwHiAiUser/result/test/input_0.bin -c /usr/local/Ascend/ascend-toolkit/latest -o /home/HwHiAiUser/result/test
         ```  
      2.**注意**：如果有多个输入，需要用**英文逗号**隔开，其他参数详情可使用--help查询，也可以不指定-c参数，详细内容请查看参数说明  
      3.若为batch输入请将数据文件合并为一个文件作为模型的输入：  
        一键式全流程精度比对（推理）工具支持多batch，但对于多batch，若用户是逐个保存输入数据文件，那么需要将这些数据文件合并为一个文件作为模型的输入。如下提供一个具体操作样例：
    获取网络模型进行网络训练时，假设保存的模型输入数据文件为.bin，将逐个保存的输入数据文件保存在某一目录，例如：/home/HwHiAiUser/input_bin/。
    调用Python执行如下代码。  
      **请根据原始模型的属性填写以下代码的各个参数。**  
      
            ```
            import os
            import numpy as np
             data_sets = []
             sample_batch_input_bin_dir = "/home/HwHiAiUser/input_bin/"
             for item in os.listdir(sample_batch_input_bin_dir):
               # 读取bin文件时，bin文件内的dtype类型须根据模型的输入类型确定，下面以float32为例
               original_input_data = np.fromfile(os.path.join(sample_batch_input_bin_dir, item), dtype=np.float32)
               # 将数据重新组织，具体根据模型输入中的shape值确定
               current_input_data = original_input_data.reshape(1024, 1024, 3)
               # 将当前的数据添加到列表中
               data_sets.append(current_input_data)
             # 将每个batch的数据保存到一个输入bin文件中，从而得到一个包含多batch的输入bin文件
             np.array(data_sets).tofile("input.bin")
            ```

- 用户不指定模型输入
   1. 参数准备

      - 昇腾AI处理器的离线模型（.om）路径
      - 模型文件（.pb或.onnx）路径

   2. 执行命令
      示例：
      ```
      python3 main.py -m /home/HwHiAiUser/onnx_prouce_data/resnet_offical.onnx -om /home/HwHiAiUser/onnx_prouce_data/model/resnet50.om  -c /usr/local/Ascend/ascend-toolkit/latest -o /home/HwHiAiUser/result/test
      ```

### 输出结果说明

```
output-path/timestamp
├── dump_data
│   ├── npu(npu的dump数据目录)
│   │   ├── timestamp
│   │   │   └── resnet50_output_0.bin
│   │   └── 20210206030403
│   │       └── 0
│   │           └── resnet50
│   │               └── 1
│   │                   └── 0
│   │                       ├── Data.inputx.1.3.1596191801455614
│   │                       └── Cast.trans_Cast_169.62.5.1596191801355614
│   ├── onnx(如果-m模型为.onnx，onnx的dump数据目录)
│   │     └── conv1_relu.0.1596191800668285.npy
│   └── tf(如果-m模型为.pb，tf的dump数据目录)
│       └── conv1_relu.0.1596191800668285.npy
├── input
│   ├── input_0.bin(随机生成的，若用户指定了数据，该文件不存在)
│   └── input_1.bin(随机生成的，若用户指定了数据，该文件不存在)
├── model
│   ├── new_model_name.onnx(把每个算子作为输出节点后新生成的onnx模型)
│   └── model_name.json(model_name为om的文件名)
├── result_2021211214657.csv
└── tmp (如果-m模型为.pb, tfdbg相关的临时目录)
```

### 参数说明

| 参数名                      | 描述                                       | 必选   |
| ------------------------ | ---------------------------------------- | ---- |
| -m，--model-path          | 模型文件（.pb或.onnx)路径，目前只支持pb模型与onnx模型       | 是    |
| -om，--offline-model-path | 昇腾AI处理器的离线模型（.om）                        | 是    |
| -i，--input-path          | 模型的输入数据路径，默认根据模型的input随机生成，多个输入以逗号分隔，例如：/home/input\_0.bin，/home/input\_1.bin | 否    |
| -c，--cann-path           | CANN包安装完后路径，默认为/usr/local/Ascend/ascend-toolkit/latest | 否    |
| -o，--output-path         | 输出文件路径，默认为当前路径                           | 否    |
| -s，--input-shape         | 模型输入的shape信息，默认为空，例如input_name1:1,224,224,3;input_name2:3,300,节点中间使用英文分号隔开。input_name必须是转换前的网络模型中的节点名称 | 否    |
| -d，--device              | 指定运行设备 [0,255]，可选参数，默认0                  | 否    |
| --output-nodes           | 用户指定的输出节点。多个节点用英文分号（;）隔开。例如:node_name1:0;node_name2:1;node_name3:0 | 否    |
| --output-size            | 指定模型的输出size，有几个输出，就设几个值。动态shape场景下，获取模型的输出size可能为0，用户需根据输入的shape预估一个较合适的值去申请内存。多个输出size用英文分号（,）隔开, 例如"10000,10000,10000"。 | 否    |


### 执行案例

#### 模型获取

1. 原始模型获取地址

   https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/003_Atc_Models/AE/ATC%20Model/painting/AIPainting_v2.pb

2. om模型获取地址

   https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/003_Atc_Models/AE/ATC%20Model/painting/AIPainting_v2.om

**参考上述使用方法，执行命令运行，如果需要运行指定模型输入，可以先执行第二种用户不指定模型输入命令，用随机生成的bin文件作为输入**  




