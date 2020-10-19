# EfficientNet_pytorch训练说明

### 1. 模型训练参数配置

在train/yaml/EfficientNet.yaml中修改相应配置， 配置项含义:

```
pytorch_config:
    data_url: 数据集路径
    epoches: 跑多少个epoch
    batch_size: 1p 参数为256 2p 512 4p 1024 8p为2048
    seed: 49
    lr: 默认参数1p 0.2 2p 0.4 4p 0.8 8p 1.6
    docker_image: docker 镜像名称:版本号
```

------







    
