#!/bin/bash

declare -i ret_ok=0
declare -i ret_error=1

CUR_PATH=$(dirname $(readlink -f "$0"))

target_dir=$CUR_PATH/code
target_patchcode_dir=$CUR_PATH/patchcode

SRC_PATH=$CUR_PATH/../../../
. $SRC_PATH/common/patch_common.sh

get_git_info(){
    local branch_args="$1"
    local run_type="$2"

    # set default branch
    [[ -z "$branch_args" ]] && { branch_args="master"; }

    if  [ "$branch_args" == "master" ];then
        branch="master"
        patch_file_name="master"
        commitid="ca293a6071e44f6286e9ef3c1415c9818c1dd7af"
        git_url="https://github.com/Ascend/ModelZoo-TensorFlow.git"
        modelzoo_sub_dir="ModelZoo-TensorFlow/TensorFlow/built-in/cv/image_classification/Resnet50v1.5_ID1721_for_TensorFlow"
    else
        echo "bad parameters : $1"
        return $ret_error
    fi

    [ "$run_type" == "modelarts" ] && { patch_file_name="modelarts_"$patch_file_name; }
    return $ret_ok
}

main(){
    if [ "$1" != "mkpatch" -a "$1" != "loadcode" ];then
        echo "target not valid in:[$1] not match [mkpatch loadcode]"
        return $ret_error
    fi

    local patch_type="$1"
    local branch_args="$2"
    local run_type="$3"

    get_git_info "$branch_args" "$run_type" || { echo "warn get git info failed"; return $ret_error; }

    BUILD_TMP_PATH=$CUR_PATH/buildtmp
    [ ! -d $BUILD_TMP_PATH ] || rm -rf $BUILD_TMP_PATH
    mkdir -p $BUILD_TMP_PATH

    if [ "$patch_type" == "mkpatch" ];then
        make_patch || { echo "warn make patch failed"; return $ret_error; }
    elif [ "$patch_type" == "loadcode" ];then
        load_code || { echo "warn make patch failed"; return $ret_error; }
        mkdir -p $CUR_PATH/doc
        mk_version_file $CUR_PATH/doc/version.txt
    else
        echo "null op"
        return $ret_error
    fi
}

main "$@"
exit $?
