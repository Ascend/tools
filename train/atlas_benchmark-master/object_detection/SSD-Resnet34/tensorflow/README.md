#  SSD-Resnet34 TensorFlow训练说明

### 1. 运行环境
Python版本: 3.7.5
主要python三方库:
- tensorflow >= 1.15.0 (satisfied with NPU)


### 2. 参数配置
在train/yaml/SSD-Resnet34.yaml中修改相应配置， 配置项含义:

```
tensorflow_config: tensorflow框架下ssd-resnet34的配置项

train_batch_size: 训练时设置的batch size大小
training_file_pattern: 数据集中训练数据集文件标签类型， 数据集中有该类型的文件夹
resnet_checkpoint: ckpt路径
validation_file_pattern: 数据集中验证数据文件标签类型， 数据集中有该类型的文件夹
val_json_file: 数据集中验证数据json文件
eval_batch_size: 评测时设置的batch size大小
num_epochs: epochs数量
model_dir: 存放模型graph等数据的路径
max_steps: 最大步数
runmode: 运行模式 边训练边评测、只训练、只评测
device_group_1p: 跑1p时的device_id
device_group_2p: 跑2p时的device_id
device_group_4p: 跑4p时的device_id
mpirun_ip: 仅集群场景时需要配置, 格式ip1:卡数量1,ip2:卡数量2
docker_image: docker镜像名称:版本号
```


SSD-Resnet34.yaml中配置项示例：
```
tensorflow_config:

    train_batch_size: 32
    training_file_pattern: /home/data/raw_data/tfrecord/train2017*
    resnet_checkpoint: /home/data/raw_data/resnet34_pretrain_model/model.ckpt-28152
    validation_file_pattern: /home/data/raw_data/tfrecord/val2017*
    val_json_file: /home/data/raw_data/annotations/instances_val2017.json
    eval_batch_size: 32
    num_epochs: 1
    model_dir: result_npu
    max_steps: 432000
    runmode: train_and_eval
    device_group_1p: 0
    device_group_2p: 0 1
    device_group_4p: 0 1 2 3
    mpirun_ip: 90.90.176.152:8,90.90.176.154:8
    docker_image: mpirun3:latest

```
SSD-Resnet34.yaml中配置注意事项：
    当ssd-resnet34在docker侧进行训练时，resnet_checkpoint、validation_file_pattern和val_json_file的路径都必须规划在training_file_pattern字段路径中的raw_data下，因配置路径较多，脚本中统一只对training_file_pattern字段路径中的raw_data下文件做映射

### 3. 启动训练脚本

#### 3.1 训练脚本启动
当前路径为benchmark包的train文件夹下
```
bash benchmark.sh -e SSD-Resnet34 -hw 1p              # host侧1p
bash benchmark.sh -e SSD-Resnet34 -hw 8p              # host侧8p
bash benchmark.sh -e SSD-Resnet34 -hw 1p -docker      # docker侧1p
bash benchmark.sh -e SSD-Resnet34 -hw 8p -docker      # docker侧8p
bash benchmark.sh -e SSD-Resnet34 -ct                 # host侧集群
bash benchmark.sh -e SSD-Resnet34 -ct -docker         # docker侧集群
```

#### 3.2 训练日志
日志在benchmark包的train路径下reuslt中找到ssd-resnet34的文件夹里。
```
./result/tf_ssd-resnet34/TrainingJob-2020xxxxxxxxxx/train_${device_id}.log
./result/tf_ssd-resnet34/TrainingJob-2020xxxxxxxxxx/device_id/hw_ssd-resnet34.log
```

### 4. 模型评测
将train/yaml/SSD-Resnet34.yaml中resnet_checkpoint的值改为训练产生的日志的路径， runmode的值改为evaluate，如2中示例；
然后运行与训练时相同的脚本，结果参看见train.log。


### 5. 训练结果参考

1p: 600
4P: 2000
8p: 4000



