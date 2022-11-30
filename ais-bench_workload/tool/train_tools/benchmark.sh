#!/bin/bash

CURDIR=$(dirname $(readlink -f $0))

echo_help(){
    echo ""
    echo "    -e  需要执行的模型名称"
    echo ""
    echo "    --help, -h       显示帮助信息"
    echo "    --list, -l       显示支持的框架与模型"
    echo ""
    exit 0
}

check()
{
    [ "$execModel" == "" ] && { echo "execModel not set"; return 1; }
    [ -d $CURDIR/src/$execModel/ ] || { echo "$CURDIR/src/$execModel/ not exist";return 1; }
    [ -f $CURDIR/config/$execModel.sh ] || { echo "$CURDIR/config/$execModel.sh not exist";return 1; }
    [ -f $CURDIR/src/$execModel/benchmark.sh ] || { echo "$CURDIR/src/$execModel/benchmark.sh not exist";return 1; }
    return 0
}

update_common_config()
{
    CONFIGFILE="$CURDIR/config/common_config.sh"
    source $CONFIGFILE

    cp $CURDIR/config/$execModel.sh $CURDIR/src/$execModel/config/config.sh

    if [ "$PYTHON_COMMAND" != "" ];then
        sed -i '/PYTHON_COMMAND=/d' $CURDIR/src/$execModel/config/config.sh
        echo -e "\nexport PYTHON_COMMAND=$PYTHON_COMMAND" >> $CURDIR/src/$execModel/config/config.sh
    fi
    if [ "$RANK_SIZE" != "" ];then
        sed -i '/RANK_SIZE=/d' $CURDIR/src/$execModel/config/config.sh
        echo -e "\nexport RANK_SIZE=$RANK_SIZE" >> $CURDIR/src/$execModel/config/config.sh
    fi
    if [ "$DEVICE_NUM" != "" ];then
        sed -i '/DEVICE_NUM=/d' $CURDIR/src/$execModel/config/config.sh
        echo -e "\nexport DEVICE_NUM=$DEVICE_NUM" >> $CURDIR/src/$execModel/config/config.sh
    fi
    if [ "$RANK_TABLE_FILE" != "" ];then
        sed -i '/RANK_TABLE_FILE=/d' $CURDIR/src/$execModel/config/config.sh
        echo -e "\nexport RANK_TABLE_FILE=$RANK_TABLE_FILE" >> $CURDIR/src/$execModel/config/config.sh
    fi
    if [ "$NODEINFO_FILE" != "" ];then
        sed -i '/NODEINFO_FILE=/d' $CURDIR/src/$execModel/config/config.sh
        echo -e "\nexport NODEINFO_FILE=$NODEINFO_FILE" >> $CURDIR/src/$execModel/config/config.sh
    fi

    echo "$execModel configfile is :"
    cat $CURDIR/src/$execModel/config/config.sh
}

main()


{
    check || { echo "check failed"; return 1; }
    ( update_common_config ) || { echo "update common config failed"; return 1; }

    echo "$execModel begin run"
    bash $CURDIR/src/$execModel/benchmark.sh || { echo "run_node_train failed"; return 1; }
    echo "$execModel end run"
    [ -f $CURDIR/result/$execModel/result.log ] && { echo "result:";cat $CURDIR/result/$execModel/result.log;echo -e "\n"; }
}

list_model ()
{
    echo "support models:"
    ls $CURDIR/src
}

while [ -n "$1" ]
do
  case "$1" in
    -e|--execmodel)
        execModel=$2;
        shift
        ;;
    -l|--list)
        list_model;
        exit
        ;;
    -h|--help)
        echo_help;
        exit
        ;;
    *)
        echo "$1 is not an option, please use --help"
        exit 1
        ;;
  esac
  shift
done

main "$@" | tee -a $CURDIR/benchmark.log
exit $?
