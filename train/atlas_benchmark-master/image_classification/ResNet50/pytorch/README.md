# ResNet50_pytorch训练说明

### 1. 模型训练参数配置

在train/yaml/ResNet50.yaml中修改相应配置， 配置项含义:

```
 pytorch_config:
    data_url: 数据集路径
    batch_size: 跑1p时batch_size为512；跑8p时batch_size为4096
    epoches: 跑多少个epoch
    mode: train_and_evaluate、evaluate两种模式
    ckpt_path: /home/train/result/pt_resnet50/training_job_20200916042624/7/checkpoint_npu7model_best.pth.tar
    docker_image: docker 镜像名称:版本号
    lr: 默认参数1p 0.2，8p 2.048
```

------







    
