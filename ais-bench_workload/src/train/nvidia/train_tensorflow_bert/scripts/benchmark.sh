#!/bin/bash

# 返回码
declare -i ret_ok=0
declare -i ret_invalid_args=1

CUR_PATH=$(dirname $(readlink -f "$0"))
export BASE_PATH=$(cd "$CUR_PATH/../";pwd)

. $CUR_PATH/common/log_util.sh
. $CUR_PATH/common/common.sh
. $CUR_PATH/common/calc_power.sh
. $CUR_PATH/common/calc_resourceinfo.sh

# 设置配置文件中的环境变量
set_config_env() {
    export PYTHONPATH=$PYTHONPATH:${CUR_PATH}:${CUR_PATH}/code
    source $CUR_PATH/config/config_pretrain.sh
}

# 环境变量检查
check_env() {
    return
}

# 文件路径和环境依赖检查
check_sys() {
    check_path_valid $BERT_CONFIG_DIR || { logger_Warn "BERT_CONFIG_DIR:${BERT_CONFIG_DIR} not valid path"; return $ret_invalid_args; }
    logger_Debug "train path valid"

    check_file_valid $TRAIN_DATA_PATH || { logger_Warn "TRAIN_DATA_PATH:${TRAIN_DATA_PATH} not valid path"; return $ret_invalid_args; }
    logger_Debug "train data file path valid"

    #check_python_version || { logger_Warn "python version not match"; return $ret_invalid_args; }
    #logger_Debug "python version valid"

    check_python_package_is_install ${PYTHON_COMMAND} "tensorflow" || { logger_Warn "tensorflow package not install"; return $ret_invalid_args; }
    logger_Debug "python packet tensorflow valid"
}

main() {
    set_config_env

    check_env

    check_sys || exit $ret_invalid_args

    calc_powerinfo_backgroud

    device_group=(0)
    run_resourceinfo_monitor_backgroud_gpu

    bash $CUR_PATH/run.sh

    calc_runing_resourceinfo_gpu $CUR_PATH/ais_utils.py  $device_group

    set_powerinfo
}

main "$@" |& tee "${BASE_PATH}/log/detail.log"
exit $?
