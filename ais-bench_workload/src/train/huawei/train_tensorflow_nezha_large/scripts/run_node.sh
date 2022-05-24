#!/bin/bash
. $WORK_PATH/common/common.sh
. $WORK_PATH/common/log_util.sh
. $WORK_PATH/common/node_common.sh

# 获取训练命令
function get_train_cmd()
{
    [[ $RANK_SIZE -gt 1 ]] && DISTRUTE_ENABLE="True" || DISTRUTE_ENABLE="False"
    train_run_cmd="${PYTHON_COMMAND} -u $WORK_PATH/code/src/pretrain/run_pretraining.py \
        --bert_config_file=$WORK_PATH/code/configs/nezha_large_config.json \
        --max_seq_length=128 \
        --max_predictions_per_seq=20 \
        --train_batch_size=64 \
        --learning_rate=1e-4 \
        --num_warmup_steps=100 \
        --num_train_steps=1000 \
        --optimizer_type=lamb \
        --manual_fp16=True \
        --use_fp16_cls=True \
        --input_files_dir=${TRAIN_DATA_PATH} \
        --eval_files_dir=$EVAL_DATA_PATH \
        --npu_bert_debug=False \
        --npu_bert_use_tdt=True \
        --do_train=True \
        --num_accumulation_steps=1 \
        --npu_bert_job_start_file= \
        --iterations_per_loop=100 \
        --save_checkpoints_steps=1000 \
        --npu_bert_clip_by_global_norm=False \
        --distributed=$DISTRUTE_ENABLE \
        --npu_bert_loss_scale=0 \
        --output_dir=$RUN_PATH/
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

    check_path_valid "${EVAL_DATA_PATH}" || { logger_Warn "EVAL_DATA_PATH:${EVAL_DATA_PATH} not valid path" ; return 1; }
    logger_Debug "EVAL_DATA_PATH is valid"

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
