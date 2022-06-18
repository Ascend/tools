# 图像分类与检测任务推理样例程序
本程序为ais-bench针对图像分类与检测任务的推理python语言样例实现，对应的软件包为inference_vision_classification_and_detection-Ais-Bench-aarch64-.tar.gz

## 依赖与安装
1. 调用如下命令安装依赖包，主要包括opencv numpy等
pip3 install -r requirements.txt 
2. 安装loadgenerator模块，即负载生成器。该部分以whl包方式提供，需要通过如下命令安装，要注意python版本与包的对应关系
```
pip3 install loadgen-0.0.1-cp36-cp36m-linux_x86_64.whl
或
pip3 install loadgen-0.0.1-cp37-cp37m-linux_x86_64.whl
```
3. 安装aclruntime模块。
```
pip3 install aclruntime-0.0.1-cp37-cp37m-linux_aarch64.whl
```
4. 设置ascend-toolkit环境变量。
```
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```

## 运行  
1. 修改配置文件 config/config.sh

```
PYTHON_COMMAND  设置运行的python命令  
PROFILE         支持的场景  
MODEL_PATH      om模型路径  
BATCH_SIZE      om模型对应的batchsize  
DATASET_PATH    数据集路径  
VOCAB_FILE      vocab.txt文件路径  
```

2. 执行 ./ais-bench-stubs test命令用于离线测试。  
3. 如果需要联机Tester测试，请配置好config.json后，然后运行 ./ais-bench-stubs  

## 配置文件介绍  
resnet50  

```
export PROFILE=resnet50_pytorch
export MODEL_PATH=/home/lcm/tool/inference_tools/test/resnet/resource/resnet50_v1_bs1_fp32.om
export BATCH_SIZE=1
export DATASET_PATH=/home/datasets/imagenet/val/

```
/home/datasets/imagenet/val/ 包含 50000张图片和val_map.txt文件。其中val_map.txt存储了图片与标签对应关系，原始数据集中不包含改文件，需要用户自行下载并添加到与图片同级的目录下。
```
yolo v3  

export PROFILE=yolov3-caffe_voc2012
export MODEL_PATH=/home/yxd/yolov3/models/YoloV3/yolov3_bs1_in32_out32.om
export BATCH_SIZE=1
export DATASET_PATH=/home/datasets/VOC2012/VOCdevkit/VOC2012/

[root@b8ae28fb8da5 dataset]# ls /home/datasets/VOC2012/VOCdevkit/VOC2012/
Annotations  ImageSets  JPEGImages  SegmentationClass  SegmentationObject  coco.names

依赖： 由于本样例依赖于cann-benchmark做推理，因此需要在code目录下增加 benchmark执行二进制程序
注意事项：VOC原生数据集不包含标签文件coco.names，需要用户下载并添加到数据集目录下。

deeplab v3  

export PROFILE=deeplabv3-tf_voc2012
export MODEL_PATH=/home/zhou/code/DeepLabv3_for_TensorFlow/deeplabv3_tf_1batch.om
export BATCH_SIZE=1
export DATASET_PATH=/home/zhou/code/DeepLabv3_for_TensorFlow/scripts/PascalVoc2012

[root@b8ae28fb8da5 dataset]# ls /home/datasets/VOC2012/VOCdevkit/VOC2012/
Annotations  ImageSets  JPEGImages  SegmentationClass  SegmentationObject  coco.names
```

## 模型获取与转换指南
本样例使用的resnet50原始模型路径如下：
https://download.pytorch.org/models/resnet50-19c8e357.pth

本样例使用的yolov3模型源于darknet转成caffe模型后再用ATC转换成om模型

本样例使用的deeplav3原始模型路径如下：
https://www.hiascend.com/zh/software/modelzoo/detail/1/7557284c9c14418bb22403ac32e4f960

更改原始模型的输入batchsize，需要使用ATC转换工具，参考文档：
https://support.huaweicloud.com/adevg-A800_3000_3010/atlasdevelopment_01_0034.html
