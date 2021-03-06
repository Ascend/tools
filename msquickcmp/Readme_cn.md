# 一键式全流程精度比对（推理）

### 功能介绍

本文介绍一键式全流程精度比对（推理）工具，该工具适用于TensorFlow和ONNX模型，用户只需要输入原始模型，对应的离线模型和输入，就能出整网比对的结果，离线模型必须是通过ATC工具转换的om模型，输入bin文件需要符合模型的输入要求（支持模型多输入）。

### 环境准备

1. 已在昇腾AI推理设备上安装开发与运行环境。

   安装参考文档：https://support.huaweicloud.com/instg-cli-cann/atlascli_03_0001.html

2. 安装python3.7.5环境

3. 通过pip3.7.5安装环境依赖onnxruntime、onnx、numpy、skl2onnx。

   pip安装依赖命令示例：

   ```
   pip3.7.5 install onnxruntime
   ```
4. 安装TensorFlow1.15.0的环境

   安装参考文档：https://bbs.huaweicloud.com/blogs/181055

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
export DDK_PATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest
export NPU_HOST_LIB=/home/HwHiAiUser/Ascend/ascend-toolkit/latest/acllib/lib64/stub
```

3. 配置ATC工具环境变量

  （如下环境变量中${install_path}以软件包使用默认安装路径为例进行说明）

  ```
  export PATH=/usr/local/python3.7.5/bin:${install_path}/atc/ccec_compiler/bin:${install_path}/atc/bin:$PATH
  export PYTHONPATH=${install_path}/atc/python/site-packages:$PYTHONPATH
  export LD_LIBRARY_PATH=${install_path}/atc/lib64:$LD_LIBRARY_PATH
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
      2. **注意**：如果有多个输入，需要用**英文逗号**隔开，其他参数详情可使用--help查询，也可以不指定-c参数，详细内容请查看参数说明

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
├── input
│	└── input_0.bin(随机生成的，若用户指定了数据，该文件不存在)
│	└── input_1.bin(随机生成的，若用户指定了数据，该文件不存在)
├── model
│   └── new_model_name.onnx(把每个算子作为输出节点后新生成的onnx模型)
│	└── model_name.json(model_name为om的文件名)
├── dump_data
│   ├── npu(npu的dump数据目录)
		│   ├── timestamp
				└── resnet50_output_0.bin
			│   ├── 20210206030403 
				│   ├── 0
                    │   ├── resnet50
                        │   ├── 1
							│   ├── 0
								└── Cast.trans_Cast_169.62.1596191801355614				
│   ├── onnx(如果-m模型为.onnx，onnx的dump数据目录)
	└── conv1_relu.0.1596191800668285.npy
│   ├── tf(如果-m模型为.pb，tf的dump数据目录)
	└── conv1_relu.0.1596191800668285.npy	
├── result_2021211214657.csv
```

### 参数说明

| 参数名                      | 描述                                       | 必选   |
| ------------------------ | ---------------------------------------- | ---- |
| -m，--model-path          | 模型文件（.pb或.onnx)路径，目前只支持pb模型与onnx模型       | 是    |
| -om，--offline-model-path | 昇腾AI处理器的离线模型（.om）                        | 是    |
| -i，--input-path          | 模型的输入数据路径，默认根据模型的input随机生成，多个输入以逗号分隔，例如：/home/input\_0.bin，/home/input\_1.bin | 否    |
| -c，--cann-path           | CANN包安装完后路径，默认为/usr/local/Ascend/ascend-toolkit/latest | 否    |
| -o，--output-path         | 输出文件路径，默认为当前路径                           | 否    |

### 执行案例

#### 模型获取

1. 原始模型获取地址

   https://modelzoo-train-atc.obs.cn-north-4.myhuaweicloud.com/003_Atc_Models/AE/ATC%20Model/painting/AIPainting_v2.pb

2. om模型获取地址

   https://modelzoo-train-atc.obs.cn-north-4.myhuaweicloud.com/003_Atc_Models/AE/ATC%20Model/painting/AIPainting_v2.om

**参考上述使用方法，执行命令运行，如果需要运行指定模型输入，可以先执行第二种用户不指定模型输入命令，用随机生成的bin文件作为输入**  
**注意：目前暂时不支持动态shape**




