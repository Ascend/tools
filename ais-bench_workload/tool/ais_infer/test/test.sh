CUR_PATH=$(dirname $(readlink -f "$0"))

set -x
set -e

main(){

    MODEL_TYPE=$1
    MODEL_PATH=$2
    DATA_PATH=$3

    source /usr/local/Ascend/ascend-toolkit/set_env.sh

    bash -x $CUR_PATH/get_pth_resnet50_data.sh
    bash -x $CUR_PATH/get_pth_resnet101_data.sh
    bash -x $CUR_PATH/get_pth_inception_v3_data.sh
    bash -x $CUR_PATH/get_bert_data.sh
    bash -x $CUR_PATH/get_yolo_data.sh
    pytest -s $CUR_PATH/ST/
    pytest -s $CUR_PATH/UT/

    return $ret_ok
}

main "$@"
exit $?