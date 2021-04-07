# One-Click Accuracy Analyzer (Inference)

### Overview

This readme describes the **main.py** tool, or One-Click Accuracy Analyzer, for inference scenarios. This tool enables one-click network-wide accuracy analysis of TensorFlow and ONNX models. You only need to prepare the original model, offline model equivalent, and model input file. Beware that the offline model must be an .om model converted using the Ascend Tensor Compiler (ATC) tool, and the .bin input file must meet the input requirements of the model (multi-input models are supported).

### Environment Setup

1. Set up the development and operating environments on the Ascend AI inference device.

   For details, visit: https://support.huaweicloud.com/intl/en-us/instg-cli-cann202/atlasrun_03_0002.html

2. Install Python 3.7.5.

3. Install environment dependencies including ONNX Runtime, ONNX, NumPy, and skl2onnx using **pip3.7.5**.

   Command example:

   ```
   pip3.7.5 install onnxruntime
   ```
4. Install TensorFlow 1.15.0.

   For details, visit: https://bbs.huaweicloud.com/blogs/181055

### Tool Download

- By downloading the package:

   Download the script from the tools repository at https://gitee.com/ascend/tools to any directory on the server, for example, **$HOME/AscendProjects/tools**.

- By running the **git** command:

   Run the following command in the **$HOME/AscendProjects** directory to download code:

   **git clone https://gitee.com/ascend/tools.git**

### Tool Usage

1. Go to the tool directory **msquickcmp**.


```
cd $HOME/AscendProjects/tools/msquickcmp/
```

2. Set environment variables.
  The following is an example only. Replace **/home/HwHiAiUser/Ascend/ascend-toolkit/latest** with the actual ACLlib installation path.

```
export DDK_PATH=/home/HwHiAiUser/Ascend/ascend-toolkit/latest
export NPU_HOST_LIB=/home/HwHiAiUser/Ascend/ascend-toolkit/latest/acllib/lib64/stub
```

3. Configure ATC environment variables.

  The following is an example only. Replace **${install_path}** with the actual ATC installation path.

  ```
  export PATH=/usr/local/python3.7.5/bin:${install_path}/atc/ccec_compiler/bin:${install_path}/atc/bin:$PATH
  export PYTHONPATH=${install_path}/atc/python/site-packages:$PYTHONPATH
  export LD_LIBRARY_PATH=${install_path}/atc/lib64:$LD_LIBRARY_PATH
  export ASCEND_OPP_PATH=${install_path}/opp
  ```

4. Run the following command.
- With model input specified:
   1. Prepare the following parameters:
      - Path of the offline model (.om) adapted to Ascend AI Processor
      - Path of the original model (.pb or .onnx)
      - Path of model input data (.bin)
   2. Execute the command.
      1. Command example:
         ```
         python3 main.py -m /home/HwHiAiUser/onnx_prouce_data/resnet_offical.onnx -om /home/HwHiAiUser/onnx_prouce_data/model/resnet50.om -i /home/HwHiAiUser/result/test/input_0.bin -c /usr/local/Ascend/ascend-toolkit/latest -o /home/HwHiAiUser/result/test
         ```
      2. **Note**: If there is more than one input data file, separate them with commas (,). For more available command-line options, use the **--help** option. The **-c** option is optional. For more details, see the Command-line Options table below.

- With model input not specified:
   1. Prepare the following parameters:

      - Path of the offline model (.om) adapted to Ascend AI Processor
      - Path of the original model (.pb or .onnx)

   2. Execute the command.
      Command example:
      ```
      python3 main.py -m /home/HwHiAiUser/onnx_prouce_data/resnet_offical.onnx -om /home/HwHiAiUser/onnx_prouce_data/model/resnet50.om  -c /usr/local/Ascend/ascend-toolkit/latest -o /home/HwHiAiUser/result/test
      ```

### Analysis Result Description

```
output-path/timestamp
├── input
│	└── input_0.bin # Randomly generated. If you have specified the input data, this file is not generated.
│	└── input_1.bin # Randomly generated. If you have specified the input data, this file is not generated.
├── model
│ └── new_model_name.onnx # Modified .onnx model with all operators specified as output nodes.
│	└── model_name.json # model_name indicates the .om file name.
├── dump_data
│   ├── npu # Dump directory on the NPU.
		│   ├── timestamp
				└── resnet50_output_0.bin
			│   ├── 20210206030403 
				│   ├── 0
                    │   ├── resnet50
                        │   ├── 1
							│   ├── 0
								└── Cast.trans_Cast_169.62.1596191801355614				
│   ├── onnx # ONNX dump directory if the -m option specifies an .onnx model.
	└── conv1_relu.0.1596191800668285.npy
│   ├── tf # TensorFlow dump directory if the -m option specifies a .pb model.
	└── conv1_relu.0.1596191800668285.npy	
├── result_2021211214657.csv
```

### Command-line Options

| Option&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; | Description                              | Required |
| ---------------------------------------- | ---------------------------------------- | -------- |
| -m, --model-path                         | Path of the original model (.pb or .onnx). Currently, only .pb and .onnx models are supported. | Yes      |
| -om, --offline-model-path                | .om model adapted to Ascend AI Processor | Yes      |
| -i, --input-path                         | Path of model input data, which is generated based on model inputs by default. Separate model inputs with commas (,), for example, **/home/input\_0.bin, /home/input\_1.bin**. | No       |
| -c, --cann-path                          | CANN installation path, defaulted to **/usr/local/Ascend/ascend-toolkit/latest** | No       |
| -o, --output-path                        | Output path, defaulted to the current directory | No       |

### Sample Execution

#### Model Download

1. Obtain the original model from:

   https://modelzoo-train-atc.obs.cn-north-4.myhuaweicloud.com/003_Atc_Models/AE/ATC%20Model/painting/AIPainting_v2.pb

2. Obtain the .om model from:

   https://modelzoo-train-atc.obs.cn-north-4.myhuaweicloud.com/003_Atc_Models/AE/ATC%20Model/painting/AIPainting_v2.om

**Run the commands by referring to the above guide to execute the sample. If you want to try with model input data specified, run the command for the scenario where input data is not specified to generate input data files (.bin) as the input.**  
**Note: Currently, dynamic shape is not supported.**



