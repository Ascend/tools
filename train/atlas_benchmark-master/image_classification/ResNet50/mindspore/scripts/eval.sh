#!/usr/bin/env bash

yamlPath=$1
toolsPath=$2
currtime=$3
currentDir=$(cd "$(dirname "$0")/.."; pwd)
train_job_dir=${currentDir%train*}/train/result/ms_resnet50/training_job_${currtime}
mkdir -p ${currentDir%train*}/train/result/ms_resnet50/training_job_${currtime}/

source ${currentDir}/config/npu_set_env.sh

export REMARK_LOG_FILE=hw_resnet50.log
benchmark_log_path=${currentDir%atlas_benchmark-master*}/atlas_benchmark-master/utils
export PYTHONPATH=$PYTHONPATH:${benchmark_log_path}

eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "mindspore_config")

device_id=${eval_device_id}
export DEVICE_NUM=1
export DEVICE_ID=${device_id}
export RANK_SIZE=${DEVICE_NUM}
export RANK_ID=${device_id}



python3.7 ${currentDir}/code/eval.py \
    --net=resnet50 \
    --dataset=imagenet2012 \
    --dataset_path=${data_url} \
    --checkpoint_path=${checkpoint_path}  > ${train_job_dir}/eval.out 2>&1
