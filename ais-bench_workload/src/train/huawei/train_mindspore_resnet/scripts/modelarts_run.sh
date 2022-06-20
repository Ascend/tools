#!/bin/bash

. $CODE_PATH/common/common.sh
. $CODE_PATH/common/log_util.sh

init()
{
    CONFIG_FILE="config.sh"
    source ${CODE_PATH}/config/$CONFIG_FILE || { logger_Warn "source file failed:$?";return 1; }
    logger_Info "init called"
}

run_train()
{
    logger_Info "run_train called"
    [ ! -f $CODE_PATH/code/ma-pre-start.sh ] && touch $CODE_PATH/code/ma-pre-start.sh
    sed -i '/SINGLESERVER_MODE=/d' $CODE_PATH/code/ma-pre-start.sh
    if [ "$SINGLESERVER_MODE" == "True" ];then
        echo "now set singleserver_mode OK"
        echo -e "\nexport SINGLESERVER_MODE=True" >> $CODE_PATH/code/ma-pre-start.sh

        ${PYTHON_COMMAND} -u ${CODE_PATH}/common/train_modelarts.py --local_code_path $CODE_PATH/code --single_server_mode || { logger_Warn "run train modelarts failed ret:$?";return 1; }
    else
        echo "now not set singleserver_mode"
        ${PYTHON_COMMAND} -u ${CODE_PATH}/common/train_modelarts.py --local_code_path $CODE_PATH/code || { logger_Warn "run train modelarts failed ret:$?";return 1; }
    fi
    ${PYTHON_COMMAND} $CODE_PATH/ais_utils.py set_result "training" "result" "OK"
}

run_eval()
{
    logger_Info "run_eval called"
}

get_result()
{
    logger_Info "get_result called"
}