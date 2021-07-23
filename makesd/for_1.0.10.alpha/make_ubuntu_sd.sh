#!/bin/bash
#
#   =======================================================================
#
# Copyright (C) 2018, Hisilicon Technologies Co., Ltd. All Rights Reserved.
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
set -x
# ************************Variable*********************************************
ScriptPath="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )""/"
DEV_NAME=$1

#********************** UPDATE TO FIX ISSUE REGARDING /dev/mmc* MOUNTED SD CARD **********

if [[ $DEV_NAME == /dev/mmc* ]]
then
    echo "Partion naming with p-prefix"	
    p1="p1"
    p2="p2"
    p3="p3"	  	
else
    echo "Partition naming without p-prefix"	
    p1="1"
    p2="2"
    p3="3"
fi

#####################################################################################


ISO_FILE_DIR=$2
ISO_FILE=$3
DRIVER_PACKAGE_tmp=$4
DRIVER_PACKAGE=${DRIVER_PACKAGE_tmp##*/}
CANN_PACKAGE=$5
echo $DRIVER_PACKAGE
echo $CANN_PACKAGE
NETWORK_CARD_DEFAULT_IP=$6
USB_CARD_DEFAULT_IP=$7
sectorEnd=$8
sectorSize=$9

if [[ ${CANN_PACKAGE}"X" != "none""X" ]];then
    tmp_package_version=${CANN_PACKAGE##*Ascend-cann-nnrt_}
    PACKAGE_VERSION=${tmp_package_version%*_linux-aarch64.run}    
fi



LogPath=${ScriptPath}"sd_card_making_log/"
TMPDIR_SD_MOUNT=${LogPath}"sd_mount_dir"
TMPDIR_SD2_MOUNT=${LogPath}"sd_mount_dir2"
TMPDIR_SD3_MOUNT=${LogPath}"sd_mount_dir3"
TMPDIR_DATE=${LogPath}"no_touch_make_sd_dir"

USER_NAME="HwHiAiUser"
USER_PWD="HwHiAiUser:\$6\$klSpdQ1K\$4Gm/7HxehX.YSum4Wf3IDFZ3v5L.clybUpGNGaw9zAh3rqzqB4mWbxvSTFcvhbjY/6.tlgHhWsbtbAVNR9TSI/:17795:0:99999:7:::"
ROOT_PWD="root:\$6\$klSpdQ1K\$4Gm/7HxehX.YSum4Wf3IDFZ3v5L.clybUpGNGaw9zAh3rqzqB4mWbxvSTFcvhbjY/6.tlgHhWsbtbAVNR9TSI/:17795:0:99999:7:::"

MINIRC_LOGROTATE_DIR="/etc/crob.minirc/"
SYSLOG_MAXSIZE="1000M"
SYSLOG_ROTATE="4"
KERNLOG_MAXSIZE="1000M"
KERNLOG_ROTATE="4"


sectorRsv=$[536870912/sectorSize+1]
sectorEnd=$[sectorEnd-sectorRsv]

#component main/backup offset
COMPONENTS_MAIN_OFFSET=$[sectorEnd+1]

COMPONENTS_BACKUP_OFFSET=$[COMPONENTS_MAIN_OFFSET+73728]
#0 512k
LPM3_OFFSET=0
LPM3_SIZE=1024
#1M 512k
TEE_OFFSET=2048
TEE_SIZE=1024
#2M 2M
DTB_OFFSET=4096
DTB_SIZE=4096
#32M 32M
IMAGE_OFFSET=8192
IMAGE_SIZE=65536
#component main header
#COMPONENTS_MAIN_HEADER=`${COMPONENTS_MAIN_OFFSET} |awk '{printf("%x\n", $0)}'`
# end

# ************************Cleanup*********************************************
# Description:  files cleanup
# ******************************************************************************
function filesClean()
{
    df -h | grep "${TMPDIR_DATE}"
    if [ $? -eq 0 ];then
        umount ${TMPDIR_DATE}
    fi
    rm -rf ${TMPDIR_DATE}
    df -h | grep "${LogPath}squashfs-root/cdtmp"
    if [ $? -eq 0 ];then
        umount ${LogPath}squashfs-root/cdtmp
    fi
    rm -rf ${LogPath}squashfs-root

    rm -rf ${LogPath}filesystem.squashfs
    df -h | grep "${TMPDIR_SD_MOUNT}"
    if [ $? -eq 0 ];then
        umount ${TMPDIR_SD_MOUNT}
    fi
    rm -rf ${TMPDIR_SD_MOUNT}
    df -h | grep "${TMPDIR_SD2_MOUNT}"
    if [ $? -eq 0 ];then
        umount ${TMPDIR_SD2_MOUNT}
    fi
    rm -rf ${TMPDIR_SD2_MOUNT}
    df -h | grep "${TMPDIR_SD3_MOUNT}"
    if [ $? -eq 0 ];then
        umount ${TMPDIR_SD3_MOUNT}
    fi
    rm -rf ${TMPDIR_SD3_MOUNT}
    rm -rf ${LogPath}driver

    if [[ ${CANN_PACKAGE}"X" != "none""X" ]];then
        rm -rf ${ISO_FILE_DIR}/nnrt
    fi
}
#end
# ************************check ip****************************************
# Description:  check ip valid or not
# $1: ip
# ******************************************************************************
function checkIpAddr()
{
    ip_addr=$1
    echo ${ip_addr} | grep "^[0-9]\{1,3\}\.\([0-9]\{1,3\}\.\)\{2\}[0-9]\{1,3\}$" > /dev/null
    if [ $? -ne 0 ]
    then
        return 1
    fi

    for num in `echo ${ip_addr} | sed "s/./ /g"`
    do
        if [ $num -gt 255 ] || [ $num -lt 0 ]
        then
            return 1
        fi
   done
   return 0
}

# ************************check Ascend package********************************
# Description:  check Ascend package valid or not
# ******************************************************************************
function checkAscendPackage()
{

    if [ ! -n "$DRIVER_PACKAGE" ]; then
        echo "find A200dk-npu-driver-*-ubuntu18.04-aarch64-minirc.tar.gz failed. please put driver package in this folder."
        return 1
    fi    
    
    if [[ ${CANN_PACKAGE}"X" != "none""X" ]];then
        chmod 750 ${CANN_PACKAGE##*/}

        ./${CANN_PACKAGE##*/} --extract=${ScriptPath}/nnrt --noexec
        if [[ $? -ne 0 ]] || [[ $(find ${ScriptPath}/nnrt/run_package/Ascend-acllib-*-linux.aarch64.run)"x" = "x" ]] || [[ $(find ${ScriptPath}/nnrt/run_package/Ascend-pyACL-*-linux.aarch64.run)"x" = "x" ]];then
            echo "extract Ascend-cann-nnrt_"${PACKAGE_VERSION}"_linux-aarch64.run failed. please check this package."
            return 1
        fi
        if [[ $(find ${ScriptPath}/nnrt/run_package/Ascend310-aicpu_kernels-*-minirc.run)"x" != "x" ]];then
            AICPU_KERNELS_PACKAGE=$(ls nnrt/run_package/Ascend310-aicpu_kernels-*-minirc.run)
            AICPU_FLAG=0
        elif [[ $(find ${ScriptPath}/nnrt/run_package/Ascend310-aicpu_kernels_minirc-*.run)"x" != "x" ]];then
            AICPU_KERNELS_PACKAGE=$(ls nnrt/run_package/Ascend310-aicpu_kernels_minirc-*.run)
	    AICPU_FLAG=0
        elif [[ $(find ${ScriptPath}/nnrt/run_package/Ascend310-aicpu_kernels-*-minirc.tar.gz)"x" != "x" ]];then
            AICPU_KERNELS_PACKAGE=$(ls nnrt/run_package/Ascend310-aicpu_kernels-*-minirc.tar.gz)
            AICPU_FLAG=1
        else
            echo "[ERROR] extract Ascend-cann-nnrt_"${PACKAGE_VERSION}"_linux-aarch64.run failed. please check this package."
            return 1
        fi

        ACLLIB_PACKAGE=$(ls nnrt/run_package/Ascend-acllib-*-linux.aarch64.run)
        PYACL_PACKAGE=$(ls nnrt/run_package/Ascend-pyACL-*-linux.aarch64.run)
    fi
    
    return 0
}

# **************check network card and usb card ip******************************
# Description:  check network card and usb card ip
# ******************************************************************************
function checkIps()
{
    if [[ ${NETWORK_CARD_DEFAULT_IP}"X" == "X" ]];then
        NETWORK_CARD_DEFAULT_IP="192.168.0.2"
    fi

    checkIpAddr ${NETWORK_CARD_DEFAULT_IP}
    if [ $? -ne 0 ];then
        echo "Failed: Invalid network card ip."
        return 1
    fi
    NETWORK_CARD_GATEWAY=`echo ${NETWORK_CARD_DEFAULT_IP} | sed -r 's/([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+/\1.1/g'`


    if [[ ${USB_CARD_DEFAULT_IP}"X" == "X" ]];then
        USB_CARD_DEFAULT_IP="192.168.1.2"
    fi
    USB_CARD_GATEWAY=`echo ${USB_CARD_DEFAULT_IP} | sed -r 's/([0-9]+\.[0-9]+\.[0-9]+)\.[0-9]+/\1.1/g'`

    checkIpAddr ${USB_CARD_DEFAULT_IP}
    if [ $? -ne 0 ];then
        echo "Failed: Invalid usb card ip."
        return 1
    fi
    return 0
}


# ************************umount SD Card****************************************
# Description:  check sd card mount, if mounted, umount it
# ******************************************************************************
function checkSDCard()
{
    paths=`df -h | grep "$DEV_NAME" | awk -F ' ' '{print $6}'`
    for path in $paths
    do
        echo "umount $path"
        umount $path
        if [ $? -ne 0 ];then
            echo "Failed: umount $path failed!"
            return 1
        fi
    done
    return 0
}
#end

# ************************Extract ubuntufs from iso*****************************
# Description:  mount iso file , extract root filesystem from squashfs, after
# execute function it will create squashfs-root/ in "./"
# ******************************************************************************
function ubuntufsExtract()
{
    mkdir ${TMPDIR_DATE}
    mount -o loop ${ISO_FILE_DIR}/${ISO_FILE} ${TMPDIR_DATE}
    cp ${TMPDIR_DATE}/install/filesystem.squashfs ${LogPath}
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy 'filesystem.squashfs' fail!"
        return 1;
    fi

    cd ${LogPath}
    unsquashfs filesystem.squashfs

    if [[ $? -ne 0 ]];then
        echo "Failed: Unsquashfs 'filesystem.squashfs' fail!"
        return 1;
    fi

    # Return to the bin directory
    cd ${ScriptPath}
    return 0
}
# end


# *****************configure syslog and kernlog**************************************
# Description:  configure syslog and kernlog
# ******************************************************************************
function configure_syslog_and_kernlog()
{
    if [ ! -d ${LogPath}squashfs-root/${MINIRC_LOGROTATE_DIR} ];then
        mkdir -p ${LogPath}squashfs-root/${MINIRC_LOGROTATE_DIR}
    fi
    
    echo "" > ${LogPath}squashfs-root/${MINIRC_LOGROTATE_DIR}minirc_logrotate
    echo "" > ${LogPath}squashfs-root/${MINIRC_LOGROTATE_DIR}minirc_logrotate.conf
    
    cat > ${LogPath}squashfs-root/${MINIRC_LOGROTATE_DIR}minirc_logrotate << EOF
#!/bin/bash

#Clean non existent log file entries from status file
cd /var/lib/logrotate
test -e status || touch status
head -1 status > status.clean
sed 's/"//g' status | while read logfile date
do
    [ -e "\${logfile}" ] && echo "\"\${logfile}\" \${date}"
done >> status.clean

test -x /usr/sbin/logrotate || exit 0
/usr/sbin/logrotate ${MINIRC_LOGROTATE_DIR}minirc_logrotate.conf
EOF

    cat > ${LogPath}squashfs-root/${MINIRC_LOGROTATE_DIR}minirc_logrotate.conf << EOF
# see "main logrotate" for details

# use the syslog group by default, since this is the owing group
# of /var/log/syslog.
su root syslog

# create new (empty) log files after rotating old ones
create
/var/log/syslog
{
        rotate ${SYSLOG_ROTATE}
        weekly
        maxsize ${SYSLOG_MAXSIZE}
        missingok
        notifempty
        compress
        postrotate
                invoke-rc.d rsyslog rotate > /dev/null
        endscript
}
/var/log/kern.log
{
        rotate ${SYSLOG_ROTATE}
        weekly
        maxsize ${SYSLOG_MAXSIZE}
        missingok
        notifempty
        compress
}
EOF
    chmod 755 ${LogPath}squashfs-root/${MINIRC_LOGROTATE_DIR}minirc_logrotate

    echo "*/30 *   * * *   root     cd / && run-parts --report ${MINIRC_LOGROTATE_DIR}" >> ${LogPath}squashfs-root/etc/crontab
    
    if [ -f ${LogPath}squashfs-root/etc/rsyslog.d/50-default.conf ];then
        sed -i 's/*.*;auth,authpriv.none/*.*;auth,authpriv,kern.none/g' ${LogPath}squashfs-root/etc/rsyslog.d/50-default.conf
    fi
    echo 'LogLevel=emerg' >> ${LogPath}squashfs-root/etc/systemd/system.conf
    echo 'MaxLevelStore=emerg' >> ${LogPath}squashfs-root/etc/systemd/journald.conf
    echo 'MaxLevelSyslog=emerg' >> ${LogPath}squashfs-root/etc/systemd/journald.conf
    echo 'MaxLevelKMsg=emerg' >> ${LogPath}squashfs-root/etc/systemd/journald.conf
    echo 'MaxLevelConsole=emerg' >> ${LogPath}squashfs-root/etc/systemd/journald.conf
    echo 'MaxLevelWall=emerg' >> ${LogPath}squashfs-root/etc/systemd/journald.conf
}


# ************************Configure ubuntu**************************************
# Description:  install ssh, configure user/ip and so on
# ******************************************************************************
function configUbuntu()
{
    # 1. configure image sources
    mkdir -p ${LogPath}squashfs-root/cdtmp
    mount -o bind ${TMPDIR_DATE} ${LogPath}squashfs-root/cdtmp
	
    echo "
#!/bin/bash
DRIVER_PACKAGE=\$1
username=\$2
password=\$3
root_pwd=\$4

# 1. apt install deb
mv /etc/apt/sources.list /etc/apt/sources.list.bak
touch /etc/apt/sources.list
echo \"deb file:/cdtmp bionic main restricted\" > /etc/apt/sources.list

locale-gen zh_CN.UTF-8 en_US.UTF-8 en_HK.UTF-8
apt-get update
echo \"make_sd_process: 5%\"
apt-get install openssh-server -y
apt-get install tar -y
apt-get install vim -y
echo \"make_sd_process: 10%\"
apt-get install gcc -y
apt-get install zlib -y
apt-get install python2.7 -y
apt-get install python3 -y
apt-get install pciutils -y
apt-get install strace -y
apt-get install nfs-common -y
apt-get install sysstat -y
apt-get install libelf1 -y
apt-get install libpython2.7 -y
apt-get install libnuma1 -y
echo \"make_sd_process: 20%\"
apt-get install dmidecode -y
apt-get install rsync -y
apt-get install net-tools -y
echo \"make_sd_process: 25%\"

mv /etc/apt/sources.list.bak /etc/apt/sources.list
echo \"recover source.list end\"
# 2. set username
useradd -m \${username} -d /home/\${username} -s /bin/bash
sed -i \"/^\${username}:/c\\\\\${password}\" /etc/shadow
sed -i \"/^root:/c\\\\\${root_pwd}\" /etc/shadow
echo \"set username end\"
# 3. config host
echo 'davinci-mini' > /etc/hostname
echo '127.0.0.1        localhost' > /etc/hosts
echo '127.0.1.1        davinci-mini' >> /etc/hosts
echo \"config host end\"
# 4. config ip
echo \"
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no 
      addresses: [${NETWORK_CARD_DEFAULT_IP}/24] 
      gateway4: ${NETWORK_CARD_GATEWAY}
      nameservers:
            addresses: [114.114.114.114]
   
    usb0:
      dhcp4: no 
      addresses: [${USB_CARD_DEFAULT_IP}/24] 
      #gateway4: ${USB_CARD_GATEWAY}
      nameservers:
            addresses: [114.114.114.114]	  
\" > /etc/netplan/01-netcfg.yaml
echo \"config network ok\"" > ${LogPath}squashfs-root/chroot_install.sh
 
    if [[ ${DRIVER_PACKAGE}"X" != "A200dk-npu-driver-20.2.0-ubuntu18.04-aarch64-minirc.tar.gz""X" ]];then
        echo "
mkdir -p /usr/lib64/aicpu_kernels
chown HwHiAiUser:HwHiAiuser /usr/lib64/aicpu_kernels
touch /usr/lib64/aicpu_kernels/aicpu_package_install.info
chown HwHiAiUser:HwHiAiUser /usr/lib64/aicpu_kernels/aicpu_package_install.info
echo \"0\" > /usr/lib64/aicpu_kernels/aicpu_package_install.info
echo \"export LD_LIBRARY_PATH=/usr/lib64/aicpu_kernels/0/aicpu_kernels_device\" >> /home/HwHiAiUser/.bashrc
echo \"export LD_LIBRARY_PATH=/usr/lib64/aicpu_kernels/0/aicpu_kernels_device\" >> /root/.bashrc" >> ${LogPath}squashfs-root/chroot_install.sh
    else
        echo "
echo \"export LD_LIBRARY_PATH=/usr/lib64\" >> /home/HwHiAiUser/.bashrc" >> ${LogPath}squashfs-root/chroot_install.sh    
    fi
    
    echo "
# 5. auto-run minirc_cp.sh and minirc_sys_init.sh when start ubuntu
echo \"#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will \"exit 0\" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.
cd /var/


/bin/bash /var/minirc_boot.sh /opt/mini/${DRIVER_PACKAGE}" >> ${LogPath}squashfs-root/chroot_install.sh

    if [[ ${CANN_PACKAGE}"X" != "none""X" ]];then
        echo "
/bin/bash /var/acllib_install.sh >/var/1.log

/bin/bash /var/aicpu_kernels_install.sh >>/var/1.log

/bin/bash /var/pyacl_install.sh >>/var/1.log" >> ${LogPath}squashfs-root/chroot_install.sh
    fi
    echo "
exit 0
\" > /etc/rc.local

echo \"config rc.local ok\"

chmod 755 /etc/rc.local
echo \"RuntimeMaxUse=50M\" >> /etc/systemd/journald.conf
echo \"SystemMaxUse=50M\" >> /etc/systemd/journald.conf
echo \"config journald ok\"" >> ${LogPath}squashfs-root/chroot_install.sh
    if [[ ${CANN_PACKAGE}"X" != "none""X" ]];then
        echo "    
echo \"export LD_LIBRARY_PATH=/home/HwHiAiUser/Ascend/acllib/lib64:\\\${LD_LIBRARY_PATH}\" >> /home/HwHiAiUser/.bashrc
echo \"export PYTHONPATH=/home/HwHiAiUser/Ascend/pyACL/python/site-packages/acl\" >> /home/HwHiAiUser/.bashrc
echo \"export ASCEND_AICPU_PATH=/home/HwHiAiUser/Ascend\" >> /home/HwHiAiUser/.bashrc
echo \"config bashrc ok\"" >> ${LogPath}squashfs-root/chroot_install.sh
    fi
    echo "
exit
# end" >> ${LogPath}squashfs-root/chroot_install.sh

    chmod 750 ${LogPath}squashfs-root/chroot_install.sh
    # 2. add user and install software
    # execute in ./chroot_install.sh

    chroot ${LogPath}squashfs-root /bin/bash -c "./chroot_install.sh ${DRIVER_PACKAGE} ${USER_NAME} '"${USER_PWD}"' '"${ROOT_PWD}"'"

    if [[ $? -ne 0 ]];then
        echo "Failed: qemu is broken or the version of qemu is not compatible!"
        return 1;
    fi

    #configure syslog and kern log
    configure_syslog_and_kernlog

    umount ${LogPath}squashfs-root/cdtmp
    rm -rf ${LogPath}squashfs-root/cdtmp
    rm ${LogPath}squashfs-root/chroot_install.sh
    return 0
}

# end

# ************************Format SDcard*****************************************
# Description:  format to ext3 filesystem and three partition
# ******************************************************************************
function formatSDcard()
{
    if [[ $(fdisk -l 2>/dev/null | grep "^${DEV_NAME}" | wc -l) -gt 1 ]];then
	for i in $(fdisk -l 2>/dev/null | grep "^${DEV_NAME}" | awk -F ' ' '{print $1}'); do
            echo "d

	    w" | fdisk ${DEV_NAME}
	done
    else
	echo "d

	w" | fdisk ${DEV_NAME}
    fi
    umount ${DEV_NAME} 2>/dev/null

    echo "n



+8G
n



+1G
n



$sectorEnd



    w" | fdisk ${DEV_NAME}

    partprobe

    fdisk -l

    sleep 5

    checkSDCard
    if [ $? -ne 0 ];then
        return 1
    fi
    echo "y
    " | mkfs.ext3 -L ubuntu_fs ${DEV_NAME}$p1 # updated by aman
    if [[ $? -ne 0 ]];then
     echo "Failed: Format ${DEV_NAME}$p1 failed!"
     return 1;
    fi

    echo "make_sd_process: 30%"
    checkSDCard
    if [ $? -ne 0 ];then
        return 1
    fi
    echo "y
    " | mkfs.ext3 -L ubuntu_fs ${DEV_NAME}$p2 # updated by aman
    if [[ $? -ne 0 ]];then
     echo "Failed: Format ${DEV_NAME}$p2 failed!"
     return 1;
    fi

    echo "make_sd_process: 35%"
    checkSDCard
    if [ $? -ne 0 ];then
        return 1
    fi
    echo "y
    " | mkfs.ext3 -L ubuntu_fs ${DEV_NAME}$p3 # updated by aman
    if [[ $? -ne 0 ]];then
     echo "Failed: Format ${DEV_NAME}$p3 failed!"
     return 1;
    fi
    echo "make_sd_process: 45%"
    return 0
}
#end

# ************************Copy files to SD**************************************
# Description:  copy rar and root filesystem to SDcard
# ******************************************************************************
function preInstallDriver()
{
    echo "start pre install driver"
	mkdir -p ${LogPath}squashfs-root/opt/mini
    chmod 755 ${LogPath}squashfs-root/opt/mini
    # 1. copy third party file
    tar zxf ${ISO_FILE_DIR}/${DRIVER_PACKAGE} -C ${LogPath} driver/scripts/minirc_install_phase1.sh 
    cp ${LogPath}driver/scripts/minirc_install_phase1.sh ${LogPath}squashfs-root/opt/mini/
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy minirc_install_phase1.sh to filesystem failed!"
        return 1
    fi
    chmod +x ${LogPath}/driver/scripts/minirc_install_phase1.sh

    echo "make_sd_process: 75%"

    tar -zxf ${ISO_FILE_DIR}/${DRIVER_PACKAGE} -C ${LogPath} driver/scripts/minirc_boot.sh
    cp ${LogPath}driver/scripts/minirc_boot.sh ${LogPath}squashfs-root/var/
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy minirc_boot.sh to filesystem failed!"
        return 1
    fi

    echo "make_sd_process: 80%"
    # 2. copy root filesystem
    if [[ ${arch} =~ "x86" ]];then
        rm ${LogPath}squashfs-root/usr/bin/qemu-aarch64-static
    fi

    #install $DRIVER_PACKAGE
    mkdir -p ${LogPath}mini_pkg_install/opt/mini
    cp ${ISO_FILE_DIR}/${DRIVER_PACKAGE}  ${LogPath}mini_pkg_install/opt/mini/
    chmod +x ${LogPath}squashfs-root/opt/mini/minirc_install_phase1.sh
    ${LogPath}driver/scripts/minirc_install_phase1.sh ${LogPath}mini_pkg_install
    res=$(echo $?)
    if [[ ${res} != "0" ]];then
        echo "Install ${DRIVER_PACKAGE} fail, error code:${res}"
        echo "Failed: Install ${DRIVER_PACKAGE} failed!"
        return 1
    fi
    
}


function generateAclLibInstallShell()
{
echo "
#!/bin/bash

chown HwHiAiUser:HwHiAiUser /home/HwHiAiUser/${ACLLIB_PACKAGE##*/}
echo \"y
\" | su HwHiAiUser -c \"/home/HwHiAiUser/${ACLLIB_PACKAGE##*/} --run\"
rm -f /home/HwHiAiUser/${ACLLIB_PACKAGE##*/}
exit 0
" >${LogPath}squashfs-root/var/acllib_install.sh

chmod 750 ${LogPath}squashfs-root/var/acllib_install.sh
}

function generatePyAclInstallShell()
{
echo "
#!/bin/bash

chown HwHiAiUser:HwHiAiUser /home/HwHiAiUser/${PYACL_PACKAGE##*/}
su HwHiAiUser -c \"/home/HwHiAiUser/${PYACL_PACKAGE##*/} --run\"
rm -f /home/HwHiAiUser/${PYACL_PACKAGE##*/}
exit 0
" >${LogPath}squashfs-root/var/pyacl_install.sh

chmod 750 ${LogPath}squashfs-root/var/pyacl_install.sh
}

function installPyAcl()
{
    echo "start install pyacl"
	
    cp -f ${ISO_FILE_DIR}/$PYACL_PACKAGE ${LogPath}squashfs-root/home/HwHiAiUser/
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy ${ISO_FILE_DIR}/$PYACL_PACKAGE to filesystem failed!"
        return 1
    fi
    chmod 750 ${LogPath}squashfs-root/home/HwHiAiUser/${PYACL_PACKAGE##*/}
	
	generatePyAclInstallShell
	
	echo "install pyacl end"	
}

function installAclLib()
{
    echo "start install acl lib"    
    cp -f ${ISO_FILE_DIR}/$ACLLIB_PACKAGE ${LogPath}squashfs-root/home/HwHiAiUser/
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy ${ISO_FILE_DIR}/$ACLLIB_PACKAGE to filesystem failed!"
        return 1
    fi
    chmod 750 ${LogPath}squashfs-root/home/HwHiAiUser/${ACLLIB_PACKAGE##*/}
	
	generateAclLibInstallShell
	
	echo "install acl lib end"	
}

function genAicpuKernInstShell_run()
{
        echo "
#!/bin/bash

chown HwHiAiUser:HwHiAiUser /home/HwHiAiUser/${AICPU_KERNELS_PACKAGE##*/}
su HwHiAiUser -c \"/home/HwHiAiUser/${AICPU_KERNELS_PACKAGE##*/} --run\"
rm -f /home/HwHiAiUser/${AICPU_KERNELS_PACKAGE##*/}

export ASCEND_AICPU_PATH=/home/HwHiAiUser/Ascend
sh /home/HwHiAiUser/Ascend/run_aicpu_toolkit.sh

exit 0
" >${LogPath}squashfs-root/var/aicpu_kernels_install.sh

    chmod 750 ${LogPath}squashfs-root/var/aicpu_kernels_install.sh
}

function installAicpuKernels_run()
{
    cp -f ${ISO_FILE_DIR}/${AICPU_KERNELS_PACKAGE} ${LogPath}squashfs-root/home/HwHiAiUser/
    if [[ $? -ne 0 ]];then
        echo "Failed: copy ${ISO_FILE_DIR}/${AICPU_KERNELS_PACKAGE} to filesystem failed!"
        return 1
    fi
    chmod 750 ${LogPath}squashfs-root/home/HwHiAiUser/${AICPU_KERNELS_PACKAGE##*/}

    genAicpuKernInstShell_run

    echo "install Aicpu_run end"
}

function genAicpuKernInstShell()
{
	echo "
#!/bin/bash

cd /home/HwHiAiUser/aicpu_kernels_device/
chmod 750 *.sh
chmod 750 scripts/*.sh
scripts/install.sh --run

rm -rf /home/HwHiAiUser/aicpu_kernels_device

exit 0
" >${LogPath}squashfs-root/var/aicpu_kernels_install.sh

    chmod 750 ${LogPath}squashfs-root/var/aicpu_kernels_install.sh
}

function installAicpuKernels()
{
    tar zxf ${ISO_FILE_DIR}/${AICPU_KERNELS_PACKAGE} -C ${LogPath}squashfs-root/home/HwHiAiUser/
    if [[ $? -ne 0 ]];then
        echo "Failed: tar zxf ${ISO_FILE_DIR}/${AICPU_KERNELS_PACKAGE} to filesystem failed!"
        return 1
    fi
    genAicpuKernInstShell
}

function copyFilesToSDcard()
{
    cp -a ${LogPath}squashfs-root/* ${TMPDIR_SD_MOUNT}
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy root filesystem to SDcard failed!"
        return 1
    fi

    cp -rf ${TMPDIR_SD_MOUNT}/home/* ${TMPDIR_SD3_MOUNT}/
    #rm -rf ${TMPDIR_SD_MOUNT}/home/*

    cp -rf ${TMPDIR_SD_MOUNT}/var/log/* ${TMPDIR_SD2_MOUNT}/
    #rm -rf ${TMPDIR_SD_MOUNT}/var/log/*
    echo "make_sd_process: 90%"
    return 0
}

function preInstallMinircPackage()
{
    preInstallDriver
    if [ $? -ne 0 ];then
        echo "Pre install driver package failed"
        return 1
    fi
    echo "pre install driver end"
    if [[ ${CANN_PACKAGE}"X" != "none""X" ]];then
        installAclLib
        if [ $? -ne 0 ];then
            echo "Pre install acllib package failed"
            return 1
        fi
        echo "pre install acl lib end"

        if [ ${AICPU_FLAG} -eq 1 ];then    
            installAicpuKernels
            if [ $? -ne 0 ];then
                echo "Pre install aicpu_kernels package failed"
                return 1
            fi
        else
            installAicpuKernels_run
            if [ $? -ne 0 ];then
                echo "Pre install aicpu_kernels package failed"
                return 1
            fi
        fi
        echo "pre install aicpu end"

        installPyAcl
        if [ $? -ne 0 ];then
            echo "Pre install pyacl package failed"
            return 1
        fi
        echo "pre install pyacl end" 
    fi
	
    rm -rf ${LogPath}mini_pkg_install/opt
    cp -rf ${LogPath}mini_pkg_install/* ${LogPath}squashfs-root/
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy mini_pkg_install to filesystem failed!"
        return 1
    fi
    echo "pre install drvier finished"
    echo "make_sd_process: 85%"
    rm -rf ${LogPath}mini_pkg_install
	
	copyFilesToSDcard
	if [ $? -ne 0 ];then
	    echo "Copy file to sdcard failed"
        return 1
    fi
}
# end

# ************************Make sysroot**************************************
# Description:  copy aarch64 gnu libs
# ******************************************************************************
function make_sysroot()
{
    echo "make sysroot start"
    if [ ! -d /usr/aarch64-linux-gnu/ ]; then
        mkdir -p /usr/aarch64-linux-gnu/
    fi
    if [ ! -d /usr/lib/aarch64-linux-gnu/ ]; then
        mkdir -p /usr/lib/aarch64-linux-gnu/
    fi
    cp -rdp ${LogPath}squashfs-root/usr/include /usr/aarch64-linux-gnu/
    echo "make_sd_process: 95%"
    cp -rdp ${LogPath}squashfs-root/usr/lib/aarch64-linux-gnu/* /usr/lib/aarch64-linux-gnu/
    echo "make_sd_process: 98%"
    cp -rdp ${LogPath}squashfs-root/lib/aarch64-linux-gnu /lib/
    if [ ! -f /usr/lib/aarch64-linux-gnu/libz.so ]; then
        ln -s /lib/aarch64-linux-gnu/libz.so.1 /usr/lib/aarch64-linux-gnu/libz.so
    fi
    ln -s /usr/aarch64-linux-gnu/include/sys /usr/include/sys
    ln -s /usr/aarch64-linux-gnu/include/bits /usr/include/bits
    ln -s /usr/aarch64-linux-gnu/include/gnu /usr/include/gnu
    
    echo "make sysroot end"
}

# ************************writePartitionHeader**************************************
# Description:  write partirion header
# ******************************************************************************
function writePartitionHeader()
{
    #sector 512��?��?��?
    secStart=16
    MAIN_HEADER=$(printf "%#x" $COMPONENTS_MAIN_OFFSET)
    BACK_HEADER=$(printf "%#x" $COMPONENTS_BACKUP_OFFSET)

    MAIN_A=$(printf "%x" $(( ($MAIN_HEADER & 0xFF000000) >> 24 )))
    MAIN_B=$(printf "%x" $(( ($MAIN_HEADER & 0x00FF0000) >> 16 )))
    MAIN_C=$(printf "%x" $(( ($MAIN_HEADER & 0x0000FF00) >> 8)))
    MAIN_D=$(printf "%x" $(( $MAIN_HEADER & 0x000000FF )))

    BACKUP_A=$(printf "%x" $(( ($BACK_HEADER & 0xFF000000) >> 24 )))
    BACKUP_B=$(printf "%x" $(( ($BACK_HEADER & 0x00FF0000) >> 16 )))
    BACKUP_C=$(printf "%x" $(( ($BACK_HEADER & 0x0000FF00) >> 8)))
    BACKUP_D=$(printf "%x" $(( $BACK_HEADER & 0x000000FF )))

    #echo 55AA55AA | xxd -r -ps > magic
    echo -e -n "\x55\xAA\x55\xAA" > magic

    echo -e -n "\x$MAIN_D\x$MAIN_C\x$MAIN_B\x$MAIN_A" > components_main_base
    echo 0000 0000 0000 0000 0000 0000\
        0004 0000 0000 0000 0008 0000 0000 0000\
        0004 0000 0000 0000 0010 0000 0000 0000\
        0010 0000 0000 0000 0020 0000 0000 0000\
        0000 0100 0000 0000 0000 0000 0000 0000\
        0000 0000 0000 0000 0000 0000 0000 0000 | xxd -r -ps >> components_main_base

    echo -e -n "\x$BACKUP_D\x$BACKUP_C\x$BACKUP_B\x$BACKUP_A" > components_backup_base
    echo 0000 0000 0000 0000 0000 0000\
        0004 0000 0000 0000 0008 0000 0000 0000\
        0004 0000 0000 0000 0010 0000 0000 0000\
        0010 0000 0000 0000 0020 0000 0000 0000\
        0000 0100 0000 0000 0000 0000 0000 0000\
        0000 0000 0000 0000 0000 0000 0000 0000 | xxd -r -ps >> components_backup_base

    dd if=magic of=${DEV_NAME} count=1 seek=$[secStart] bs=$sectorSize
    dd if=magic of=${DEV_NAME} count=1 seek=$[secStart+1] bs=$sectorSize
    dd if=components_main_base of=${DEV_NAME} count=1 seek=$[secStart+2] bs=$sectorSize
    dd if=components_backup_base of=${DEV_NAME} count=1 seek=$[secStart+3] bs=$sectorSize

    rm -rf magic
    rm -rf components_main_base
    rm -rf components_backup_base
}


# ************************writeComponents**************************************
# Description:  write components main/backup
# ******************************************************************************
function writeComponents()
{
    FWM_DIR="${LogPath}squashfs-root/fw/"
    OF_DIR=$1
    echo "\${OF_DIR} = ${OF_DIR}"
    echo "\${DEV_NAME} = ${DEV_NAME}"
    echo "\${LPM3_OFFSET} = ${LPM3_OFFSET}"
    echo "\$[OF_DIR+LPM3_OFFSET] = $[OF_DIR+LPM3_OFFSET]"
    echo "\${sectorSize} = ${sectorSize}"

    if [[ -d "${FWM_DIR}" ]];then
        echo "fw exist"
    else
        echo "failed: fw no exist"
    fi

    dd if=${FWM_DIR}lpm3.img of=${DEV_NAME} count=$LPM3_SIZE seek=$[OF_DIR+LPM3_OFFSET] bs=$sectorSize
    if [ $? -ne 0 ];then
        echo "failed: $OF_DIR lpm3"
        return 1
    fi
    dd if=${FWM_DIR}tee.bin of=${DEV_NAME} count=$TEE_SIZE seek=$[OF_DIR+TEE_OFFSET] bs=$sectorSize
    if [ $? -ne 0 ];then
        echo "failed: $OF_DIR tee"
        return 1
    fi
    dd if=${FWM_DIR}dt.img of=${DEV_NAME} count=$DTB_SIZE seek=$[OF_DIR+DTB_OFFSET] bs=$sectorSize
    if [ $? -ne 0 ];then
        echo "failed: $OF_DIR dt"
        return 1
    fi    
    dd if=${FWM_DIR}Image of=${DEV_NAME} count=$IMAGE_SIZE seek=$[OF_DIR+IMAGE_OFFSET] bs=$sectorSize
    if [ $? -ne 0 ];then
        echo "failed: $OF_DIR Image"
        return 1
    fi


}

# ########################Begin Executing######################################
# ************************Check args*******************************************
function main()
{
    echo "make_sd_process: 2%"
    if [[ $# -lt 4 ]];then
        echo "Failed: Number of parameter illegal! Usage: $0 <dev fullname> <img path> <iso fullname> <mini filename>"
        return 1;
    fi

    # ***************check network and usb card ip**********************************
    checkIps
    if [ $? -ne 0 ];then
        return 1
    fi

    # ***************check ascend cann package **********************************
    checkAscendPackage
    if [ $? -ne 0 ];then
        echo "Make SD card failed"
        return 1
    fi
    # ************************umount dev_name***************************************
    checkSDCard
    if [ $? -ne 0 ];then
        return 1
    fi

    # ************************Extract ubuntufs**************************************
    # output:squashfs-root/
    ubuntufsExtract
    if [ $? -ne 0 ];then
        return 1
    fi
    # end

    # ************************Check architecture************************************
    arch=$(uname -m)
    if [[ ${arch} =~ "x86" ]];then
         cp /usr/bin/qemu-aarch64-static ${LogPath}squashfs-root/usr/bin/
         if [ $? -ne 0 ];then
             echo "Failed: qemu-user-static or binfmt-support not found!"
             return 1;
         fi
         chmod 755 ${LogPath}squashfs-root/usr/bin/qemu-aarch64-static
    fi
    # end

    # ************************Configure ubuntu**************************************
    echo "Process: 1/4(Configure ubuntu filesystem)"
    configUbuntu
    if [ $? -ne 0 ];then
        return 1
    fi
    # end

    # ************************Format SDcard*****************************************
    echo "Process: 2/4(Format SDcard)"
    formatSDcard
    if [ $? -ne 0 ];then
        return 1
    fi

    # ************************Copy files to SD**************************************
    if [[ -d "${TMPDIR_SD_MOUNT}" ]];then
        umount ${TMPDIR_SD_MOUNT} 2>/dev/null
        rm -rf ${TMPDIR_SD_MOUNT}
    fi
    mkdir ${TMPDIR_SD_MOUNT}
    mount ${DEV_NAME}$p1 ${TMPDIR_SD_MOUNT} 2>/dev/null  # updated by aman

    if [[ -d "${TMPDIR_SD2_MOUNT}" ]];then
        umount ${TMPDIR_SD2_MOUNT} 2>/dev/null
        rm -rf ${TMPDIR_SD2_MOUNT}
    fi
    mkdir ${TMPDIR_SD2_MOUNT}
    mount ${DEV_NAME}$p2 ${TMPDIR_SD2_MOUNT} 2>/dev/null  # updated by aman
    echo "make_sd_process: 50%"

    if [[ -d "${TMPDIR_SD3_MOUNT}" ]];then
        umount ${TMPDIR_SD3_MOUNT} 2>/dev/null
        rm -rf ${TMPDIR_SD3_MOUNT}
    fi
    mkdir ${TMPDIR_SD3_MOUNT}
    mount ${DEV_NAME}$p3 ${TMPDIR_SD3_MOUNT} 2>/dev/null  # updated by aman
    echo "make_sd_process: 55%"

    echo "Process: 3/4(Pre install each run package and copy filesystem to SDcard)"
    preInstallMinircPackage    
    if [ $? -ne 0 ];then
        return 1
    fi

    # end

    # ************************write Components************************************** 
    writeComponents ${COMPONENTS_MAIN_OFFSET}
    if [ $? -ne 0 ];then
        echo "Failed: writeComponents main"
        return 1
    fi
    echo "writeComponents main Succ"
    # end

    writeComponents ${COMPONENTS_BACKUP_OFFSET}
    if [ $? -ne 0 ];then
        echo "Failed: writeComponents backup"
        return 1s
    fi
    echo "writeComponents backup Succ"
    # end

    # ************************write Partition Header********************************
    writePartitionHeader
    if [ $? -ne 0 ];then
        echo "Failed: writePartitionHeader"
        return 1
    fi
    echo "writePartitionHeader Succ"
    #end

    echo "Process: 4/4(Make sysroot)"
    make_sysroot
    umount ${TMPDIR_SD_MOUNT} 2>/dev/null
    if [[ $? -ne 0 ]];then
        echo "Failed: Umount ${TMPDIR_SD_MOUNT} to SDcard failed!"
        return 1
    fi
 
    umount ${TMPDIR_SD2_MOUNT} 2>/dev/null
    if [[ $? -ne 0 ]];then
        echo "Failed: Umount ${TMPDIR_SD2_MOUNT} to SDcard failed!"
        return 1
    fi

    umount ${TMPDIR_SD3_MOUNT} 2>/dev/null
    if [[ $? -ne 0 ]];then
        echo "Failed: Umount ${TMPDIR_SD3_MOUNT} to SDcard failed!"
        return 1
    fi
    echo "Finished!"
    return 0
}

main $*
ret=$?
#clean files
echo "make sd car finished ,clean files" 
filesClean

if [[ ret -ne 0 ]];then
    echo "Failed" > ${LogPath}/make_ubuntu_sd.result
    exit 1
fi
echo "Success" > ${LogPath}/make_ubuntu_sd.result
exit 0
# end


