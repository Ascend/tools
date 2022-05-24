
resnet_staticbatch()
{
    # 静态batch测试
    staticbatch="1 2 4"
    for batchsize in $staticbatch; do
        input_shape="$input_tensor_name:$batchsize,3,224,224"
        om_path_pre="${resource_path}/resnet50_v1_bs${batchsize}_fp32"
        om_path="$om_path_pre.om"
        if [ ! -f $om_path ];then
            cmd="atc --model=$onnx_file --output=$om_path_pre --framework=5 --input_shape=$input_shape --input_format=NCHW --soc_version=Ascend310"
            $cmd || { echo "atc run $cmd failed"; return 1; }
        fi

        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path  || { echo "inference run $cmd failed"; return 1; }
        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --loop 100  || { echo "inference run $cmd failed"; return 1; }

        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result/ || { echo "inference run $cmd failed"; return 1; }
        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result/ --device_id 3 || { echo "inference run $cmd failed"; return 1; }
    done
}

resnet_dynamicbatch()
{
    # 动态batch测试
    dymbatch="1,2,4,8"
    om_path_pre="${resource_path}/resnet50_v1_dynamicbatchsize_fp32"
    om_path="$om_path_pre.om"
    if [ ! -f $om_path ];then
        cmd="atc --model=$onnx_file --output=$om_path_pre --framework=5 --input_shape=$input_tensor_name:-1,3,224,224 --input_format=NCHW --soc_version=Ascend310 --dynamic_batch_size=$dymbatch"
        $cmd || { echo "atc run $cmd failed"; return 1; }
    fi

    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --output=$base_path/result/ || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymBatch 1 || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymBatch 2 || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymBatch 4 || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymBatch 8 || { echo "inference run failed"; return 1; }
}

resnet_dynamichw()
{
    # 动态dims测试
    dymhw="224,224;448,448"
    om_path_pre="${resource_path}/resnet50_v1_dynamichw_fp32"
    om_path="$om_path_pre.om"
    if [ ! -f $om_path ];then
        cmd="atc --model=$onnx_file --output=$om_path_pre --framework=5 --input_shape=$input_tensor_name:8,3,-1,-1 --dynamic_image_size=$dymhw --soc_version=Ascend310 --input_format=NCHW"
        $cmd || { echo "atc run $cmd failed"; return 1; }
    fi

    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymHW "224,224" || { echo "inference run failed"; return 1; }
}

resnet_dynamicdims()
{
    # 动态dims测试
    dymdims="1,224,224;8,448,448"
    om_path_pre="${resource_path}/resnet50_v1_dynamicdims_fp32"
    om_path="$om_path_pre.om"
    if [ ! -f $om_path ];then
        cmd="atc --model=$onnx_file --output=$om_path_pre --framework=5 --input_shape=$input_tensor_name:-1,3,-1,-1 --soc_version=Ascend310 --input_format=ND --dynamic_dims=$dymdims"
        $cmd || { echo "atc run $cmd failed"; return 1; }
    fi

    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymDims "$input_tensor_name:1,3,224,224" || { echo "inference run failed"; return 1; }
}

resnet_dynamicshape()
{
    # 动态dims测试
    dymshapes="[1~8,3,200~300,200~300]"
    om_path_pre="${resource_path}/resnet50_v1_dynamicshape_fp32"
    om_path="$om_path_pre.om"
    if [ ! -f $om_path ];then
        cmd="atc --model=$onnx_file --output=$om_path_pre --framework=5 --input_shape_range=$input_tensor_name:$dymshapes --soc_version=Ascend310 --input_format=NCHW"
        $cmd || { echo "atc run $cmd failed"; return 1; }
    fi

    # 纯推理场景
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymShape "$input_tensor_name:1,3,224,224" --outputSize 10000 || { echo "inference run failed"; return 1; }

    # 文件输入场景
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymShape "$input_tensor_name:1,3,224,224" --outputSize 10000 || { echo "inference run failed"; return 1; }
}

resnet_test()
{
    # 传递 onnx模型文件 用于模型转换
    # onnx文件请参考https://bbs.huaweicloud.com/forum/thread-97042-1-1.html
    onnx_file=$1
    # 传递数据集处理后的路径。比如 bin文件 需要与模型输入匹配
    # 数据集请处理为模型需要格式 比如nchw格式
    data_path=$2
    # 基本目录。用于保存临时文件
    base_path=$3

    resource_path=$base_path/resource
    mkdir -p $base_path/result/

    input_tensor_name="actual_input_1"

    resnet_staticbatch || { echo "inference failed"; return 1; }
    resnet_dynamicbatch || { echo "inference failed"; return 1; }
    resnet_dynamichw || { echo "inference failed"; return 1; }
    resnet_dynamicdims || { echo "inference failed"; return 1; }
    resnet_dynamicshape || { echo "inference failed"; return 1; }
    return 0
}