
bert_staticbatch()
{
    # 静态batch测试
    staticbatch="1 2 4 8"
    for batchsize in $staticbatch; do
        input_shape="$ids_name:$batchsize,384;$mask_name:$batchsize,384;$seg_name:$batchsize,384"
        om_path_pre="${resource_path}/bert_squad_bs${batchsize}"
        om_path="$om_path_pre.om"
        if [ ! -f $om_path ];then
            cmd="atc --model=$pb_file --output=$om_path_pre --framework=3 --input_shape=$input_shape --soc_version=Ascend310 --out_nodes=logits:0"
            $cmd || { echo "atc run $cmd failed"; return 1; }
        fi

        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --debug || { echo "inference run $cmd failed"; return 1; }
        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --loop 30 || { echo "inference run $cmd failed"; return 1; }
        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path/$ids_name,$data_path/$mask_name,$data_path/$seg_name --output=$base_path/result/ || { echo "inference run $cmd failed"; return 1; }
        $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --device_id 3 --input=$data_path/$ids_name,$data_path/$mask_name,$data_path/$seg_name --output=$base_path/result/ || { echo "inference run $cmd failed"; return 1; }
    done
}

bert_dynamicbatch()
{
    # 动态batch测试
    dymbatch="1,2,4,8"
    om_path_pre="${resource_path}/bert_squad_dynamicbatchsize"
    om_path="$om_path_pre.om"
    if [ ! -f $om_path ];then
        batchsize=-1
        input_shape="$ids_name:$batchsize,384;$mask_name:$batchsize,384;$seg_name:$batchsize,384"
        cmd="atc --model=$pb_file --output=$om_path_pre --framework=3 --input_shape=$input_shape --soc_version=Ascend310 --dynamic_batch_size=$dymbatch --out_nodes=logits:0"
        $cmd || { echo "atc run $cmd failed"; return 1; }
    fi

    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --output=$base_path/result/ || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path/$ids_name,$data_path/$mask_name,$data_path/$seg_name --output=$base_path/result --dymBatch 1 || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path/$ids_name,$data_path/$mask_name,$data_path/$seg_name --output=$base_path/result --dymBatch 2 || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path/$ids_name,$data_path/$mask_name,$data_path/$seg_name --output=$base_path/result --dymBatch 4 || { echo "inference run failed"; return 1; }
    $PYTHON_COMMAND $CUR_PATH/../frontend/main.py --model $om_path --input=$data_path/$ids_name,$data_path/$mask_name,$data_path/$seg_name --output=$base_path/result --dymBatch 8 || { echo "inference run failed"; return 1; }
}

bert_test()
{
    # pb文件和数据集处理路径请参考 https://www.hiascend.com/zh/software/modelzoo/detail/1/0731fc6fb5fa4be7a4e7dfc9fe3e3110
    pb_file=$1
    data_path=$2
    base_path=$3

    resource_path=$base_path/resource
    mkdir -p $base_path/result/

    ids_name="input_ids"
    mask_name="input_mask"
    seg_name="segment_ids"

    bert_staticbatch || { echo "inference failed"; return 1; }
    bert_dynamicbatch || { echo "inference failed"; return 1; }
    # resnet_dynamichw || { echo "inference failed"; return 1; }
    # resnet_dynamicdims || { echo "inference failed"; return 1; }
    # resnet_dynamicshape || { echo "inference failed"; return 1; }
    return 0
}