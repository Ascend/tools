# 运行程序使用的python命令
export PYTHON_COMMAND=python3.7.5
# 作业到达模式，默认为离线到达模式
export QUERY_ARRIVAL_MODE=offline
# 加载到内存中最大样本个数 如果运行设备内存受限，请开启该宏 填写符合匹配设备内存的值。
#export MAX_LOADSAMPLES_COUNT=1000
# 只处理如下变量个数的样本，而不是全部样本，用于调试。对于A500，建议用1000张图片
#export SAMPLE_COUNT=100
# 设置cache缓存地址，可以省略前处理过程 快速进行推理验证
#export CACHE_PATH=XXX

# 支持的profile场景,请查看readme文档
export PROFILE=resnet50_onnx
# om模型路径，请根据对应的profie场景的基准网站中查找原始模型和转换操作
export MODEL_PATH=/home/lcm/tool/ais_infer/test/resnet/resource/resnet50_v1_bs1_fp32.om
# batchszie大小。不设置默认为1
export BATCH_SIZE=1
# 数据集路径，请根据对应的profie场景的基准网站查找数据集来源和相关转换操作。
export DATASET_PATH=/home/datasets/imagenet/val/
# 指定推理运行的硬件卡数，默认为0卡
export DEVICE_ID=0

