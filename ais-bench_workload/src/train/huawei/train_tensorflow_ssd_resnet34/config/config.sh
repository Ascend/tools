export PYTHON_COMMAND=python3.7

# 参数信息
export MODE=train
export BATCH_SIZE=32
export TRAINING_FILE_PATTERN=/home/datasets/raw_data_tfrecord/train2017*
export RESNET_CHECKPOINT=/home/datasets/raw_data/resneet32_pretrain_model/model.ckpt-28152
export VALIDATION_FILE_PATTERN=/home/datasets/raw_data/tfrecord/val2017*
export VAL_JSON_FILE=/home/datasets/raw_data/annotations/instances_val2017.json

# 网络信息
export RANK_TABLE_FILE=/home/tools/rank_table_8p_62.json
export RANK_SIZE=1
export DEVICE_NUM=1

#export NODEINFO_FILE=/home/tools/2node_6264.json
