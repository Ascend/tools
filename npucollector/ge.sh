#!/bin/bash
graph_path=/extra-info/graph

pre_process()
{
    base_path=$1
    mkdir -p $base_path$graph_path
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
