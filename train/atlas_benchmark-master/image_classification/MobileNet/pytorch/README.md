# MobileNet_pytorch训练说明

### 1. 模型训练参数配置

在train/yaml/MobileNet.yaml中修改相应配置， 配置项含义:

```
pytorch_config:
    data_url: 数据集路径
    epoches: 跑多少个epoch
    batch_size: 单p默认768 2p 1534 4p 3072  8p默认6144
    lr: 默认参数1p 0.03 2p 0.06 4p 0.12 8p 0.24
    seed: 123456
    docker_image: docker 镜像名称:版本号
```

------







    
