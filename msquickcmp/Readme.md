# One-Click Accuracy Analyzer (Inference)

### Overview

This readme describes the **main.py** tool, or One-Click Accuracy Analyzer, for inference scenarios. This tool enables one-click network-wide accuracy analysis of TensorFlow and ONNX models. You only need to prepare the original model, offline model equivalent, and model input file. Beware that the offline model must be an .om model converted using the Ascend Tensor Compiler (ATC) tool, and the .bin input file must meet the input requirements of the model (multi-input models are supported).  
For details about the usage restrictions of the tool, visit https://support.huaweicloud.com/intl/en-us/tg-cannApplicationDev330/atlasaccuracy_16_0011.html.

### Environment Setup

1. Set up an operating and development environment powered by Ascend AI Processors.

2. Install Python 3.7.5.

3. Install environment dependencies, including **onnxruntime**, **onnx**, **numpy**, **skl2onnx**, **pexpect**, and **gnureadline** using **pip3.7.5**.

   Command example:

   ```
   pip3.7.5 install onnxruntime
   ```
4. Install TensorFlow 1.15.0.

   For details, visit: https://bbs.huaweicloud.com/blogs/181055
- Note: If the installation of dependent modules fails using the pip command, it is recommended to execute the command **pip3 install --upgrade pip** to avoid installation failure due to low pip version.
### Tool Download

- By downloading the package:

   Download the script from the tools repository at https://github.com/Ascend/tools to any directory on the server, for example, **$HOME/AscendProjects/tools**.

- By running the **git** command:

   Run the following command in the **$HOME/AscendProjects** directory to download code:

   **git clone https://github.com/Ascend/tools.git**

### Tool Usage

1. Go to the tool directory **msquickcmp**.


```
cd $HOME/AscendProjects/tools/msquickcmp/
```

2. Set environment variables.
   The following is an example only. Replace **/home/HwHiAiUser/Ascend/ascend-toolkit/latest** with the actual ACLlib installation path.

```
export install_path=/home/HwHiAiUser/Ascend/ascend-toolkit/latest
export DDK_PATH=${install_path}
export NPU_HOST_LIB=${install_path}/acllib/lib64/stub
```

3. Configure ATC environment variables.

  The following is an example only. Replace **${install_path}** with the actual ATC installation path.

  ```
  export PATH=/usr/local/python3.7.5/bin:${install_path}/atc/ccec_compiler/bin:${install_path}/atc/bin:$PATH
  export PYTHONPATH=${install_path}/atc/python/site-packages:$PYTHONPATH
  export LD_LIBRARY_PATH=${install_path}/atc/lib64:${install_path}/acllib/lib64:$LD_LIBRARY_PATH
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
      3. For batch input, please combine the data files into one file as the input of the model:
           The full-process accuracy comparison (inference) tool supports multiple batches, but for multiple batches, if the user saves the input data files one by one, these data files need to be combined into one file as the input of the model. A specific operation example is provided as follows:
         When acquiring a network model for network training, assuming that the saved model input data file is .bin, save the input data files saved one by one in a certain directory, for example: /home/HwHiAiUser/input_bin/. Call Python to execute the following code.  
         **Please fill in each parameter of the following code according to the properties of the original model.**
         ```
            import os
            import numpy as np
             data_sets = []
             sample_batch_input_bin_dir = "/home/HwHiAiUser/input_bin/"
             for item in os.listdir(sample_batch_input_bin_dir):
               # When reading the bin file, the dtype type in the bin file must be determined according to the input type of the model. The following takes float32 as an example.
               original_input_data = np.fromfile(os.path.join(sample_batch_input_bin_dir, item), dtype=np.float32)
               # Reorganize the data according to the shape value in the model input.
               current_input_data = original_input_data.reshape(1024, 1024, 3)
               # Add the current data to the list.
               data_sets.append(current_input_data)
             # Save the data of each batch to an input bin file to get an input bin file containing multiple batches.
             np.array(data_sets).tofile("input.bin")
            ```
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
├── dump_data
│   ├── npu # Dump directory on the NPU.
│   │   ├── timestamp
│   │   │   └── resnet50_output_0.bin
│   │   └── 20210206030403
│   │       └── 0
│   │           └── resnet50
│   │               └── 1
│   │                   └── 0
│   │                       ├── Data.inputx.1.3.1596191801455614
│   │                       └── Cast.trans_Cast_169.62.5.1596191801355614
│   ├── onnx # ONNX dump directory if the -m option specifies an .onnx model.
│   │     └── conv1_relu.0.1596191800668285.npy
│   └── tf # TensorFlow dump directory if the -m option specifies a .pb model.
│       └── conv1_relu.0.1596191800668285.npy
├── input
│   ├── input_0.bin # Randomly generated. If you have specified the input data, this file is not generated.
│   └── input_1.bin # Randomly generated. If you have specified the input data, this file is not generated.
├── model
│   ├── new_model_name.onnx # Modified .onnx model with all operators specified as output nodes.
│   └── model_name.json # model_name indicates the .om file name.
├── result_2021211214657.csv
└── tmp # tfdbg dump data directory if the -m option specifies a .pb model.
```

### Command-line Options

| Option&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; | Description                              | Required |
| ---------------------------------------- | ---------------------------------------- | -------- |
| -m, --model-path                         | Path of the original model (.pb or .onnx). Currently, only .pb and .onnx models are supported. | Yes      |
| -om, --offline-model-path                | Path of the offline model (.om) adapted to the Ascend AI Processor. | Yes      |
| -i, --input-path                         | Path of model input data, which is generated based on model inputs by default. Separate model inputs with commas (,), for example, **/home/input\_0.bin, /home/input\_1.bin**. | No       |
| -c, --cann-path                          | CANN installation path, defaulted to **/usr/local/Ascend/ascend-toolkit/latest** | No       |
| -o, --output-path                        | Output path, defaulted to the current directory | No       |
| -s，--input-shape                         | Shape information of model inputs. Separate multiple nodes with semicolons, for example, **input_name1:1,224,224,3;input_name2:3,300**. By default, this option is left blank. **input_name** must be the node name in the network model before model conversion. | No       |
| -d，--device                              | Specify running device [0,255], default 0. | No       |
| --output-nodes                           | Output node specified by the user. Separate multiple nodes with semicolons, for example, **node_name1:0;node_name2:1;node_name3:0**. | No       |
| --output-size                            | Specify the output size of the model. If there are several outputs, set several values. In the dynamic shape scenario, the output size of the acquired model may be 0. The user needs to estimate a more appropriate value according to the input shape to apply for memory. Multiple output sizes are separated by English semicolons (,), such as "10000,10000,10000"。 | No       |

### Sample Execution

#### Model Download

1. Obtain the original model from:

   https://modelzoo-train-atc.obs.cn-north-4.myhuaweicloud.com/003_Atc_Models/AE/ATC%20Model/painting/AIPainting_v2.pb

2. Obtain the .om model from:

   https://modelzoo-train-atc.obs.cn-north-4.myhuaweicloud.com/003_Atc_Models/AE/ATC%20Model/painting/AIPainting_v2.om

**Run the commands by referring to the above guide to execute the sample. If you want to try with model input data specified, run the command for the scenario where input data is not specified to generate input data files (.bin) as the input.**




