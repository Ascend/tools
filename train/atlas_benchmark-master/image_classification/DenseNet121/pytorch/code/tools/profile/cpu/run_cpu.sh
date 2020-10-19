export LD_LIBRARY_PATH=/usr/local/lib/:/usr/lib/:/usr/local/Ascend/fwkacllib/lib64/:/usr/local/Ascend/driver/lib64/common/:/usr/local/Ascend/driver/lib64/driver/:/usr/local/Ascend/add-ons/:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
export PATH=$PATH:/usr/local/Ascend/fwkacllib/ccec_compiler/bin
export ASCEND_OPP_PATH=/usr/local/Ascend/opp
export NEW_GE_FE_ID=1
export GE_AICPU_FLAG=1
export PYTHONPATH=/usr/local/Ascend/atc/python/site-packages/te.egg:/usr/local/Ascend/atc/python/site-packages/topi.egg:/usr/local/Ascend/atc/python/site-packages/auto_tune.egg:/usr/local/Ascend/atc/python/site-packages/schedule_search.egg:/usr/local
export CUSTOM_OP_LIB_PATH=/usr/local/Ascend/ops/framework/built-in/tensorflow
export OPTION_EXEC_EXTERN_PLUGIN_PATH=/usr/local/Ascend/fwkacllib/lib64/plugin/opskernel/libfe.so:/usr/local/Ascend/fwkacllib/lib64/plugin/opskernel/libaicpu_plugin.so:/usr/local/Ascend/fwkacllib/lib64/plugin/opskernel/libge_local_engine.so
export PLUGIN_LOAD_PATH=/usr/local/Ascend/fwkacllib/lib64/plugin/opskernel/libfe.so:/usr/local/Ascend/fwkacllib/lib64/plugin/opskernel/libaicpu_plugin.so:/usr/local/Ascend/fwkacllib/lib64/plugin/opskernel/libge_local_engine.so:/usr/local/Ascend/fwkacllib/lib64/plugin/opskernel/librts_engine.so

#export DEVICE_ID=0
#export SLOG_PRINT_TO_STDOUT=1

#su HwHiAiUser -c "adc --host 0.0.0.0:22118 --log \"SetLogLevel(0)[error]\" --device 0"

#python3 pytorch-benchmark-resnet50.py
python3 net_show_cpu.py
#python3 pytorch-resnet50-profiling.py


