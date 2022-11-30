#!/bin/bash
CURDIR=$(dirname $(readlink -f $0))
ROOT_PATH=$(readlink -f $CURDIR/../../)
PACKET_NAME="ais-bench-train-tools"
OUTPUT_PATH="$CURDIR/$PACKET_NAME/"

PACKET_TYPE="train"
MANUFACTORY="huawei"

function packet_target()
{
    BASE_PATH="$1"
    TARGETDIR="$2"

    # exec build.sh and cp files
    TARGET_PATH=$ROOT_PATH/src/$PACKET_TYPE/$MANUFACTORY/$TARGETDIR
    if [ -f $TARGET_PATH/build.sh ];then
        bash $TARGET_PATH/build.sh || { echo "warn build target failed"; return $ret_error; }
    fi

    if [ ! -d $TARGET_PATH/output ];then
        echo "targetdir:$TARGET_PATH not find output return"
        return $ret_error
    fi

    BASE_PATH="$1"
    mkdir -p $BASE_PATH/$TARGETDIR

    cp -rf $TARGET_PATH/output/*  $BASE_PATH/$TARGETDIR

    # chanage base_path
    sed -i "s|export WORK_PATH=\${BASE_PATH}.*|export WORK_PATH=\${BASE_PATH}/../result/$TARGETDIR|g" $BASE_PATH/$TARGETDIR/cluster_offline_run.sh

    cp $BASE_PATH/$TARGETDIR/config/config.sh $OUTPUT_PATH/config/$TARGETDIR.sh

    # del common config args
    sed -i '/PYTHON_COMMAND=/d' $OUTPUT_PATH/config/$TARGETDIR.sh
    sed -i '/RANK_SIZE=/d' $OUTPUT_PATH/config/$TARGETDIR.sh
    sed -i '/DEVICE_NUM=/d' $OUTPUT_PATH/config/$TARGETDIR.sh
    sed -i '/RANK_TABLE_FILE=/d' $OUTPUT_PATH/config/$TARGETDIR.sh
    sed -i '/NODEINFO_FILE=/d' $OUTPUT_PATH/config/$TARGETDIR.sh
}

function main()
{
    [ ! -d $OUTPUT_PATH ] || rm -rf $OUTPUT_PATH
    mkdir -p $OUTPUT_PATH
    mkdir -p $OUTPUT_PATH/src
    mkdir -p $OUTPUT_PATH/result
    mkdir -p $OUTPUT_PATH/config

    for path in $ROOT_PATH/src/$PACKET_TYPE/$MANUFACTORY/*; do
        # get train_ prefix folder
        if [[ -d $path && "$(basename "$path")" =~ ^train_.* ]];then
            packet_target "$OUTPUT_PATH/src" "$(basename "$path")"
            echo "$path packet"
        fi
    done

    cp benchmark.sh $OUTPUT_PATH/
    cp common_config.sh $OUTPUT_PATH/config/
    cp *.doc $OUTPUT_PATH/

    cd $CURDIR
    rm -rf $CURDIR/$PACKET_NAME.tar.gz
    tar -czf $CURDIR/$PACKET_NAME.tar.gz $PACKET_NAME
}

main "$@"
exit $?
