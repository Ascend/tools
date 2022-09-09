#!/bin/bash
declare -i ret_ok=0
declare -i ret_invalid_args=1
CUR_PATH=$(dirname $(readlink -f "$0"))
. $CUR_PATH/utils.sh
set -x
set -e

main() {
    if [ $# -lt 1 ]; then
        echo "at least one parameter. for example: bash test.sh python3.7.5"
        return $ret_invalid_args
    fi

    PYTHON_COMMAND=$1
    DATA_PATH=$4

    if [ -f /usr/local/Ascend/nnae/set_env.sh ]; then
        source /usr/local/Ascend/nnae/set_env.sh
    elif [ -f /usr/local/Ascend/ascend-toolkit/set_env.sh ]; then
        source /usr/local/Ascend/ascend-toolkit/set_env.sh
    elif [ -f ~/Ascend/nnae/set_env.sh ]; then
        source ~/Ascend/nnae/set_env.sh
    elif [ -f ~/Ascend/ascend-toolkit/set_env.sh ]; then
        source ~/Ascend/ascend-toolkit/set_env.sh
    else
        echo "warning find no env so not set"
        return $ret_invalid_args
    fi

    check_python_package_is_install $PYTHON_COMMAND "aclruntime" || {
        echo "aclruntime package install failed please install or source set_env.sh"
        return $ret_invalid_args
    }
    echo "python packet aclruntime valid"

    bash -x $CUR_PATH/get_pth_resnet50_data.sh
    #bash -x $CUR_PATH/get_pth_resnet101_data.sh
    #bash -x $CUR_PATH/get_pth_inception_v3_data.sh
    #bash -x $CUR_PATH/get_bert_data.sh
    #bash -x $CUR_PATH/get_yolo_data.sh
    ${PYTHON_COMMAND} -m pytest -s $CUR_PATH/ST/
    ${PYTHON_COMMAND} -m pytest -s $CUR_PATH/UT/

    return $ret_ok
}

main "$@"
exit $?
