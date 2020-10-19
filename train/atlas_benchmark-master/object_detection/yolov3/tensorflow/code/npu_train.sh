#!/bin/bash
scriptDir=$(cd "$(dirname "$0")"; pwd)
currentDir=$(cd "$(dirname "$scriptDir")"; pwd)

# set env
source ${currentDir}/config/npu_set_env.sh

# setting main path
CODE_PATH=currentDir/code

# set env
export ASCEND_HOME=/usr/local/Ascend
export LD_LIBRARY_PATH=/usr/local/lib/:/usr/lib/:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/lib64:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/
export PYTHONPATH=$PYTHONPATH:/usr/local/Ascend/ascend-toolkit/latest/opp/op_impl/built-in/ai_core/tbe:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/python/site-packages/te:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/python/site-packages/topi:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/python/site-packages/hccl:/usr/local/Ascend/ascend-toolkit/latest/tfplugin/python/site-packages:$currentDir
export PATH=$PATH:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/ccec_compiler/bin
export ASCEND_OPP_PATH=/usr/local/Ascend/ascend-toolkit/latest/opp/

export DDK_VERSION_FLAG=1.60.T49.0.B201
export NEW_GE_FE_ID=1
export GE_AICPU_FLAG=1
export SOC_VERSION=Ascend910
#export DUMP_GE_GRAPH=2
#export DUMP_GRAPH_LEVEL=3
#export PRINT_MODEL=1
export SLOG_PRINT_TO_STDOUT=0

# dump op data
#export DISABLE_REUSE_MEMORY=1
#export DUMP_OP=1

ulimit -c unlimited

# local variable
RANK_SIZE=$1
RANK_TABLE_FILE=./hccl_config/${RANK_SIZE}p.json
RANK_ID_START=0
SAVE_PATH=training/t1

# training stage
MODE=$2

for((RANK_ID=$RANK_ID_START;RANK_ID<$((RANK_SIZE+RANK_ID_START));RANK_ID++));
do
echo
su HwHiAiUser -c "adc --host 0.0.0.0:22118 --log \"SetLogLevel(0)[error]\" --device "$RANK_ID
TMP_PATH=$SAVE_PATH/D$RANK_ID
mkdir -p $TMP_PATH
cp run_yolov3.sh $TMP_PATH/
cp $RANK_TABLE_FILE $TMP_PATH/rank_table.json
cd $TMP_PATH
nohup bash run_yolov3.sh $RANK_ID $RANK_SIZE $CODE_PATH $MODE > train_$RANK_ID.log &
cd -

done




