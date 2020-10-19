# ResNet50_tensorflow训练说明

### 1. 模型训练参数配置

在train/yaml/ResNet50.yaml中修改相应配置， 配置项含义:

```
 tensorflow_config:
    data_url: 数据集路径
    batch_size: 32
    # 1p/8p, epoches设为90
    epoches: 1
    max_train_steps: 1000
    epochs_between_evals: 1
    iterations_per_loop: 100
    save_checkpoints_steps: 115200

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







    
