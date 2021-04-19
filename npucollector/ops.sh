#!/bin/bash
ops_path=/extra-info/ops

pre_process()
{
    base_path=$1
    mkdir -p $base_path$ops_path
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
}

$1 $2
