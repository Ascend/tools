#!/bin/bash

currentDir=$(cd "$(dirname "$0")"; pwd)
yamlpath=${currentDir%train*}train/yaml/cluster_info.yaml
toolsPath=${currentDir%train*}train/atlas_benchmark-master/utils/shell
# 从 yaml 获取配置

eval $(${toolsPath}/get_params_for_yaml.sh ${yamlpath} 'tensorflow_config')

# docker网络桥接
echo $(route -n|awk '{print $1}'|sed -n '4p')
echo $(route -n|awk '{print $2}'|sed -n '3p')
echo $(route -n|awk '{print $8}'|sed -n '3p')
docker network create -d macvlan  --subnet=$(route -n|awk '{print $1}'|sed -n '4p')/${epcount} --gateway=$(route -n|awk '{print $2}'|sed -n '3p') -o parent=$(route -n|awk '{print $8}'|sed -n '3p') $(route -n|awk '{print $8}'|sed -n '3p')


data="-v ${imagenet_data}:${imagenet_data} -v ${yolo_data}:${yolo_data} -v ${ssd_data}:${ssd_data} -v ${bert_data}:${bert_data}"

# docroute -nker容器挂载
	
docker run -ti -d --net=$(route -n|awk '{print $8}'|sed -n '3p') --ip=${ip} --name mpirun --shm-size=16g -e ASCEND_VISIBLE_DEVICES=0-7 -v ${currentDir%train*}/train:${currentDir%train*}/train ${data} -v /var/log/npu/slog/:/var/log/npu/slog -v /var/log/npu/profiling/:/var/log/npu/profiling -v /var/log/npu/dump/:/var/log/npu/dump -v /var/log/npu/:/usr/slog ${docker_images} /bin/bash

docker exec -ti mpirun /bin/bash -c "/etc/init.d/ssh start"
