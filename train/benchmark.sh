#!/bin/bash

parentDir=$(dirname "$PWD")
currentDir=$(cd "$(dirname "$0")"; pwd)

execModel=AlexNet
mode=host
framework=tensorflow
hardware=1p

framework_group="tensorflow pytorch mindspore"
hardware_group="1p 2p 4p 8p cluster ct"

echo_help(){
    echo ""
    echo "    --execmodel, -e  (选填) 需要执行的模型名称, 默认 ResNet50"
    echo "    --hardware, -hw  (选填) 选择 1p, 2p, 4p, 8p, cluster|ct(集群), 默认 1p"
    echo "    --yamlpath, -y   (选填) yaml 文件的路径, 默认为 yaml 路径下的 {execmodel}.yaml"
    echo "    --framework, -f  (选填) 模型训练框架, 默认 tensorflow"
    echo "    -docker, -host   (选填) 选择 docker 或 host 下执行, 默认使用 host"
    echo ""
    echo "    --help, -h       显示帮助信息"
    echo "    --list, -l       显示支持的框架与模型"
    echo ""
    echo "    示例1，docker 环境下启动 MobileNet 多卡（8p）训练："
    echo "        ./benckmark.sh -e MobileNet -hw 8p -y ./yaml/MobileNet.yaml -docker"
    echo "    示例2，host 环境下启动 MobileNet 单卡（1p）训练，yaml 使用默认文件："
    echo "        ./benckmark.sh -e MobileNet"
    echo ""
    exit 0
}

error_log(){
    echo -e "\nERROR:\n\n$1"
    exit 1
}

exec_train(){

    if [ x"${yamlPath}" == x"" ];then
        yamlPath=$(find ${currentDir}/yaml/ -iregex ".*${execModel}.yaml$" 2>/dev/null)
    fi

    [ -f ${yamlPath} ] || error_log "No such file or directory: ${yamlPath}\n"

    error_msg=""
    echo $hardware_group | grep -wq "$hardware" || error_msg+="hardware: $hardware not in '$hardware_group'\n"
    echo $framework_group | grep -wq "$framework" || error_msg+="framework: $framework not in '$framework_group'\n"
    if [ x"$error_msg" != x"" ];then
        error_log "$error_msg"
    fi
    chmod -R u+x ${currentDir}/*
    exec_train_file=$(find ${currentDir} -iregex ".*${execModel}/${framework}/scripts/run.sh$" 2>/dev/null)
    file_count=$(echo ${exec_train_file} | wc -w)
    start_file=$currentDir/atlas_benchmark-master/utils/shell/start.sh
    [ x"$hardware" == x"ct" ] && hardware="cluster"
    if [ "${file_count}" -eq 1 ] && [ -a ${exec_train_file} ]; then
        modelDir=$(cd $(dirname "$exec_train_file")/..;pwd)
        echo "find script path success"
        echo "run train script file path is "${exec_train_file}
        bash "${start_file}" ${mode} ${hardware} "${yamlPath}" "${modelDir}" "${framework}"
    else
        error_log "The model($execModel) does not support the framework($framework) temporarily.\nplease use --list\n"
        exit 1
    fi
}

list_model (){
    for i in $framework_group;do
        echo -e "\n${i}:\n"
        for d in  $(find ${currentDir} -iregex ".*/${i}/scripts/run.sh$" 2>/dev/null);do
            echo $d|awk -F / '{print "    "$(NF-3)}'
        done
    done
    echo ""
}

while [ -n "$1" ]
do
  case "$1" in
    -e|--execmodel)
        execModel=$2;
        shift
        ;;
    -host|-docker)
        tmp=$1
        mode=${tmp:1}
        ;;
    -y|--yamlpath)
        yamlPath=$2
        shift
        ;;
    -f|--framework)
        framework=$2
        shift
        ;;
    -hw|--hardware)
        hardware=$2
        shift
        ;;
    -l|--list)
        list_model;
        exit
        ;;
    -h|--help)
        echo_help;
        exit
        ;;
    *)
        echo "$1 is not an option, please use --help"
        exit 1
        ;;
  esac
  shift
done

exec_train
