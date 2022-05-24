#!/bin/bash
export PYTHON_COMMAND=python3.7.5
export BERT_CONFIG_DIR=/path_to_bert_model_folder
export TRAIN_DATA_PATH=/path_to_bert_data_file
export TRAIN_STEPS=200
export CUDA_VISIBLE_DEVICES="0"
export BATCH_SIZE=1
export MAX_SEQ_LENGTH=512

# bmc info get power info from bmc
export BMC_IP=""
export BMC_USER="Administrator"
export BMC_PASSWORD=""
