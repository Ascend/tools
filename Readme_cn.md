中文|[英文](Readme.md)

# tools

#### 介绍

Ascend tools，昇腾工具仓库。

**请根据自己的需要进入对应文件夹获取工具，或者点击下面的说明链接选择需要的工具进行使用。**

#### 使用说明

1.  [msame](https://github.com/Ascend/tools/tree/master/msame)

    **模型推理工具**：输入.om模型和模型所需要的输入bin文件，输出模型的输出数据文件。

2.  [img2bin](https://github.com/Ascend/tools/tree/master/img2bin)

    **bin文件生成工具**：生成模型推理所需的输入数据，以.bin格式保存。

3.  [makesd](https://github.com/Ascend/tools/tree/master/makesd)
    
    **制卡工具**：制卡工具包，提供ubuntu下制卡功能。

4.  [faster_install](https://github.com/Ascend/tools/tree/master/faster_install)
    
    **快速安装脚本**：环境快速安装脚本。

5.  [configure_usb_ethernet](https://github.com/Ascend/tools/tree/master/configure_usb_ethernet)  
     **USB虚拟网卡连接脚本**：配置USB网卡对应的IP地址。
    
6. [pt2pb](https://github.com/Ascend/tools/tree/master/pt2pb)  

   **pytorch模型转tensorflow pb模型工具**：输入pytorch权重参数模型，转为onnx，再转为pb模型

7. [dnmetis](https://github.com/Ascend/tools/tree/master/dnmetis)  

   **NPU推理精度和性能测试工具**：使用Python封装ACL的C++接口，输入om模型和原始数据集图片、标签，即可执行模型推理，输出精度数据和性能数据  

8. [msquickcmp](https://github.com/Ascend/tools/tree/master/msquickcmp)    

   **一键式全流程精度比对工具**：该工具适用于tensorflow和onnx模型，输入原始模型和对应的离线om模型，输出精度比对结果。    

9. [dockerimages](./dockerimages)    
   **docker 镜像**：Atlas200DK/Atlas300开发/开发运行环境的docker镜像。 

10. [dockerimages](./precision_tool)    
   **精度问题分析工具**：该工具包提供了精度比对常用的功能，当前该工具主要适配Tensorflow训练场景，同时提供Dump数据/图信息的交互式查询和操作入口。 
#### 贡献

欢迎参与贡献。更多详情，请参阅我们的[贡献者Wiki](./CONTRIBUTING.md)。

#### 许可证
[Apache License 2.0](LICENSE)

