#!/bin/bash

declare -i ret_error=1

CUR_PATH=$(dirname $(readlink -f "$0"))

git_url="https://github.com/google-research/bert.git"
git_url="https://gitee.com/lanhaibo4/bert.git"
branch="master"

master_commitid="eedf5716ce1268e56f0a50264a88cafad334ac61"
bert_sub_dir="bert"

target_dir=$CUR_PATH/code
target_patchcode_dir=$CUR_PATH/patchcode

get_bert_base_code_by_git() {
    git clone $git_url -b $branch
    cd $bert_sub_dir
    git reset --hard $commitid
    cd -
}

make_patch() {
    cd $BUILD_TMP_PATH
    get_bert_base_code_by_git
    cp $bert_sub_dir -rf $BUILD_TMP_PATH/origin
    cp $target_dir -rf $BUILD_TMP_PATH/code

    diff -Nur -x ".git*" origin code >$BUILD_TMP_PATH/$branch.patch

    cp $BUILD_TMP_PATH/$branch.patch $CUR_PATH/
}

load_code() {
    cd $BUILD_TMP_PATH
    get_bert_base_code_by_git
    cp $bert_sub_dir -rf $BUILD_TMP_PATH/origin
    cp $bert_sub_dir -rf $BUILD_TMP_PATH/code

    patch -p0 <$CUR_PATH/$branch.patch

    [ ! -d $target_patchcode_dir ] || rm -rf $target_patchcode_dir
    mkdir $target_patchcode_dir
    cp $BUILD_TMP_PATH/code/* -rf $target_patchcode_dir/
}

main() {
    if [ "$1" != "mkpatch" -a "$1" != "loadcode" ]; then
        echo "target not valid in:[$1] not match [mkpatch loadcode]"
        return $ret_error
    fi

    commitid=$master_commitid

    echo "patch.sh run type:$1 branch:$branch"

    BUILD_TMP_PATH=$CUR_PATH/buildtmp
    [ ! -d $BUILD_TMP_PATH ] || rm -rf $BUILD_TMP_PATH
    mkdir -p $BUILD_TMP_PATH

    if [ "$1" == "mkpatch" ]; then
        make_patch
    elif [ "$1" == "loadcode" ]; then
        load_code
    else
        echo "null op"
    fi
}

main "$@"
exit $?
