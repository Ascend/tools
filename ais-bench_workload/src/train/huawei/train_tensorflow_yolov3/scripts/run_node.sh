#!/bin/bash
. $WORK_PATH/common/common.sh
. $WORK_PATH/common/log_util.sh
. $WORK_PATH/common/node_common.sh

# 获取训练命令
function get_train_cmd()
{
    rm -rf $WORK_PATH/code/data
    ln -sf $DATA_PATH $RUN_PATH
    ln -sf $DATA_PATH $WORK_PATH/code
    train_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/train.py \
        --mode=$MODE \
        "
    return 0
}

function get_eval_cmd()
{
    rm -rf $WORK_PATH/code/data
    ln -sf $DATA_PATH $RUN_PATH
    ln -sf $DATA_PATH $WORK_PATH/code
    cp $WORK_PATH/code/eval_coco.py $RUN_PATH/
    eval_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/eval.py \
        --save_json=True \
        --score_thresh=0.0001 \
        --nms_thresh=0.55 \
        --max_boxes=100 \
        --restore_path=$RESTORE_PATH \
        --max_test=10000 \
        --save_json_path=eval_res_D$RANK_ID.json \
        "
    return
}

function node_init()
{
    export PYTHONPATH=$PYTHONPATH:$WORK_PATH:$WORK_PATH/code
    source $WORK_PATH/config/tensorflow_env.sh
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
    check_python_package_is_install ${PYTHON_COMMAND} "tensorflow" || { logger_Warn "tensorflow package not install" ; return $ret_invalid_args;}
    logger_Debug "python packet tensorflow valid"

    check_path_valid "${DATA_PATH}" || { logger_Warn "DATA_PATH:${DATA_PATH} not valid path" ; return 1; }
    logger_Debug "DATA_PATH is valid"

    logger_Debug "EVAL_DATA_PATH is valid"

}

function node_train()
{
    # 调用通用训练接口
    node_common_train "true" "false" || { logger_Warn "run train failed" ; return 1; }
}

function node_eval()
{
    RUN_PATH=$WORK_PATH/train_parallel$RANK_ID
    RESTORE_PATH=$RUN_PATH/training/
    cd $RUN_PATH

    get_eval_cmd
    echo "start eval RUN_PATH:${RUN_PATH} SERVER_ID:$SERVER_ID rank $RANK_ID device $DEVICE_ID begin cmd:${eval_run_cmd}"
    $eval_run_cmd > $RUN_PATH/eval.log || { echo "run eval node error ret:$?"; return 1; }

    if [ -f  "$RUN_PATH/eval.log" ];then
        accuracy=`cat $PATH/eval.log |grep "Average Precision" |grep -v grep |awk -F= 'NR==1{print $NF}'`
        logger_Info "accuracy: $accuracy"
        echo "$accuracy" > $RESULT_PATH/eval_acc.log
    fi

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
