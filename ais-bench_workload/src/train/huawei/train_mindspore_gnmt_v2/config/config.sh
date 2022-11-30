export PYTHON_COMMAND=python3.7
export TRAIN_DATASET=/home/datasets/wmt16/mindrecord/train.tok.clean.bpe.32000.en.mindrecord
export TEST_DATASET=/home/datasets/wmt16/mindrecord/newstest2014.en.mindrecord
export EXISTED_CKPT_PATH=/home/datasets/pretrain_model/gnmt_v2/gnmtv2_ascend_v180_wmtende_official_nlp_acc24.ckpt
export VOCAB_ADDR=/home/datasets/wmt16/vocab.bpe.32000
export BPE_CODE_ADDR=/home/datasets/wmt16/bpe.32000
export TEST_TARGET=/home/datasets/wmt16/newstest2014.de

# 8p
export RANK_SIZE=8
export DEVICE_NUM=8

# options needed only if rank_size > 1
export RANK_TABLE_FILE=/home/tools/rank_table_8p_62.json

# needed only in cluster mode
# export NODEINFO_FILE=/home/lcm/tool/ssh64_66.json

