# TensorFlow1.15 saved_model模型转om工具

## 功能
支持将TensorFlow1.15存储的saved_model转换为om

## 使用环境
1. 用户环境中安装了CANN包的Linux机器

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
	
### 2. 安装CANN包，配置CANN包中的环境变量  

    在Ascend/ascend-toolkit目录下执行source set_env.sh

### 3. saved_model模型文件转om
执行转换脚本

   ```
   python3 saved_model2om.py --input_path=/xxx/xxx/saved_model --output_path=/xxx/output/model --input_shape "input:16,224,224,3" --soc_version Ascend310
   ```

需要调优时

   ```
   python3 saved_model2om.py --input_path=/xxx/xxx/saved_model --output_path=/xxx/output/model --input_shape "input:16,224,224,3" --profiling 1
   ```
​       参数说明：

​       --input_path:  saved_model的存储目录，saved_model按如下目录格式存储：

```
               输入目录：
                   |--save-model.pb
                   |--variable
                         |--variables.data-00000-of-00001
                         |--variables.index

```
​       --output_path: 输出的om文件，会自动补齐后缀，例如设置为/xxx/output/model时，输出文件为/xxx/output/model.om

​       --input_shape: 模型输入shape, 格式为"name1:shape;name2:shape;name3:shape", 当为设置input_shape时，模型输入shape中未明确定义的维度会被自动设置为1

​       --soc_version：输出om的soc_version。当--profiling参数启用时无需配置该项，此时的soc_version根据所在设备决定

​       --profiling:   可选参数:1, 2。该项被设置则会开启aoe调优，配置为1时启用子图调优，配置为2时启用算子调优。（该参数配置后无需再指定job_type）
        
   该工具同时支持对atc/aoe的参数进行透传，如果需要使用其余的参数，当--profiling未被指定时请参考ATC使用文档，当指定--profiling参数时请参考Aoe使用文档
