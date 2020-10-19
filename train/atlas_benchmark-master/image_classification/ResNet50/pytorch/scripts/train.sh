#!/usr/bin/env bash

device_id=$1
rank_size=$2
yamlPath=$3
currtime=$4
toolsPath=$5

currentDir=$(cd "$(dirname "$0")/.."; pwd)

export REMARK_LOG_FILE=hw_resnet50.log

mkdir -p ${currentDir%train*}/train/result/pt_resnet50/training_job_${currtime}/
export train_job_dir=${currentDir%train*}/train/result/pt_resnet50/training_job_${currtime}/


source ${currentDir}/config/npu_set_env.sh


benchmark_log_path=${currentDir%atlas_benchmark-master*}/atlas_benchmark-master/utils
#atlasboost_path=${currentDir%atlas_benchmark-master*}/atlas_benchmark-master/utils/atlasboost
code_dir_path=${currentDir}/code
export PYTHONPATH=$PYTHONPATH:${benchmark_log_path}:${code_dir_path}

# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "pytorch_config")

# user env
export YAML_PATH=$3
export HCCL_CONNECT_TIMEOUT=600
export JOB_ID=9999001
#export HCCL_RANK_TABLE_PATH=${currentDir}/config/${rank_size}p.json
export RANK_SIZE=${rank_size}
export RANK_INDEX=0
export SLOG_PRINT_TO_STDOUT=0
export DEVICE_ID=$1
DEVICE_INDEX=$(( DEVICE_ID + RANK_INDEX * 8 ))
export DEVICE_INDEX=${DEVICE_INDEX}
export MODEL_CKPT_PATH=${train_job_dir}/${device_id}/ckpt${device_id}

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
    eval_data_url="--data=${data_url} --evaluate --resume=${ckpt_path}"
else
    eval_data_url="--data=${data_url}"
fi
if [ x"${rank_size}" == x"1" ];then
    python3.7 ${currentDir}/code/pytorch-resnet50-apex.py \
        ${eval_data_url} \
        --workers=64 \
        --epochs=${epoches} \
        --batch-size=${batch_size} \
        --learning-rate=${lr} \
        --warmup=5 \
        --label-smoothing=0.1 \
        --optimizer-batch-size=1024 \
        --npu=${device_id} > ${train_job_dir}/train_1p.log 2>&1

else
    export KERNEL_NAME_ID=${device_id}
    rank_id=$6
    python3.7 ${currentDir}/code/DistributedResnet50/main-apex-d76-npu.py \
        --data=${data_url} \
        --addr=$(hostname -I |awk '{print $1}') \
        --seed=49 \
        --workers=184 \
        --learning-rate=${lr} \
        --warmup=8 \
        --label-smoothing=0.1 \
        --mom=0.875 \
        --weight-decay=3.0517578125e-05 \
        --static-loss-scale=128 \
        --print-freq=1 \
        --dist-url='tcp://127.0.0.1:50000' \
        --dist-backend='hccl' \
        --multiprocessing-distributed \
        --world-size=1 \
        --rank=${rank_id} \
        --gpu=${device_id} \
        --benchmark=0 \
        --device='npu' \
        --epochs=${epoches} \
        --device_num=${rank_size} \
        --batch-size=${batch_size} > ${train_job_dir}/train_${rank_size}p.log 2>&1
fi

if [ $? -eq 0 ] ;
then
    echo ":::ABK 1.0.0 resnet50 train success"
    echo ":::ABK 1.0.0 resnet50 train success" >> ${train_job_dir}/train_${rank_size}p.log
    echo ":::ABK 1.0.0 resnet50 train success" >> ${train_job_dir}/${device_id}/hw_resnet50.log
else
    echo ":::ABK 1.0.0 resnet50 train failed"
    echo ":::ABK 1.0.0 resnet50 train failed" >>${train_job_dir}/train_${rank_size}p.log
    echo ":::ABK 1.0.0 resnet50 train failed" >> ${train_job_dir}/${device_id}/hw_resnet50.log
fi

endTime=`date +%Y%m%d-%H:%M:%S`
endTime_s=`date +%s`

sumTime=$[ $endTime_s - $startTime_s ]

hour=$(( $sumTime/3600 ))
min=$(( ($sumTime-${hour}*3600)/60 ))
sec=$(( $sumTime-${hour}*3600-${min}*60 ))
echo ":::ABK 1.0.0 resnet50 train total time：${hour}:${min}:${sec}"

echo ":::ABK 1.0.0 resnet50 train total time：${hour}:${min}:${sec}" >> ${train_job_dir}/${device_id}/hw_resnet50.log

