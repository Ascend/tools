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

# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "tensorflow_config")
source ${currentDir}/config/npu_set_env.sh

if [ x"$runmode" != x"evaluate" ];then
    currtime=`date +%Y%m%d%H%M%S`
    mkdir -p ${currentDir%train*}/train/result/tf_yolov3/training_job_${currtime}/
    train_job_dir=${currentDir%train*}/train/result/tf_yolov3/training_job_${currtime}/
    echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] ${train_job_dir} &"
fi


# device 列表, 若无指定 device 根据 rank_size 顺序选择
eval device_group=\$device_group_${rank_size}p
if [ x"${device_group}" == x"" ] || [ ${rank_size} -ge 8 ];then
    device_group="$(seq 0 "$(expr $rank_size - 1)")"
fi

# get last device id in device_group, hw log in performance from the dir named first_device_id
device_group_str=`echo ${device_group} | sed 's/ //g'`
first_device_id=`echo ${device_group_str: 0:1}`

argsFilePath=${currentDir}/code/args_${mode}.py

#echo "argsFilePath is "${argsFilePath}
sed -i "0,/batch_size.*$/s//batch_size\ = ${batch_size}/g" ${argsFilePath}
sed -i "s/save_epoch.*$/save_epoch\ = ${save_epoch}/g" ${argsFilePath}
sed -i "s/total_epoches =.*$/total_epoches\ = ${total_epoches}/g" ${argsFilePath}
sed -i 's/\r//g' ${argsFilePath}

if [ x"${CLUSTER}" == x"True" ];then
    # ln hw log
    ln -snf ${train_job_dir}/0/hw_yolov3.log ${train_job_dir}
    this_ip=$(hostname -I |awk '{print $1}')
    for ip in $MPIRUN_ALL_IP;do
        if [ x"$ip" != x"$this_ip" ];then
            scp $yamlPath root@$ip:$yamlPath
            scp $argsFilePath root@$ip:$argsFilePath
        fi
    done
    export PATH=$PATH:/usr/local/mpirun4.0/bin
    mpirun -H ${mpirun_ip} \
    --bind-to none -map-by slot\
    --allow-run-as-root \
    --mca btl_tcp_if_exclude lo,docker0,endvnic,virbr0,vethf40501b,docker_gwbridge,br-f42ac38052b4\
    --prefix /usr/local/mpirun4.0/ \
    ${currentDir}/scripts/train.sh 0 $rank_size $yamlPath $currtime ${toolsPath} ${CLUSTER}
elif [ $runmode == "train" ];then
    ln -snf ${train_job_dir}/${first_device_id}/hw_yolov3.log ${train_job_dir}
    rank_id=0
    for device_id in $device_group;do
      #echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] start: train ${device_id} & " >> ${currentDir}/result/main.log
      ${currentDir}/scripts/train.sh $device_id $rank_size $yamlPath $currtime ${toolsPath} $rank_id&
      let rank_id++
    done
else
    echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] ${ckpt_path} &"
    ln -snf ${train_job_dir}/${first_device_id}/hw_yolov3.log ${train_job_dir}
    bash ${currentDir}/scripts/eval.sh ${rank_size} ${ckpt_path}
fi

wait

#echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] all train exit " >> ${currentDir}/result/main.log

