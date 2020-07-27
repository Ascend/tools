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

# ************************Variable*********************************************
ScriptPath="$( cd "$(dirname "$0")" ; pwd -P )""/"
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
RUN_MINI=$4
NETWORK_CARD_DEFAULT_IP=$5
USB_CARD_DEFAULT_IP=$6

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
    rm -rf ${LogPath}mini_developerkit
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

    #Return to the bin directory
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
    echo 'LogLevel=emerg' >> /etc/systemd/system.conf
    echo 'MaxLevelStore=emerg' >> /etc/systemd/journald.conf
    echo 'MaxLevelSyslog=emerg' >> /etc/systemd/journald.conf
    echo 'MaxLevelKMsg=emerg' >> /etc/systemd/journald.conf
    echo 'MaxLevelConsole=emerg' >> /etc/systemd/journald.conf
    echo 'MaxLevelWall=emerg' >> /etc/systemd/journald.conf
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
RUN_MINI=\$1
username=\$2
password=\$3
root_pwd=\$4

# 1. apt install deb
mv /etc/apt/sources.list /etc/apt/sources.list.bak
touch /etc/apt/sources.list
echo \"deb file:/cdtmp xenial main restrict\" > /etc/apt/sources.list

locale-gen zh_CN.UTF-8 en_US.UTF-8 en_HK.UTF-8
apt-get update
apt-get install openssh-server -y
apt-get install unzip -y
apt-get install vim -y
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
apt-get install dmidecode -y
apt-get install rsync -y

mv /etc/apt/sources.list.bak /etc/apt/sources.list

# 2. set username
useradd -m \${username} -d /home/\${username} -s /bin/bash
sed -i \"/^\${username}:/c\\\\\${password}\" /etc/shadow
sed -i \"/^root:/c\\\\\${root_pwd}\" /etc/shadow

# 3. config host
echo 'davinci-mini' > /etc/hostname
echo '127.0.0.1        localhost' > /etc/hosts
echo '127.0.1.1        davinci-mini' >> /etc/hosts

# 4. config ip
echo \"source /etc/network/interfaces.d/*
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
address ${NETWORK_CARD_DEFAULT_IP}
netmask 255.255.255.0
gateway ${NETWORK_CARD_GATEWAY}

auto usb0
iface usb0 inet static
address ${USB_CARD_DEFAULT_IP}
netmask 255.255.255.0
\" > /etc/network/interfaces

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

/bin/bash /var/minirc_boot.sh /opt/mini/\${RUN_MINI}

exit 0
\" > /etc/rc.local

echo \"RuntimeMaxUse=50M\" >> /etc/systemd/journald.conf
echo \"SystemMaxUse=50M\" >> /etc/systemd/journald.conf

exit
# end" > ${LogPath}squashfs-root/chroot_install.sh

    chmod 750 ${LogPath}squashfs-root/chroot_install.sh
    # 2. add user and install software
    # execute in ./chroot_install.sh

    chroot ${LogPath}squashfs-root /bin/bash -c "./chroot_install.sh ${RUN_MINI} ${USER_NAME} '"${USER_PWD}"' '"${ROOT_PWD}"'"

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



+5G
n



+1G
n




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
     echo "Failed: Format SDcard1 failed!"
     return 1;
    fi

    checkSDCard
    if [ $? -ne 0 ];then
        return 1
    fi
    echo "y
    " | mkfs.ext3 -L ubuntu_fs ${DEV_NAME}$p2 # updated by aman
    if [[ $? -ne 0 ]];then
     echo "Failed: Format SDcard2 failed!"
     return 1;
    fi

    checkSDCard
    if [ $? -ne 0 ];then
        return 1
    fi
    echo "y
    " | mkfs.ext3 -L ubuntu_fs ${DEV_NAME}$p3 # updated by aman
    if [[ $? -ne 0 ]];then
     echo "Failed: Format SDcard3 failed!"
     return 1;
    fi
    return 0
}
#end

