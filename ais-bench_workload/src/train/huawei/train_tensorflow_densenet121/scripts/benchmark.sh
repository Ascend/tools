#!/bin/bash

# 返回码
declare -i ret_ok=0
declare -i ret_init_failed=1
declare -i ret_run_train_failed=2
declare -i ret_run_eval_failed=3
declare -i ret_get_result_failed=4

CUR_PATH=$(dirname $(readlink -f "$0"))
export CODE_PATH=$CUR_PATH
export BASE_PATH=$(cd "$CUR_PATH/../";pwd)

. $CODE_PATH/common/log_util.sh
. $CODE_PATH/common/common.sh

RUNTYPE="cluster_offline"

[ $RUNTYPE == "modelarts" ] && . $CODE_PATH/modelarts_run.sh
[ $RUNTYPE == "cluster_offline" ] && . $CODE_PATH/cluster_offline_run.sh

main(){
    init || { logger_Warn "init failed:$?";return $ret_init_failed; }
    run_train || { logger_Warn "run_train failed ret:$?";return $ret_run_train_failed; }
    run_eval || { logger_Warn "run_eval failed ret:$?";return $ret_run_eval_failed; }
    get_result || { logger_Warn "get_result failed ret:$?";return $ret_get_result_failed; }
    return $ret_ok
}

main "$@"
exit $?
