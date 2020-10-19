#!/usr/bin/env bash

yamlPath=$1
toolsPath=$2


currentDir=$(cd "$(dirname "$0")/.."; pwd)
export REMARK_LOG_FILE=hw_mobilenet.log
benchmark_log_path=${currentDir%atlas_benchmark-master*}/atlas_benchmark-master/utils
export PYTHONPATH=$PYTHONPATH:${benchmark_log_path}

eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "common_config")

cd ${ckpt_path%results*}/results
rm -rf ./hw_mobilenet.log
rm -rf ./eval.out

python3.7 ${currentDir}/code/eval_image_classifier_mobilenet.py --dataset_dir=${data_url} \
        --checkpoint_path=${ckpt_path}  > ./eval.out 2>&1

