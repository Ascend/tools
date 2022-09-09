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

function get_aippConfig_file()
{
    rm -rf "$1"
    aipp_config_url="https://github.com/Ascend/ModelZoo-PyTorch/raw/master/ACL_PyTorch/built-in/cv/InceptionV3_for_Pytorch/aipp_inceptionv3_pth.config"
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
        local _input_shape="$_input_tensor_name:$batchsize,3,299,299"
        local _pre_name=${_input_file%.*}
        local _om_path_pre="${_pre_name}_bs${batchsize}"
        local _om_path="$_om_path_pre.om"
        if [ ! -f $_om_path ];then
            local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
                --input_shape=$_input_shape --soc_version=$_soc_version \
                --input_format=NCHW --enable_small_channel=1"
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

    local _input_shape="$_input_tensor_name:-1,3,299,299"
    local _pre_name=${_input_file%.*}
    local _om_path_pre="${_pre_name}_dymbatch"
    local _om_path="$_om_path_pre.om"

    if [ ! -f $_om_path ];then
        local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
        --input_shape=$_input_shape -soc_version=$_soc_version --dynamic_batch_size=$_dymbatch \
        --input_format=NCHW --enable_small_channel=1"
        [ "$_aippconfig" != "" ] && _cmd="$_cmd --insert_op_conf=$_aippconfig"
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
    local _aippconfig=$5
    local _framework=5

    local _input_shape="$_input_tensor_name:1,3,-1,-1"
    local _pre_name=${_input_file%.*}
    local _om_path_pre="${_pre_name}_dymwh"
    local _om_path="$_om_path_pre.om"

    if [ ! -f $_om_path ];then
        local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
        --input_shape=$_input_shape -soc_version=$_soc_version --dynamic_image_size=$_dymhw
        --input_format=NCHW --enable_small_channel=1"
        [ "$_aippconfig" != "" ] && _cmd="$_cmd --insert_op_conf=$_aippconfig"
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
    local _aippconfig=$5
    local _framework=5

    local _input_shape="$_input_tensor_name:-1,3,-1,-1"
    local _pre_name=${_input_file%.*}
    local _om_path_pre="${_pre_name}_dymdim"
    local _om_path="$_om_path_pre.om"

    if [ ! -f $_om_path ];then
        local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
            --input_shape=$_input_shape -soc_version=$_soc_version --input_format=ND --dynamic_dims=$_dymdim \
            --enable_small_channel=1"
        [ "$_aippconfig" != "" ] && _cmd="$_cmd --insert_op_conf=$_aippconfig"
        $_cmd || { echo "atc run $_cmd failed"; return 1; }
    fi
}

# 动态shape转换
convert_dymshape_om()
{
    local _input_file=$1
    local _soc_version=$2
    local _dymshapes=$3
    local _input_tensor_name=$4
    local _aippconfig=$5
    local _framework=5

    local _pre_name=${_input_file%.*}
    local _om_path_pre="${_pre_name}_dymshape"
    local _om_path="$_om_path_pre.om"

    if [ ! -f $_om_path ];then
        local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
            --input_shape_range=$_input_tensor_name:$_dymshapes --soc_version=$_soc_version \
            --input_format=NCHW --enable_small_channel=1"
        [ "$_aippconfig" != "" ] && _cmd="$_cmd --insert_op_conf=$_aippconfig"
        $_cmd || { echo "atc run $_cmd failed"; return 1; }
    fi
}

# 基准路径 https://github.com/Ascend/ModelZoo-PyTorch/tree/master/ACL_PyTorch/built-in/cv/Resnet101_Pytorch_Infer
main()
{
    SOC_VERSION="Ascend310"
    PYTHON_COMMAND="python3.7.5"
    TESTDATA_PATH=$CUR_PATH/testdata/
    [ -d $TESTDATA_PATH ] || mkdir $TESTDATA_PATH

    model_url="https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/003_Atc_Models/AE/ATC%20Model/InceptionV3/inceptionv3.onnx"
    onnx_file="$TESTDATA_PATH/pth_inceptionv3.onnx"
    if [ ! -f $onnx_file ]; then
        try_download_url $model_url $onnx_file || { echo "donwload stubs failed";return 1; }
    fi
    input_tensor_name="actual_input_1"

    AIPPCONFIG_FILE_PATH=$TESTDATA_PATH/aipp_inceptionsv3.aippconfig
    get_aippConfig_file $AIPPCONFIG_FILE_PATH || { echo "get aipp file failed";return 1; }

    # staticbatch="1 2 4 8"
    # convert_staticbatch_om $onnx_file $SOC_VERSION "${staticbatch[*]}" $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert static om failed";return 1; }
    dymbatch="1,2,4,8"
    convert_dymbatch_om $onnx_file $SOC_VERSION $dymbatch $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert dymbatch om failed";return 1; }
    dymhw="299,299"
    convert_dymhw_om $onnx_file $SOC_VERSION $dymhw $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert dymhw om failed";return 1; }
    # dymdims="1,224,224;8,448,448"
    # convert_dymdim_om $onnx_file $SOC_VERSION $dymdims $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert dymdim om failed";return 1; }
    # dymshapes="[1~16,3,200~300,200~300]"
    # convert_dymshape_om $onnx_file $SOC_VERSION $dymshapes $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert dymshape om failed";return 1; }
}

main "$@"
exit $?
