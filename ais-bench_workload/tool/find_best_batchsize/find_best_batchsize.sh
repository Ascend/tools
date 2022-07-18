#!/bin/bash
CUR_PATH=$(dirname $(readlink -f "$0"))

# 返回码
declare -i ret_ok=0
declare -i ret_run_failed=1

echo_help()
{
    echo "./find_best_batch.sh --model_path /home/BERT_Base_SQuAD1_1_BatchSize_None.pb --input_shape_str \"input_ids:batchsize,384;input_mask:batchsize,384;segment_ids:batchsize,384\" --soc_version \"Ascend310\" --max_batch_num 4"
    echo "./find_best_batch.sh --model_path /home/resnet50_official.onnx --input_shape_str \"actual_input_1:batchsize,3,224,224\" --soc_version \"Ascend310\" --max_batch_num 120"
}

function check_command_exist()
{
    command=$1
    if type $command >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_python_package_is_install()
{
    local PYTHON_COMMAND=$1
    ${PYTHON_COMMAND} -c "import $2" >> /dev/null 2>&1
    ret=$?
    if [ $ret != 0 ]; then
        echo "python package:$1 not install"
        return 1
    fi
    return 0
}

get_framework()
{
    local _model_path=$1
    extension="${_model_path##*.}"
    [ $extension == "prototxt" ] && { FRAMEWORK=0;return 0; }
    [ $extension == "pb" ] && { FRAMEWORK=3;return 0; }
    [ $extension == "onnx" ] && { FRAMEWORK=5;return 0; }
    echo "find no valid framework extension:$extension"
    return 1
}

check_args_valid()
{
    [ -f "$MODEL_PATH" ] || { echo "model_path:$MODEL_PATH not valid"; return 1; }
    get_framework "$MODEL_PATH" || { echo "find no valid framework model_path:$MODEL_PATH"; return 1; }
    [[ $FRAMEWORK == 0 && ! -f "$WEIGHT_PATH" ]] && { echo "caffe wight_path:$WEIGHT_PATH not valid"; return 1; }
    [[ $MAX_BATCH_NUM -gt 0 && $MAX_BATCH_NUM -le 100 ]] || { echo "max_batch_num:$MAX_BATCH_NUM not valid"; }
    [ "$INPUT_SHAPE_STR" != "" ] || { echo "input_shape_str:$INPUT_SHAPE_STR not valid"; return 1; }
    [[ "$SOC_VERSION" != "" ]] || { echo "soc_version:$SOC_VERSION not valid"; return 1; }
    return 0
}

check_env_valid()
{
    check_command_exist atc || { echo "atc cmd not valid"; return $ret_run_failed; }
    check_python_package_is_install ${PYTHON_COMMAND} "aclruntime" \
    || { echo "aclruntime package not install"; return $ret_run_failed;}
}

convert_and_run_model()
{
    for batchsize in `seq $MAX_BATCH_NUM`; do
        input_shape=${INPUT_SHAPE_STR//batchsize/$batchsize}
        om_path_pre="$CACHE_PATH/model_bs${batchsize}"
        mkdir -p $CACHE_PATH/$batchsize
        om_path="$om_path_pre.om"
        if [ ! -f $om_path ];then
            cmd="atc --model=$MODEL_PATH --output=$om_path_pre --framework=$FRAMEWORK --input_shape=$input_shape --soc_version=$SOC_VERSION"
            [ $FRAMEWORK == 0 ] && cmd="$cmd --weight=$WEIGHT_PATH"
            $cmd || { echo "atc run $cmd failed"; return 1; }
        fi

        cmd="$PYTHON_COMMAND $CUR_PATH/../ais_infer/ais_infer.py --model $om_path --loop $LOOP_COUNT --batchsize=$batchsize --output $CACHE_PATH/$batchsize --device_id=$DEVICE_ID"
        $cmd || { echo "inference run $cmd failed"; return 1; }
    done
}

get_sumary_throughput()
{
    local _sumaryfile=$1
    cat ${_sumaryfile} | $PYTHON_COMMAND -c 'import sys,json;print(json.load(sys.stdin)["throughput"])' 2>/dev/null
}

calc_throughput()
{
    best_batchsize=0
    best_throughput=0
    for batchsize in `seq $MAX_BATCH_NUM`; do
        sumary_file=`find $CACHE_PATH/$batchsize -name sumary.json`
        local _throughput=$(get_sumary_throughput ${sumary_file} )
        echo "batchsize:$batchsize throughput:$_throughput"
        [[ `expr $_throughput \> $best_throughput` == 0 ]] || { best_throughput=$_throughput;best_batchsize=$batchsize; }
     done
    echo "calc end best_batchsize:$best_batchsize best_throughput:$best_throughput"
}

main()
{
    while [ -n "$1" ]
do
  case "$1" in
    -m|--model_path)
        MODEL_PATH=$2
        shift
        ;;
    # only caffe model need
    -w|--weight_path)
        WEIGHT_PATH=$2
        shift
        ;;
    -n|--max_batch_num)
        MAX_BATCH_NUM=$2
        shift
        ;;
    -i|--input_shape_str)
        INPUT_SHAPE_STR=$2
        shift
        ;;
    -v|--soc_version)
        SOC_VERSION=$2
        shift
        ;;
    -p|--python_command)
        PYTHON_COMMAND=$2
        shift
        ;;
    -l|--loop_count)
        LOOP_COUNT=$2
        shift
        ;;
    -d|--device_id)
        DEVICE_ID=${2}
        shift
        ;;
    -h|--help)
        echo_help;
        exit
        ;;
    *)
        echo "$1 is not an option, please use --help"
        exit 1
        ;;
  esac
  shift
done

    [ "$PYTHON_COMMAND" != "" ] || { PYTHON_COMMAND="python3.7";echo "set default pythoncmd:$PYTHON_COMMAND"; }
    [ "$MAX_BATCH_NUM" != "" ] || { MAX_BATCH_NUM="64";echo "set default max_batch_num:$MAX_BATCH_NUM"; }
    [ "$LOOP_COUNT" != "" ] || { LOOP_COUNT="1000";echo "set default loop_count:$LOOP_COUNT"; }
    [ "$DEVICE_ID" != "" ] || { DEVICE_ID="0";echo "set default device_id:$DEVICE_ID"; }

    CACHE_PATH=$CUR_PATH/cache
    [ ! -d $CACHE_PATH ] || rm -rf $CACHE_PATH
    mkdir -p $CACHE_PATH

    check_args_valid || { echo "check args not valid return"; return $ret_run_failed; }
    check_env_valid || { echo "check env not valid return"; return $ret_run_failed; }

    convert_and_run_model
    calc_throughput
    return $ret_ok
}

main "$@"
exit $?
