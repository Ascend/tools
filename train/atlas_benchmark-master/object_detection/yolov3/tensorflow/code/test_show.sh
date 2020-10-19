
#export CUDA_VISIBLE_DEVICES=''
#export CUDA_VISIBLE_DEVICES=7



# setting main path
MAIN_PATH=$(dirname $(readlink -f $0))

# set env
export PYTHONPATH=/usr/local/Ascend/ops/op_impl/built-in/ai_core/tbe/:$MAIN_PATH/../../../
export LD_LIBRARY_PATH=/usr/local/lib/:/usr/lib/:/usr/local/Ascend/fwkacllib/lib64/:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/:/usr/lib/x86_64-linux-gnu
PATH=$PATH:$HOME/bin
export PATH=$PATH:/usr/local/Ascend/fwkacllib/ccec_compiler/bin:$PATH
export ASCEND_OPP_PATH=/usr/local/Ascend/opp
export DDK_VERSION_FLAG=1.60.T49.0.B201
export NEW_GE_FE_ID=1
export GE_AICPU_FLAG=1
export SOC_VERSION=Ascend910
export RANK_ID=7
export RANK_SIZE=1
export DEVICE_ID=$RANK_ID
export DEVICE_INDEX=$RANK_ID
export JOB_ID=10087
export FUSION_TENSOR_SIZE=1000000000
#export SLOG_PRINT_TO_STDOUT=1
#export DUMP_GE_GRAPH=2
#export DUMP_GRAPH_LEVEL=3

su HwHiAiUser -c "adc --host 0.0.0.0:22118 --log \"SetLogLevel(0)[debug]\" --device "$RANK_ID

#RESTORE_PATH=/opt/npu/wujianping/epoch200/
RESTORE_PATH=/opt/npu/w00558981/yolov3_ok_bak_zip/training/t1/D0/training/
#RESTORE_PATH=/opt/npu/w00558981/training_done_yolov3/training/t1/D0/training/model-epoch_200_step_182000_loss_20.7852_lr_0

while :
do

#python3.7 eval.py \
#--save_img True \
#--score_thresh 0.2 \
#--restore_path $RESTORE_PATH \
#--max_test 10 \


python3.7 eval.py \
--save_json True \
--score_thresh 0.001 \
--restore_path $RESTORE_PATH \
--max_test 10000

break
sleep 1200

done


