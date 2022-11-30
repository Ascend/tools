# 图像分类与检测任务推理样例程序
本程序为ais-bench针对图像分类与检测任务的推理python语言样例实现，对应的软件包为inference_vision_classification_and_detection-Ais-Bench-aarch64-.tar.gz



ais-bench标准化性能测试软件,又称AI Server Benchmark软件，是根据AI标准（IEEE 2937及 T/CESA 1169-2021）对AI服务器进行性能测试的工具软件。

本样例主要基于ais-bench软件，实现图像分类与检测任务样例程序。

## 软件依赖
1. loadgen模块

  负载生成器LoadGenerator模块是AIS-Bench推理任务的必备的控制套件，负责负载生成、控制、统计等功能。会根据不同的设置与参数，对负载执行不同的分发策略，以满足不同场景下的测试要求。

  请获取loadgen程序包，进行安装。该部分以whl包方式提供，需要通过如下命令安装，要注意python版本与包的对应关系

  ```
  pip3 install loadgen-0.0.1-cp37-cp37m-linux_aarch64.whl
  ```

2. aclruntime模块

   [aclruntime模块](https://github.com/Ascend/tools/tree/master/ais-bench_workload/tool/ais_infer)是基于华为cann软件栈开发的推理程序包。在官网地址可以直接编译出python程序包。

   执行如下命令，进行安装。

   ```
   pip3 install aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
   ```

3. 其他软件依赖

   请查看 基准路径/code/requirements.txt，查看负载程序要求的依赖，执行如下命令进行安装

   ```
   pip3 install -r requirements.txt
   ```
## 当前支持的场景

当前已经支持的场景如下

| 场景宏定义(对应配置文件中PROFILE值) | 基准的modelzoo链接                                           |      |
| ----------------------------------- | ------------------------------------------------------------ | ---- |
| *resnet50_onnx*                     | *[ModelZoo-PyTorch_Resnet50_Pytorch_Infer_link](https://github.com/Ascend/ModelZoo-PyTorch/tree/master/ACL_PyTorch/built-in/cv/Resnet50_Pytorch_Infer)* |      |
| *resnet101_onnx*                    | *[ModelZoo-PyTorch_Resnet101_Pytorch_Infer](https://github.com/Ascend/ModelZoo-PyTorch/tree/master/ACL_PyTorch/built-in/cv/Resnet101_Pytorch_Infer)* |      |
| *inceptionv3_onnx*                  | *[ModelZoo-PyTorch_InceptionV3_for_Pytorch](https://github.com/Ascend/ModelZoo-PyTorch/tree/master/ACL_PyTorch/built-in/cv/InceptionV3_for_Pytorch)* |      |
| *yolov3-caffe_voc2012*                  | *[yolov3_for_caffe](https://cowtransfer.com/s/6630ab0d898649)* |      |
| *deeplabv3-tf_voc2012*                  | *[ModelZoo-TensorFlow_deepLabv3_for_tf](https://github.com/Ascend/ModelZoo-TensorFlow/tree/master/ACL_TensorFlow/built-in/cv/DeepLabv3_for_ACL)* |      |
|                                     |                                                              |      |
