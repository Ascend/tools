source set_env_b023.sh

su HwHiAiUser -c "adc --host 0.0.0.0:22118 --log \"SetLogLevel(0)[error]\" --device 0"

export SLOG_PRINT_TO_STDOUT=0
export TASK_QUEUE_ENABLE=0
nohup taskset -c 1-40 python3.7 densenet121_1p_main.py \
	--workers 40 \
	--arch densenet121 \
	--npu 0 \
	--lr 0.1 \
	--momentum 0.9 \
	--amp \
	--print-freq 1 \
	--eval-freq 5\
	--batch-size 256 \
	--epoch 90 \
	--data /opt/npu/dataset/imagenet > output_1p.log &
