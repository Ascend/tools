#!/bin/bash
CURDIR=$(dirname $(readlink -f $0))
PLATFORM=`uname -i`
PACKET_NAME="aclruntime-$PLATFORM"
OUTPUT_PATH="$CURDIR/$PACKET_NAME/"

main()
{
    [ ! -d $OUTPUT_PATH ] || rm -rf $OUTPUT_PATH
    mkdir -p $OUTPUT_PATH

    cd $OUTPUT_PATH
    rm -rf $CURDIR/backend/*.egg-info $CURDIR/backend/build
    pip3 wheel -v $CURDIR/backend/ || { echo "pip run failed"; return 1; }

    cp $CURDIR/frontend -rf $OUTPUT_PATH/
    cp $CURDIR/requirements.txt $OUTPUT_PATH/
    cp $CURDIR/README.md $OUTPUT_PATH/

    cd $CURDIR
    rm -rf $CURDIR/$PACKET_NAME.tar.gz
    tar -czf $CURDIR/$PACKET_NAME.tar.gz $PACKET_NAME

    rm -rf ${CURDIR}/output/*
    mkdir -p ${CURDIR}/output
    cp $CURDIR/$PACKET_NAME.tar.gz ${CURDIR}/output
}

main "$@"
exit $?
