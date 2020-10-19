#!/bin/bash
# 0 $currtime $yamlPath  0 cluster ${toolsPath}
device_id=$1
currtime=$2
yamlPath=$3
toolsPath=$6
rank_size=$7


export YAML_PATH=$3

mainDir=$(cd "$(dirname "$0")/.."; pwd)

mkdir -p ${mainDir%train*}/train/result/tf_bert_large/training_job_${currtime}/
export train_job_dir=${mainDir%train*}/train/result/tf_bert_large/training_job_${currtime}/


#exec_path=${train_job_dir}

cd ${train_job_dir}

export utilDir=$(cd "$(dirname "$yamlPath")/../atlas_benchmark-master/utils"; pwd)
export utilDir=$(cd "$(dirname "$yamlPath")/../atlas_benchmark-master/utils/atlasboost"; pwd)
source ${mainDir}/config/npu_set_env.sh


# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "tensorflow_config")

# 声明变量
export REMARK_LOG_FILE=hw_bert.log  # 打点日志文件名称， 必须hw_后跟模型名称小写
# 添加日志打点模块路径
benchmark_log_path=${mainDir%atlas_benchmark-master*}/atlas_benchmark-master/utils
export PYTHONPATH=$PYTHONPATH:${benchmark_log_path}

export JOB_ID=9999001
export RANK_TABLE_FILE=${mainDir}/config/${rank_size}p.json
export RANK_SIZE=${rank_size}

export SLOG_PRINT_TO_STDOUT=0
export DEVICE_ID=${device_id}
export DEVICE_INDEX=$DEVICE_ID
export RANK_INDEX=0

if [ ${PROFILING_MODE} == True ];
then
        export PROFILING_MODE=true
else
        export PROFILING_MODE=false
fi

if [ ${PROFILING_MODE} == True ];
then
        export AICPU_PROFILING_MODE=true
else
        export AICPU_PROFILING_MODE=false
fi
export PROFILING_OPTIONS=${PROFILING_OPTIONS}
export FP_POINT=${FP_POINT}
export BP_POINT=${BP_POINT}

if  [ x"${device_id}" = x ] ;
then
    echo "turing train fail" >> ${exec_path}/train_${device_id}.log
    exit
else
    export DEVICE_ID=${device_id}
fi


env > ${currentDir}/env_${device_id}.log

cd ${train_job_dir}

if [ x"$5" != x"True" ];then
        rank_id=$4
        export RANK_ID=$4
else
        device_id_mo=$(python3.7 -c "import src.tensorflow.mpi_ops as atlasboost;atlasboost.init(); \
                device_id = atlasboost.local_rank();cluster_device_id = str(device_id); \
                atlasboost.set_device_id(device_id);print(atlasboost.rank())")
        device_id_mo=`echo $device_id_mo`
        rank_id=${device_id_mo##* }
        #echo rank_id is $rank_id
        export RANK_ID=${rank_id}
        device=${device_id_mo##*deviceid = }
        device_id=${device%% phyid=*}
        export DEVICE_ID=${device_id}
        #echo device_id is $device_id
        hccljson=${train_job_dir}/*.json
        cp ${hccljson} ${mainDir}/config/${rank_size}p.json
fi
env > ${currentDir}/env_${device_id}.log
#mkdir exec path


mkdir -p ${train_job_dir}/${device_id}/ckpt${DEVICE_ID}
cd ${train_job_dir}/${device_id}

startTime=`date +%Y%m%d-%H:%M:%S`
startTime_s=`date +%s`


#start exec
python3.7 ${mainDir}/code/bert-Nv/run_pretraining.py \
    --bert_config_file=${mainDir}/config/${bert_config_file} \
    --max_seq_length=${max_seq_length} \
    --max_predictions_per_seq=${max_predictions_per_seq} \
    --train_batch_size=${train_batch_size} \
    --learning_rate=${learning_rate} \
    --num_warmup_steps=${num_warmup_steps} \
    --num_train_steps=${num_train_steps} \
    --optimizer_type=${optimizer_type} \
    --manual_fp16=${manual_fp16} \
    --use_fp16_cls=${use_fp16_cls} \
    --input_files_dir=${input_files_dir} \
    --eval_files_dir=${eval_files_dir} \
    --do_train=${do_train} \
    --do_eval=${do_eval} \
    --num_accumulation_steps=${num_accumulation_steps} \
    --npu_bert_job_start_file=None \
    --iterations_per_loop=${iterations_per_loop} \
    --npu_bert_loss_scale=${npu_bert_loss_scale} \
    --distributed=${distributed} \
    --graph_memory_max_size=${graph_memory_max_size} \
    --variable_memory_max_size=${variable_memory_max_size} \
    --npu_bert_tail_optimize=${npu_bert_tail_optimize} \
    --save_checkpoints_steps=${save_checkpoints_steps} \
    --npu_bert_clip_by_global_norm=${npu_bert_clip_by_global_norm} \
    --output_dir=${train_job_dir}/${device_id}/ckpt${DEVICE_ID} > ${train_job_dir}/train_${device_id}.log 2>&1


if [ $? -eq 0 ] ;then
    echo ":::ABK 1.0.0 bert train success"
    echo ":::ABK 1.0.0 bert train success" >> ${train_job_dir}/train_${device_id}.log
    echo ":::ABK 1.0.0 bert train success" >> ${train_job_dir}/${device_id}/hw_bert.log
else
    echo ":::ABK 1.0.0 bert train failed"
    echo ":::ABK 1.0.0 bert train failed" >> ${train_job_dir}/train_${device_id}.log
    echo ":::ABK 1.0.0 bert train failed" >> ${train_job_dir}/${device_id}/hw_bert.log
fi

endTime=`date +%Y%m%d-%H:%M:%S`
endTime_s=`date +%s`
sumTime=$[ $endTime_s - $startTime_s ]
hour=$(( $sumTime/3600 ))
min=$(( ($sumTime-${hour}*3600)/60 ))
sec=$(( $sumTime-${hour}*3600-${min}*60 ))
echo ":::ABK 1.0.0 bert train total time ${hour}:${min}:${sec}"
echo ":::ABK 1.0.0 bert train total time ${hour}:${min}:${sec}" >> ${train_job_dir}/${device_id}/hw_bert.log


