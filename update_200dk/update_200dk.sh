#!/bin/bash
#
#   =======================================================================
#
# Copyright (c) Huawei Technologies Co., Ltd. 2019-2020. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   1 Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#   2 Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   3 Neither the names of the copyright holders nor the names of the
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#   =======================================================================
# ************************Variable*********************************************
ScriptPath="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )"
# ************************check Ascend package********************************
# Description:  check Ascend package valid or not
# ******************************************************************************
function CheckPackage()
{ 
    declare -a cann_array
    declare -i cann_array_item=0
    for i in $(ls Ascend-cann-nnrt_*.run 2>/dev/null);do
        cann_array[$((cann_array_item++))]=${i}
    done
    length=${#cann_array[@]}
    if [[ ${length} -gt 1 ]];then
        echo "There are multiple cann packages"
        echo "Current cann packages list:"
        for (( i=0; i<$length; i++ ));do
            echo "$(expr $i + 1) : ${cann_array[i]}"
        done
        CANN_CHOICE=""
        declare -i CHOICE_TIMES=1
        while [[ ${CANN_CHOICE}"x" = "x" ]];do
            # three times choice 
            [[ ${CHOICE_TIMES} -gt 3 ]] && break || ((CHOICE_TIMES++))

            read -p "Please input your cann package in this list(eg:1):" CANN_CHOICE
            if [[ $CANN_CHOICE"x" = "x" ]]; then
                echo "[ERROR] Input empty,please input cann package choice(eg:1)"
            else
                for i in `seq  1 ${length}`;do
                    if [[ "${CANN_CHOICE}" = "${i}" ]];then
                        break
                    fi

                    if [[ "${i}" = "${length}" ]] && [[ "${CANN_CHOICE}" != "${i}" ]];then
                        echo "Input CANN_CHOICE Error,Please check your input"
                        CANN_CHOICE=""
                    fi
                done
            fi
        done 
        if [[ ${CHOICE_TIMES} -gt 3 ]];then
            return 1
        fi
        CANN_PACKAGE=${cann_array[$(expr ${CANN_CHOICE} - 1)]}
    elif [[ ${length} -eq 0 ]];then
        echo "[ERROR] find Ascend-cann-nnrt_*.run failed. please put this package in this folder."
        return 1
    elif [[ ${length} -eq 1 ]];then
        CANN_PACKAGE=${cann_array[0]}
    fi

    chmod 750 ${CANN_PACKAGE}

    ./${CANN_PACKAGE} --extract=${ScriptPath}/nnrt --noexec
    if [[ $? -ne 0 ]] || [[ $(find ${ScriptPath}/nnrt/run_package/Ascend-acllib-*-linux.aarch64.run)"x" = "x" ]] || [[ $(find ${ScriptPath}/nnrt/run_package/Ascend-pyACL-*-linux.aarch64.run)"x" = "x" ]];then
        echo "[ERROR] extract Ascend-cann-nnrt_*_linux-aarch64.run failed. please check this package."
        return 1
    fi
    if [[ $(find ${ScriptPath}/nnrt/run_package/Ascend310-aicpu_kernels*minirc*.run)"x" != "x" ]];then
        AICPU_KERNELS_PACKAGE=$(ls ${ScriptPath}/nnrt/run_package/Ascend310-aicpu_kernels*minirc*.run)
	    AICPU_FLAG=0
    elif [[ $(find ${ScriptPath}/nnrt/run_package/Ascend310-aicpu_kernels-*-minirc.tar.gz)"x" != "x" ]];then
        AICPU_KERNELS_PACKAGE=$(ls ${ScriptPath}/nnrt/run_package/Ascend310-aicpu_kernels-*-minirc.tar.gz)
        AICPU_FLAG=1
    else
        echo "[ERROR] extract Ascend-cann-nnrt_*_linux-aarch64.run failed. please check this package."
        return 1
    fi
    echo "AICPU_FLAG is ${AICPU_FLAG}"

    ACLLIB_PACKAGE=$(ls ${ScriptPath}/nnrt/run_package/Ascend-acllib-*-linux.aarch64.run)
    PYACL_PACKAGE=$(ls ${ScriptPath}/nnrt/run_package/Ascend-pyACL-*-linux.aarch64.run)
    echo ${AICPU_KERNELS_PACKAGE}
    return 0
}

# ************************upgrade Aicpu package********************************
function UpgradeAicpu()
{
    echo "[INFO] start the installation"
    tar zxvf ${AICPU_KERNELS_PACKAGE}
    ./aicpu_kernels_device/scripts/install.sh --run
    rm -rf ./aicpu_kernels_device
    return 0
}

function UpgradeAicpu_run()
{
    aicpu_old=`cat /var/davinci/aicpu_kernels/version.info |head -n 1|cut -d '.' -f 2`
    if [[ ${aicpu_old} -eq '' ]];then
        echo "[INFO] Aicpu is not installed, start the installation"
        chown HwHiAiUser:HwHiAiUser ${AICPU_KERNELS_PACKAGE}
        echo "y
        " | su HwHiAiUser -c "${AICPU_KERNELS_PACKAGE} --run"
        rm -f ${AICPU_KERNELS_PACKAGE}
    else
        echo "[INFO] start upgrade Aicpu"
        chown HwHiAiUser:HwHiAiUser ${AICPU_KERNELS_PACKAGE}
        echo "y
        " | su HwHiAiUser -c "${AICPU_KERNELS_PACKAGE} --run"
        rm -f ${AICPU_KERNELS_PACKAGE}
    fi

    grep "export ASCEND_AICPU_PATH=/home/HwHiAiUser/Ascend" /home/HwHiAiUser/.bashrc > /dev/null
    if [ $? -ne 0 ];then
        echo "export ASCEND_AICPU_PATH=/home/HwHiAiUser/Ascend" >> /home/HwHiAiUser/.bashrc 
    fi

    grep "export LD_LIBRARY_PATH=/usr/lib64/aicpu_kernels/0/aicpu_kernels_device:\$LD_LIBRARY_PATH" /home/HwHiAiUser/.bashrc > /dev/null
    if [ $? -ne 0 ];then
        echo "export LD_LIBRARY_PATH=/usr/lib64/aicpu_kernels/0/aicpu_kernels_device:\$LD_LIBRARY_PATH" >> /home/HwHiAiUser/.bashrc
    fi

    export ASCEND_AICPU_PATH=/home/HwHiAiUser/Ascend
    if [ -f "/home/HwHiAiUser/Ascend/run_aicpu_toolkit.sh" ];then
        sh /home/HwHiAiUser/Ascend/run_aicpu_toolkit.sh
        if [ $? -ne 0 ];then
        return 1
        fi
    fi
}

# ************************upgrade Acllib package********************************
function UpgradeAcllib()
{
    acllib_old=`cat /home/HwHiAiUser/Ascend/acllib/version.info |head -n 1|cut -d '.' -f 2`

    grep "export LD_LIBRARY_PATH=/home/HwHiAiUser/Ascend/acllib/lib64:\$LD_LIBRARY_PATH" /home/HwHiAiUser/.bashrc > /dev/null
    if [ $? -ne 0 ];then
        echo "export LD_LIBRARY_PATH=/home/HwHiAiUser/Ascend/acllib/lib64:\$LD_LIBRARY_PATH" >> /home/HwHiAiUser/.bashrc
    fi

    if [[ ${acllib_old} -eq '' ]];then
        echo "[INFO] Acllib is not installed, start the installation"
        chown HwHiAiUser:HwHiAiUser ${ACLLIB_PACKAGE}
        echo "y
        " | su HwHiAiUser -c "${ACLLIB_PACKAGE} --run"
        rm -f ${ACLLIB_PACKAGE}
        return 0
    else
        echo "[INFO] start upgrade Acllib"
        chown HwHiAiUser:HwHiAiUser ${ACLLIB_PACKAGE}
        echo "y
        " | su HwHiAiUser -c "${ACLLIB_PACKAGE} --upgrade"
        rm -f ${ACLLIB_PACKAGE}
        return 0
    fi
}

# ************************upgrade Pyacl package********************************
function UpgradePyacl()
{
    pyacl_old=`cat /home/HwHiAiUser/Ascend/pyACL/ascend-pyACL_install.info |head -n 1|cut -d '.' -f 2`

    grep "export PYTHONPATH=/home/HwHiAiUser/Ascend/pyACL/python/site-packages/acl:\$PYTHONPATH" /home/HwHiAiUser/.bashrc > /dev/null
    if [ $? -ne 0 ];then
        echo "export PYTHONPATH=/home/HwHiAiUser/Ascend/pyACL/python/site-packages/acl:\$PYTHONPATH" >> /home/HwHiAiUser/.bashrc
    fi
    
    if [[ ${pyacl_old} -eq '' ]];then
        echo "[INFO] pyacl is not installed, start the installation"
        chown HwHiAiUser:HwHiAiUser ${PYACL_PACKAGE}
        su HwHiAiUser -c "${PYACL_PACKAGE} --run"
        rm -f ${PYACL_PACKAGE}
        return 0
    else
        echo "[INFO] start upgrade pyacl"
        chown HwHiAiUser:HwHiAiUser ${PYACL_PACKAGE}
        su HwHiAiUser -c "${PYACL_PACKAGE} --upgrade"
        rm -f ${PYACL_PACKAGE}
        return 0
    fi
}

# ********************** UPDATE PACKAGE ************************************
function main()
{	
    echo "start update"
    # ***************check upgrade package**********************************
    CheckPackage
    if [ $? -ne 0 ];then
        rm -rf ./nnrt
        return 1
    fi
	
    # ***************upgrade Acllib package**********************************
    UpgradeAcllib
    if [ $? -ne 0 ];then
        rm -rf ./nnrt
        return 1
    fi

    # ***************upgrade Pyacl package**********************************
    UpgradePyacl
    if [ $? -ne 0 ];then
        rm -rf ./nnrt
        return 1
    fi

    # ***************upgrade AICPU package**********************************
    if [ ${AICPU_FLAG} -eq 1 ];then
        UpgradeAicpu
        if [ $? -ne 0 ];then
	    rm -rf ./nnrt
            return 1
        fi
    else
        UpgradeAicpu_run
        if [ $? -ne 0 ];then
            rm -rf ./nnrt
            return 1
        fi
    fi
    rm -rf ./nnrt
    echo "If the upgrade is successful, switch to the running user and run the source ~/.bashrc command to make the environment variables take effect."
}
main
