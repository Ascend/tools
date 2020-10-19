#!/bin/bash

rank_size=$1
yamlPath=$2
toolsPath=$3
currentDir=$(cd "$(dirname "$0")/.."; pwd)
if [ -f /.dockerenv ];then
        CLUSTER=$4
		MPIRUN_ALL_IP="$5"
        export CLUSTER=${CLUSTER}
fi
#export RANK_ID=npu${rank_size}p

# 从 yaml 获取配置
eval $(${toolsPath}/get_params_for_yaml.sh ${yamlPath} "tensorflow_config")

data_url_new=`echo ${data_url//\//\\\\/}`
echo ${data_url}
echo ${max_steps}
echo ${epoches}
if [ x"${CLUSTER}" == x"True" ];then
    jsonFilePath=${currentDir}/code/resnext50_train/configs/res50_32bs_8p.py
elif [ ${rank_size} -lt 8 ];then
    jsonFilePath=${currentDir}/code/resnext50_train/configs/res50_32bs_1p.py
    if [ ${rank_size} -eq 1 ];then
        sed -i "0,/rank_size.*$/s//rank_size\': ${rank_size},/" ${jsonFilePath}

    elif [ ${rank_size} -eq 2 ];then
        sed -i "0,/rank_size.*$/s//rank_size\': ${rank_size},/" ${jsonFilePath}
    else
        sed -i "0,/rank_size.*$/s//rank_size\': ${rank_size},/" ${jsonFilePath}
    fi
        
else
    jsonFilePath=${currentDir}/code/resnext50_train/configs/res50_32bs_8p.py
    if [ ${rank_size} -eq 8 ];then
        sed -i "0,/rank_size.*$/s//rank_size\': ${rank_size},/" ${jsonFilePath}
    else
        rank_size=16
        sed -i "0,/rank_size.*$/s//rank_size\': ${rank_size},/" ${jsonFilePath}
    fi
fi

#echo "jsonfilepath is "${jsonFilePath}
sed -i "s/data_url.*$/data_url\': \'${data_url_new}\',/g" ${jsonFilePath}
#sed -i "s/max_train_steps.*$/max_train_steps\': ${max_steps},/g" ${jsonFilePath}
sed -i "s/num_epochs.*$/num_epochs\': ${epoches},/g" ${jsonFilePath}
sed -i "0,/batch_size.*$/s//batch_size\': ${batch_size},/" ${jsonFilePath}
sed -i "s/epochs_between_evals.*$/epochs_between_evals\': ${epochs_between_evals},/g" ${jsonFilePath}
sed -i 's/\r//g' ${jsonFilePath}


currtime=`date +%Y%m%d%H%M%S`
mkdir -p ${currentDir%train*}/train/result/tf_resnext50/training_job_${currtime}/
train_job_dir=${currentDir%train*}/train/result/tf_resnext50/training_job_${currtime}/
echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] ${train_job_dir} &"
# device 列表, 若无指定 device 或大于等于 8p 时根据 rank_size 顺序选择
eval device_group=\$device_group_${rank_size}p
if [ x"${device_group}" == x"" ] || [ ${rank_size} -ge 8 ];then
    device_group="$(seq 0 "$(expr $rank_size - 1)")"
fi

# get last device id in device_group, hw log in performance from the dir named last_device_id  
device_group_str=`echo ${device_group} | sed 's/ //g'`
first_device_id=`echo ${device_group_str: 0:1}`
echo ${device_group_str}
echo ${first_device_id}

rank_id=0

if [ x"${CLUSTER}" == x"True" ];then
    # ln hw log
    ln -snf ${currentDir%train*}/train/result/tf_resnext50/training_job_${currtime}/0/hw_resnext50.log ${currentDir%train*}/train/result/tf_resnext50/training_job_${currtime}/
    this_ip=$(hostname -I |awk '{print $1}')
    for ip in $MPIRUN_ALL_IP;do
        if [ x"$this_ip" != x"$ip" ];then
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
    ln -snf ${currentDir%train*}/train/result/tf_resnext50/training_job_${currtime}/${first_device_id}/hw_resnext50.log ${currentDir%train*}/train/result/tf_resnext50/training_job_${currtime}/
    for device_id in $device_group;do
      #echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] start: train ${device_id} & " >> ${currentDir}/result/main.log
      ${currentDir}/scripts/train.sh $device_id $rank_size $yamlPath $currtime ${toolsPath} $rank_id&
      let rank_id++
    done
fi
wait


