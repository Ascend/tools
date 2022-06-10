#!/bin/bash

if [ $# -lt 2 ];then
    echo -e "\033[31m[ERROR] argument num at least be 2 \033[0m"
    echo "argument1: npu dump onnx graph file, name has after_infershape, for example ge_onnx_00000012_graph_0_after_infershape.pbtxt"
    echo "argument2: on tf inference case: pb file used for atc command; on onnx inference case: onnx file used for atc command; on tf train case: geop dump graph from adapter, for example TF_GeOp5_0.pbtxt;"
    echo "argument3: on inference case: input_shape info, content consisted with pass to atc; other cast not need"
    exit
fi

npu_dump_graph=$1
cpu_file=$2
input_shape=$3
last_node=$4

if [ ! -f $npu_dump_graph ];then
    echo -e "\033[31m[ERROR] npu dump graph file not exist \033[0m"
    echo "argument1: npu dump onnx graph file, name has after_infershape, for example ge_onnx_00000012_graph_0_after_infershape.pbtxt"
    echo "argument2: on tf inference case: pb file used for atc command; on onnx inference case: onnx file used for atc command; on tf train case: geop dump graph from adapter, for example TF_GeOp5_0.pbtxt;"
    echo "argument3: on inference case: input_shape info, content consisted with pass to atc; other cast not need"
    exit
fi

if [ ! -f $cpu_file ];then
    echo -e "\033[31m[ERROR] cpu file not exist \033[0m"
    echo "argument1: npu dump onnx graph file, name has after_infershape, for example ge_onnx_00000012_graph_0_after_infershape.pbtxt"
    echo "argument2: on tf inference case: pb file used for atc command; on onnx inference case: onnx file used for atc command; on tf train case: geop dump graph from adapter, for example TF_GeOp5_0.pbtxt;"
    echo "argument3: on inference case: input_shape info, content consisted with pass to atc; other cast not need"
    exit
fi

if ! grep -q -E '.*ge_onnx.*after_infershape\.pbtxt$' <<< "$npu_dump_graph"; then
    echo -e "\033[31m[ERROR] npu dump graph must use onnx version, and use the one named after_infershape \033[0m"
    echo "argument1: npu dump onnx graph file, name has after_infershape, for example ge_onnx_00000012_graph_0_after_infershape.pbtxt"
    echo "argument2: on tf inference case: pb file used for atc command; on onnx inference case: onnx file used for atc command; on tf train case: geop dump graph from adapter, for example TF_GeOp5_0.pbtxt;"
    echo "argument3: on inference case: input_shape info, content consisted with pass to atc; other cast not need"
    exit
fi

is_train=0
is_pb=0
if grep -q -E '*.*\.pbtxt$' <<< "$cpu_file"; then
    is_train=1
    is_pb=1
elif grep -q -e '\.pb$' <<< "$cpu_file"; then
    is_train=0
    is_pb=1
elif grep -q -e '\.onnx$' <<< "$cpu_file"; then
    is_train=0
    is_pb=0
else
    echo -e "\033[31m[ERROR] cpu file not invalid \033[0m"
    echo "argument1: npu dump onnx graph file, name has after_infershape, for example ge_onnx_00000012_graph_0_after_infershape.pbtxt"
    echo "argument2: on tf inference case: pb file used for atc command; on onnx inference case: onnx file used for atc command; on tf train case: geop dump graph from adapter, for example TF_GeOp5_0.pbtxt;"
    echo "argument3: on inference case: input_shape info, content consisted with pass to atc; other cast not need"
    exit
fi

if [ -f cpu_infershape_result ];then
    rm -rf cpu_infershape_result
fi
if [ -f npu_infershape_result ];then
    rm -rf npu_infershape_result
fi


echo "[INFO] start to get cpu infershape result"

if [ $is_pb -eq 1 ];then
  ./pb_infer_run.sh $cpu_file $input_shape
else
  python3 onnx_model_infershape.py -m=$cpu_file -i=$input_shape
fi

if [ $? != 0 ];then
    echo -e "\033[31m[FOUND] cpu cannot infershape, please check origin model and input shape. \033[0m"
    exit
fi

if [ ! -f cpu_infershape_result ];then
    echo -e "\033[31m[ERROR] failed to get cpu infershape result \033[0m"
    exit
fi
echo "[INFO] finish to get cpu infershape result, store in file cpu_infershape_result"


echo "[INFO] start to analyze npu infershape result"

python3 analyze_onnx_graph.py $npu_dump_graph

if [ ! -f npu_infershape_result ];then
    echo -e "\033[31m[ERROR] failed to analyze npu infershape result \033[0m"
    exit
fi
echo "[INFO] finish to analyze npu infershape result, store in file npu_infershape_result"


echo "[INFO] start to compare two infershape result"

bash compare.sh $last_node


