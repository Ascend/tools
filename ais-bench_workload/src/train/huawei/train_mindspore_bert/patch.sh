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
    [[ -z "$branch_args" ]] && { branch_args="r1.5"; }

    modelzoo_sub_dir="mindspore/model_zoo/official/nlp/bert"
    if [ "$branch_args" == "r1.1" ];then
        branch="r1.1"
        patch_file_name="r1.1"
        commitid="9c133b6f709e12ed7085c31f028e7c925ee57828"
        git_url="https://gitee.com/mindspore/mindspore.git"
    elif [ "$branch_args" == "r1.2" ];then
        branch="r1.2"
        patch_file_name="r1.2"
        commitid="cd002779dc5e2bc2da85b9a33e8950aa3bb50ed2"
        git_url="https://gitee.com/mindspore/mindspore.git"
    elif [ "$branch_args" == "r1.3" ];then
        branch="r1.3"
        patch_file_name="r1.3"
        commitid="d9d4960262617d964d669ef8e3287daf347d5a7c"
        git_url="https://gitee.com/mindspore/mindspore.git"
    elif [ "$branch_args" == "r1.5" ];then
        branch="master"
        patch_file_name="r1.5"
        commitid="a6cbc7bc9e23fd04b53a406e72ba87e88d7980d0"
        git_url="https://gitee.com/mindspore/models.git"
        modelzoo_sub_dir="models/official/nlp/bert"
    elif [ "$branch_args" == "r1.6" ];then
        branch="r1.6"
        patch_file_name="r1.6"
        commitid="6496c699bd404076b12a6edcc40889dafaeb5285"
        git_url="https://gitee.com/mindspore/models.git"
        modelzoo_sub_dir="models/official/nlp/bert"
    elif [ "$branch_args" == "r1.7" ];then
        branch="master"
        patch_file_name="r1.7"
        commitid="3406fdabaee92f1b22ce0703fa25befa3c40d18e"
        git_url="https://gitee.com/mindspore/models.git"
        modelzoo_sub_dir="models/official/nlp/bert"
    elif [ "$branch_args" == "r1.8" ];then
        branch="master"
        patch_file_name="r1.8"
        commitid="b68b6bfa919465567d89bc7fdcf6d0e63967d5aa"
        git_url="https://gitee.com/mindspore/models.git"
        modelzoo_sub_dir="models/official/nlp/bert"
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
