#!/bin/bash
. $WORK_PATH/common/common.sh
. $WORK_PATH/common/log_util.sh
. $WORK_PATH/common/node_common.sh

# 获取训练命令
function get_train_cmd()
{
    cp $WORK_PATH/code/labels.json $RUN_PATH/
    train_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/train.py --device_target=$DEVICE_TARGET "
    return 0
}

function get_eval_cmd()
{
    eval_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/eval.py \
                --pretrain_ckpt $CHECKPOINT_PATH \
                --device_target=$DEVICE_TARGET \
                "
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
    node_common_check "${PYTHON_COMMAND}" "${RANK_SIZE}" "" || { logger_Warn "node common check failed" ; return 1; }
    # 检测是否安装对应框架软件

    check_mindspore_run_ok ${PYTHON_COMMAND} || { logger_Warn "mindspore running failed" ; return 1; }
    logger_Debug "mindspore running successfully"
}


function node_train()
{
    # 调用通用训练接口
    node_common_train "true" "false" || { logger_Warn "run train failed" ; return 1; }
}

function node_eval()
{
    CHECKPOINT_PATH=`find ${WORK_PATH}/train_parallel$RANK_ID/ -name "*.ckpt" | xargs ls -t | awk 'NR==1{print}'`
    [ -f $CHECKPOINT_PATH ] || { logger_Warn "CHECKPOINT_PATH:${CHECKPOINT_PATH} not valid path" ; return 1; }
    RUN_PATH=$WORK_PATH/train_parallel$RANK_ID
    cd $RUN_PATH
    get_eval_cmd
    echo "start eval RUN_PATH:${RUN_PATH} SERVER_ID:$SERVER_ID rank $RANK_ID device $DEVICE_ID begin cmd:${eval_run_cmd}"
    $eval_run_cmd || { echo "run eval node error ret:$?"; return 1; }
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
