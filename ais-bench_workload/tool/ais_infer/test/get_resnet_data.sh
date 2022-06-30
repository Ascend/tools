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

# 取自https://github.com/Ascend/ModelZoo-PyTorch/blob/master/ACL_PyTorch/built-in/cv/Resnet50_Pytorch_Infer/pth2onnx.py
function get_convert_file()
{
    (
      cat << EOF
import sys

import torch
import torch.onnx
import torchvision.models as models


def convert(pthfile, onnx_path):
    model = models.resnet50(pretrained=False)
    resnet50 = torch.load(pthfile, map_location='cpu')
    model.load_state_dict(resnet50)
    print(model)

    input_names = ["actual_input_1"]
    output_names = ["output1"]
    dummy_input = torch.randn(16, 3, 224, 224)
    torch.onnx.export(
        model, 
        dummy_input,
        onnx_path,
        input_names=input_names, 
        output_names=output_names, 
        opset_version=11)


if __name__ == "__main__":
    pth_path = sys.argv[1]
    onnx_path = sys.argv[2]
    convert(pth_path, onnx_path)
EOF
    ) > $1
}

# 取自https://github.com/Ascend/ModelZoo-PyTorch/blob/master/ACL_PyTorch/built-in/cv/Resnet50_Pytorch_Infer/aipp_resnet50.aippconfig
function get_aippConfig_file()
{
    (
      cat << EOF
aipp_op{
    aipp_mode:static
    input_format : RGB888_U8

    src_image_size_w : 256
    src_image_size_h : 256

    crop: true
    load_start_pos_h : 16
    load_start_pos_w : 16
    crop_size_w : 224
    crop_size_h: 224

    min_chn_0 : 123.675
    min_chn_1 : 116.28
    min_chn_2 : 103.53
    var_reci_chn_0: 0.0171247538316637
    var_reci_chn_1: 0.0175070028011204
    var_reci_chn_2: 0.0174291938997821
}
EOF
    ) > $1
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
        local _input_shape="$_input_tensor_name:$batchsize,3,224,224"
        local _pre_name=${_input_file%.*}
        local _om_path_pre="${_pre_name}_bs${batchsize}"
        local _om_path="$_om_path_pre.om"
        if [ ! -f $_om_path ];then
            local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
                --input_shape=$_input_shape --soc_version=$_soc_version \
                --input_format=NCHW --enable_small_channel=1"
            [ "$_aippconfig" != "" ] && cmd="$cmd --insert_op_conf=$_aippconfig"
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

    local _input_shape="$_input_tensor_name:-1,3,224,224"
    local _pre_name=${_input_file%.*}
    local _om_path_pre="${_pre_name}_dymbatch"
    local _om_path="$_om_path_pre.om"

    if [ ! -f $_om_path ];then
        local _cmd="atc --model=$_input_file --output=$_om_path_pre --framework=$_framework \
        --input_shape=$_input_shape -soc_version=$_soc_version --dynamic_batch_size=$_dymbatch \
        --input_format=NCHW --enable_small_channel=1"
        [ "$_aippconfig" != "" ] && cmd="$cmd --insert_op_conf=$_aippconfig"
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
        [ "$_aippconfig" != "" ] && cmd="$cmd --insert_op_conf=$_aippconfig"
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
        [ "$_aippconfig" != "" ] && cmd="$cmd --insert_op_conf=$_aippconfig"
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
        [ "$_aippconfig" != "" ] && cmd="$cmd --insert_op_conf=$_aippconfig"
        $_cmd || { echo "atc run $_cmd failed"; return 1; }
    fi
}

main()
{
    SOC_VERSION="Ascend310"
    PYTHON_COMMAND="python3.7"
    TESTDATA_PATH=$CUR_PATH/testdata/
    [ -d $TESTDATA_PATH ] || mkdir $TESTDATA_PATH

    model_url="https://download.pytorch.org/models/resnet50-0676ba61.pth"
    resnet_pth_file="$TESTDATA_PATH/resnet50.pth"
    if [ ! -f $resnet_pth_file ]; then
        try_download_url $model_url $resnet_pth_file || { echo "donwload stubs failed";return 1; }
    fi

    resnet_onnx_file="$TESTDATA_PATH/resnet50_official.onnx"
    input_tensor_name="actual_input_1"
    if [ ! -f $resnet_onnx_file ]; then
        # generate resnet50_convert_pth_to_onnx.py
        CONVERT_FILE_PATH=$TESTDATA_PATH/resnet50_convert_pth_to_onnx.py
        get_convert_file $CONVERT_FILE_PATH || { echo "get convert file failed";return 1; }
        $PYTHON_COMMAND $CONVERT_FILE_PATH $resnet_pth_file  $resnet_onnx_file || { echo "convert pth to onnx failed";return 1; }
    fi

    AIPPCONFIG_FILE_PATH=$TESTDATA_PATH/aipp_resnet50.aippconfig
    get_aippConfig_file $AIPPCONFIG_FILE_PATH || { echo "get aipp file failed";return 1; }

    staticbatch="1 2 4 8"
    convert_staticbatch_om $resnet_onnx_file $SOC_VERSION "${staticbatch[*]}" $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert static om failed";return 1; }
    dymbatch="1,2,4,8"
    convert_dymbatch_om $resnet_onnx_file $SOC_VERSION $dymbatch $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert dymbatch om failed";return 1; }
    dymhw="224,224;448,448"
    convert_dymhw_om $resnet_onnx_file $SOC_VERSION $dymhw $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert dymhw om failed";return 1; }
    dymdims="1,224,224;8,448,448"
    convert_dymdim_om $resnet_onnx_file $SOC_VERSION $dymdims $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert dymdim om failed";return 1; }
    dymshapes="[1~16,3,200~300,200~300]"
    convert_dymshape_om $resnet_onnx_file $SOC_VERSION $dymshapes $input_tensor_name $AIPPCONFIG_FILE_PATH || { echo "convert dymshape om failed";return 1; }
}

main "$@"
exit $?