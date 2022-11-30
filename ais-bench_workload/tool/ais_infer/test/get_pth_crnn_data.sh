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

function get_convert_file()
{
    rm -rf "$1"
    local convert_url="https://github.com/Ascend/ModelZoo-PyTorch/raw/master/ACL_PyTorch/built-in/cv/Resnet101_Pytorch_Infer/resnet101_pth2onnx.py"
    wget $convert_url -O $1
}

function get_aippConfig_file()
{
    rm -rf "$1"
    local aipp_config_url="https://github.com/Ascend/ModelZoo-PyTorch/raw/master/ACL_PyTorch/built-in/cv/Resnet50_Pytorch_Infer/aipp_resnet50.aippconfig"
    #local aipp_config_url="https://github.com/Ascend/ModelZoo-PyTorch/raw/master/ACL_PyTorch/built-in/cv/Resnet101_Pytorch_Infer/aipp.config"
    wget $aipp_config_url -O $1
}

convert_staticbatch_om()
{
    local _input_file=$1
    local _soc_version=$2
    local _staticbatch=$3
    local _input_tensor_name=$4
    local _aippconfig=$5
    local _framework=5

    # 静态batch转换
    for batchsize in $_staticbatch; do
        local _input_shape="$_input_tensor_name:$batchsize,1,32,100"
        local _pre_name=${_input_file%.*}
        local _om_path_pre="${_pre_name}_bs${batchsize}"
        local _om_path="$_om_path_pre.om"
        if [ ! -f $_om_path ];then
            local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
                --input_shape=$_input_shape --soc_version=$_soc_version \
                --input_format=NCHW "
            [ "$_aippconfig" != "" ] && _cmd="$_cmd --insert_op_conf=$_aippconfig"
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
    local _aippconfig=$5
    local _framework=5

    local _input_shape="$_input_tensor_name:-1,1,32,100"
    local _pre_name=${_input_file%.*}
    local _om_path_pre="${_pre_name}_dymbatch"
    local _om_path="$_om_path_pre.om"

    if [ ! -f $_om_path ];then
        local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
        --input_shape=$_input_shape -soc_version=$_soc_version --dynamic_batch_size=$_dymbatch \
        --input_format=NCHW "
        [ "$_aippconfig" != "" ] && _cmd="$_cmd --insert_op_conf=$_aippconfig"
        $_cmd || { echo "atc run $_cmd failed"; return 1; }
    fi
}


# 基准路径 https://github.com/Ascend/ModelZoo-PyTorch/tree/master/ACL_PyTorch/built-in/cv/Resnet101_Pytorch_Infer
main()
{
    SOC_VERSION=${1:-"Ascend310P3"}
    PYTHON_COMMAND=${2:-"python3"}
    TESTDATA_PATH=$CUR_PATH/testdata/crnn/model
    [ -d $TESTDATA_PATH ] || mkdir -p $TESTDATA_PATH

    model_url="https://ascend-repo-modelzoo.obs.cn-east-2.myhuaweicloud.com/c-version/CRNN_for_PyTorch/zh/1.3/m/CRNN_for_PyTorch_1.3_model.zip"
    crnn_onnx_file="$TESTDATA_PATH/pth_crnn.onnx"
    if [ ! -f $crnn_onnx_file ]; then
        crnn_zip_file="$TESTDATA_PATH/crnn.zip"
        try_download_url $model_url $crnn_zip_file || { echo "donwload crnn zip failed";return 1; }
        unzip $crnn_zip_file -d $TESTDATA_PATH
        cp $TESTDATA_PATH/CRNN_for_PyTorch_1.3_model/checkpoin.onnx $crnn_onnx_file
        [ ! -f $crnn_onnx_file ] && { echo "crnn file:$crnn_onnx_file not find";return 1; }
    fi

    input_tensor_name="actual_input_1"

    staticbatch="1 2 4 8 16"
    convert_staticbatch_om $crnn_onnx_file $SOC_VERSION "${staticbatch[*]}" $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert static om failed";return 1; }
    dymbatch="1,2,4,8,16"
    convert_dymbatch_om $crnn_onnx_file $SOC_VERSION $dymbatch $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert dymbatch om failed";return 1; }
}

main "$@"
exit $?