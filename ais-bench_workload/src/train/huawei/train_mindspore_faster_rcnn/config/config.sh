#!/bin/bash
export PYTHON_COMMAND=python3.7
export TRAIN_DATA_PATH=/home/datasets/coco
export MINDRECORD_PATH=/home/datasets/coco/mindrecord_coco_train
export PRETRAIN_MODEL_PATH=/home/datasets/pretrain_model/faster_rcnn/pretrained_model.ckpt
export VALIDATION_JSON_FILE=/home/datasets/coco/annotations/instances_val2017.json
export EPOCH_SIZE=20

export RANK_SIZE=8
export DEVICE_NUM=8

# need if rank_size > 1
export RANK_TABLE_FILE=/home/tools/rank_table_8p_66.json
# cluster need for node info
#export NODEINFO_FILE=/home/lcm/tool/ssh64_66.json

