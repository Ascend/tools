#!/bin/bash
. $WORK_PATH/common/common.sh
. $WORK_PATH/common/log_util.sh
. $WORK_PATH/common/node_common.sh

# ȡѵ
function get_train_cmd()
{
    train_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/train.py --data_file=$TRAIN_DATA_FILE  \
                    --train_dir=$RUN_PATH \
                    --train_epochs=$EPOCH_SIZE  \
                    --batch_size=32  \
                    --crop_size=513  \
                    --base_lr=0.015  \
                    --lr_type=cos  \
                    --min_scale=0.5  \
                    --max_scale=2.0  \
                    --ignore_label=255  \
                    --num_classes=21  \
                    --model=deeplab_v3_s16  \
                    --ckpt_pre_trained=$PRETRAIN_MODEL_PATH  \
                    --save_steps=1500  \
                    --keep_checkpoint_max=200
                    "
      return 0
}

function get_eval_cmd()
{
    eval_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/eval.py \
                    --data_root=$TRAIN_DATA_PATH  \
                    --data_lst=$EVAL_DATA_FILE_PATH \
                    --batch_size=32  \
                    --crop_size=513  \
                    --ignore_label=255  \
                    --num_classes=21  \
                    --model=deeplab_v3_s16  \
                    --scales_type=0  \
                    --freeze_bn=True  \
                    --ckpt_path=$CHECKPOINT_PATH \
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

    # ͨü Ҫ PYTHON_COMMAND RANK_SIZERANK_TABLE
    node_common_check "${PYTHON_COMMAND}" "${RANK_SIZE}" "$RANK_TABLE_FILE" || { logger_Warn "node common check failed" ; return 1; }
    # ǷװӦ

    check_mindspore_run_ok ${PYTHON_COMMAND} || { logger_Warn "mindspore running failed" ; return 1; }
    logger_Debug "mindspore running successfully"

    check_file_valid "${TRAIN_DATA_FILE}" || { logger_Warn "TRAIN_DATA_FILE:${TRAIN_DATA_FILE} not valid file" ; return 1; }
    logger_Debug "TRAIN_DATA_FILE is valid"
}


function node_train()
{
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
