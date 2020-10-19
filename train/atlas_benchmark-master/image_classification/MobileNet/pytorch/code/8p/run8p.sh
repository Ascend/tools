#!/usr/bin/env bash
source set_env_b023.sh

su HwHiAiUser -c "adc --host 0.0.0.0:22118 --log \"SetLogLevel(0)[error]\" --device 0"
su HwHiAiUser -c "adc --host 0.0.0.0:22118 --log \"SetLogLevel(0)[error]\" --device 4"

export SLOG_PRINT_TO_STDOUT=0
export TASK_QUEUE_ENABLE=0
nohup python3.7 ./mobilenetv2_8p_main.py \
    --addr='10.246.246.76' \
    --seed 49  \
    --workers 80 \
    --lr 0.24 \
    --print-freq 1 \
    --eval-freq 5\
    --dist-url 'tcp://127.0.0.1:50002' \
    --dist-backend 'hccl' \
    --multiprocessing-distributed \
    --world-size 1 \
    --batch-size 6144 \
    --epochs 600 \
    --rank 0 \
    --amp \
    --benchmark 0 \
    --data /opt/npu/dataset/imagenet > output_8p.log &

