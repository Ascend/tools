export PYTHON_COMMAND=python3.7.5
export QUERY_ARRIVAL_MODE=offline
# 加载到内存中最大样本个数
#export MAX_LOADSAMPLES_COUNT=1000
# 只处理如下变量个数的样本，而不是全部样本，用于定制
#export SAMPLE_COUNT=100
# 设置cache缓存地址，可以省略前处理过程 快速进行推理验证
#export CACHE_PATH=XXX

# resnet
export PROFILE=resnet50_pytorch
export MODEL_PATH=/home/lcm/tool/inference_tools/test/resnet/resource/resnet50_v1_bs1_fp32.om
export BATCH_SIZE=1
export DATASET_PATH=/home/datasets/imagenet/val/

# yolo
#export PROFILE=yolov3-caffe_voc2012
#export MODEL_PATH=/home/yxd/yolov3/models/YoloV3/yolov3_bs1_in32_out32.om
#export BATCH_SIZE=1
#export DATASET_PATH=/home/datasets/VOC2012/VOCdevkit/VOC2012/

# deeplabv3
# export PROFILE=deeplabv3-tf_voc2012
# export MODEL_PATH=/home/zhou/code/DeepLabv3_for_TensorFlow/deeplabv3_tf_1batch.om
# export BATCH_SIZE=1
# export DATASET_PATH=/home/zhou/code/DeepLabv3_for_TensorFlow/scripts/PascalVoc2012