# MobileNet_tensorflow训练说明

### 1. 模型训练参数配置

在train/yaml/MobileNet.yaml中修改相应配置， 配置项含义:

```
tensorflow_config:
    # 基本参数
    max_steps: 1000
    data_url: 数据集路径
    epoches: 跑多少个epoch

    # 训练(train) 或 评测(evaluate)
    mode: train
    batch_size: 256
    #仅在 mode 为 evaluate 时用到
    ckpt_path: /opt/0908/benchmark-benchmark_Alpha/train/result/tf_mobilenet/trainingJob_20200905171017/0/results/model.ckpt-123125

    # 仅多机执行需要配置: ip1:卡数量1,ip2:卡数量2
    mpirun_ip: 90.90.176.152:8,90.90.176.154:8

    # docker 镜像名称:版本号
    docker_image: c73:b021

    # 指定 device id, 多个 id 使用空格分隔, 数量需与 rank_size 相同
    device_group_1p: 0
    device_group_2p: 0 1
    device_group_4p: 0 1 2 3    
    
    profiling_mode: false
    profiling_options: training_trace
    fp_point: L2Loss
    bp_point: gradients/AddN_30
    aicpu_profiling_mode: false

```

------







    
