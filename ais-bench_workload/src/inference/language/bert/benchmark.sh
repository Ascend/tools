#!/bin/bash
export CUR_PATH=$(cd "$(dirname "$0")";pwd)
export CODE_PATH=$CUR_PATH
export BASE_PATH=$(cd "$CUR_PATH/../";pwd)

. $CUR_PATH/common/log_util.sh
. $CUR_PATH/common/common.sh

# 设置配置文件中的环境变量
set_config_env()
{
    export SET_RESULT_PATH=$CUR_PATH/ais_utils.py
    export PYTHONPATH=$PYTHONPATH:$CUR_PATH/core
    source $CUR_PATH/config/config.sh
}

# 文件路径和环境依赖检查
check_sys()
{
    : "${PYTHON_COMMAND?PYTHON_COMMAND not set}"
    : "${PROFILE?PROFILE not set}"

    check_file_valid "${DATASET_PATH}" || { logger_Warn "DATASET_PATH:${DATASET_PATH} not valid path" ; return 1; }
    logger_Debug "DATASET_PATH is valid"

    check_file_valid ${MODEL_PATH} || { logger_Warn "MODEL_PATH:${MODEL_PATH} not valid" ; return 1; }
    logger_Debug "MODEL_PATH file valid"

    check_file_valid ${VOCAB_FILE} || { logger_Warn "VOCAB_FILE:${VOCAB_FILE} not valid" ; return 1; }
    logger_Debug "VOCAB_FILE file valid"

    check_python_package_is_install $PYTHON_COMMAND "aclruntime" || { logger_Warn "aclruntime package install failed please install or source set_env.sh" ; return $ret_invalid_args;}
    logger_Debug "python packet aclruntime valid"

    check_python_package_is_install $PYTHON_COMMAND "loadgen" || { logger_Warn "loadgen package install failed please install" ; return $ret_invalid_args;}
    logger_Debug "python packet loadgen valid"
}

exec_inference()
{
    logger_Debug "python begin run"

    export WORK_PATH=${BASE_PATH}/work
    rm -rf ${WORK_PATH};mkdir -p ${WORK_PATH}
    cp -rf $CODE_PATH/*  ${WORK_PATH}

    cd ${WORK_PATH}
    infer_run_cmd="$PYTHON_COMMAND -u $WORK_PATH/main.py --profile=$PROFILE --dataset_path=$DATASET_PATH \
            --model $MODEL_PATH --vocab_path $VOCAB_FILE --query_arrival_mode=$QUERY_ARRIVAL_MODE"
    [ "$SAMPLE_COUNT" != "" ] && infer_run_cmd="${infer_run_cmd} --count=$SAMPLE_COUNT"
    [ "$MAX_LOADSAMPLES_COUNT" != "" ] && infer_run_cmd="${infer_run_cmd} --maxloadsamples_count=$MAX_LOADSAMPLES_COUNT"
    [ "$CACHE_PATH" != "" ] && infer_run_cmd="${infer_run_cmd} --cache_path=$CACHE_PATH"
    [ "$DEVICE_ID" != "" ] && infer_run_cmd="${infer_run_cmd} --device_id=$DEVICE_ID"

    [ "$BATCH_SIZE" != "" ] && infer_run_cmd="${infer_run_cmd} --batchsize=$BATCH_SIZE"
    [ "$DYM_BATCH" != "" ] && infer_run_cmd="${infer_run_cmd} --dymBatch=$DYM_BATCH"
    [ "$DYM_HW" != "" ] && infer_run_cmd="${infer_run_cmd} --dymHW=$DYM_HW"
    [ "$DYM_DIMS" != "" ] && infer_run_cmd="${infer_run_cmd} --dymDims=$DYM_DIMS"
    [ "$DYM_SHAPE" != "" ] && infer_run_cmd="${infer_run_cmd} --dymShape=$DYM_SHAPE"
    [ "$OUTPUT_SIZE" != "" ] && infer_run_cmd="${infer_run_cmd} --outputSize=$OUTPUT_SIZE"

    ${infer_run_cmd} || { logger_Warn "inference run failed"; return $ret_inference_failed; }

    $PYTHON_COMMAND $WORK_PATH/ais_utils.py set_result "inference" "result" "OK"

    logger_Debug "python end run"
}

main()
{
    set_config_env

    check_sys || { logger_Warn "check sys failed";return 1; }

    exec_inference
}

main "$@"
exit $?
