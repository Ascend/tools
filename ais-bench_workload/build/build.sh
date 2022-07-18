#!/bin/bash

declare -i ret_ok=0
declare -i ret_error=1

CURDIR=$(dirname $(readlink -f $0))
ROOT_PATH=$(readlink -f $CURDIR/../)
OUTPUT_PATH="$ROOT_PATH/output/"

export VERSION="1.0"

check_command_exist()
{
    command=$1
    if type $command >/dev/null  2>&1;then
        return 0
    else
        return 1
    fi
}

function check_env()
{
    check_command_exist git || { echo "git running failed" ; return 1; }
    return $ret_ok
}

function get_and_check_args()
{
    # check args num is valid
    [ $# -ge 4 ] || { echo "args should >=3 not valid";return 1; }

    STUBS_PACKETS=$1
    STUBS_NAME=$(basename $STUBS_PACKETS)
    STUBS_SUBNAME=${STUBS_NAME%.tar.gz}

    # according type get application base dir
    basedir="$2"
    manufactory_group=`ls $ROOT_PATH/src/$basedir`
    echo $manufactory_group | grep -wq "$3" ||  { echo "$3 not invliad in [$manufactory_group] return";return 1; }
    MANUFACTORY=$3

    target_group=`ls $ROOT_PATH/src/$basedir/$MANUFACTORY`
    echo $target_group | grep -wq "$4" || { echo "$4 not invliad in [$target_group] return";return 1; }
    TARGETDIR=$4

    shift
    shift
    shift
    shift
    scripts_args="$@"
}

# copy doc files to packet
copy_doc_files()
{
    local branch_args="$1"
    local run_type="$2"

    [ -d $OUTPUT_BASE_DIR/code/doc/ ] || mkdir -p $OUTPUT_BASE_DIR/code/doc/
    cp $ROOT_PATH/doc/*.md $OUTPUT_BASE_DIR/code/doc/

    [[ "$PACKET_TYPE" == "inference" ]] && { cp $OUTPUT_BASE_DIR/code/doc/ais-bench_workload_inference*.md $OUTPUT_BASE_DIR/README.md;return; }

    # train modelarts mode
    [[ "$PACKET_TYPE" == "train" && "$run_type" == "modelarts" ]] && { cp $OUTPUT_BASE_DIR/code/doc/ais-bench_workload_train_modelarts*.md $OUTPUT_BASE_DIR/README.md;return; }
    # default as train offline mode
    cp $OUTPUT_BASE_DIR/code/doc/ais-bench_workload_train_offline*.md $OUTPUT_BASE_DIR/README.md
}

function build_packet()
{
    get_and_check_args "$@" || { echo "get check args failed ret:$ret";return $ret_error; }

    PACKET_TYPE="$2"

    BUILD_TMP_PATH=$CURDIR/buildtmp
    [ ! -d $BUILD_TMP_PATH ] || rm -rf $BUILD_TMP_PATH
    mkdir -p $BUILD_TMP_PATH

    # untar packfile
    tar xvf $STUBS_PACKETS -C $BUILD_TMP_PATH || { echo "tar file failed ret";return $ret_error; }

    # exec build.sh and cp files
    TARGET_PATH=$ROOT_PATH/src/$PACKET_TYPE/$MANUFACTORY/$TARGETDIR
    if [ -f $TARGET_PATH/build.sh ];then
        bash $TARGET_PATH/build.sh $scripts_args || { echo "warn build target failed"; return $ret_error; }
    fi

    if [ ! -d $TARGET_PATH/output ];then
        echo "targetdir:$TARGET_PATH not find output return"
        return $ret_error
    fi

    cd $BUILD_TMP_PATH
    # get untar dir
    OUTPUT_BASE_DIR=`find ./ -name "Ais-Benchmark-Stubs*" -type d`
    if [[ ! -d "$OUTPUT_BASE_DIR" || ! -d "$OUTPUT_BASE_DIR/code" ]];then
        echo "find no path:$OUTPUT_BASE_DIR return"
        return $ret_error
    fi

    cp $TARGET_PATH/output/* -rf $OUTPUT_BASE_DIR/code
    chmod -R u+x $OUTPUT_BASE_DIR/code

    # for stubs old versions add adapter new ais_utils.py file
    [ ! -f $OUTPUT_BASE_DIR/code/ais_utils.py ] && { cp ${ROOT_PATH}/src/ais_utils_adapter.py $OUTPUT_BASE_DIR/code/ais_utils.py; }

    copy_doc_files $scripts_args
    
    #PLATFORM=`uname -i`
    # OUTPUT_PACKET_NAME="$PACKET_TYPE"_"$MANUFACTORY"_"$TARGETDIR-Ais-Bench-$PLATFORM-${scripts_args// /_}"
    OUTPUT_PACKET_NAME="$PACKET_TYPE"_"$MANUFACTORY"_"$TARGETDIR-$STUBS_SUBNAME-${scripts_args// /_}"
    rm -rf $OUTPUT_PATH/$OUTPUT_PACKET_NAME.tar.gz
    mv $OUTPUT_BASE_DIR $OUTPUT_PACKET_NAME
    tar -czf $OUTPUT_PATH/$OUTPUT_PACKET_NAME.tar.gz  $OUTPUT_PACKET_NAME
    ret=$?
    if [ $ret != 0 ];then
        echo "tar out packet failed ret:$ret"
        return $ret_error
    fi
    return $ret_ok
}

function main()
{
    [[ $1 == *"tar.gz" && -f $1 ]] || { echo "args1:$1 not valid file" ; return 1; }

    if [ "$2" != "inference" -a "$2" != "train" ];then
        echo "target not valid in:[$1] not match [train inference]"
        return $ret_error
    fi

    [ -d $OUTPUT_PATH ] || { mkdir -p $OUTPUT_PATH; }

    target=$2
    echo "target:$target now building"
    check_env || { ret=$?;echo "check env failed ret:$ret";return $ret; }

    if [ "$target" == "inference" -o "$target" == "train" ];then
        build_packet "$@" || { echo "build build_inference failed:$?";return 1; }
    else
        echo "target:$target return"
        return 1
    fi
    echo "target:$target now build done"
    return $ret_ok
}

main "$@"
exit $?
