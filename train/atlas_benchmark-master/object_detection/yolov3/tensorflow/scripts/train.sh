#!/bin/bash
scriptDir=$(cd "$(dirname "$0")"; pwd)
mainDir=$(cd "$(dirname "$scriptDir")"; pwd)

device_id=$1
rank_size=$2
yamlPath=$3
currentDir=$(cd "$(dirname "$0")/.."; pwd)
currtime=$4
toolsPath=$5
export YAML_PATH=$3
mkdir -p ${currentDir%train*}/train/result/tf_yolov3/training_job_${currtime}/
export train_job_dir=${currentDir%train*}/train/result/tf_yolov3/training_job_${currtime}/



# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "tensorflow_config")


source ${currentDir}/config/npu_set_env.sh
# 声明变量
export REMARK_LOG_FILE=hw_yolov3.log  # 打点日志文件名称， 必须hw_后跟模型名称小写
# 添加日志打点模块路径
benchmark_log_path=${currentDir%atlas_benchmark-master*}/atlas_benchmark-master/utils
export PYTHONPATH=$PYTHONPATH:${benchmark_log_path}

# user env
export HCCL_CONNECT_TIMEOUT=600
export RANK_TABLE_FILE=${currentDir}/config/${rank_size}p.json
export RANK_SIZE=${rank_size}
export SLOG_PRINT_TO_STDOUT=0
export DEVICE_ID=${device_id}
export DEVICE_INDEX=${DEVICE_INDEX}
export DEVICE_INDEX=$RANK_ID
export JOB_ID=123678
export FUSION_TENSOR_SIZE=1000000000


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

num_cpus=$(getconf _NPROCESSORS_ONLN)
num_cpus_per_device=$((num_cpus/8))
PID_START=$((num_cpus_per_device*device_id))
PID_END=$((num_cpus_per_device*device_id+num_cpus_per_device-1))

startTime=`date +%Y%m%d-%H:%M:%S`
startTime_s=`date +%s`

#KERNEL_NUM=20
#PID_START=$((KERNEL_NUM * DEVICE_ID))
#PID_END=$((PID_START + KERNEL_NUM - 1))

#sleep 5
taskset -c  $PID_START-$PID_END python3.7 $mainDir/code/train.py --mode $mode > ${train_job_dir}/train_${device_id}.log 2>&1

if [ $? -eq 0 ] ;then
    echo ":::ABK 1.0.0 yolov3 train success"
    echo ":::ABK 1.0.0 yolov3 train success" >> ${train_job_dir}/train_${device_id}.log
    echo ":::ABK 1.0.0 yolov3 train success" >> ${train_job_dir}/${device_id}/hw_yolov3.log
else
    echo ":::ABK 1.0.0 yolov3 train failed"
    echo ":::ABK 1.0.0 yolov3 train failed" >> ${train_job_dir}/train_${device_id}.log
    echo ":::ABK 1.0.0 yolov3 train failed" >> ${train_job_dir}/${device_id}/hw_yolov3.log
fi

endTime=`date +%Y%m%d-%H:%M:%S`
endTime_s=`date +%s`
sumTime=$[ $endTime_s - $startTime_s ]
hour=$(( $sumTime/3600 ))
min=$(( ($sumTime-${hour}*3600)/60 ))
sec=$(( $sumTime-${hour}*3600-${min}*60 ))
echo ${hour}:${min}:${sec}
echo ":::ABK 1.0.0 yolov3 train total time ${hour}:${min}:${sec}" >> ${train_job_dir}/${device_id}/hw_yolov3.log
