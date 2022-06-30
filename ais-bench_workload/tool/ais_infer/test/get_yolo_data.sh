#!/bin/bash
CUR_PATH=$(dirname $(readlink -f "$0"))

try_download_url(){
    local _url=$1
    local _packet=$2
    cmd="wget $_url --no-check-certificate -O $_packet"
    $cmd #>/dev/null 2>&1
    ret=$?
    if [ "$ret" == 0 -a -s "$_packet" ];then
        echo "download cmd:$cmd targetfile:$ OK"
    else
        echo "downlaod targetfile by $cmd Failed please check network or manual download to target file"
        return 1
    fi
}

convert_staticbatch_om()
{
    local _input_file=$1
    local _soc_version=$2
    local _staticbatch=$3
    local _input_tensor_name=$4
    local _framework=5

    # 静态batch转换
    for batchsize in $_staticbatch; do
        local _input_shape="$_input_tensor_name:$batchsize,3,416,416"
        local _pre_name=${_input_file%.*}
        local _om_path_pre="${_pre_name}_bs${batchsize}"
        local _om_path="$_om_path_pre.om"
        if [ ! -f $_om_path ];then
            local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework --input_shape=$_input_shape --soc_version=$_soc_version"
            $_cmd || { echo "atc run $_cmd failed"; return 1; }
        fi
    done
}

# 动态batch转换
convert_dymbatch_om()
{
    local _input_file=$1
    local _soc_version=$2
    local _dymbatch=$3
    local _input_tensor_name=$4
    local _framework=5

    local _input_shape="$_input_tensor_name:-1,3,416,416"
    local _pre_name=${_input_file%.*}
    local _om_path_pre="${_pre_name}_dymbatch"
    local _om_path="$_om_path_pre.om"

    if [ ! -f $_om_path ];then
        local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework --input_shape=$_input_shape -soc_version=$_soc_version --dynamic_batch_size=$_dymbatch"
        $_cmd || { echo "atc run $_cmd failed"; return 1; }
    fi
}

# 动态宽高 转换
convert_dymhw_om()
{
    local _input_file=$1
    local _soc_version=$2
    local _dymhw=$3
    local _input_tensor_name=$4
    local _framework=5

    local _input_shape="$_input_tensor_name:1,3,-1,-1"
    local _pre_name=${_input_file%.*}
    local _om_path_pre="${_pre_name}_dymwh"
    local _om_path="$_om_path_pre.om"

    if [ ! -f $_om_path ];then
        local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework --input_shape=$_input_shape -soc_version=$_soc_version --dynamic_image_size=$_dymhw"
        $_cmd || { echo "atc run $_cmd failed"; return 1; }
    fi
}

# 动态dims转换
convert_dymdim_om()
{
    local _input_file=$1
    local _soc_version=$2
    local _dymdim=$3
    local _input_tensor_name=$4
    local _framework=5

    local _input_shape="$_input_tensor_name:-1,3,-1,-1"
    local _pre_name=${_input_file%.*}
    local _om_path_pre="${_pre_name}_dymdim"
    local _om_path="$_om_path_pre.om"

    if [ ! -f $_om_path ];then
        local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
            --input_shape=$_input_shape -soc_version=$_soc_version --input_format=ND --dynamic_dims=$_dymdim"
        $_cmd || { echo "atc run $_cmd failed"; return 1; }
    fi
}

main()
{
    SOC_VERSION="Ascend310"
    PYTHON_COMMAND="python3.7"
    TESTDATA_PATH=$CUR_PATH/testdata/
    [ -d $TESTDATA_PATH ] || mkdir $TESTDATA_PATH
    [ -d $TESTDATA_PATH/tmp ] || mkdir $TESTDATA_PATH/tmp/

    model_url="https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/turing/resourcecenter/model/ATC%20Yolov3%20from%20Pytorch%20Ascend310/zh/1.1/ATC_Yolov3_from_Pytorch_Ascend310.zip"
    yolo_onnx_file="$TESTDATA_PATH/yolov3.onnx"
    if [ ! -f $yolo_onnx_file ]; then
        try_download_url $model_url $TESTDATA_PATH/tmp/a.zip || { echo "donwload stubs failed";return 1; }
        unzip $TESTDATA_PATH/tmp/a.zip -d $TESTDATA_PATH/tmp/
        origin_file="yolov3_bs16.onnx"
        find $TESTDATA_PATH/tmp/ -name $origin_file | xargs -I {} cp {} $yolo_onnx_file
    fi

    [ -f $yolo_onnx_file ] || { echo "find no $yolo_onnx_file return";return 1; }
    input_tensor_name="images"
    #out_nodes="Reshape_219:0;Reshape_203:0;Reshape_187:0"

    staticbatch="1 2 4 8"
    convert_staticbatch_om $yolo_onnx_file $SOC_VERSION "${staticbatch[*]}" $input_tensor_name || { echo "convert static om failed";return 1; }
    dymbatch="1,2,4,8"
    convert_dymbatch_om $yolo_onnx_file $SOC_VERSION $dymbatch $input_tensor_name || { echo "convert dymbatch om failed";return 1; }
    dymhw="224,224;448,448"
    convert_dymhw_om $yolo_onnx_file $SOC_VERSION $dymhw $input_tensor_name || { echo "convert dymhw om failed";return 1; }
    dymdims="1,224,224;8,448,448"
    convert_dymdim_om $yolo_onnx_file $SOC_VERSION $dymdims $input_tensor_name || { echo "convert dymdim om failed";return 1; }
}

main "$@"
exit $?