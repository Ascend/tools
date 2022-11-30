#!/bin/bash
CUR_PATH=$(dirname $(readlink -f "$0"))

# 返回码
declare -i ret_ok=0
declare -i ret_run_failed=1

# common function

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

get_infer_count_from_json()
{
    local file=$1
    cat ${file} | python3 -c 'import sys,json;s=json.load(sys.stdin);print(len(s["npu_compute_time_list"]));' 2>/dev/null
}

get_infer_pid_from_json()
{
    local file=$1
    cat ${file} | python3 -c 'import sys,json;s=json.load(sys.stdin);print(s.get("pid"));' 2>/dev/null
}

get_topk_array_from_json()
{
    local file=$1
    cat ${file} | python3 -c 'import sys,json;s=json.load(sys.stdin);sa = [ str(i) for i in s];print(" ".join(sa));' 2>/dev/null
}

get_infer_time_from_json()
{
    local file=$1
    local index=$2
    cat ${file} | python3 -c "import sys,json;s=json.load(sys.stdin);print(s[\"npu_compute_time_list\"][${index}]);" 2>/dev/null
}

# func 


check_args_valid()
{
    [ -f "$MODEL" ] || { echo "model:$MODEL not valid"; return 1; }
    return 0
}

check_env_valid()
{
    [ -d "$ASCEND_TOOLKIT_HOME" ] || { echo "ASCEND_TOOLKIT_HOME:$ASCEND_TOOLKIT_HOME not valid, please set"; return $ret_run_failed; }

    check_python_package_is_install ${PYTHON_COMMAND} "aclruntime" \
    || { echo "aclruntime package not install"; return $ret_run_failed;}

    msprof_bin="$ASCEND_TOOLKIT_HOME/toolkit/tools/profiler/bin/msprof"
    [ -f ${msprof_bin} ] || { echo "msprof:${msprof_bin} not valid"; return $ret_run_failed; }

    # set log level = info
    #export ASCEND_GLOBAL_LOG_LEVEL=1
}

get_infer_cmd()
{
    local tool=$1
    if [ "${tool}" == "msame" ]; then
        infer_cmd="$CUR_PATH/../../../msame/out/msame --model $MODEL --output $CACHE_PATH/ --device $DEVICE --loop $LOOP"
    else
        infer_cmd="$PYTHON_COMMAND $CUR_PATH/../ais_infer/ais_infer.py --model $MODEL --output $CACHE_PATH/ \
        --device $DEVICE --loop $LOOP --output_dirname=aisout"
    fi

    [ "$INPUT" != "" ] && { infer_cmd="$infer_cmd --input $INPUT"; }
}

run_infer()
{
    local tool=$1
    get_infer_cmd $tool

    if [ $PROFILER == "true" ]; then
        $msprof_bin --output=${CACHE_PATH} --application="$infer_cmd"  \
            --sys-hardware-mem=on --sys-cpu-profiling=on --sys-profiling=on --sys-pid-profiling=on \
            --dvpp-profiling=on --runtime-api=on --task-time=on --aicpu=on \
        | tee -a $CACHE_PATH/$tool.log || { echo "msprof run failed"; return $ret_run_failed; }
    else
        $infer_cmd | tee -a $CACHE_PATH/$tool.log || { echo "msprof run failed"; return $ret_run_failed; }
    fi

    if [ $TOOL == "msame" ]; then
        cat $CACHE_PATH/$tool.log | grep 'Inference time:' | awk '{print $3}' | sed '1d' > $CACHE_PATH/$tool.times
        cat $CACHE_PATH/$tool.log | grep pid | awk '{print $3}' > $CACHE_PATH/$tool.pid
        $PYTHON_COMMAND $CUR_PATH/info_convert_json.py $CACHE_PATH/$tool.times $CACHE_PATH/$tool.pid $CACHE_PATH/${tool}.json
    else
        cp $CACHE_PATH/aisout/sumary.json $CACHE_PATH/${tool}.json
    fi

    cmd="$PYTHON_COMMAND $CUR_PATH/analyser.py --mode times --summary_path $CACHE_PATH/${tool}.json --output $CACHE_PATH/"
    $cmd || { echo "cmd:$cmd analyse times failed"; return $ret_run_failed; }
}

