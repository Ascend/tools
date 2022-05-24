#!/bin/bash

. $WORK_PATH/common/common.sh
. $WORK_PATH/common/log_util.sh
. $WORK_PATH/common/node_common.sh

function get_data_preprocess_cmd(){
    LINE_COUNT=`cat ${TRAIN_DATA_FILE} | wc -l`
    data_preprocess_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/src/preprocess_data.py \
        --data_path=$WORK_PATH/data/ \
        --dense_dim=13 --slot_dim=26 --threshold=100 --train_line_count=$LINE_COUNT --skip_id_convert=0
    "
    return 0
}

function get_train_cmd()
{
    [[ $RANK_SIZE -gt 1 ]] && DISTRUTE_ENABLE="True" || DISTRUTE_ENABLE="False"

    train_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/train.py --data_path=$DATASET_PATH --dataset_type=mindrecord"
    return 0
}

function get_eval_cmd()
{
    DATASET_PATH=$WORK_PATH/data/mindrecord
    eval_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/eval.py \
        --data_path=$DATASET_PATH --dataset_type=mindrecord --ckpt_path=$CHECKPOINT_PATH"
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

    # ͨü Ҫ PYTHON_COMMAND RANK_SIZERANK_TABLE
    node_common_check "${PYTHON_COMMAND}" "${RANK_SIZE}" "$RANK_TABLE_FILE" || { logger_Warn "node common check failed" ; return 1; }
    # ǷװӦ
    check_mindspore_run_ok ${PYTHON_COMMAND} || { logger_Warn "mindspore running failed" ; return 1; }
    logger_Debug "mindspore running successfully"

    check_file_valid "${TRAIN_DATA_FILE}" || { logger_Warn "TRAIN_DATA_FILE:${TRAIN_DATA_FILE} not valid file" ; return 1; }
    logger_Debug "TRAIN_DATA_FILE is valid"
}

function node_data_preprocess()
{
    # data
    rm -rf $WORK_PATH/data/*
    mkdir -p $WORK_PATH/data/origin_data
    ln -sf ${TRAIN_DATA_FILE}  $WORK_PATH/data/origin_data/train.txt

    get_data_preprocess_cmd
    $data_preprocess_cmd || { logger_Warn "preprocess run failed"; return 1; }

    DATASET_PATH=$WORK_PATH/data/mindrecord
    check_path_valid $DATASET_PATH || { logger_Warn "mindpath:${DATASET_PATH} not valid path" ; return 1; }
}

function node_train()
{
    node_data_preprocess

    # ͨѵӿ
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
