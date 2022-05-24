#!/bin/bash
. $WORK_PATH/common/common.sh
. $WORK_PATH/common/log_util.sh
. $WORK_PATH/common/node_common.sh

# 获取训练命令
function get_train_cmd()
{
    train_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/train.py \
        --dataset_dir=$TRAIN_DATA_PATH  \
        --max_train_steps=$MAX_TRAIN_STEPS \
        --iterations_per_loop=10 \
        --model_name=\"mobilenet_v2\" \
        --moving_average_decay=0.9999 \
        --label_smoothing=0.1 \
        --preprocessing_name=\"inception_v2\" \
        --weight_decay='0.000004' \
        --batch_size=$BATCH_SIZE \
        --learning_rate_decay_type='cosine_annealing' \
        --learning_rate=0.4 \
        --optimizer='momentum' \
        --momentum='0.9' \
        --warmup_epochs=5 \
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

    check_path_valid "${TRAIN_DATA_PATH}" || { logger_Warn "TRAIN_DATA_PATH:${TRAIN_DATA_PATH} not valid path" ; return 1; }
    logger_Debug "TRAIN_DATA_PATH is valid"

}

function node_train()
{
    # 调用通用训练接口
    node_common_train "false" "false" || { logger_Warn "run train failed" ; return 1; }
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
