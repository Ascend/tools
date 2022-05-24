#!/bin/bash
declare -i ret_invalid_args=1
declare -i ret_train_failed=2
CUR_PATH=$(dirname $(readlink -f "$0"))
export BASE_PATH=$(cd "$CUR_PATH/../";pwd)

. $CUR_PATH/common/log_util.sh
. $CUR_PATH/common/common.sh

ulimit -u unlimited

run_train() {
    # create work path
    rm -rf $BASE_PATH/work
    mkdir -p $BASE_PATH/work
    cp $CUR_PATH/code/* $BASE_PATH/work -rf

    train_run_cmd="python3 -u $BASE_PATH/work/run_pretraining.py \
    --input_file=$TRAIN_DATA_PATH \
    --output_dir=$BASE_PATH/work \
    --do_train=True \
    --do_eval=True \
    --bert_config_file=$BERT_CONFIG_DIR/bert_config.json \
    --max_seq_length=$MAX_SEQ_LENGTH \
    --max_predictions_per_seq=76 \
    --num_train_steps=$TRAIN_STEPS \
    --num_warmup_steps=0 \
    --train_batch_size=$BATCH_SIZE
    "

    logger_Info "train run cmd:$train_run_cmd"
    $train_run_cmd  || { ret=$ret_train_failed;logger_Warn "run train failed ret:$?"; }
    logger_Info "train run done cmd:$train_run_cmd"
    return $ret
}

main() {
    python3 $CUR_PATH/ais_utils.py set_result "training" "proc_start_time" $(date "+%Y-%m-%d %H:%M:%S")
    run_train || { logger_Warn "train failed ret:$?"; return $ret_train_failed; }
    python3 $CUR_PATH/ais_utils.py set_result "training" "proc_end_time" $(date "+%Y-%m-%d %H:%M:%S")
    callback_throught_rate=`cat ${BASE_PATH}/log/detail.log | grep "examples/sec:" | tail -n 1 | awk -F ' ' '{print $NF}'`
    echo "actual callback_throught_rate:$callback_throught_rate"

    python3 $CUR_PATH/ais_utils.py set_result "training" "result" "OK"
}

main "$@"
exit $?
