# main env
if [ -d /usr/local/Ascend/nnae/latest ];then

	export LD_LIBRARY_PATH=/usr/local/:/usr/local/lib/:/usr/lib/:/usr/local/Ascend/nnae/latest/fwkacllib/lib64:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/:/usr/local/Ascend/driver/tools/hccn_tool/:/usr/local/mpirun4.0/lib
	export PYTHONPATH=$PYTHONPATH:/usr/local/Ascend/tfplugin/latest/tfplugin/python/site-packages:/usr/local/Ascend/nnae/latest/opp/op_impl/built-in/ai_core/tbe:/usr/local/Ascend/nnae/latest/fwkacllib/python/site-packages/:/usr/local/Ascend/tfplugin/latest/tfplugin/python/site-packages
	export PATH=$PATH:/usr/local/Ascend/nnae/latest/fwkacllib/ccec_compiler/bin:/usr/local/mpirun4.0/bin
	export ASCEND_OPP_PATH=/usr/local/Ascend/nnae/latest/opp
else
	export LD_LIBRARY_PATH=/usr/local/lib/:/usr/lib/:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/lib64:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/:/usr/local/mpirun4.0/lib
	export PYTHONPATH=$PYTHONPATH:/usr/local/Ascend/tfplugin/latest/tfplugin/python/site-packages:/usr/local/Ascend/ascend-toolkit/latest/opp/op_impl/built-in/ai_core/tbe:/usr/local/Ascend/ascend-toolkit/latest//fwkacllib/python/site-packages/:/usr/local/Ascend/ascend-toolkit/latest/tfplugin/python/site-packages:$projectDir
	export PATH=$PATH:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/ccec_compiler/bin:/usr/local/mpirun4.0/bin
	export ASCEND_OPP_PATH=/usr/local/Ascend/ascend-toolkit/latest/opp/
	
fi
export SOC_VERSION=Ascend910
export HCCL_CONNECT_TIMEOUT=600

# user env
export JOB_ID={JOB_ID}
export RANK_TABLE_FILE={RANK_TABLE_FILE}
#export RANK_SIZE={RANK_SIZE}
#export RANK_INDEX={RANK_INDEX}
#export RANK_ID={RANK_ID}

# profiling env

export PROFILING_MODE=false
export PROFILING_OPTIONS=training_trace
export FP_POINT=resnet34/conv2d/Conv2Dresnet34/batch_normalization/FusedBatchNormV3_Reduce
export BP_POINT=Momentum/update_resnet34/conv2d/kernel/ApplyMomentum
export AICPU_PROFILING_MODE=false

# debug env
#export DUMP_GE_GRAPH=2
#export DUMP_OP=1
#export DUMP_OP_LESS=1
#export PRINT_MODEL=1
#export TE_PARALLEL_COMPILER=0

# system env
ulimit -c unlimited
