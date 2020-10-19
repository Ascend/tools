#!/usr/bin/env bash

device_id=$1
rank_size=$2
yamlPath=$3
currentDir=$(cd "$(dirname "$0")/.."; pwd)
currtime=$4
toolsPath=$5

export YAML_PATH=$3
mkdir -p ${currentDir%train*}/train/result/pt_mobilenet/training_job_${currtime}/
export train_job_dir=${currentDir%train*}/train/result/pt_mobilenet/training_job_${currtime}/


# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "pytorch_config")
export REMARK_LOG_FILE=hw_mobilenet.log
benchmark_log_path=${currentDir%atlas_benchmark-master*}/atlas_benchmark-master/utils
export PYTHONPATH=$PYTHONPATH:${benchmark_log_path}


source ${currentDir}/config/set_env_b023.sh

# user env
export HCCL_CONNECT_TIMEOUT=600
export JOB_ID=9999001
export RANK_TABLE_FILE=${currentDir}/config/${rank_size}p.json
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
        echo rank_id is $rank_id
        export RANK_ID=${rank_id}
        device=${device_id_mo##*deviceid = }
        device_id=${device%% phyid=*}
        export DEVICE_ID=${device_id}
        echo device_id is $device_id
        hccljson=${train_job_dir}/*.json
        cp ${hccljson} ${currentDir}/config/${rank_size}p.json
fi

#mkdir exec path
mkdir -p ${train_job_dir}/${device_id}
cd ${train_job_dir}/${device_id}

startTime=`date +%Y%m%d-%H:%M:%S`
startTime_s=`date +%s`


if [ x"$6" == x"True" ];then
    python3.7 ${currentDir}/code/8p/mobilenetv2_8p_main.py \
        --addr=$(hostname -I |awk '{print $1}') \
        --seed 49  \
        --workers 128 \
        --lr 0.24 \
        --print-freq 1 \
        --eval-freq 5\
        --dist-url 'tcp://127.0.0.1:50002' \
        --dist-backend 'hccl' \
        --multiprocessing-distributed \
        --world-size 1 \
        --batch-size ${batch_size} \
        --epochs ${epoches} \
        --rank 0 \
        --amp \
        --benchmark 0 \
        --data ${data_url} > ${train_job_dir}/train_${rank_size}p.log 2>&1
elif [ x"${rank_size}" == x"1" ];then
    # 单卡
    python3.7 ${currentDir}/code/1p/main_apex.py \
		--workers 128 \
		--seed 123456 \
		--lr 0.03 \
		--amp \
		--opt-level 'O2' \
		--loss-scale-value 64 \
		--momentum 0.9 \
		--batch-size ${batch_size} \
		--weight-decay 1e-5 \
		--epoch ${epoches} \
		--print-freq 1 \
		--device ${device_single}\
		--eval-freq 1 \
		--summary-path './runs/mobilenetv2/npu_O2_ls64_c75b150_0909' \
		--data  ${data_url} > ${train_job_dir}/train_${rank_size}p.log 2>&1
elif [ ${rank_size} -le 8 ];then
    # 多卡单机
	python3.7 ${currentDir}/code/8p/mobilenetv2_8p_main_anycard.py \
        --addr=$(hostname -I |awk '{print $1}') \
        --seed 49  \
        --workers 128 \
        --lr ${lr} \
        --print-freq 1 \
        --loss-scale 64 \
        --eval-freq 1\
        --dist-url 'tcp://127.0.0.1:50002' \
        --dist-backend 'hccl' \
        --multiprocessing-distributed \
        --world-size 1 \
        --batch-size ${batch_size} \
        --epochs ${epoches} \
        --rank 0 \
        --amp \
	--device-list ${device_group_mutli} \
        --benchmark 0 \
        --data ${data_url} > ${train_job_dir}/train_${rank_size}p.log 2>&1
fi



if [ $? -eq 0 ];then
    echo ":::ABK 1.0.0 hw_mobilenet train success"
    echo ":::ABK 1.0.0 hw_mobilenet train success" >> ${train_job_dir}/train_${rank_size}p.log
    echo ":::ABK 1.0.0 hw_mobilenet train success" >> ./hw_mobilenet.log
else
    echo ":::ABK 1.0.0 hw_mobilenet train failed"
    echo ":::ABK 1.0.0 hw_mobilenet train failed" >> ${train_job_dir}/train_${rank_size}p.log
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
