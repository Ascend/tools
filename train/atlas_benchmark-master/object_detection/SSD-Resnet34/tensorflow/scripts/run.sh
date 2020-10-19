#!/bin/bash

rank_size=$1
yamlPath=$2

toolsPath=$3
if [ -f /.dockerenv ];then
        CLUSTER=$4
        MPIRUN_ALL_IP="$5"
        export CLUSTER=${CLUSTER}
fi

currentDir=$(cd "$(dirname "$0")/.."; pwd)
model_name=$(cd $currentDir/..;basename `pwd`)

# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "tensorflow_config")

#mkdir train job path
currtime=`date +%Y%m%d%H%M%S`
mkdir -p ${currentDir%train*}/train/result/tf_ssd_resnet34/training_job_${currtime}/
train_job_dir=${currentDir%train*}/train/result/tf_ssd_resnet34/training_job_${currtime}/
echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] ${train_job_dir} &"
jsonFilePath=${currentDir}/code/ssd_constants.py

echo "start to modify inner config file"
echo "jsonfilepath is "${jsonFilePath}

sed -i "s/EVAL_STEPS = (.*,)$/EVAL_STEPS = (${max_steps},)/g" ${jsonFilePath}

# device 列表, 若无指定 device 根据 rank_size 顺序选择
eval device_group=\$device_group_${rank_size}p
if [ x"${device_group}" == x"" ] || [ ${rank_size} -ge 8 ];then
    device_group="$(seq 0 "$(expr $rank_size - 1)")"
fi

# get last device id in device_group, hw log in performance from the dir named first_device_id  
device_group_str=`echo ${device_group} | sed 's/ //g'`
first_device_id=`echo ${device_group_str: 0:1}`

if [ x"${CLUSTER}" == x"True" ];then
    # ln hw log
    ln -snf ${train_job_dir}/0/hw_SSD-Resnet34.log ${train_job_dir}
    this_ip=$(hostname -I |awk '{print $1}')
    for ip in $MPIRUN_ALL_IP;do
        if [ x"$ip" != x"$this_ip" ];then
            scp $yamlPath root@$ip:$yamlPath
            scp $jsonFilePath root@$ip:$jsonFilePath
        fi
    done
    export PATH=$PATH:/usr/local/mpirun4.0/bin
    mpirun -H ${mpirun_ip} \
    --bind-to none -map-by slot\
    --allow-run-as-root \
    --mca btl_tcp_if_exclude lo,docker0,endvnic,virbr0,vethf40501b,docker_gwbridge,br-f42ac38052b4\
    --prefix /usr/local/mpirun4.0/ \
    ${currentDir}/scripts/train.sh 0 $rank_size $yamlPath $currtime ${toolsPath} ${CLUSTER}
else
    # ln hw log
    ln -snf ${train_job_dir}/${first_device_id}/hw_SSD-Resnet34.log ${train_job_dir}
    rank_id=0
    for device_id in $device_group;do
      ${currentDir}/scripts/train.sh $device_id $rank_size $yamlPath $currtime ${toolsPath} $rank_id &
      let rank_id++
    done
fi
wait

#echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] all train exit " >> ${currentDir}/result/main.log

