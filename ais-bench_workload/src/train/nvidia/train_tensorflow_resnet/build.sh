#!/bin/bash

declare -i ret_ok=0
declare -i ret_error=1

CURDIR=$(dirname $(readlink -f $0))

function main()
{
    rm -rf ${CURDIR}/output/*
    mkdir -p ${CURDIR}/output
    echo "build call args:$@"
    bash $CURDIR/patch.sh loadcode "$@" || { echo "warn run patch failed"; return 1; }
    cp -rf ${CURDIR}/patchcode ${CURDIR}//output/code
    cp ${CURDIR}/scripts/* ${CURDIR}//output/
    cp ${CURDIR}/../../../common -r ${CURDIR}//output/
    cp ${CURDIR}/config -r ${CURDIR}//output/
}

main "$@"
exit $?