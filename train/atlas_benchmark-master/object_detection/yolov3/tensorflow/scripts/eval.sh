
# setting main path
MAIN_PATH=$(dirname $(readlink -f $0))
echo $MAIN_PATH

DEVICE_NUM=$1
ckpt_path=$2

#echo $1
#echo $2
# set env
export DDK_VERSION_FLAG=1.60.T49.0.B201
export NEW_GE_FE_ID=1
export GE_AICPU_FLAG=1
export SOC_VERSION=Ascend910

export JOB_ID=10087
export FUSION_TENSOR_SIZE=1000000000


export RANK_ID=yolo
#echo "device_num is  $DEVICE_NUM"
for((i=0;i<${DEVICE_NUM};i++));
do

export RANK_SIZE=$DEVICE_NUM
export DEVICE_ID=$i
export DEVICE_INDEX=$i

#su HwHiAiUser -c "adc --host 0.0.0.0:22118 --log \"SetLogLevel(0)[debug]\" --device "$RANK_ID
cd ${MAIN_PATH}/../result
if [ x"${ckpt_path}" == x"" ];then
    lastresult=$(ls -t | grep -E "Train*" | head -n 1)
    RESTORE_PATH=${lastresult}/${i}/training/
   
else
    lastresult=${ckpt_path}
    RESTORE_PATH=${ckpt_path}/${i}/training/
   
fi
echo $RESTORE_PATH
 python3.7 ${MAIN_PATH}/../code/eval.py \
--save_json True \
--score_thresh 0.0001 \
--nms_thresh 0.55 \
--max_boxes 100 \
--restore_path $RESTORE_PATH \
--max_test 10000 \
--save_json_path eval_res_D$DEVICE_NUM.json > ${lastresult}/eval_$i.out 2>&1

done


