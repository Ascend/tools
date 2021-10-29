#!/bin/bash

set -e

WORK_PATH=$1
SCRIPT_PATH=$(dirname $(readlink -f $0))
MINI_RC_HOOK="${WORK_PATH}/var/minirc_hook.sh"

function add_rc_hook()
{
local hook=$1
if [[ ! -f ${MINI_RC_HOOK} ]]; then
echo "#!/bin/bash" > ${MINI_RC_HOOK}
fi

echo "add rc hook $hook"
echo "$hook" >> ${MINI_RC_HOOK}

chmod 750 ${MINI_RC_HOOK}
}

function create_nnrt_install_script()
{
local cann_minirc=$1
local nnrt_hook="/var/nnrt_install.sh"
local nnrt_package_file="$(basename ${cann_minirc})"

echo "#!/bin/bash
if [ ! -f /home/HwHiAiUser/${nnrt_package_file} ]; then
exit 0
fi

echo y | /home/HwHiAiUser/${nnrt_package_file} --install --chip=Ascend310-minirc
if [ \$? -eq 0 ]; then
echo \"install ${nnrt_package_file} success\"
rm -f /home/HwHiAiUser/${nnrt_package_file}
fi

if [ ! -d /usr/lib64/aicpu_kernels ];then
mkdir /usr/lib64/aicpu_kernels > /dev/null
fi
chown HwHiAiUser:HwHiAiUser /usr/lib64/aicpu_kernels > /dev/null

if [ ! -d /usr/lib64/aicpu_kernels/0/aicpu_kernels_device ];then
mkdir -p /usr/lib64/aicpu_kernels/0/aicpu_kernels_device
chown HwHiAiUser:HwHiAiUser /usr/lib64/aicpu_kernels/0/aicpu_kernels_device
fi

touch /usr/lib64/aicpu_kernels/aicpu_package_install.info > /dev/null
chown HwHiAiUser:HwHiAiUser /usr/lib64/aicpu_kernels/aicpu_package_install.info > /dev/null
echo \"0\" > /usr/lib64/aicpu_kernels/aicpu_package_install.info 2> /dev/null
grep \"/usr/lib64/aicpu_kernels/0/aicpu_kernels_device\" /root/.bashrc >/dev/null
if [ \$? -ne 0 ];then
echo \"export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/usr/lib64/aicpu_kernels/0/aicpu_kernels_device\" >> ~/.bashrc 2> /dev/null
source /root/.bashrc
fi
grep \"/usr/lib64/aicpu_kernels/0/aicpu_kernels_device\" /home/HwHiAiUser/.bashrc >/dev/null
if [ \$? -ne 0 ];then
echo \"export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/usr/lib64/aicpu_kernels/0/aicpu_kernels_device\" >>/home/HwHiAiUser/.bashrc 2> /dev/null
source /home/HwHiAiUser/.bashrc
fi
exit 0
" > ${WORK_PATH}/${nnrt_hook}
echo "creat nnrt install success"
chmod 750 ${WORK_PATH}/${nnrt_hook}
add_rc_hook ${nnrt_hook}
}

function create_install_nnrt_pack_hook()
{
local unpack_dir="$SCRIPT_PATH/unpack_tmp_dir"

mkdir -p ${unpack_dir}
rm -rf ${unpack_dir}/*

cann_minirc=$(ls $SCRIPT_PATH/Ascend-cann-nnrt*.run)
if [[ -n "$cann_minirc" && -f "$cann_minirc" ]]; then
echo "Ascend-cann-minirc found: $cann_minirc"
chmod 750 ${cann_minirc}
cp ${cann_minirc} ${WORK_PATH}/home/HwHiAiUser/
create_nnrt_install_script ${cann_minirc}
else
echo "Ascend-cann-minirc not found"
fi
rm -rf ${unpack_dir}
}

function main()
{
if [[ $# -lt 1 ]]; then
echo "failed: number of parameter illegal! usage: $0 <work path>"
return 1
fi

mkdir -p ${WORK_PATH}/home/HwHiAiUser/
mkdir -p ${WORK_PATH}/var/

create_install_nnrt_pack_hook
return 0
}

main "$@"
exit $?
