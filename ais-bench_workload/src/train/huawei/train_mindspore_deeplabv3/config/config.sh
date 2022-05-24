#!/bin/bash
export PYTHON_COMMAND=python3.7
export TRAIN_DATA_PATH=/home/datasets/vocaug
export TRAIN_DATA_FILE=/home/datasets/vocaug/vocaug_mindrecord/vocaug_mindrecord0
export PRETRAIN_MODEL_PATH=/home/datasets/pretrain_model/deeplabv3/resnet101_ascend_v120_imagenet2012_official_cv_bs32_acc78.ckpt
export EVAL_DATA_FILE_PATH=/home/datasets/vocaug/voc_val_lst.txt
export EPOCH_SIZE=200

export RANK_SIZE=8
export DEVICE_NUM=8

# need if rank_size > 1
export RANK_TABLE_FILE=/home/tools/rank_table_8p_64.json
# cluster need for node info
#export NODEINFO_FILE=/home/lcm/tool/ssh64_66.json

