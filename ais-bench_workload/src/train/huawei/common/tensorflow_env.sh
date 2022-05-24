#!/bin/bash

# Please change to the actual installation path
export install_path=/usr/local/Ascend

# driver
export LD_LIBRARY_PATH=${install_path}/driver/lib64/common/:${install_path}/driver/lib64/driver/:$LD_LIBRARY_PATH

if [ -d /usr/local/Ascend/nnae/latest ];then
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/Ascend/nnae/latest/fwkacllib/lib64:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/:/usr/local/Ascend/driver/tools/hccn_tool/:/usr/local/mpirun4.0/lib
    export PYTHONPATH=$PYTHONPATH:/usr/local/Ascend/tfplugin/latest/tfplugin/python/site-packages:/usr/local/Ascend/nnae/latest/opp/op_impl/built-in/ai_core/tbe:/usr/local/Ascend/nnae/latest/fwkacllib/python/site-packages/:/usr/local/Ascend/tfplugin/latest/tfplugin/python/site-packages
    export PATH=$PATH:/usr/local/Ascend/nnae/latest/fwkacllib/ccec_compiler/bin:/usr/local/mpirun4.0/bin
    export ASCEND_OPP_PATH=/usr/local/Ascend/nnae/latest/opp
    export TBE_IMPL_PATH=/usr/local/Ascend/nnae/latest/opp/op_impl/built-in/ai_core
else
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/lib64:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/:/usr/local/mpirun4.0/lib
    export PYTHONPATH=$PYTHONPATH:/usr/local/Ascend/tfplugin/latest/tfplugin/python/site-packages:/usr/local/Ascend/ascend-toolkit/latest/opp/op_impl/built-in/ai_core/tbe:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/python/site-packages/:/usr/local/Ascend/ascend-toolkit/latest/tfplugin/python/site-packages:$projectDir
    export PATH=$PATH:/usr/local/Ascend/ascend-toolkit/latest/fwkacllib/ccec_compiler/bin:/usr/local/mpirun4.0/bin
    export ASCEND_OPP_PATH=/usr/local/Ascend/ascend-toolkit/latest/opp/
    export TBE_IMPL_PATH=/usr/local/Ascend/ascend-toolkit/latest/opp/op_impl/built-in/ai_core
fi

# Ascend-dmi
export LD_LIBRARY_PATH=/usr/local/dcmi:${install_path}/toolbox/latest/Ascend-DMI/lib64:${LD_LIBRARY_PATH}
export PATH=${install_path}/toolbox/latest/Ascend-DMI/bin:${PATH}

export JOB_ID=123456789

export HCCL_CONNECT_TIMEOUT=600
export HCCL_WHITELIST_DISABLE=1

# log
export ASCEND_SLOG_PRINT_TO_STDOUT=0
export ASCEND_GLOBAL_LOG_LEVEL=3
/usr/local/Ascend/driver/tools/msnpureport -d 0 -g error
/usr/local/Ascend/driver/tools/msnpureport -d 4 -g error
export SLOG_PRINT_TO_STDOUT=0

#system env
ulimit -c unlimited
