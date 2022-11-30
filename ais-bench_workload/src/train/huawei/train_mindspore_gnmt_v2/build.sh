#!/bin/bash

declare -i ret_ok=0
declare -i ret_error=1

CURDIR=$(dirname $(readlink -f $0))

file_change()
{
    local run_type=$1
    [ "$run_type" == "modelarts" ] && { sed -i 's|RUNTYPE=.*|RUNTYPE="modelarts"|g' ${CURDIR}//output/benchmark.sh; }
    return 0
}

function main()
{
    rm -rf ${CURDIR}/output/*
    mkdir -p ${CURDIR}/output
    echo "build call args:$@"
    bash $CURDIR/patch.sh loadcode "$@" || { echo "warn run patch failed"; return 1; }
    cp -rf ${CURDIR}/patchcode ${CURDIR}//output/code
    cp -rf ${CURDIR}/scripts/* ${CURDIR}//output/
    cp ${CURDIR}/../../../common -r ${CURDIR}//output/

    mkdir -p ${CURDIR}/output/config
    cp ${CURDIR}/../common/*  -r ${CURDIR}//output/config/
    cp ${CURDIR}/config/config.sh -r ${CURDIR}//output/config/
    cp ${CURDIR}/config/modelarts_config.py -r ${CURDIR}//output/config/
    [ "$1" == "r1.3" ] && { cp ${CURDIR}/config/modelarts_config.py.r1.3 -r ${CURDIR}//output/config/modelarts_config.py; }
    [ -d ${CURDIR}/doc ] && cp ${CURDIR}/doc -r ${CURDIR}/output/

    file_change "$2" || { echo "file change failed"; return 1; }
}

main "$@"
exit $?
