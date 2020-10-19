#!/bin/bash

rank_size=$1
yamlPath=$2
modelDir=$3
config_section=$4
currentDir=$(cd "$(dirname "$0")"; pwd)

# 从 yaml 获取配置
eval $(${currentDir}/get_params_for_yaml.sh ${yamlPath} ${config_section})

# device 列表, 若无指定 device 时根据 rank_size 顺序选择
eval device_group=\$device_group_${rank_size}p
if [ x"${device_group}" == x"" ];then
    device_group="$(seq 0 "$(expr $rank_size - 1)")"
fi

arr=($device_group)
if [ ${#arr[@]} -ne ${rank_size} ];then
    echo "ERROR: device_group: $device_group, quantity is not equal to rank_size: $rank_size"
    exit 1
fi

HCCL_dir=$modelDir/config
cp ${currentDir}/hccl_sample.json ${HCCL_dir}/${rank_size}p.json

DEVICES=""

rank_id=0
for device_id in $device_group;do
    DEVICE_IP=`hccn_tool -i ${device_id} -ip -g|awk -F ":" '/ipaddr/{print $2}'`
    DEVICES+="\n\
            {\n\
                \"device_id\": \"${device_id}\",\n\
                \"device_ip\": \"${DEVICE_IP}\",\n\
                \"rank_id\": \"${rank_id}\"\n\
            },"
    let rank_id++
done
sed -i 's#{devices}#'"${DEVICES%?}"'#g' ${HCCL_dir}/${rank_size}p.json
