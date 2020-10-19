# DeepMar_pytorch训练说明

### 1. 数据集处理

#### 1.1. 下载并准备数据集：
百度云盘https://pan.baidu.com/s/1q8nsydT7xkDjZJOxvPcoEw
passwd: 5vep
或者https://drive.google.com/open?id=1q4cux17K3zNBgIrDV4FtcHJPLzXNKfYG

存放地址
./dataset/peta/images/*.png
./dataset/peta/PETA.mat

#### 1.2 运行以下命令，分割训练集、测试集（路径修改成自己存放数据集路径）
python script/dataset/transform_peta.py 
生成 peta_dataset.pkl，peta_partition.pkl 文件

### 2. 模型训练参数配置

在train/yaml/DeepMar.yaml中修改相应配置， 配置项含义:

```
pytorch_config:
    data_url: 数据集路径
    epoches: 跑多少个epoch
    batch_size:1p 参数为256 2p 512 4p 1024  8p为2048
    seed: 49
    lr: 默认参数1p 0.01 2p 0.016 4p 0.016 8p 0.016
    docker_image: docker 镜像名称:版本号
```

------







    
