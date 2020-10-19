#!/usr/bin/env bash

device_id=$1
rank_size=$2
yamlPath=$3

currentDir=$(cd "$(dirname "$0")/.."; pwd)
currtime=$4
toolsPath=$5
export YAML_PATH=$3
mkdir -p ${currentDir%train*}/train/result/pt_efficientnet/training_job_${currtime}/
export train_job_dir=${currentDir%train*}/train/result/pt_efficientnet/training_job_${currtime}/

# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "pytorch_config")

export REMARK_LOG_FILE=hw_efficientnet.log  # 打点日志文件名称， 必须hw_后跟模型名称小写
benchmark_log_path=${currentDir%atlas_benchmark-master*}/atlas_benchmark-master/utils
export PYTHONPATH=$PYTHONPATH:${benchmark_log_path}


#source ${currentDir}/config/npu_set_env.sh
source ${currentDir}/config/set_env_b023.sh
# user env
export HCCL_CONNECT_TIMEOUT=600
export JOB_ID=9999001
export HCCL_RANK_TABLE_PATH=${currentDir}/config/${rank_size}p.json
export RANK_SIZE=${rank_size}
export SLOG_PRINT_TO_STDOUT=0
export DEVICE_ID=${device_id}
DEVICE_INDEX=$(( DEVICE_ID + RANK_INDEX * 8 ))
export DEVICE_INDEX=${DEVICE_INDEX}

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


# 根据单卡/多卡区分调用参数
if [ x"$6" == x"True" ];then
    # 多卡多机
    export CLUSTER=True
fi

if [ x"${mode}" == x"evaluate" ];then
    pass


elif [ x"${rank_size}" == x"1" ];then
    # 单卡
	taskset -c 0-128 python3.7 ${currentDir}/code/examples/imagenet/main.py \
	--data=${data_url} \
	--arch=efficientnet-b0 \
	--batch-size=${batch_size} \
    --lr=0.2 \
    --momentum=0.9 \
	--epochs=${epoches} \
    --autoaug \
	--amp \
    --pm=O1 \
    --loss_scale=128 \
    --val_feq=10 \
    --npu=${device} > ${train_job_dir}/train_${rank_size}p.log 2>&1


elif [ ${rank_size} -le 8 ];then
    # 单机多卡
    taskset -c 0-128 python3.7 ${currentDir}/code/examples/imagenet/main.py \
    --data=${data_url} \
    --arch=efficientnet-b0 \
    --batch-size=${batch_size} \
    --lr=${lr} \
    --momentum=0.9 \
    --epochs=${epoches} \
    --autoaug \
	--amp \
    --pm=O1 \
    --loss_scale=128 \
    --val_feq=10 \
    --addr=$(hostname -I |awk '{print $1}') \
    --dist-backend=hccl \
    --multiprocessing-distributed \
    --world-size 1 \
    --rank 0 \
    --device_list ${device_group} > ${train_job_dir}/train_${rank_size}p.log 2>&1


fi

#taskset -c 0-20 python3.7 ${currentDir}/code/efficientnet.py > ./train.log 2>&1

if [ $? -eq 0 ];then
    echo ":::ABK 1.0.0 efficientnet train success"
    echo ":::ABK 1.0.0 efficientnet train success" >> ${train_job_dir}/train_${rank_size}p.log
    echo ":::ABK 1.0.0 efficientnet train success" >> ./hw_efficientnet.log
else
    echo ":::ABK 1.0.0 efficientnet train failed"
    echo ":::ABK 1.0.0 efficientnet train failed" >> ${train_job_dir}/train_${rank_size}p.log
    echo ":::ABK 1.0.0 efficientnet train failed" >> ./hw_efficientnet.log
fi

endTime=`date +%Y%m%d-%H:%M:%S`
endTime_s=`date +%s`
sumTime=$[ $endTime_s - $startTime_s ]
hour=$(( $sumTime/3600 ))
min=$(( ($sumTime-${hour}*3600)/60 ))
sec=$(( $sumTime-${hour}*3600-${min}*60 ))
echo ":::ABK 1.0.0 efficientnet train total time： ${hour}:${min}:${sec}" >> ${train_job_dir}/${device_id}/hw_efficientnet.log
