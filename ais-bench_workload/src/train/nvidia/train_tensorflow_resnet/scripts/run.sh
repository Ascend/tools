#!/bin/bash
declare -i ret_invalid_args=1
CUR_PATH=$(dirname $(readlink -f "$0"))
export BASE_PATH=$(cd "$CUR_PATH/../";pwd)

. $CUR_PATH/common/log_util.sh
. $CUR_PATH/common/common.sh

ulimit -u unlimited

run_train(){
    # create work path
    rm -rf $BASE_PATH/work
    mkdir -p $BASE_PATH/work
    cp $CUR_PATH/code/* $BASE_PATH/work/ -rf

    train_run_cmd="python -u $BASE_PATH/work/official/resnet/imagenet_main.py \
    --data_dir=${TRAIN_DATA_PATH} \
    --train_epochs=$EPOCH_SIZE \
    --resnet_size=$RESNET_SIZE \
    --model_dir=$BASE_PATH/work \
    --epochs_between_evals=$EPOCH_SIZE \
    "
    $train_run_cmd
    cp -f $BASE_PATH/work/model.ckpt-* $BASE_PATH/result
    logger_Info "train run done"
}

main()
{
    python $CUR_PATH/ais_utils.py set_result "training" "proc_start_time" `date "+%Y-%m-%d %H:%M:%S"`

    run_train
    python $CUR_PATH/ais_utils.py set_result "training" "proc_end_time" `date "+%Y-%m-%d %H:%M:%S"`
    python3 $CUR_PATH/ais_utils.py set_result "training" "result" "OK"
}

main "$@"
exit $?
