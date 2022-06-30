export PYTHON_COMMAND=python3.7
export QUERY_ARRIVAL_MODE=offline
# 加载到内存中最大样本个数
#export MAX_LOADSAMPLES_COUNT=1000
# 只处理如下变量个数的样本，而不是全部样本，用于定制
export SAMPLE_COUNT=70
# 设置cache缓存地址，可以省略前处理过程 快速进行推理验证
#export CACHE_PATH=XXX

export PROFILE=bert_large_masked_lm
export MODEL_PATH=/home/wb/ais-bench-master/src/inference/language/bert-maskedlm/saved_model.om
export DATASET_PATH=/home/wb/ais-bench-master/src/inference/language/bert-maskedlm/sample_text.txt
export VOCAB_FILE=/home/wb/ais-bench-master/src/inference/language/bert-maskedlm/uncased_L-24_H-1024_A-16/vocab.txt
export BATCH_SIZE=1
export DEVICE_ID=0
# export PROFILE=bert_large_squad
# export MODEL_PATH=/home/lcm/tool/ais-bench-inference-tools-aarch64/test/bert/resource/bert_squad_bs1.om
# export DATASET_PATH=/home/lcm/tool/infer_bert/data/SQuAD1.1/dev-v1.1.json
# export VOCAB_FILE=/home/lcm/tool/infer_bert/data/uncased_L-12_H-768_A-12/vocab.txt
# export BATCHSIZE=1
