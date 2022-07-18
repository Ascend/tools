#!/bin/bash
bbox_path=/extra-info/bbox
device_stackcore_path=/extra-info/stackcore/device

host_cann_log_path=/log/host/cann
host_cann_debug_log_path=/log/host/cann/debug
host_cann_run_log_path=/log/host/cann/run
host_driver_log_path=/log/host/driver
device_aicpu_path=/log/device/aicpu
device_driver_path=/log/device/driver
device_firmware_path=/log/device/firmware
device_system_path=/log/device/system


device_msreport_path=/log/device-msreport

pre_process()
{
    base_path=$1
    mkdir -p $base_path$bbox_path
    mkdir -p $base_path$device_stackcore_path

    mkdir -p $base_path$host_cann_log_path
    mkdir -p $base_path$host_driver_log_path
    mkdir -p $base_path$device_aicpu_path
    mkdir -p $base_path$device_driver_path
    mkdir -p $base_path$device_firmware_path
    mkdir -p $base_path$device_system_path

    mkdir -p $base_path$device_msreport_path
    mkdir -p $base_path$device_msreport_path/target
}

running_process_once()
{
    base_path=$1
    #process host
    if [ -d $base_path/tmp/plog/ ];then
        \cp -f $base_path/tmp/plog/* $base_path$host_cann_log_path
    fi
    #adapter new log dir
    if [ -d $base_path/tmp/debug/plog/ ];then
        \cp -rf $base_path/tmp/debug/plog/* $base_path$host_cann_debug_log_path
    fi
    if [ -d $base_path/tmp/run/plog/ ];then
        \cp -rf $base_path/tmp/run/plog/* $base_path$host_cann_run_log_path
    fi
    #process device aicpu
    if [ -d $base_path/tmp/device-*/ ];then
        \cp -rf $base_path/tmp/device* $base_path$device_aicpu_path
    fi
    if [ -d $base_path/tmp/debug/device-*/ ];then
        \cp -rf $base_path/tmp/debug/device* $base_path$device_aicpu_path
    fi
    #process device_msreport
    if [ "$HOME" == "/root" ];then
        cd $base_path$device_msreport_path
        msnpureport >/dev/null 2>&1
        if [ $? -ne 0 ];then
            echo "[error] cmd msnpureport for get device log info failed"
        fi
        curr_dir_name=`ls | grep -v target`
        if [ -n "$curr_dir_name" ];then
            \cp -rf ./$curr_dir_name/* target
            rm -rf ./$curr_dir_name
        fi
    fi
}

running_process()
{
    while true
    do
        running_process_once $1
    sleep 1
    done
}

post_process()
{
    base_path=$1
    #process host
    if [ "`ls -A $base_path$host_cann_log_path`" == "" ];then
        echo "[error] no host log collected"
    fi

    #process aicpu
    if [ "`ls -A $base_path$device_aicpu_path`" == "" ];then
        echo "[error] no device-aicpu log collected"
    fi

    rm -rf $base_path/tmp

    #process device_msreport
    if [ "$HOME" == "/root" ];then
        if [ "`ls -A $base_path$device_msreport_path/target/`" == "" ];then
            echo "[error] no device-msreport log collected"
        else
            #bbox
            for file in `ls -l $base_path$device_msreport_path/target/hisi_logs | grep ^- | awk '{print $9}'`
            do
                mv $base_path$device_msreport_path/target/hisi_logs/$file $base_path$bbox_path
            done
 
            for dir in `ls -l $base_path$device_msreport_path/target/hisi_logs | grep ^d | awk '{print $9}'`
            do
                mkdir -p $base_path$bbox_path/$dir
                for file in `find $base_path$device_msreport_path/target/hisi_logs/$dir -type f`
                do
                    mv $file $base_path$bbox_path/$dir
                done
            done

            #driver
            for dir in `ls -l $base_path$device_msreport_path/target/message | grep ^d | awk '{print $9}'`
            do
                mkdir -p $base_path$device_driver_path/$dir
                for file in `find $base_path$device_msreport_path/target/message/$dir -type f`
                do
                    mv $file $base_path$device_driver_path/$dir
                done
            done

            #system
            for dir in `ls -l $base_path$device_msreport_path/target/slog | grep ^d | awk '{print $9}'`
            do
                mkdir -p $base_path$device_system_path/$dir
                for file in `find $base_path$device_msreport_path/target/slog/$dir/device-os -type f`
                do
                    mv $file $base_path$device_system_path/$dir
                done
                for file in `find $base_path$device_msreport_path/target/slog/$dir/slogd -type f`
                do
                    mv $file $base_path$device_system_path/$dir
                done
            done

            #firmware
            for absolute_dir in `find $base_path$device_msreport_path/target/slog/ -name "device-[0-9]"`
            do
                mkdir -p $base_path$device_firmware_path/${absolute_dir##*/}
                for file in `find $absolute_dir -type f`
                do
                    mv $file $base_path$device_firmware_path/${absolute_dir##*/}
                done
            done

            #stackcore
            for dir in `ls -l $base_path$device_msreport_path/target/stackcore | grep ^d | awk '{print $9}'`
            do
                mkdir -p $base_path$device_stackcore_path/$dir
                for file in `find $base_path$device_msreport_path/target/stackcore/$dir -type f`
                do
                    mv $file $base_path$device_stackcore_path/$dir
                done
            done

        fi
    else
        echo "[info] user not root, skip device-msreport log collect"
    fi
    rm -rf $base_path$device_msreport_path

    #process host message
    if [ "$HOME" == "/root" ];then
        file=/var/log/messages
        if [ -f $file -a -r $file ];then
            cp $file $base_path$host_driver_log_path
        else
            echo "[error] messages_file:$file can't reach"
        fi
    else
        echo "[info] user not root, skip messages log collect"
    fi
}

$1 $2
