#!/bin/bash

CURRENT_PATH=$(cd "$(dirname "$0")";pwd)
WORK_PATH=${CURRENT_PATH}
OUTPUT_PATH=${CURRENT_PATH}/output

prepare(){
    [ ! -d $OUTPUT_PATH ] || rm -rf $OUTPUT_PATH
    mkdir -p $OUTPUT_PATH

    mkdir -p ${WORK_PATH}/libs/
    mkdir -p ${WORK_PATH}/include

    export CMAKE_LIBRARY_PATH=${WORK_PATH}/libs/
    export CMAKE_INCLUDE_PATH=${WORK_PATH}/include
}

copy_files()
{
    cp -rf $WORK_PATH/*.py $OUTPUT_PATH/
    cp -rf $WORK_PATH/*.md $OUTPUT_PATH/
    cp -rf $WORK_PATH/*.txt $OUTPUT_PATH/
    cp -rf $WORK_PATH/config $OUTPUT_PATH/
    cp -rf $WORK_PATH/yolo $OUTPUT_PATH/
    cp -rf $WORK_PATH/benchmark.sh $OUTPUT_PATH/
    cp ${WORK_PATH}/../../../common -r ${OUTPUT_PATH}/
    cp ${WORK_PATH}/../../core -r ${OUTPUT_PATH}/
}

main(){
    prepare
    copy_files
}

main "$@"
exit $?