#!/bin/bash
install_path=/log/host/install
environment_path=/extra-info/environment

pre_process()
{
    base_path=$1
    mkdir -p $base_path$install_path
    mkdir -p $base_path$environment_path

    ps aux > $base_path$environment_path/process_status
    free > $base_path$environment_path/cache_memory_status
    df -h > $base_path$environment_path/disk_memory_status

    uname -a > $base_path$environment_path/kernel_info
    cat /proc/version > $base_path$environment_path/os_info
}

running_process_once()
{
    return
}

running_process()
{
    base_path=$1
    while true
    do
        running_process_once $1
	sleep 60
    done
}

post_process()
{
    base_path=$1
    if [ "$HOME" == "/root" ];then
        file=/var/log/ascend_seclog/ascend_install.log
	if [ -e $file -a -r $file ];then
	    cp $file $base_path$install_path
	else
            echo "[error] install_file:$file can't reach"
        fi
    else
        file=$HOME/var/log/ascend_seclog/ascend_install.log
	if [ -e $file -a -r $file ];then
	    cp $file $base_path$install_path
	else
            echo "[error] install_file:$file can't reach"
        fi
    fi
}

$1 $2
