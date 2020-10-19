#!/usr/bin/env bash

rank_size=$1
yamlPath=$2
toolsPath=$3
if [ -f /.dockerenv ];then
        CLUSTER=$4
		MPIRUN_ALL_IP="$5"
        export CLUSTER=${CLUSTER}
fi

currentDir=$(cd "$(dirname "$0")/.."; pwd)

source ${currentDir}/config/npu_set_env.sh

eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "pytorch_config")


rm -rf /var/log/npu/slog/host-0/*
currtime=`date +%Y%m%d%H%M%S`
mkdir -p ${currentDir%train*}/train/result/pt_mobilenet/training_job_${currtime}/
train_job_dir=${currentDir%train*}/train/result/pt_mobilenet/training_job_${currtime}/

echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] ${train_job_dir}"
# device 列表, 若无指定 device 或大于等于 8p 时根据 rank_size 顺序选择
eval device_group=\$device_group_${rank_size}p
if [ x"${device_group}" == x"" ] || [ ${rank_size} -ge 8 ];then
    device_group="$(seq 0 "$(expr $rank_size - 1)")"
fi

device_group_str=`echo ${device_group} | sed 's/ //g'`
first_device_id=`echo ${device_group_str: 0:1}`

rank_id=0

if [ x"${CLUSTER}" == x"True" ];then
    ln -snf ${currentDir%train*}/train/result/pt_mobilenet/training_job_${currtime}/0/hw_mobilenet.log ${currentDir%train*}/train/result/pt_mobilenet/training_job_${currtime}/
	this_ip=$(hostname -I |awk '{print $1}')
    for ip in $MPIRUN_ALL_IP;do
        if [ x"$this_ip" != x"$ip" ];then
           scp $yamlPath root@$ip:$yamlPath
           scp $jsonFilePath root@$ip:$jsonFilePath
        fi
    done
    export PATH=$PATH:/usr/local/mpirun4.0.2/bin
    mpirun -H ${mpirun_ip} \
    --bind-to none -map-by slot\
    --allow-run-as-root \
    --mca btl_tcp_if_exclude lo,docker0,endvnic,virbr0,vethf40501b,docker_gwbridge,br-f42ac38052b4\
    --prefix /usr/local/mpirun4.0.2/ \
    ${currentDir}/scripts/train.sh 0 $rank_size $yamlPath $currtime ${toolsPath} ${CLUSTER}
else
    ln -snf ${currentDir%train*}/train/result/pt_mobilenet/training_job_${currtime}/${first_device_id}/hw_mobilenet.log ${currentDir%train*}/train/result/pt_mobilenet/training_job_${currtime}/
    #for device_id in $device_group;do
      #echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] start: train ${device_id} & " >> ${currentDir}/result/main.log
    ${currentDir}/scripts/train.sh 0 $rank_size $yamlPath $currtime ${toolsPath} $rank_id&
	  #let rank_id++
    #done
fi
wait
