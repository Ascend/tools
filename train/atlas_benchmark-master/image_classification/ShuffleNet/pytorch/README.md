# ShuffleNet_pytorch训练说明

### 1. 模型训练参数配置

在train/yaml/ShuffleNet.yaml中修改相应配置， 配置项含义:

```
pytorch_config:
    # 基本参数
    data_url: /home/imagenet/
    #跑1p时batch_size为1024, 2p为2048，4p为4096，8p时为8196
    batch_size: 1024
    epoches: 240
    epochs_between_evals: 5
    # 默认参数1p 0.5 2p 1 4p 2 8p 4
    lr: 0.5

    # docker 镜像名称:版本号
    docker_image: c73:b02

    # 指定 device id, 多个 id 使用空格分隔, 数量需与 rank_size 相同，目前，只有shufflenet 的1p支持指定device id,多p不支持指定device id。
    device_group_1p: 0
    device_group_2p: 0 1
    device_group_4p: 0 1 2 3
```

------







    
