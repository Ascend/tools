export ASCEND_HOME=/usr/local/Ascend
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/:/usr/lib/:/usr/local/Ascend/nnae/latest/fwkacllib/lib64:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/:/usr/local/python3.7.5/lib/
export PYTHONPATH=${PYTHONPATH}:/usr/local/Ascend/nnae/latest/fwkacllib/python/site-packages/:/usr/local/Ascend/nnae/latest/fwkacllib/python/site-packages/auto_tune.egg/auto_tune:/usr/local/Ascend/nnae/latest/fwkacllib/python/site-packages/schedule_search.egg:/usr/local/Ascend/nnae/latest/opp/op_impl/built-in/ai_core/tbe:/usr/local/Ascend/nnae/latest/fwkacllib/python/site-packages/hccl
export PATH=$PATH:/usr/local/Ascend/nnae/latest/fwkacllib/ccec_compiler/bin
export ASCEND_OPP_PATH=/usr/local/Ascend/nnae/latest/opp/
export PYTHONPATH=$PYTHONPATH:${PWD}
export SLOG_PRINT_TO_STDOUT=0
export TASK_QUEUE_ENABLE=1
taskset -c 0-64 python3.7 examples/imagenet/main.py --data=/data/imagenet --arch=efficientnet-b0 --batch-size=256 --lr=0.2 --epochs=200 --autoaug --npu=0 --amp --pm=O1 --loss_scale=1024
