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

usb_ethernet=""
usb_ip=""

usb_ethernets=`dmesg | grep "renamed from usb" | sort -r | cut -d ":" -f 2| cut -c 5- | uniq`
usb_number=`dmesg | grep "renamed from usb" | sort -r | cut -d ":" -f 2| cut -c 5- | uniq | wc -l`

function check_ip_addr()
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

function configure_usb_ethernet()
{
    name=$1
    address=$2
	fileName=$3
    echo "
network:
  version: 2
  renderer: NetworkManager
  ethernets:
     ${name}: 
       dhcp4: no 
       addresses: [${address}/24] 
       gateway4: 255.255.255.0 
       nameservers:
         addresses: [114.114.114.114]
" >> /etc/netplan/${fileName}
}

usage()
{
    echo "*********************************************************************************************************"
    echo "* Usage :"
    echo "* ./configure_usb_ethernet.sh .............    ..: configure usb by default ip: 192.168.1.166"
    echo "* ./configure_usb_ethernet.sh -s ip              : set usb with given ip"
    echo "* ./configure_usb_ethernet.sh -s usb_ethernet ip : if more than one usb name, set with usb name and ip"
    echo "* ./configure_usb_ethernet.sh -h|-help           : print help message"
    echo "*********************************************************************************************************"

    exit 1
}

function main()
{
    while true
    do
        case "$1" in
        -h | --h | -help | --help)
            usage
            exit 0
            ;;
        -s)
            if [ $# -eq 2 ]; then
                usb_ip=$2
                check_ip_addr ${usb_ip}
                if [ $? -ne 0 ];then
                    echo "Invalid ip, please check your command."
                    usage
                    exit 1
                fi
            elif [ $# -ge 3 ];then
                usb_ethernet=$2
                usb_ip=$3
                check_ip_addr ${usb_ip}
                if [ $? -ne 0 ];then
                    echo "Invalid ip, please check your command."
                    usage
                    exit 1
                fi
            fi
                break
                ;;
        "")
            break
            ;;
        *)
            echo "Invalid command."
            usage
            break
            ;;
        esac
    done

    if [ ${usb_number} -eq 0 ];then
        echo "No any unconfigured usb ethernet found, please check your environment."
        exit 1
    elif [ ${usb_number} -eq 1 ];then
        if [[ ${usb_ethernet}"X" == "X" ]];then
            usb_ethernet=${usb_ethernets}
        fi
    else
        if [[ ${usb_ethernet}"X" == "X" ]];then
            echo -e "Too many usb ethernets found: \n${usb_ethernets}\nPlease input usb ethernet which to configure."
            usage
            exit 1
        fi
    fi
    if [[ ${usb_ip}"X" == "X" ]];then
        echo "No input usb ip, use 192.168.1.166"
        usb_ip="192.168.1.166"
    fi
    echo ${usb_ethernets} | grep ${usb_ethernet} 1>/dev/null 2>&1
    if [ $? -ne 0 ];then
        echo "Input usb_ethernet: ${usb_ethernet} is not found, please check your command."
        exit 1
    fi
	
	cd "/etc/netplan"
	fileNum=`ls -l |grep "^-"|wc -l`
	cd -

	if [ $fileNum -eq 0 ];then
		touch /etc/netplan/01-network-manager-all.yaml
		fileName="01-network-manager-all.yaml"
	elif [ $fileNum -eq 1 ];then
		fileName=`ls /etc/netplan`
		grep "${usb_ethernet}:" /etc/netplan/$fileName 1>/dev/null 2>&1
		if [ $? -eq 0 ];then
			echo "${usb_ethernet}'s is already configured in /etc/netplan/interfaces, please check file for configuration."
			exit 0
		fi
    else
		echo "too many file in /etc/netplan, please check"
        exit 1
	fi
	
    /sbin/ifconfig | grep "${usb_ip}" 1>/dev/null 2>&1
    if [ $? -eq 0 ];then
        echo "Ip ${usb_ip} is already used, please input a unused usb ip."
        usage
        exit 1
    fi
    echo "Configure ${usb_ethernet} by ${usb_ip}"
    configure_usb_ethernet ${usb_ethernet} ${usb_ip} ${fileName}
    if [ -f "/etc/NetworkManager/NetworkManager.conf" ]; then
        sed -i "s/managed=false/managed=true/g" /etc/NetworkManager/NetworkManager.conf
        ifconfig ${usb_ethernet} down 1>/dev/null 2>&1
        ifconfig ${usb_ethernet} up 1>/dev/null 2>&1
        echo "Configure usb ip successfully."
		netplan apply
		echo "netplan apply successfully."
    else
        ifconfig ${usb_ethernet} down 1>/dev/null 2>&1
        #service networking restart
        /etc/init.d/networking restart
        echo "Configure usb ip successfully."
		netplan apply
		echo "netplan apply successfully."
    fi
}

main $*
