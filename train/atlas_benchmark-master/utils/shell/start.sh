#!/bin/bash


model=$1
hardware=$2
yamlPath=$3
modelDir=$4
framework=$5

modelScripts="$modelDir/scripts"

currentDir=$(cd "$(dirname "$0")"; pwd)
yamlDir=$(cd "$(dirname "${yamlPath}")";pwd)
train_dir=${currentDir%train*}/train
timeout=360000
# 从 yaml 获取配置
if [ x"${framework}" == x"tensorflow" ]; then
    config_section="tensorflow_config"
elif [ x"${framework}" == x"pytorch" ]; then
    config_section="pytorch_config"
else
    config_section="mindspore_config"
fi
eval $(${currentDir}/get_params_for_yaml.sh ${yamlPath} ${config_section})

if [ x"${hardware}" == x"cluster" ];then
    export CLUSTER=True
    IFS=","
    array=($mpirun_ip)
    m=${array[0]#*:}
    rank_size=0
    mpirun_all_ip=""
    for var in ${array[@]}; do
        n=${var#*:}
        mpirun_all_ip+=" ${var%:*}"
        let a="$n & ($n-1)"
        let rank_size+=$n
        if [ $a -ne 0 ] || [ $n -ne $m ];then
            echo "mpirun_ip: $mpirun_ip error"
            exit 1
        fi
    done
    export MPIRUN_ALL_IP=${mpirun_all_ip#?}
else
    rank_size=${hardware%?}
fi

eval device_group=\$device_group_${rank_size}p
if [ x"${device_group}" == x"" ] || [ ${rank_size} -ge 8 ];then
    device_group="$(seq 0 "$(expr $rank_size - 1)")"
fi

#tensorflow docker时要映射的路径
if [ x"${framework}" == x"tensorflow" ]; then
    if [ x"${hardware}" != x"cluster" ];then
	# 仅单机执行需要配置 json
        bash ${currentDir}/set_json.sh ${rank_size} ${yamlPath} ${modelDir} ${config_section} || exit 1
    fi
    yaml_file_name=${yamlPath##*/}
    train_model_name=${yaml_file_name%%.*}
    if [ x"${train_model_name}" == x"Bert-Base" ] || [ x"${train_model_name}" == x"Bert-Large" ]; then
        data_urls="-v ${input_files_dir}:${input_files_dir} -v ${eval_files_dir}:${eval_files_dir}"
    elif [ x"${train_model_name}" == x"MobileNet" ] || [ x"${train_model_name}" == x"YoLoV3" ]; then
        data_urls="-v ${data_url}:${data_url} -v ${ckpt_path}:${ckpt_path}"
    elif [ x"${train_model_name}" == x"SSD-Resnet34" ]; then
        raw_data=${training_file_pattern%raw_data*}raw_data
        data_urls="-v ${raw_data}:${raw_data}"
    else
        data_urls="-v ${data_url}:${data_url}"
    fi
fi


if [ x"${framework}" == x"pytorch" ]; then
    if [ x"${train_model_name}" == x"ResNet50" ]; then
        data_urls="-v ${data_url}:${data_url} -v ${ckpt_path}:${ckpt_path}"
    else
        data_urls="-v ${data_url}:${data_url}"
    fi
fi


if [ x"$model" == x"docker" ];then
    # docker 侧执行
    if [ x"${hardware}" == x"cluster" ];then
        # docker多机
        docker exec -i mpirun /bin/bash -c "${modelScripts}/run.sh ${rank_size} ${yamlPath} ${currentDir} ${CLUSTER} '${MPIRUN_ALL_IP}'" &
    else
        DEVICE_DEV=""
        for device_id in $device_group;do
            DEVICE_DEV=`echo "${DEVICE_DEV}" --device=/dev/davinci${device_id}`
        done
        docker run -i --ipc=host \
        ${DEVICE_DEV} --device=/dev/davinci_manager \
        --device=/dev/devmm_svm --device=/dev/hisi_hdc \
        -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
        -v /usr/local/Ascend/add-ons/:/usr/local/Ascend/add-ons/ \
        -v ${train_dir}:${train_dir} \
        -v ${modelDir}:${modelDir}  \
        ${data_urls} \
        -v ${yamlDir}:${yamlDir}  \
        -v /var/log/npu/conf/slog/slog.conf:/var/log/npu/conf/slog/slog.conf \
        -v /var/log/npu/slog/:/var/log/npu/slog -v /var/log/npu/profiling/:/var/log/npu/profiling \
        -v /var/log/npu/dump/:/var/log/npu/dump -v /var/log/npu/:/usr/slog ${docker_image} \
        /bin/bash -c "${modelScripts}/run.sh ${rank_size} ${yamlPath} ${currentDir}" &
    fi
elif [ x"$model" == x"host" ]; then
    # host 侧执行
    bash ${modelScripts}/run.sh ${rank_size} ${yamlPath} ${currentDir} &
fi
workshell=$!
timeused=0
while true
do
    ret=`ps -ef | grep ${modelScripts}/run.sh | grep ${workshell} | grep -v grep`
    if [ x"${ret}" = x ];
    then
        break
    else
        echo "[`date +%Y%m%d-%H:%M:%S`] [INFO] train job is working, wait more 5s "
        sleep 5
        let timeused+=5
        #如果超过配置的timeout时间，则kill 掉python训练进程
        if [ ${timeused} -gt ${timeout} ];
        then
          echo "[`date +%Y%m%d-%H:%M:%S`] [ERROR] training  timeout ! "
          #获取python进程ID
          train_sh_pid=`pgrep -P $(pgrep -P $workshell)`
          for pid in $train_sh_pid
          do
            id=`pgrep -P $pid`
            kill -9 $id
          done
          break
        fi
    fi
done

echo "[`date +%Y%m%d-%H:%M:%S`] [INFO]  process end "
