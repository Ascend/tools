#! /bin/bash

# Copyright (c) 2019 NVIDIA CORPORATION. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

export JOB_ID=1
export RANK_ID=0
export RANK_SIZE=1
export DEVICE_ID=0
export RANK_TABLE_FILE=./config/rank_table_1980intra_1rank.json
#export FUSION_TENSOR_SIZE=1000000000
export PYTHONPATH=${dir}:$PYTHONPATH

#export DUMP_GE_GRAPH=3

echo "Container nvidia build = " $NVIDIA_BUILD_ID

train_batch_size_phase1=${1:-16}
train_batch_size_phase2=${2:-8}
eval_batch_size=${3:-8}
learning_rate_phase1=${4:-"7.5e-4"}
learning_rate_phase2=${5:-"5e-4"}
precision=${6:-"fp16"}
use_xla=${7:-"false"}
warmup_steps_phase1=${9:-"2000"}
warmup_steps_phase2=${10:-"200"}
train_steps=${11:-7820}
save_checkpoints_steps=${12:-100}
num_accumulation_steps_phase1=${13:-1}
num_accumulation_steps_phase2=${14:-512}
bert_model=${15:-"large"}

DATA_DIR=${DATA_DIR:-data}
#Edit to save logs & checkpoints in a different directory
RESULTS_DIR=${RESULTS_DIR:-./results}

if [ "$bert_model" = "large" ] ; then
    export BERT_CONFIG=data/uncased_L-24_H-1024_A-16/bert_config.json
else
    export BERT_CONFIG=data/uncased_L-12_H-768_A-12/bert_config.json
fi

PREC=""
if [ "$precision" = "fp16" ] ; then
   PREC="--use_fp16"
elif [ "$precision" = "fp32" ] ; then
   PREC=""
elif [ "$precision" = "manual_fp16" ] ; then
   PREC="--manual_fp16"
else
   echo "Unknown <precision> argument"
   exit -2
fi

if [ "$use_xla" = "true" ] ; then
    PREC="$PREC --use_xla"
    echo "XLA activated"
fi

#PHASE 1

train_steps_phase1=$(expr $train_steps \* 9 \/ 10) #Phase 1 is 10% of training
gbs_phase1=$(expr $train_batch_size_phase1 \* $num_accumulation_steps_phase1)
seq_len=128
max_pred_per_seq=20
RESULTS_DIR_PHASE1=${RESULTS_DIR}/phase_1
mkdir -m 777 -p $RESULTS_DIR_PHASE1

INPUT_FILES="/opt/npu/bert-170-zhanghui/cn-news-128-f100"
EVAL_FILES="/opt/npu/bert-170-zhanghui/cn-news-128-f100"

#Check if all necessary files are available before training
for DIR_or_file in $DATA_DIR $RESULTS_DIR_PHASE1 $BERT_CONFIG; do
  if [ ! -d "$DIR_or_file" ] && [ ! -f "$DIR_or_file" ]; then
     echo "Error! $DIR_or_file directory missing. Please mount correctly"
     exit -1
  fi
done

python3 ./run_pretraining.py \
     --input_files_dir=$INPUT_FILES \
     --eval_files_dir=$EVAL_FILES \
     --output_dir=$RESULTS_DIR_PHASE1 \
     --bert_config_file=$BERT_CONFIG \
     --do_train=True \
     --train_batch_size=$train_batch_size_phase1 \
     --eval_batch_size=$eval_batch_size \
     --max_seq_length=$seq_len \
     --max_predictions_per_seq=$max_pred_per_seq \
     --num_train_steps=$train_steps_phase1 \
     --num_accumulation_steps=$num_accumulation_steps_phase1 \
     --num_warmup_steps=$warmup_steps_phase1 \
     --save_checkpoints_steps=$save_checkpoints_steps \
     --learning_rate=$learning_rate_phase1 \
     --optimizer_type=adam \
     --manual_fp16=True \
     --use_fp16_cls=True \
     --npu_bert_debug=False \
     --npu_bert_use_tdt=True \
     --npu_bert_clip_by_global_norm=False \
     --npu_bert_job_start_file="./config/deviceid_devindex_jobstart"