analyse_plog()
{
    local infer_pid=$(get_infer_pid_from_json "${CACHE_PATH}/aisout/sumary.json")
    [[ "$infer_pid" != "" ]] || { echo "infer_pid:$infer_pid not find";return $ret_run_failed; }
    plog=`find $HOME/ascend/log/ -name "plog-${infer_pid}_*.log"`
    [[ "$plog" != "" ]] || { echo "find no plog for $HOME/ascend/log/plog/plog-${infer_pid}_*.log";return $ret_run_failed; }

    start_aclmdlExecute_str="aclmdlExecute: start to execute aclmdlExecute"
    end_aclmdlExecute_str="aclmdlExecute: aclmdlExecute success"

    infer_count=`cat $plog | grep "$start_aclmdlExecute_str" | wc -l`

    cat $plog | grep "$end_aclmdlExecute_str" | awk 'NR==1{print}'

    local topk_arr=($(get_topk_array_from_json "${CACHE_PATH}/topk_index.json"))
    echo ">>>>>>>>>>>>>>>>>>>>>   sumary topk_arr:$topk_arr infer_count:${infer_count}"
    k=${#topk_arr[@]}
    for ((i=0; i<$k; i++)); do {
        index="${topk_arr[$i]}"
        # add warmup count
        real_index=$((index+2))
        local infer_time=($(get_infer_time_from_json "${CACHE_PATH}/aisout/sumary.json" ${index}))
        start_line=`cat $plog | grep -n "$start_aclmdlExecute_str" | cut -d : -f 1 | sed -n ${real_index}p`
        end_line=`cat $plog | grep -n "$end_aclmdlExecute_str" | cut -d : -f 1 | sed -n ${real_index}p`
        echo ">> top${i} infer_time:${infer_time}"
        sed -n "${start_line},${end_line}p" ${plog}
        echo ""
        echo ""
    } done

    cat $CACHE_PATH/p.log | grep 'Inference time:' | awk '{print $3}' | sed '1d' | sort --version-sort | tail -n 10

    # cmd="$PYTHON_COMMAND $CUR_PATH/analyser.py  --mode plog --plog $plog --summary_path $CACHE_PATH/aisout/sumary.json --output $CACHE_PATH/"
    # $cmd || { echo "cmd:$cmd analyse plog failed"; return $ret_run_failed; }
}

generate_topk_index()
{
    cmd="$PYTHON_COMMAND $CUR_PATH/analyser.py --mode times --summary_path  $CACHE_PATH/aisout/sumary.json --output $CACHE_PATH/"
    $cmd || { echo "cmd:$cmd analyse times failed"; return $ret_run_failed; }
}

get_timeline()
{
    local topk_arr=($(get_topk_array_from_json "${CACHE_PATH}/topk_index.json"))
    echo "topk_arr:$topk_arr"
    k=${#topk_arr[@]}
    profiler_path=`find $CACHE_PATH/ -name "device_*"`
    for ((i=0; i<$k; i++)); do {
        index="${topk_arr[$i]}"
        # add warmup count and 0index
        real_index=$((index+2))
        $msprof_bin --export=on --output=$profiler_path --iteration-id=$real_index >/dev/null  2>&1 || { echo "msprof export failed"; return $ret_run_failed; }
    } done
}

main()
{
    while [ -n "$1" ]
do
  case "$1" in
    -m|--model)
        MODEL=$2
        shift
        ;;
    -p|--python_command)
        PYTHON_COMMAND=$2
        shift
        ;;
    -input|--input)
        INPUT=$2
        shift
        ;;
    -d|--device)
        DEVICE=${2}
        shift
        ;;
    -tool|--tool)
        TOOL=$2
        shift
        ;;
    -profiler|--profiler)
        PROFILER=$2
        shift
        ;;
    -loop|--loop)
        LOOP=$2
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
    [ "$LOOP" != "" ] || { LOOP="1";echo "set default LOOP:$LOOP"; }
    [ "$DEVICE" != "" ] || { DEVICE="0";echo "set default DEVICE:$DEVICE"; }
    [ "$TOOL" != "" ] || { TOOL="ais_infer";echo "set default TOOL:$TOOL"; }
    [ "$PROFILER" != "" ] || { PROFILER="false";echo "set default PROFILER:$PROFILER"; }

    CACHE_PATH=$CUR_PATH/cache
    [ ! -d $CACHE_PATH ] || rm -rf $CACHE_PATH
    mkdir -p $CACHE_PATH

    check_args_valid || { echo "check args not valid return"; return $ret_run_failed; }
    check_env_valid || { echo "check env not valid return"; return $ret_run_failed; }

    if [ $TOOL == "all" ]; then
        run_infer "msame" || { echo "run infer failed"; return $ret_run_failed; }
        run_infer "ais_infer" || { echo "run infer failed"; return $ret_run_failed; }
    else
        run_infer "${TOOL}" || { echo "run infer failed"; return $ret_run_failed; }
    fi

    if [ $PROFILER == "true" ]; then
        get_timeline || { echo "get timeline failed"; return $ret_run_failed; }
    fi

    #analyse_plog || { echo "analyse plog failed"; return $ret_run_failed; }

    return $ret_ok
}

main "$@"
exit $?
