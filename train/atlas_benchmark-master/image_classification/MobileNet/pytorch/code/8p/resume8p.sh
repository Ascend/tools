source set_env_b023.sh

su HwHiAiUser -c "adc --host 0.0.0.0:22118 --log \"SetLogLevel(0)[error]\" --device 0"
su HwHiAiUser -c "adc --host 0.0.0.0:22118 --log \"SetLogLevel(0)[error]\" --device 4"

export SLOG_PRINT_TO_STDOUT=0
export TASK_QUEUE_ENABLE=0
nohup python3.7 ./densenet121_8p_main.py \
    --addr='10.246.246.57' \
    --seed 49  \
    --workers 80 \
    --lr 0.8 \
    --print-freq 1 \
    --eval-freq 5\
    --arch densenet121 \
    --dist-url 'tcp://127.0.0.1:50000' \
    --dist-backend 'hccl' \
    --multiprocessing-distributed \
    --world-size 1 \
    --batch-size 2048 \
    --epochs 45 \
    --rank 0 \
    --amp \
    --benchmark 0 \
    --resume checkpoint.pth.tar \
    --data /train/imagenet > resume_8p.log &