# ************************Copy files to SD**************************************
# Description:  copy rar and root filesystem to SDcard
# ******************************************************************************
function copyFilesToSDcard()
{
    # 1. copy third party file
    mkdir -p ${LogPath}squashfs-root/opt/mini
    chmod 755 ${LogPath}squashfs-root/opt/mini
    unzip ${ISO_FILE_DIR}/${RUN_MINI} mini_developerkit/scripts/minirc_install_phase1.sh -d ${LogPath}
    cp ${LogPath}mini_developerkit/scripts/minirc_install_phase1.sh ${LogPath}squashfs-root/opt/mini/
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy minirc_install_phase1.sh to filesystem failed!"
        return 1
    fi
    chmod +x ${LogPath}/mini_developerkit/scripts/minirc_install_phase1.sh

    unzip ${ISO_FILE_DIR}/${RUN_MINI} mini_developerkit/scripts/minirc_boot.sh -d ${LogPath}
    cp ${LogPath}mini_developerkit/scripts/minirc_boot.sh ${LogPath}squashfs-root/var/
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy minirc_boot.sh to filesystem failed!"
        return 1
    fi

    unzip ${ISO_FILE_DIR}/${RUN_MINI} mini_developerkit/extend_rootfs/perf -d ${LogPath}
    cp ${LogPath}mini_developerkit/extend_rootfs/perf ${LogPath}squashfs-root/usr/bin/perf
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy perf.sh to filesystem failed!"
        return 1
    fi
    chmod +x ${LogPath}squashfs-root/usr/bin/perf

    # 2. copy root filesystem
    if [[ ${arch} =~ "x86" ]];then
        rm ${LogPath}squashfs-root/usr/bin/qemu-aarch64-static
    fi

    #install $RUN_MINI
    mkdir -p ${LogPath}mini_pkg_install/opt/mini
    cp ${ISO_FILE_DIR}/${RUN_MINI}  ${LogPath}mini_pkg_install/opt/mini/
    chmod +x ${LogPath}squashfs-root/opt/mini/minirc_install_phase1.sh
    ${LogPath}mini_developerkit/scripts/minirc_install_phase1.sh ${LogPath}mini_pkg_install
    res=$(echo $?)
    if [[ ${res} != "0" ]];then
        echo "Install ${RUN_MINI} fail, error code:${res}"
        echo "Failed: Install ${RUN_MINI} failed!"
        return 1
    fi
    rm -rf ${LogPath}mini_pkg_install/opt
    cp -rf ${LogPath}mini_pkg_install/* ${LogPath}squashfs-root/
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy mini_pkg_install to filesystem failed!"
        return 1
    fi

    rm -rf ${LogPath}mini_pkg_install
    cp -a ${LogPath}squashfs-root/* ${TMPDIR_SD_MOUNT}
    if [[ $? -ne 0 ]];then
        echo "Failed: Copy root filesystem to SDcard failed!"
        return 1
    fi

    cp -rf ${TMPDIR_SD_MOUNT}/home/* ${TMPDIR_SD3_MOUNT}/
    #rm -rf ${TMPDIR_SD_MOUNT}/home/*

    cp -rf ${TMPDIR_SD_MOUNT}/var/log/* ${TMPDIR_SD2_MOUNT}/
    #rm -rf ${TMPDIR_SD_MOUNT}/var/log/*
    return 0
}
# end

# ************************Make sysroot**************************************
# Description:  copy aarch64 gnu libs
# ******************************************************************************
function make_sysroot()
{
    if [ ! -d /usr/aarch64-linux-gnu/ ]; then
        mkdir -p /usr/aarch64-linux-gnu/
    fi
    if [ ! -d /usr/lib/aarch64-linux-gnu/ ]; then
        mkdir -p /usr/lib/aarch64-linux-gnu/
    fi
    cp -rdp ${LogPath}squashfs-root/usr/include /usr/aarch64-linux-gnu/
    cp -rdp ${LogPath}squashfs-root/usr/lib/aarch64-linux-gnu/* /usr/lib/aarch64-linux-gnu/
    cp -rdp ${LogPath}squashfs-root/lib/aarch64-linux-gnu /lib/
    if [ ! -f /usr/lib/aarch64-linux-gnu/libz.so ]; then
        ln -s /lib/aarch64-linux-gnu/libz.so.1 /usr/lib/aarch64-linux-gnu/libz.so
    fi
    ln -s /usr/aarch64-linux-gnu/include/sys /usr/include/sys
    ln -s /usr/aarch64-linux-gnu/include/bits /usr/include/bits
    ln -s /usr/aarch64-linux-gnu/include/gnu /usr/include/gnu
}

# ########################Begin Executing######################################
# ************************Check args*******************************************
function main()
{
    if [[ $# -lt 4 ]];then
        echo "Failed: Number of parameter illegal! Usage: $0 <dev fullname> <img path> <iso fullname> <mini filename>"
        return 1;
    fi

    # ***************check network and usb card ip**********************************
    checkIps
    if [ $? -ne 0 ];then
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
    # end

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

    if [[ -d "${TMPDIR_SD3_MOUNT}" ]];then
        umount ${TMPDIR_SD3_MOUNT} 2>/dev/null
        rm -rf ${TMPDIR_SD3_MOUNT}
    fi
    mkdir ${TMPDIR_SD3_MOUNT}
    mount ${DEV_NAME}$p3 ${TMPDIR_SD3_MOUNT} 2>/dev/null  # updated by aman

    echo "Process: 3/4(Copy filesystem and mini package to SDcard)"
    copyFilesToSDcard
    if [ $? -ne 0 ];then
        return 1
    fi
    # end

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
filesClean

if [[ ret -ne 0 ]];then
    echo "Failed" > ${LogPath}/make_ubuntu_sd.result
    exit 1
fi
echo "Success" > ${LogPath}/make_ubuntu_sd.result
exit 0
# end
