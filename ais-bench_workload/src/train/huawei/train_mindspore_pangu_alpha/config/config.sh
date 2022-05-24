#!/bin/bash
export PYTHON_COMMAND=python3.7
export TRAIN_DATA_PATH=/home/datasets/pangu_30_step_ba64
export PARAM_INIT_TYPE=fp32
export MODE=2.6B
export STAGE_NUM=1
export MICRO_SIZE=1
export PER_BATCH=8

export RANK_SIZE=8
export DEVICE_NUM=8

# need if rank_size > 1
export RANK_TABLE_FILE=/home/tools/rank_table_8p_64.json
# cluster need for node info
#export NODEINFO_FILE=/home/lcm/tool/ssh64_66.json

