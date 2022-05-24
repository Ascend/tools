export PYTHON_COMMAND=python3.7
export TRAIN_DATA_PATH=/home/datasets/Bert-Dataset/
export EVAL_DATA_PATH=/home/datasets/Bert-TestData/

export PRETRAIN_MODEL_PATH=/home/models/ms_bert_large.ckpt

export EPOCH_SIZE=5
export TRAIN_STEPS=12000

# 8p
export RANK_SIZE=8
export DEVICE_NUM=8

# options needed only if rank_size > 1
export RANK_TABLE_FILE=/home/lcm/tool/rank_table_8p.json

# needed only in cluster mode
# export NODEINFO_FILE=/home/lcm/tool/ssh64_66.json
