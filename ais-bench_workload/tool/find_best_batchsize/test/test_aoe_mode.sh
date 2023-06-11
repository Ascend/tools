#!/bin/bash

# --python_command 需要依据具体python版本修改
# --model_path 需要依据具体模型路径修改
# --weight_path 需要依据具体权重文件路径修改
# --input_shape_str 需要依据具体模型配置

declare -i ret_ok=0

# 功能测试 
echo "test: model_type onnx, aoe_mode on, max_batch_num = 64"
echo "to test aoe mode for onnx model"
cmd="bash ../find_best_batchsize.sh 
    --model_path /home/y30044005/onnx_MDL/ResNeSt50/resnest50.onnx 
    --python_command python3.8 
    --input_shape_str actual_input_1:batchsize,3,224,244 
    --soc_version Ascend310
    --loop_count 100
    --max_batch_num 64
    --aoe_mode 1
    --job_type 1
    "
$cmd
cmd="rm -rf ../cache/"
$cmd

echo "test: model_type onnx, aoe_mode off, max_batch_num = 4"
echo "to test atc mode still avaliable"
cmd="bash ../find_best_batchsize.sh 
    --model_path /home/y30044005/onnx_MDL/ResNeSt50/resnest50.onnx
    --python_command python3.8 
    --input_shape_str actual_input_1:batchsize,3,224,244
    --soc_version Ascend310
    --loop_count 100
    --max_batch_num 4
    --aoe_mode 0
    --job_type 1
    "
$cmd
cmd="rm -rf ../cache/"
$cmd


# echo "test: model_type pb, aoe_mode on, max_batch_num = 8"
# echo "to test aoe mode for tf model"
# cmd="bash ../find_best_batchsize.sh 
#     --model_path /home/y30044005/tf_MDL/ResNet50/tf_resnet50.pb
#     --python_command python3.8 
#     --input_shape_str actual_input_1:batchsize,3,224,244
#     --soc_version Ascend310
#     --loop_count 100
#     --max_batch_num 8
#     --aoe_mode 1
#     --job_type 1
#     "
# $cmd
# cmd="rm -rf ../cache/"
# $cmd


# echo "test: model_type caffemodel, aoe_mode on, max_batch_num = 8"
# echo "to test aoe mode for caffe model"
# cmd="bash ../find_best_batchsize.sh 
#     --model_path /home/y30044005/caffe_MDL/ResNet50/ResNet50.prototxt
#     --weight_path /home/y30044005/caffe_MDL/ResNet50/ResNet50.caffemodel
#     --python_command python3.8 
#     --input_shape_str actual_input_1:batchsize,3,224,244
#     --soc_version Ascend310
#     --loop_count 100
#     --max_batch_num 64
#     --aoe_mode 1
#     --job_type 1
#     "
# $cmd
# cmd="rm -rf ../cache/"
# $cmd


# 异常情况测试
echo "test: model_type onnx, aoe_mode = 3, max_batch_num = 8"
echo "to test illegal aoe_mode input"
cmd="bash ../find_best_batchsize.sh 
    --model_path /home/y30044005/onnx_MDL/ResNeSt50/resnest50.onnx
    --python_command python3.8 
    --input_shape_str actual_input_1:batchsize,3,224,244
    --soc_version Ascend310
    --loop_count 100
    --max_batch_num 8
    --aoe_mode 3
    --job_type 1
    "
$cmd
cmd="rm -rf ../cache/"
$cmd


echo "test: model_type onnx, job_type = 3, max_batch_num = 8"
echo "to test illegal job_type input"
cmd="bash ../find_best_batchsize.sh 
    --model_path /home/y30044005/onnx_MDL/ResNeSt50/resnest50.onnx
    --python_command python3.8 
    --input_shape_str actual_input_1:batchsize,3,224,244
    --soc_version Ascend310
    --loop_count 100
    --max_batch_num 8
    --aoe_mode 1
    --job_type 3
    "
$cmd
cmd="rm -rf ../cache/"
$cmd