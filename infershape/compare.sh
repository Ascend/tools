#!/bin/bash

npu_file=npu_infershape_result
cpu_file=cpu_infershape_result

cat $npu_file | while read npu_line
do
    npu_array=(${npu_line/ / })
    npu_node=${npu_array[0]}
    npu_index=${npu_array[1]}
    npu_shape=${npu_array[2]}

    # search name, no match then skip
    cpu_line=`grep -r "$npu_node" $cpu_file`
    if [ "$cpu_line" == "" ]; then
        echo "[INFO] cpu result has no $npu_node"
        continue
    fi

    # search name and index, no match then judge ERROR
    cpu_line=`grep -r "$npu_node $npu_index" $cpu_file`
    if [ "$cpu_line" == "" ]; then
        echo -e "\033[31m[ERROR] cpu result has no same $npu_index for $npu_node \033[0m"
        exit
    fi

    # shape match judge, match then continue
    cpu_array=(${cpu_line/ / })
    cpu_shape=${cpu_array[2]}
    if [ $cpu_shape == $npu_shape ]; then
        continue
    fi

    # shape not match, search ? in cpu result, if exist print warning and go on, else judge ERROR
    cpu_shape_raw=${cpu_shape##*shape:[}
    cpu_shape_raw=${cpu_shape_raw%%]}

    npu_shape_raw=${npu_shape##*shape:[}
    npu_shape_raw=${npu_shape_raw%%]}

    cpu_shape_array=(${cpu_shape_raw//,/ })
    npu_shape_array=(${npu_shape_raw//,/ })

    i=0
    for cpu_dim in ${cpu_shape_array[@]}
    do
        if [ $cpu_dim != ${npu_shape_array[$i]} ] && [ $cpu_dim != "?"]; then
            echo -e "\033[31m[FOUND] $npu_node is the first one which out $npu_index's $npu_shape different from cpu $cpu_shape \033[0m"
            exit
        fi
        i=$i+1
    done
    echo "[WARNING] $node cpu infer result is unknown, can't be compared"
done

echo "[INFO] end to compare, no mismatch node found"
