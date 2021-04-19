#!/bin/bash
core_path=/extra-info/stackcore/host

pre_process()
{
    base_path=$1
    mkdir -p $base_path$core_path

    cat /proc/sys/kernel/core_pattern > $base_path$core_path/pattern
    ulimit -c > $base_path$core_path/config

    echo "$base_path$core_path/core.%e.%p" > /proc/sys/kernel/core_pattern
}

running_process_once()
{
    return
}

running_process()
{
    while true
    do
        running_process_once $1
	sleep 60
    done
}

post_process()
{
    base_path=$1
    cat $base_path$core_path/pattern > /proc/sys/kernel/core_pattern
    ulimit -c `cat $base_path$core_path/config`
    rm $base_path$core_path/pattern
    rm $base_path$core_path/config
}

$1 $2
