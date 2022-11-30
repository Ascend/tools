#!/bin/bash
. $WORK_PATH/common/common.sh
. $WORK_PATH/common/log_util.sh
. $WORK_PATH/common/node_common.sh

function get_train_cmd()
{
    [[ $RANK_SIZE -gt 1 ]] && DISTRUTE_ENABLE="true" || DISTRUTE_ENABLE="false"

    train_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/run_pretrain.py \
        --distribute=$DISTRUTE_ENABLE \
        --epoch_size=$EPOCH_SIZE \
        --enable_save_ckpt=true \
        --enable_lossscale=true \
        --do_shuffle=true \
        --enable_data_sink=true \
        --data_sink_steps=100 \
        --accumulation_steps=1 \
        --save_checkpoint_path=$RUN_PATH \
        --save_checkpoint_steps=$TRAIN_STEPS \
        --save_checkpoint_num=1 \
        --load_checkpoint_path=$PRETRAIN_MODEL_PATH \
        --data_dir=${TRAIN_DATA_PATH} \
        --device_id=${DEVICE_ID} \
        --device_num=${DEVICE_NUM} \
        --train_steps=${TRAIN_STEPS} \
        --config_path=$WORK_PATH/code/pretrain_config_Ascend_Boost.yaml
        "
    return 0
}

function get_eval_cmd()
{
    CONFIG_FILE=$WORK_PATH/code/pretrain_config_Ascend_Boost.yaml
    sed -i "s|eval_data_dir:.*|eval_data_dir: '$EVAL_DATA_PATH'|g" "$CONFIG_FILE"
    sed -i "s|schema_file:.*|schema_file: null|g" "$CONFIG_FILE"
    sed -i "s|eval_ckpt:.*|eval_ckpt: '$CHECKPOINT_PATH'|g" "$CONFIG_FILE"
    eval_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/pretrain_eval.py --config_path=$CONFIG_FILE"
    return 0
}

function node_init()
{
    export PYTHONPATH=$PYTHONPATH:$WORK_PATH
    source $WORK_PATH/config/mindspore_env.sh
    # for eval env set
    [ $1 == "eval" ] && { export RANK_SIZE=1; export DEVICE_ID=0; : "${SINGLE_CARD_INDEX:=0}";export RANK_ID=$SINGLE_CARD_INDEX; unset RANK_TABLE_FILE; }
    [[ -z "$RESULT_PATH" ]] || { mkdir -p $RESULT_PATH; }
}

function node_check()
{
    CONFIG_FILE_PATH=$1
    source $CONFIG_FILE_PATH

    node_common_check "${PYTHON_COMMAND}" "${RANK_SIZE}" "$RANK_TABLE_FILE" || { logger_Warn "node common check failed" ; return 1; }

    check_mindspore_run_ok ${PYTHON_COMMAND} || { logger_Warn "mindspore running failed" ; return 1; }
    logger_Debug "mindspore running successfully"

    check_file_valid ${PRETRAIN_MODEL_PATH} || { logger_Warn "PRETRAIN_MODEL_PATH:${PRETRAIN_MODEL_PATH} not valid" ; return 1; }
    logger_Debug "PRETRAIN_MODEL_PATH path valid"

    check_path_valid "${TRAIN_DATA_PATH}" || { logger_Warn "TRAIN_DATA_PATH:${TRAIN_DATA_PATH} not valid path" ; return 1; }
    logger_Debug "TRAIN_DATA_PATH is valid"

    check_path_valid "${EVAL_DATA_PATH}" || { logger_Warn "EVAL_DATA_PATH:${EVAL_DATA_PATH} not valid path" ; return 1; }
    logger_Debug "EVAL_DATA_PATH is valid"
}

function node_train()
{
    # 调用通用训练接口
    node_common_train "false" "false" || { logger_Warn "run train failed" ; return 1; }
}

function node_eval()
{
    CHECKPOINT_PATH=`find ${WORK_PATH}/train_parallel$RANK_ID/ -name "*.ckpt" | xargs ls -t | awk 'NR==1{print}'`
    [ -f $CHECKPOINT_PATH ] || { logger_Warn "CHECKPOINT_PATH:${CHECKPOINT_PATH} not valid path" ; return 1; }
    cp $CHECKPOINT_PATH  $RESULT_PATH/
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
