#!/bin/bash
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2029. All rights reserved.
# This script used to install mindxedge whitebox

CUR_DIR=$(dirname $(readlink -f "$0"))
SCRIPT_DIR="${CUR_DIR}/scripts"

source ${SCRIPT_DIR}/costant.sh
source ${SCRIPT_DIR}/log_util.sh
source ${SCRIPT_DIR}/file_util.sh

WHITE_BOX_INSTALL_SRC_PATH="${CUR_DIR}"

FILE_LIST=(
install_pre_opt.sh
install_white_box.sh
install_post_opt.sh
)
FILE_SIZE=${#FILE_LIST[*]}

function do_install()
{
    local ret
    is_real_path "${WHITE_BOX_INSTALL_SRC_PATH}"
    ret=$?
    if [[ ${ret} -ne 0 ]]; then
        logger_Error "Install failed: ${WHITE_BOX_INSTALL_SRC_PATH} invalid"
    fi

    is_real_path "${WHITE_BOX_INSTALL_DST_PATH}"
    ret=$?
    if [[ ${ret} -ne 0 ]]; then
        logger_Error "Install failed: ${WHITE_BOX_INSTALL_DST_PATH} invalid"
    fi

    for((i=0;i<$FILE_SIZE;i++));
    do
        local file="${SCRIPT_DIR}/${FILE_LIST[$i]}"
        if [[ ! -f "${file}" ]]; then
            logger_Error "${file} not exist"
            return ${ret_failed_config_file_not_exist}
        fi

        is_real_path "${file}"
        ret=$?
        if [[ ${ret} -ne 0 ]]; then
            logger_Error "${file} invalid"
            return ${ret}
        fi

        bash ${file} ${WHITE_BOX_INSTALL_SRC_PATH} ${WHITE_BOX_INSTALL_DST_PATH} ${OPT_TYPE}
        ret=$?
        if [[ ${ret} -ne 0 ]]; then
            logger_Error "${file} failed. err=${ret}"
            return ${ret}
        fi
    done

    return 0
}

function main()
{
    OPT_TYPE="install"
    WHITE_BOX_INSTALL_DST_PATH="/opt/middleware/MindXOMWhiteBox"
    if [[ "$#" -gt 0 ]]; then
        method=$1
        case "$method" in
            "install")
                OPT_TYPE="install"
            ;;
            "upgrade")
                OPT_TYPE="upgrade"
                WHITE_BOX_INSTALL_DST_PATH="/opt/middleware/MindXOMUpgrade"
            ;;
            * )
                logger_Error "Not support operation: ${OPT_TYPE}"
                exit 1
            ;;
        esac
    fi

    logger_Info "start install whitebox operation:${OPT_TYPE}"

    local ret
    do_install
    ret=$?
    if [[ ${ret} -ne 0 ]]; then
        logger_Error "do_install failed. err=${ret}"
        return ${ret}
    fi

    logger_Info "Install whitebox success!"
    return 0
}

main "$@"
RESULT=$?
exit ${RESULT}