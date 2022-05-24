export PYTHON_COMMAND=python3.7

# 参数信息
export TRAIN_DATA_PATH=/home/datasets/imagenet_TF
export MAX_TRAIN_STEPS=200
# 网络信息
export RANK_TABLE_FILE=/home/tools/rank_table_8p_62.json
export RANK_SIZE=8
export DEVICE_NUM=8

#export NODEINFO_FILE=/home/tools/2node_6264.json
