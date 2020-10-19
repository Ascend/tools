# Bert-Large_tensorflow训练说明

### 1. 模型训练参数配置

在train/yaml/Bert-Large.yaml中修改相应配置， 配置项含义:

```
tensorflow_config:
    #中文数据用 bert_config_large_cn.json 英文用bert_config_large_en.json
    bert_config_file: bert_config_large_cn.json
    #数据集句子长度是256时 设置为 256,40，句子长度是128时设置为128,20 
    max_seq_length: 128
    max_predictions_per_seq: 20
    
    # 最佳性能train_batch_size为96，如果超显存，可调小至32 
    train_batch_size: 96
    learning_rate: 3.125e-5
    num_warmup_steps: 100
    num_train_steps: 1000
    optimizer_type: adam
    manual_fp16: True
    use_fp16_cls: True
    input_files_dir: /home/BertData/cn-wiki-128/
    eval_files_dir: /home/BertData/cn-wiki-128/ 
    do_train: True
    do_eval: True
    num_accumulation_steps: 1
    iterations_per_loop: 100
    npu_bert_loss_scale: 0
    save_checkpoints_steps: 1000
    npu_bert_clip_by_global_norm: False

    # docker 镜像名称:版本号
    docker_image: c73:b021

    # 仅多机执行需要配置: ip1:卡数量1,ip2:卡数量2
    mpirun_ip: 90.90.140.199:8,90.90.140.229:8

    # 指定 device id, 多个 id 使用空格分隔, 数量需与 rank_size 相同
    device_group_1p: 0
    device_group_2p: 0 1
    device_group_4p: 0 1 2 3
    
```

------







    
