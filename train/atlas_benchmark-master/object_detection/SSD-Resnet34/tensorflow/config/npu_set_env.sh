#!/bin/bash

rm -rf /var/log/npu/slog/host-0/*
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

export DDK_VERSION_FLAG=1.60.T17.B830
export HCCL_CONNECT_TIMEOUT=600
export JOB_ID=9999001

export NEW_GE_FE_ID=1
export GE_AICPU_FLAG=1
export SOC_VERSION=Ascend910
export DUMP_GE_GRAPH=1
export DUMP_GRAPH_LEVEL=3
export PRINT_MODEL=1
export SLOG_PRINT_TO_STDOUT=1


export PROFILING_MODE=false
export PROFILING_OPTIONS=training_trace
export FP_POINT=ssd/block7-conv1x1/Relu
export BP_POINT=gradients/resnet34/Relu_grad/ReluGrad
export AICPU_PROFILING_MODE=false