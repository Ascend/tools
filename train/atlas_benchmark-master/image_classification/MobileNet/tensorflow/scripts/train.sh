#!/usr/bin/env bash

device_id=$1
rank_size=$2
yamlPath=$3
currentDir=$(cd "$(dirname "$0")/.."; pwd)
currtime=$4
toolsPath=$5

export YAML_PATH=$3
mkdir -p ${currentDir%train*}/train/result/tf_mobilenet/training_job_${currtime}/
export train_job_dir=${currentDir%train*}/train/result/tf_mobilenet/training_job_${currtime}/



# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "tensorflow_config")
export REMARK_LOG_FILE=hw_mobilenet.log
benchmark_log_path=${currentDir%atlas_benchmark-master*}/atlas_benchmark-master/utils
export PYTHONPATH=$PYTHONPATH:${benchmark_log_path}

source ${currentDir}/config/npu_set_env.sh

# user env
export HCCL_CONNECT_TIMEOUT=600
export JOB_ID=9999001
export RANK_TABLE_FILE=${currentDir}/config/${rank_size}p.json
export RANK_SIZE=${rank_size}
export SLOG_PRINT_TO_STDOUT=0
export DEVICE_ID=${device_id}
DEVICE_INDEX=$(( DEVICE_ID + RANK_INDEX * 8 ))
export DEVICE_INDEX=${DEVICE_INDEX}

if [ ${profiling_mode} == True ];
then
	export PROFILING_MODE=true
else
	export PROFILING_MODE=false
fi

if [ ${aicpu_profiling_mode} == True ];
then
	export AICPU_PROFILING_MODE=true
else
        export AICPU_PROFILING_MODE=false
fi

export PROFILING_OPTIONS=${profiling_options}
export FP_POINT=${fp_point}
export BP_POINT=${bp_point}



cd ${train_job_dir}
curd_dir=${currentDir%atlas_benchmark-master*}/atlas_benchmark-master/utils/atlasboost
export PYTHONPATH=$PYTHONPATH:${curd_dir}

if [ x"$6" != x"True" ];then
        rank_id=$6
        export RANK_ID=$6
else
        device_id_mo=$(python3.7 -c "import src.tensorflow.mpi_ops as atlasboost;atlasboost.init(); \
                device_id = atlasboost.local_rank();cluster_device_id = str(device_id); \
                atlasboost.set_device_id(device_id);print(atlasboost.rank())")
        device_id_mo=`echo $device_id_mo`
        rank_id=${device_id_mo##* }
        export RANK_ID=${rank_id}
        device=${device_id_mo##*deviceid = }
        device_id=${device%% phyid=*}
        export DEVICE_ID=${device_id}
        hccljson=${train_job_dir}/*.json
        cp ${hccljson} ${currentDir}/config/${rank_size}p.json
fi

#mkdir exec path
mkdir -p ${train_job_dir}/${device_id}
cd ${train_job_dir}/${device_id}

startTime=`date +%Y%m%d-%H:%M:%S`
startTime_s=`date +%s`

if [ x"${mode}" == x"evaluate" ];then
    # 评测
    python3.7 ${currentDir}/code/eval_image_classifier_mobilenet.py \
        --checkpoint_path="${ckpt_path}" \
        --dataset_dir=${data_url} > ./train.log 2>&1
else
    # 根据单卡/多卡区分调用参数
    if [ x"$6" == x"True" ];then
        export CLUSTER=True
        python3.7 ${currentDir}/code/train.py \
            --dataset_dir=${data_url} \
            --max_epoch=${epoches} \
            --model_name="mobilenet_v2" \
            --moving_average_decay=0.9999 \
            --label_smoothing=0.1 \
            --preprocessing_name="inception_v2" \
            --weight_decay='0.00004' \
            --batch_size=${batch_size} \
            --learning_rate_decay_type='cosine_annealing' \
            --learning_rate=0.8 \
            --optimizer='momentum' \
            --momentum='0.9' \
            --warmup_epochs=5 > ${train_job_dir}/train_${device_id}.log 2>&1
    elif [ x"${rank_size}" == x"1" ];then
        # 单卡
        python3.7 ${currentDir}/code/train.py \
            --dataset_dir=${data_url} \
            --max_train_steps=${max_steps} \
            --iterations_per_loop=50 \
            --model_name="mobilenet_v2" \
            --moving_average_decay=0.9999 \
            --label_smoothing=0.1 \
            --preprocessing_name="inception_v2" \
            --weight_decay='0.00004' \
            --batch_size=${batch_size} \
            --learning_rate_decay_type='cosine_annealing' \
            --learning_rate=0.4 \
            --optimizer='momentum' \
            --momentum='0.9' \
            --warmup_epochs=5 > ${train_job_dir}/train_${device_id}.log 2>&1
    elif [ ${rank_size} -le 8 ];then
        # 多卡单机
        python3.7 ${currentDir}/code/train.py \
            --dataset_dir=${data_url} \
            --max_epoch=${epoches} \
            --model_name="mobilenet_v2" \
            --moving_average_decay=0.9999 \
            --label_smoothing=0.1 \
            --preprocessing_name="inception_v2" \
            --weight_decay='0.00004' \
            --batch_size=${batch_size} \
            --learning_rate_decay_type='cosine_annealing' \
            --learning_rate=0.8 \
            --optimizer='momentum' \
            --momentum='0.9' \
            --warmup_epochs=5 > ${train_job_dir}/train_${device_id}.log 2>&1
    fi
fi

if [ $? -eq 0 ];then
    echo ":::ABK 1.0.0 hw_mobilenet train success"
    echo ":::ABK 1.0.0 hw_mobilenet train success" >> ${train_job_dir}/train_${device_id}.log 2
    echo ":::ABK 1.0.0 hw_mobilenet train success" >> ./hw_mobilenet.log
else
    echo ":::ABK 1.0.0 hw_mobilenet train failed"
    echo ":::ABK 1.0.0 hw_mobilenet train failed" >> ${train_job_dir}/train_${device_id}.log 2
    echo ":::ABK 1.0.0 hw_mobilenet train failed" >> ./hw_mobilenet.log
fi

endTime=`date +%Y%m%d-%H:%M:%S`
endTime_s=`date +%s`

sumTime=$[ $endTime_s - $startTime_s ]

hour=$(( $sumTime/3600 ))
min=$(( ($sumTime-${hour}*3600)/60 ))
sec=$(( $sumTime-${hour}*3600-${min}*60 ))
echo ":::ABK 1.0.0 mobilenet train total time：${hour}:${min}:${sec}"

echo ":::ABK 1.0.0 mobilenet train total time： ${hour}:${min}:${sec}" >> ./hw_mobilenet.log
