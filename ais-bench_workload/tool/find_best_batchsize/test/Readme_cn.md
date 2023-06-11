### test_aoe_mode.sh的相关说明
测试`find_best_batchsize.sh`需要指定模型路径以及相关开发环境的配置，`test_aoe_mode.sh`中部分命令需要用户自行修改：
```cmd
cmd="bash /../find_best_batchsize.sh 
    --model_path /xxx.prototxt  # 需要依据具体模型路径修改
    --weight_path /xxx.caffemodel # 需要依据具体权重文件路径修改，onnx和tf模型不需要
    --python_command python3.8  # 需要依据具体python版本修改
    --input_shape_str actual_input_1:batchsize,3,224,244 # 需要依据具体模型配置shape
    --soc_version Ascend310
    --loop_count 100
    --max_batch_num 64
    --aoe_mode 1
    --job_type 1
    "
$cmd
```