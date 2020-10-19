#  YOLOv3_TensorFlow训练说明

### 1. 介绍
YOLOv3是基于第三方TensorFlow开源代码，使用darknet-53作为主干网络，同时支持单尺度与多尺度训练。包含训练集和验证集两部分，可选用包括COCO2014、COCO2017等， 本文档以COCO2014数据集为例，说明yolov3训练操作步骤。

### 2. 运行环境
Python版本: 3.7.5
主要python三方库:
- tensorflow >= 1.15.0 (satisfied with NPU)

- opencv-python

  1、直接pip  install opencv-python

  2、如果直接使用pip install opencv-python无法正常安装三方库，则采用离线安装方法安装。

      (1)'解压opencv包'
        
      (2)'进入解压后的opencv包  cd opencv'
        
      (3)'mkdir -p build'
        
      (4)'cd build'
        
      (5)'cmake -D BUILD_opencv_python3=yes -D BUILD_opencv_python2=no -D          PYTHON3_EXECUTABLE=/usr/local/python3.7.5/bin/python3.7m -D PYTHON3_INCLUDE_DIR=/usr/local/python3.7.5/include/python3.7m -D PYTHON3_LIBRARY=/usr/local/python3.7.5/lib/libpython3.7m.so -D PYTHON3_NUMPY_INCLUDE_DIRS=/usr/local/python3.7.5/lib/python3.7/site-packages/numpy/core/include -D PYTHON3_PACKAGES_PATH=/usr/local/python3.7.5/lib/python3.7/site-packages -D PYTHON_DEFAULT_EXECUTABLE=/usr/local/python3.7.5/bin/python3.7m ..'
        
      (5)'make -j4'
      (6)'make install'

   说明：cmake -D 后参数匹配当前环境

- tqdm          安装方式：pip  install  tqdm

- pycocotools     安装方式：pip  install pycocotools

  说明： 评测的时候需要用到三方库pycocotools

### 3. 数据集预处理
#### 3.1 修改coco_dataset_path的值
在yolov3/tensorflow/code下对coco_minival_anns.py和coco_trainval_anns.py中coco_dataset_path的值改为当前环境的数据集路径， 如/opt/dataset/coco2014。

#### 3.2 运行脚本
```
python3.7 coco_minival_anns.py
python3.7 coco_trainval_anns.py
```
生成训练和验证样本标注文件coco2014_trainval.txt和coco2014_minival.txt，请将这2个文件放置到yolov3/tensorflow/code/data下。
生成的txt文件内容示例如下：
```
0 xxx/xxx/a.jpg 1920 1080 0 453 369 473 391 1 588 245 608 268
1 xxx/xxx/b.jpg 1920 1080 1 466 403 485 422 2 793 300 809 320
...
```

### 4. 准备预训练模型
#### 4.1 下载预训练模型
请从链接https://pjreddie.com/media/files/yolov3.weights下载darknet框架下的预训练模型。

#### 4.2  模型转换
使用train/atlas_benchmark-master/object_detection/yolov3/tensorflow/code下的convert_weight.py将预处理模型转换为TensorFlow框架的ckpt文件：
在convert_weight.py中将weight_path修改为下载下的预训练模型文件的路径，save_path的值修改为命名的转换为TensorFlow框架的ckpt文件的路径； 如
```
weight_path = '../yolov3-tf2/data/darknet53.conv.74'
save_path = './data/darknet_weights/darknet53.ckpt'
```
然后执行
```
python3.7 convert_weight.py

```
注意：save_path中ckpt文件的路径不是在train/atlas_benchmark-master/object_detection/yolov3/tensorflow/code/data/darknet_weights/下时， 请将其手动移至该路径；

### 5. 模型训练
#### 5.1 训练参数配置
在train/yaml/YoLoV3.yaml中修改相应配置， 配置项含义:
```
mode: yolov3的单尺度或者多尺度模式，值为single或者 multi
data_url:数据集路径
runmode: 运行模式，是训练还是评测，值为train或者evaluate
ckpt_path: 评测时要用到的ckpt文件的路径， 仅在evaluate时用到
total_epoches: 跑多少个epoch，
save_epoch: 多少epoch保存一次ckpt文件
device_group_1p: 跑1p时的device_id
device_group_2p: 跑2p时的device_id
device_group_4p: 跑4p时的device_id
mpirun_ip: 仅集群场景时需要配置, 格式ip1:卡数量1,ip2:卡数量2
docker_image: docker镜像名称:版本号
```
YoLoV3.yaml中配置项示例：
```
mode: single
data_url: /opt/npu/dataset
runmode: train
ckpt_path: /home/benchmark-master720/train/atlas_benchmark-master/object_detection/yolov3/tensorflow/result/TrainingJob-20200724115042
total_epoches: 1
save_epoch: 3
device_group_1p: 0
device_group_2p: 0 1
device_group_4p: 0 1 2 3
mpirun_ip: 90.90.176.152:8,90.90.176.154:8
docker_image: mpirun3:latest
```

#### 5.2 训练脚本启动
当前路径为benchmark包的train文件夹下
```
bash benchmark.sh -e YoLoV3 -hw 1p              # host侧1p
bash benchmark.sh -e YoLoV3 -hw 8p              # host侧8p
bash benchmark.sh -e YoLoV3 -hw 1p -docker      # docker侧1p
bash benchmark.sh -e YoLoV3 -hw 8p -docker      # docker侧8p
bash benchmark.sh -e YoLoV3 -ct                 # host侧集群
bash benchmark.sh -e YoLoV3 -ct -docker         # docker侧集群
```

#### 5.3 训练日志
日志在benchmark包的train路径下reuslt中找到YoLoV3的文件夹里。
```
./result/tf_yolov3/TrainingJob-2020xxxxxxxxxx/train_${device_id}.log
./result/TrainingJob-2020xxxxxxxxxx/train_${device_id}.log
./result/tensorflow/yolov3t/TrainingJob-2020xxxxxxxxxx/device_id/hw_yolov3.log
```

### 6. 模型评测
将train/yaml/YoLoV3.yaml中ckpt_path的值改为训练产生的日志的路径， runmode的值改为evaluate，如5.1中示例；
然后运行与训练时相同的脚本，结果参看见train.log。


### 7. 训练结果参考

| Model                 | Npu_nums | mAP      | FPS       |
| :-------------------- | :------: | :------: | :------:  |
| single_scale          | 8        |    30.0  | 740       |
| multi_scale           | 8        |    31.0  | 340       |
| single_scale          | 1        |    ----  | 96        |
| multi_scale           | 1        |    ----  | 44        |



-------


