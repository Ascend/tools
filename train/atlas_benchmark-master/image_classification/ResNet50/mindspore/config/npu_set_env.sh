#!/bin/bash

rm -rf /var/log/npu/slog/host-0/*
if [ -d /usr/local/Ascend/nnae/latest ];then

	export LD_LIBRARY_PATH=/usr/local/:/usr/local/lib/:/usr/lib/:/usr/local/Ascend/nnae/latest/fwkacllib/lib64:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/:/usr/local/Ascend/driver/tools/hccn_tool/:/usr/local/mpirun4.0/lib
	export PYTHONPATH=$PYTHONPATH:/usr/local/Ascend/tfplugin/latest/tfplugin/python/site-packages:/usr/local/Ascend/nnae/latest/opp/op_impl/built-in/ai_core/tbe:/usr/local/Ascend/nnae/latest/fwkacllib/python/site-packages/:/usr/local/Ascend/tfplugin/latest/tfplugin/python/site-packages
	export PATH=$PATH:/usr/local/Ascend/nnae/latest/fwkacllib/ccec_compiler/bin:/usr/local/mpirun4.0/bin
	export ASCEND_OPP_PATH=/usr/local/Ascend/nnae/latest/opp
        export TBE_IMPL_PATH=/usr/local/Ascend/nnae/latest/opp/op_impl/built-in/ai_core
else
	export LD_LIBRARY_PATH=/usr/local/lib/:/usr/lib/:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/lib64:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/:/usr/local/mpirun4.0/lib
	export PYTHONPATH=$PYTHONPATH:/usr/local/Ascend/tfplugin/latest/tfplugin/python/site-packages:/usr/local/Ascend/ascend-toolkit/latest/opp/op_impl/built-in/ai_core/tbe:/usr/local/Ascend/ascend-toolkit/latest//fwkacllib/python/site-packages/:/usr/local/Ascend/ascend-toolkit/latest/tfplugin/python/site-packages:$projectDir
	export PATH=$PATH:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/ccec_compiler/bin:/usr/local/mpirun4.0/bin
	export ASCEND_OPP_PATH=/usr/local/Ascend/ascend-toolkit/latest/opp/
	export TBE_IMPL_PATH=TBE_IMPL_PATH=/usr/local/Ascend/ascend-toolkit/latest/opp/op_impl/built-in/ai_core
fi

