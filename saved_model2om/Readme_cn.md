# TensorFlow1.15 saved_model模型转om工具

## 功能
支持将TensorFlow1.15存储的saved_model生成基于NPU版本TensorFlow的HW saved_model用于加载om

## 使用环境
1. 用户环境中安装了CANN-Toolkit + CANN-tfplugin的Linux机器

2. 已经安装TensorFlow

3. 调优功能需要在昇腾设备上执行

## 预置条件

1.saved_model模型文件。模型保存接口示例：

   ```
tf.saved_model.simple_save(sess, 'models/', 
                           inputs={'inputs': inputs_tensor},
                           outputs={'outputs': outputs_tensor})
   ```


## 工具获取

**方法1. 下载压缩包方式获取**

将 https://github.com/Ascend/tools 仓中的脚本下载至服务器的任意目录。

例如存放路径为：$HOME/AscendProjects/tools。

**方法2. 命令行使用git命令方式获取**

在命令行中：$HOME/AscendProjects目录下执行以下命令下载代码。

    git clone https://github.com/Ascend/tools.git



## 使用方法

### 1. 安装TensorFlow1.15   

    pip3 install tensorflow==1.15

### 2. 安装CANN-Toolkit包与CANN-tfplugin包，配置CANN包中的环境变量  

    在Ascend/ascend-toolkit,Ascend/tfplugin目录下执行source set_env.sh

### 3. saved_model模型文件转om
执行转换脚本

   ```shell
python3 saved_model2om.py --input_path=/xxx/xxx/saved_model --output_path=/xxx/output/model --input_shape "input:16,224,224,3" --soc_version Ascend310
   ```

需要调优时

   ```shell
python3 saved_model2om.py --input_path=/xxx/xxx/saved_model --output_path=/xxx/output/model --input_shape "input:16,224,224,3" --profiling 1
   ```
参数说明

| 参数 | 参数说明 |
| - | - |
| --input_path | 原始saved_model的存储目录，需按如下目录格式存储<br />输入目录<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├──saved_model.pb<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──variables<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├──variables.data-0000-of-0001<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──variables.index |
| --output_path | 转换成功后再指定output_path的父目录下生成对应的HW saved_model，路径为${output_path_dir}/{om_name}_{timestamp}<br />例如设置为/xxx/output/model时，输出路径为/xxx/output/model_load_om_saved_model_20230101_01_00_00 |
| --input_shape | 模型输入shape, 格式为"name1:shape;name2:shape;name3:shape"<br />当设置input_shape时，模型输入shape中未明确定义的维度会被自动设置为1 |
| --soc_version | 输出om模型的芯片类型。<br />当设置--profiling参数时，无需配置此参数，由当前执行转换的设备决定 |
| --profiling | 设置此参数时，则会开启AOE调优。（该参数配置后无需再指定job_type）<br />- 取值为1时，启用子图调优<br />- 取值为2时，启用算子调优<br />如需进行子图或算子调优，则该参数必选 |
| --method_name | 用于配置TF Serving运行时用于推理的方法，不配置则会从原始saved_model中获取 |
| --new_input_nodes | 重新选择输入节点，格式为"算子:类型:算子名;算子:类型:算子名"<br />例如"embedding:DT_FLOAT:bert/embedding/word_embeddings:0;add:DT_INT:bert/embedding/add:0" |
| --new_output_nodes | 重新选择输出节点，格式为"算子:算子名"<br />例如"loss:loss/Softmax:0" |
| --output_type | ATC/AOE参数，指定网络输出数据类型或指定某个输出节点的输出类型，使用方法请参考对应使用文档。可选参数。 |
| --input_fp16_nodes | ATC/AOE参数，指定输入数据类型为FP16的输入节点名称，使用方法请参考对应使用文档。可选参数。 |

### 4.ATC/AOE参数透传

该工具同时支持对ATC/AOE的参数进行透传。

如果需要使用其余的参数，当`--profiling`未被指定时请参考ATC使用文档，当指定`--profiling`参数时请参考AOE使用文档。

当您使用参数透传时，若您使用了如下参数，请参考如下参数的支持情况（以下参数在ATC/AOE中一致）：

- --out_nodes
  - 功能：用于指定输出节点。
  - 该功能工具已支持，详见本工具参数`--new_output_nodes`。
  - **本工具暂不支持使用参数透传`--out_nodes`**
- --is_input_adjust_hw_layout
  - 功能：用于指定网络输入数据类型是否为FP16，数据格式是否为NC1HWC0。
  - **本工具暂不支持使用参数透传该参数**
- --is_output_adjust_hw_layout
  - 功能：用于指定网络输出数据类型是否为FP16，数据格式是否为NC1HWC0。
  - **本工具暂不支持使用参数透传该参数**


