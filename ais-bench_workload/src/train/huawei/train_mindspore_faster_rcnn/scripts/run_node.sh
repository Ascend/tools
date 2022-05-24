#!/bin/bash
. $WORK_PATH/common/common.sh
. $WORK_PATH/common/log_util.sh
. $WORK_PATH/common/node_common.sh

# 获取训练命令
function get_train_cmd()
{
    COCO_CONFIG_FILE=$WORK_PATH/code/default_config.yaml
    train_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/train.py --config_path=$COCO_CONFIG_FILE  \
        --coco_root=$TRAIN_DATA_PATH       \
        --pre_trained=$PRETRAIN_MODEL_PATH \
        --backbone="resnet_v1.5_50"    \
        --mindrecord_dir=$MINDRECORD_PATH \
        "

    # for mindspore1.5
    export ENV_FUSION_CLEAR=1
    export ENV_SINGLE_EVAL=1
    export SKT_ENABLE=1
    export DATASET_ENABLE_NUMA=True
}

function get_eval_cmd()
{
    return 0
}

function node_init()
{
    export PYTHONPATH=$PYTHONPATH:$WORK_PATH:$WORK_PATH/code
    source $WORK_PATH/config/mindspore_env.sh
    # for eval env set
    [ $1 == "eval" ] && { export RANK_SIZE=1; export DEVICE_ID=0; : "${SINGLE_CARD_INDEX:=0}";export RANK_ID=$SINGLE_CARD_INDEX; unset RANK_TABLE_FILE; }
    [[ -z "$RESULT_PATH" ]] || { mkdir -p $RESULT_PATH; }
}

function node_check()
{
    CONFIG_FILE_PATH=$1
    source $CONFIG_FILE_PATH

    # 通用检测 主要检测 PYTHON_COMMAND RANK_SIZE和RANK_TABLE
    node_common_check "${PYTHON_COMMAND}" "${RANK_SIZE}" "$RANK_TABLE_FILE" || { logger_Warn "node common check failed" ; return 1; }

    # 检测是否安装对应框架软件
    check_mindspore_run_ok ${PYTHON_COMMAND} || { logger_Warn "mindspore running failed" ; return 1; }
    logger_Debug "mindspore running successfully"

    check_path_valid "${TRAIN_DATA_PATH}" || { logger_Warn "TRAIN_DATA_PATH:${TRAIN_DATA_PATH} not valid file" ; return 1; }
    logger_Debug "TRAIN_DATA_PATH is valid"

    check_file_valid "${PRETRAIN_MODEL_PATH}" || { logger_Warn "PRETRAIN_MODEL_PATH:${PRETRAIN_MODEL_PATH} not valid file" ; return 1; }
    logger_Debug "PRETRAIN_MODEL_PATH is valid"

    check_file_valid "${VALIDATION_JSON_FILE}" || { logger_Warn "VALIDATION_JSON_FILE:${VALIDATION_JSON_FILE} not valid file" ; return 1; }
    logger_Debug "VALIDATION_JSON_FILE is valid"
}

function node_train()
{
    # 调用通用训练接口
    node_common_train "true" "false" || { logger_Warn "run train failed" ; return 1; }
}

function node_eval()
{
    return 0
}

main()
{
    type="$1"
    shift
    node_init $type || { logger_Warn "init failed"; return 1; }
    if [ "$type" == "train" ];then
        node_train "$@" || { logger_Warn "run_node_train failed"; return 1; }
    elif [ "$type" == "eval" ];then
        node_eval "$@" || { logger_Warn "run_node_eval failed"; return 1; }
    elif [ "$type" == "check" ];then
        node_check "$@" || { logger_Warn "run_node_check failed"; return 1; }
    else
        { logger_Warn "invalid argument '${type}'"; return 1; }
    fi
}

main "$@"
exit $?
