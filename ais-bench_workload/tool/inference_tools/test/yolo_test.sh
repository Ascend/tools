
yolo_staticbatch()
{
    # 静态batch测试
    staticbatch="1"
    for batchsize in $staticbatch; do
        input_shape="$input_tensor_name:$batchsize,3,416,416"
        om_path_pre="${resource_path}/yolo_bs${batchsize}"
        om_path="$om_path_pre.om"
        if [ ! -f $om_path ];then
            cmd="atc --model=$onnx_file --output=$om_path_pre --framework=5 --input_shape=$input_shape --out_nodes=$out_nodes --input_format=NCHW --soc_version=Ascend310"
            $cmd || { echo "atc run $cmd failed"; return 1; }
        fi

        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path  || { echo "inference run $cmd failed"; return 1; }
        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --loop 100  || { echo "inference run $cmd failed"; return 1; }

        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result/ || { echo "inference run $cmd failed"; return 1; }
        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result/ --device_id 3 || { echo "inference run $cmd failed"; return 1; }
    done
}

yolo_dynamicbatch()
{
    # 动态batch测试
    dymbatch="1,2,4,8"
    om_path_pre="${resource_path}/yolo_dynamicbatchsize"
    om_path="$om_path_pre.om"
    if [ ! -f $om_path ];then
        cmd="atc --model=$onnx_file --output=$om_path_pre --framework=5 --input_shape=$input_tensor_name:-1,3,416,416 --out_nodes=$out_nodes --input_format=NCHW --soc_version=Ascend310 --dynamic_batch_size=$dymbatch"
        $cmd || { echo "atc run $cmd failed"; return 1; }
    fi

    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --output=$base_path/result/ || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymBatch 1 || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymBatch 2 || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymBatch 4 || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymBatch 8 || { echo "inference run failed"; return 1; }
}

yolo_dynamichw()
{
    # 动态dims测试
    dymhw="416,416;832,832"
    om_path_pre="${resource_path}/yolo_dynamichw"
    om_path="$om_path_pre.om"
    if [ ! -f $om_path ];then
        cmd="atc --model=$onnx_file --output=$om_path_pre --framework=5 --input_shape=$input_tensor_name:1,3,-1,-1 --out_nodes=$out_nodes --input_format=NCHW --soc_version=Ascend310 --dynamic_image_size=$dymhw"
        $cmd || { echo "atc run $cmd failed"; return 1; }
    fi

    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path --output=$base_path/result --dymHW "416,416" || { echo "inference run failed"; return 1; }
}

yolo_test()
{
    # 传递 onnx模型文件 用于模型转换
    # onnx文件请参考https://www.hiascend.com/zh/software/modelzoo/detail/1/36ea401e0d844f549da2693c6289ad89
    onnx_file=$1
    # 传递数据集处理后的路径。比如 bin文件 需要与模型输入匹配
    # 数据集请处理为模型需要格式 比如nchw格式
    data_path=$2
    # 基本目录。用于保存临时文件
    base_path=$3

    resource_path=$base_path/resource
    mkdir -p $base_path/result/

    input_tensor_name="images"
    out_nodes="Reshape_219:0;Reshape_203:0;Reshape_187:0"

    yolo_staticbatch || { echo "inference failed"; return 1; }
    yolo_dynamicbatch || { echo "inference failed"; return 1; }
    #yolo_dynamichw || { echo "inference failed"; return 1; }
    return 0
}