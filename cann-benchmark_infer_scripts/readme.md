# cann-benchmark infer scripts

#### 介绍

cann-benchmark_infer_scripts，模型处理脚本目录。本目录下存放cann-benchmark推理软件对应的模型前后处理脚本。 与cann-benchmark工具配套。完成样例模型的前处理。模型输出的评估等工作。 可参考cann-benchmark工具说明手册说明操作。

#### 脚本文件说明 

| 序号  | 脚本文件名称                          | 适配模型                                   | 文件功能                            | 备注 |
| :---: | ------------------------------------- | ------------------------------------------ | ----------------------------------- | ---- |
|   1   | bert_base_get_info.py                 | bert base                                  | bert base模型info生成脚本           |      |
|   2   | bert_base_pth2onnx.py                 | bert base                                  | bert base模型 XX 转onnx格式处理脚本 |      |
|   3   | bert_metric.py                        | bert                                       | bert 模型精度统计脚本               |      |
|   4   | get_info.py                           | 分类模型                                   | 分类模型生成数据集脚本              |      |
|   5   | get_yolo_info.py                      | yolo                                       | yolo检测模型生成数据集脚本          |      |
|   6   | imagenet_torch_preprocess.py          | tourchvision类模型                         | tourchvision类模型数据预处理脚本    |      |
|   7   | inception_tf_preprocess.py            | inceptionV3                                | inceptionV3模型数据预处理脚本       |      |
|   8   | map_calculate.py                      | yolo/faster_rcnn_r50/ResNet50V1.5/WideDeep | mAP精度统计脚本                     |      |
|   9   | mobilenet_caffe_preprocess.py         | MobileNets                                 | MobileNets模型数据预处理脚本        |      |
|  10   | mobilenetv2_tf_preprocess.py          | MobileNetsV2                               | MobileNetsV2模型预处理脚本          |      |
|  11   | parse_COCO.py                         | 多模型                                     | 解析原始COCO数据集脚本              |      |
|  12   | parse_VOC2007.py                      | 多模型                                     | 解析原始VOC数据脚本                 |      |
|  13   | resnet50_caffe_preprocess.py          | ResNet50                                   | ResNet50 caffe模型预处理脚本        |      |
|  14   | resnet50_torch_preprocess.py          | ResNet50                                   | ResNet50 pytorch模型数据预处理脚本  |      |
|  15   | ssd-mobilenetv1-fpn_tf_postprocess.py | ssdmobilenetv1_fpn                         | ssdmobilenetv1_fpn模型后处理脚本    |      |
|  16   | ssd-mobilenetv1-fpn_tf_preprocess.py  | ssdmobilenetv1_fpn                         | ssdmobilenetv1_fpn模型前处理脚本    |      |
|  17   | transform_tf_postprocess.py           | Transform                                  | Transform模型后处理脚本             |      |
|  18   | transform_tf_preprocess.py            | Transform                                  | Transform模型前处理脚本             |      |
|  19   | vision_metric.py                      | vison模型                                  | vision模型精度统计脚本              |      |
|  20   | yolo_caffe_postprocess.py             | yoloV3                                     | yoloV3 caffe模型后处理脚本          |      |
|  21   | yolo_caffe_preprocess.py              | yoloV3                                     | yoloV3 caffe模型数据预处理脚本      |      |
|  22   | yolo_tf_postprocess.py                | yoloV3                                     | yoloV3 TensorFlow模型后处理脚本     |      |
|  23   | yolo_tf_preprocess.py                 | yoloV3                                     | yoloV3 TensorFlow模型数据预处理脚本 |      |



#### 贡献

欢迎参与贡献。更多详情，请参阅我们的[贡献者Wiki](../CONTRIBUTING.md)。

#### 许可证
[Apache License 2.0](LICENSE)

