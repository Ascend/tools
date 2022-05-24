#!/bin/bash
. $WORK_PATH/common/common.sh
. $WORK_PATH/common/log_util.sh
. $WORK_PATH/common/node_common.sh

# 获取训练命令
function get_train_cmd()
{
    [[ $RANK_SIZE -gt 1 ]] && DISTRUTE_ENABLE="True" || DISTRUTE_ENABLE="False"
    train_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/train.py --distribute=$DISTRUTE_ENABLE  \
                    --device_num=$DEVICE_NUM \
                    --data_url=$TRAIN_DATA_PATH  \
                    --run_type=train  \
                    --param_init_type=$PARAM_INIT_TYPE  \
                    --mode=$MODE  \
                    --stage_num=$STAGE_NUM     \
                    --micro_size=$MICRO_SIZE
                    --per_batch_size=$PER_BATCH
                    "
      return 0
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

    check_file_valid "${TRAIN_DATA_FILE}" || { logger_Warn "TRAIN_DATA_FILE:${TRAIN_DATA_FILE} not valid file" ; return 1; }
    logger_Debug "TRAIN_DATA_FILE is valid"
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
