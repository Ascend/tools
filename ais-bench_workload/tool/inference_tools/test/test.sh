CUR_PATH=$(dirname $(readlink -f "$0"))

. $CUR_PATH/resnet_test.sh
. $CUR_PATH/bert_test.sh
. $CUR_PATH/yolo_test.sh

download_packet()
{
    url=$1
    target_file=$2

    cmd="wget $url --no-check-certificate"
    [ "$target_file" != "" ]  && cmd="$cmd -O $target_file"
    echo "try download packet cmd:$cmd"
    #timeout 6400 $cmd
    $cmd
    echo "try download packet cmd:$cmd finish"
}

main(){

    MODEL_TYPE=$1
    MODEL_PATH=$2
    DATA_PATH=$3

    source /usr/local/Ascend/ascend-toolkit/set_env.sh

    export PYTHON_COMMAND=python3.7

    if [ "$MODEL_TYPE" == "resnet" ];then
        mkdir -p $CUR_PATH/resnet
        resnet_test $MODEL_PATH $DATA_PATH $CUR_PATH/resnet || { echo "resnet run failed"; return 1; }
    elif [ "$MODEL_TYPE" == "bert" ];then
        mkdir -p $CUR_PATH/bert
        bert_test $MODEL_PATH $DATA_PATH $CUR_PATH/bert || { echo "bert run failed"; return 1; }
    elif [ "$MODEL_TYPE" == "yolo" ];then
        mkdir -p $CUR_PATH/yolo
        yolo_test $MODEL_PATH $DATA_PATH $CUR_PATH/yolo || { echo "yolo run failed"; return 1; }
    fi

    return $ret_ok
}

main "$@"
exit $?