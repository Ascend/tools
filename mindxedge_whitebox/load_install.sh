#!/bin/bash
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2029. All rights reserved.
# This script used to install mindxedge whitebox

CUR_DIR=$(dirname $(readlink -f "$0"))
INSTALL_SCRIPT_PATH="${CUR_DIR}/install_whitebox.sh"
INSTALL_ZIP_PATH=""
WHITE_BOX_DIR="/home/data/WhiteBox"
WHITE_BOX_PKG_DIR="/home/data/WhiteBox/pkg"
WHITE_BOX_TMP_PATH="/home/data/WhiteBox/tmp"
WHITE_BOX_ZIP_DIR=""
LOG_FILE="/var/plog/upgrade.log"

function do_check_all()
{
    if [[ "$(whoami)" != "root" ]]; then
        echo "Install failed:user not root!" >> ${LOG_FILE}
        return 1
    fi

    if [[ ! -f "${INSTALL_SCRIPT_PATH}" ]]; then
        echo "${INSTALL_SCRIPT_PATH} not exist" >> ${LOG_FILE}
        return 2
    fi

    local zip_name=$(ls -l ${CUR_DIR} | grep "Ascend-mindxedge-whitebox.\{1,\}.zip$" | awk '{print $9}')
    if [[ -z "${zip_name}" ]]; then
        echo "no whitebox zip in ${CUR_DIR}!" >> ${LOG_FILE}
        return 3
    fi

    INSTALL_ZIP_PATH=${CUR_DIR}/${zip_name}
    WHITE_BOX_ZIP_DIR=${WHITE_BOX_DIR}/${zip_name}
    return 0
}

function do_create_dst_path()
{
    if [ ! -d "${WHITE_BOX_DIR}" ]; then
        mkdir -p ${WHITE_BOX_DIR} && chmod 640 ${WHITE_BOX_DIR}
    fi

    rm -rf ${WHITE_BOX_PKG_DIR}
    if [ ! -d "${WHITE_BOX_PKG_DIR}" ]; then
        mkdir -p ${WHITE_BOX_PKG_DIR} && chmod 640 ${WHITE_BOX_PKG_DIR}
    fi

    rm -rf ${WHITE_BOX_TMP_PATH}
    if [ ! -d "${WHITE_BOX_TMP_PATH}" ]; then
        mkdir -p ${WHITE_BOX_TMP_PATH} && chmod 640 ${WHITE_BOX_TMP_PATH}
    fi

    return 0
}

function do_unzip_package()
{
    unzip ${INSTALL_ZIP_PATH} -d ${WHITE_BOX_PKG_DIR}

    mv ${INSTALL_ZIP_PATH} ${WHITE_BOX_DIR}

    local tar_gz_name=$(ls -l ${WHITE_BOX_PKG_DIR} | grep "Ascend-mindxedge-whitebox.\{1,\}.tar.gz$" | awk '{print $9}')
    if [[ -z "${tar_gz_name}" ]]; then
        echo "no whitebox tar.gz in ${WHITE_BOX_PKG_DIR}!" >> ${LOG_FILE}
        return 3
    fi

    tar -zxvf ${WHITE_BOX_PKG_DIR}/${tar_gz_name} -C ${WHITE_BOX_TMP_PATH}
    mv ${INSTALL_SCRIPT_PATH} ${WHITE_BOX_TMP_PATH}
    chmod +x ${WHITE_BOX_TMP_PATH}/install_whitebox.sh
    return 0
}

function do_install_package()
{
    cd ${WHITE_BOX_TMP_PATH}
    /bin/bash install_whitebox.sh install
    local ret=$?
    return ${ret}
}

function do_delete_package()
{
    rm -rf ${WHITE_BOX_PKG_DIR}
    rm -rf ${WHITE_BOX_TMP_PATH}/*
    rm -rf ${WHITE_BOX_ZIP_DIR}
    return 0
}

function do_restart_service()
{
    echo "Install success will restart all service!"
    echo "Install success will restart all service!" >> ${LOG_FILE}

    local service=("ibma-edge-start" "platform-app" "om-init")
    for ((i = 0; i < ${#service[@]}; i++)); do
        echo "stop ${service[i]} service"
        echo "stop ${service[i]} service" >> ${LOG_FILE}
        systemctl stop ${service[i]} > /dev/null 2>&1
    done

    service=("om-init" "platform-app" "ibma-edge-start")
    for ((i = 0; i < ${#service[@]}; i++)); do
        echo "start ${service[i]} service"
        echo "start ${service[i]} service" >> ${LOG_FILE}
        systemctl start ${service[i]} > /dev/null 2>&1
    done

    echo "restart all service end!"
    echo "restart all service end!" >> ${LOG_FILE}
}

function do_work()
{
    local ret
    do_check_all
    ret=$?
    if [[ ${ret} -ne 0 ]]; then
        echo "do_check_all failed,err=${ret}" >> ${LOG_FILE}
        return ${ret}
    fi

    do_create_dst_path
    ret=$?
    if [[ ${ret} -ne 0 ]]; then
        echo "do_create_dst_path failed,err=${ret}" >> ${LOG_FILE}
        return ${ret}
    fi

    do_unzip_package
    ret=$?
    if [[ ${ret} -ne 0 ]]; then
        echo "do_unzip_package failed,err=${ret}" >> ${LOG_FILE}
        do_delete_package
        return ${ret}
    fi

    do_install_package
    ret=$?
    if [[ ${ret} -ne 0 ]]; then
        echo "do_install_package failed,err=${ret}" >> ${LOG_FILE}
        do_delete_package
        return ${ret}
    fi

    do_delete_package

    echo "Install whitebox success" >> ${LOG_FILE}
    return 0
}

function main()
{
    local ret
    do_work
    ret=$?
    if [[ ${ret} -ne 0 ]]; then
        echo "Install whitebox failed,err=${ret}"
        return ${ret}
    fi

    echo "Install whitenox success"
    do_restart_service
    return 0
}

main
RESULT=$?
exit ${RESULT}