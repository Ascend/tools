# ResNet101_tensorflow训练说明

### 1. 模型训练参数配置

在train/yaml/ResNet101.yaml中修改相应配置， 配置项含义:

```
tensorflow_config:
    # 基本参数
    data_url: /home/imagenet_TF/
    # 1p/8p,epoches设为150
    epoches: 1
    epochs_between_evals: 1
    max_train_steps: 1000
    batch_size: 128

    # 仅多机执行需要配置: ip1:卡数量1,ip2:卡数量2
    mpirun_ip: 90.90.176.152:8,90.90.176.154:8

    # docker 镜像名称:版本号
    docker_image: c73:b02

    # 指定 device id, 多个 id 使用空格分隔, 数量需与 rank_size 相同
    device_group_1p: 0
    device_group_2p: 0 1
    device_group_4p: 0 1 2 3
```

------







    
