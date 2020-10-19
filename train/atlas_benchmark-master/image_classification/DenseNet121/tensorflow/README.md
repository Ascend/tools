# DenseNet121_tensorflow训练说明

### 1. 模型训练参数配置

在train/yaml/DenseNet121.yaml中修改相应配置， 配置项含义:

```
tensorflow_config:
    # 基本参数
    data_url: 数据集路径
    epoches: 跑多少个epoch
    epochs_between_evals: 1
    batch_size: 32
    log_dir: ./ckpt

    # 1p参数
    mode_1p: train     # train、evaluate、train_and_evaluate三种模式
    max_train_steps_1p: 100
    iterations_per_loop_1p: 10
    display_every: 10
    log_name_1p: densenet121_1p.log

    # 8p参数
    mode_8p: train_and_evaluate   # train、evaluate、train_and_evaluate三种模式
    iterations_per_loop_8p: 5004
    lr: 0.1
    log_name_8p: densenet121_8p.log

    mpirun_ip: 仅多机执行需要配置: ip1:卡数量1,ip2:卡数量2
    docker_image:docker 镜像名称:版本号

    # 指定 device id, 多个 id 使用空格分隔, 数量需与 rank_size 相同
    device_group_1p: 0
    device_group_2p: 0 1
    device_group_4p: 0 1 2 3
```

------







    
