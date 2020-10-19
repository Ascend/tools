#!/usr/bin/env bash

device_id=$1
rank_size=$2
yamlPath=$3

currentDir=$(cd "$(dirname "$0")/.."; pwd)
currtime=$4
toolsPath=$5
export YAML_PATH=$3
mkdir -p ${currentDir%train*}/train/result/pt_deepmar/training_job_${currtime}/
export train_job_dir=${currentDir%train*}/train/result/pt_deepmar/training_job_${currtime}/

# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "pytorch_config")

export REMARK_LOG_FILE=hw_deepmar.log  # 打点日志文件名称， 必须hw_后跟模型名称小写
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

# 数据集预处理
python3.7 ${currentDir}/code/transform_peta.py \
	--save_dir=${data_url} \
	--traintest_split_file=${data_url}/peta_partition.pkl

# 根据单卡/多卡区分调用参数
if [ x"$6" == x"True" ];then
    # 多卡多机
    export CLUSTER=True
fi

if [ x"${mode}" == x"evaluate" ];then
    pass


elif [ x"${rank_size}" == x"1" ];then
    # 单卡
	python3.7 ${currentDir}/code/train_deepmar_resnet50.py \
    --dataset=peta \
    --save_dir=${data_url} \
    --workers=32 \
    --npu=${device} \
    --partition_idx=0 \
    --split=trainval \
    --test_split=test \
    --batch_size=${batch_size} \
    --resize="(224,224)" \
    --exp_subpath=deepmar_resnet50 \
    --new_params_lr=0.01 \
    --finetuned_params_lr=0.01 \
    --staircase_decay_at_epochs="(50,100)" \
    --total_epochs=${epoches} \
    --epochs_per_val=10 \
    --epochs_per_save=50 \
    --steps_per_log=10 \
    --drop_pool5=True \
    --drop_pool5_rate=0.5 \
    --run=1 \
    --resume=False \
    --ckpt_file= \
    --load_model_weight=False \
    --model_weight_file= \
    --amp \
    --opt_level O2 \
    --loss_scale 512 \
    --set_seed True \
    --pretrained True \
    --test_only=False > ${train_job_dir}/train_${rank_size}p.log 2>&1

elif [ ${rank_size} -le 8 ];then
    # 单机多卡
    #source ${currentDir}/config/set_env_b023.sh
    python3.7 ${currentDir}/code/train_deepmar_resnet50_8p.py \
    --addr=$(hostname -I |awk '{print $1}') \
    --save_dir=${data_url} \
    --dataset=peta \
    --workers=80 \
    --partition_idx=0 \
    --split=trainval \
    --test_split=test \
    --batch_size=${batch_size} \
    --resize="(224,224)" \
    --exp_subpath=deepmar_resnet50 \
    --new_params_lr=${lr} \
    --finetuned_params_lr=${lr} \
    --staircase_decay_at_epochs="(50,100)" \
    --total_epochs=${epoches} \
    --epochs_per_val=10 \
    --epochs_per_save=50 \
    --steps_per_log=10 \
    --drop_pool5=True \
    --drop_pool5_rate=0.5 \
    --run=1 \
    --resume=False \
    --ckpt_file= \
    --load_model_weight=False \
    --model_weight_file=ckpt_epoch101.pth\
    --amp \
    --opt_level O2 \
    --loss_scale 512.0 \
    --set_seed True \
    --pretrained True \
    --test_only=False \
    --dist_url 'tcp://127.0.0.1:50000' \
    --dist_backend 'hccl' \
    --multiprocessing_distributed \
    --world_size 1 \
    --npus_per_node=${rank_size} \
    --rank 0 > ${train_job_dir}/train_${rank_size}p.log 2>&1


fi

#taskset -c 0-20 python3.7 ${currentDir}/code/densenet121.py > ./train.log 2>&1

if [ $? -eq 0 ];then
    echo ":::ABK 1.0.0 deepmar train success"
    echo ":::ABK 1.0.0 deepmar train success" >> ${train_job_dir}/train_${rank_size}p.log
    echo ":::ABK 1.0.0 deepmar train success" >> ./hw_deepmar.log
else
    echo ":::ABK 1.0.0 deepmar train success"
    echo ":::ABK 1.0.0 deepmar train failed" >> ${train_job_dir}/train_${rank_size}p.log
    echo ":::ABK 1.0.0 deepmar train failed" >> ./hw_deepmar.log
fi

endTime=`date +%Y%m%d-%H:%M:%S`
endTime_s=`date +%s`
sumTime=$[ $endTime_s - $startTime_s ]
hour=$(( $sumTime/3600 ))
min=$(( ($sumTime-${hour}*3600)/60 ))
sec=$(( $sumTime-${hour}*3600-${min}*60 ))
echo ":::ABK 1.0.0 deepmar train total time： ${hour}:${min}:${sec}" >> ${train_job_dir}/${device_id}/hw_deepmar.log
