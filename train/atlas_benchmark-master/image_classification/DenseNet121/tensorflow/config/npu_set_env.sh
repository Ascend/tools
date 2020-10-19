#!/bin/bash

rm -rf /var/log/npu/slog/host-0/*
#安装toolkit
#export LD_LIBRARY_PATH=/usr/local/lib/:/usr/lib/:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/lib64:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/
#export PYTHONPATH=$PYTHONPATH:/usr/local/Ascend/ascend-toolkit/latest/opp/op_impl/built-in/ai_core/tbe:/usr/local/Ascend/ascend-toolkit/latest//fwkacllib/python/site-packages/te:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/python/site-packages/topi:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/python/site-packages/hccl:/usr/local/Ascend/ascend-toolkit/latest/tfplugin/python/site-packages
#export PATH=$PATH:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/ccec_compiler/bin
#export ASCEND_OPP_PATH=/usr/local/Ascend/ascend-toolkit/latest/opp/

#安装nnae等
#export LD_LIBRARY_PATH=/usr/local/:/usr/local/lib/:/usr/lib/:/usr/local/Ascend/nnae/latest/x86_64-linux_gcc7.3.0/fwkacllib/lib64/:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/
#export PYTHONPATH=/home/train/resnet50_tf/code:/usr/local/Ascend/nnae/latest/x86_64-linux_gcc7.3.0/opp/op_impl/built-in/ai_core/tbe/:/usr/local/Ascend/nnae/latest/x86_64-linux_gcc7.3.0/fwkacllib/python/site-packages/te/:/usr/local/Ascend/nnae/latest/x86_64-linux_gcc7.3.0/fwkacllib/python/site-packages/topi/:/usr/local/Ascend/nnae/latest/x86_64-linux_gcc7.3.0/fwkacllib/python/site-packages/hccl/:/usr/local/Ascend/tfplugin/latest/x86_64-linux_gcc7.3.0/tfplugin/python/site-packages/:/usr/local/Ascend/tfplugin/latest/x86_64-linux_gcc7.3.0/tfplugin/python/site-packages/npu_bridge:/code
#export PATH=$PATH:/usr/local/Ascend/nnae/latest/x86_64-linux_gcc7.3.0/fwkacllib/ccec_compiler/bin/
#export ASCEND_OPP_PATH=/usr/local/Ascend/nnae/latest/x86_64-linux_gcc7.3.0/opp/


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

export SLOG_PRINT_TO_STDOUT=0

