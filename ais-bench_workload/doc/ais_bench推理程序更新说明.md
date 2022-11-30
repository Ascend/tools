# ais_bench推理程序更新说明



## ais-bench推理程序0.0.2版本更新说明

### 新增模块入口  python -m ais_bench

原有推理程序使用ais_infer.py作为入口，新版本增加ais_bench.whl包，安装该whl包后。可以通过python3 -m ais_bench 作为入口进行调用。ais_bench程序包按照请查考Readme.md

**ais_bench是基于AI标准的性能测试软件。本程序是使用ais_bench的推理功能。所以后续命名为ais_bench推理工具。**

**为了保持兼容，原有的ais_infer.py继续保留，可以直接使用。**

```bash
# 原方式
python3 ais_infer.py --model /home/model/resnet50_v1.om
```

```bash
# 新方式
python3 -m ais_bench --model /home/model/resnet50_v1.om
```



### profiling功能增强

原有程序使用acl接口进行profiling功能开启，但是没有解析功能。新程序进行完善，如果当前环境中可以找到msprof程序，使用msprof程序对推理程序进行拉起调用。这样可以不光可以采集，也可以解析profiling数据，使用更方便。

msprof命令在ascend-toolkit里。如果执行source  xxx/Ascend/ascend-toolkit/set_env.sh后。环境中就有msprof命令调用了。

auto_set_dymshape_mode



### 自动设置shape模式（动态shape模型）

针对动态shape模型。输入数据的shape可能是不固定的，比如一个输入文件shape为1,3,224,224 另一个输入文件shape为 1,3,300,300。如果两个文件要一起推理的话，需要设置两次动态shape参数，那正常的话是不支持的。针对该种场景，增加auto_set_dymshape_mode模式，根据输入文件的shape信息自动设置模型的shape参数，

```
python3 -m ais_bench --model ./resnet50_v1_bs1_fp32.om --acl_json_path ./acl.json
```



### 自动设置dims模式（动态dims模型）

针对动态dims模型，增加auto_set_dymdims_mode参数，根据输入文件的shape信息自动设置模型的shape参数。



### dymShape_range自动range测试模式（动态shape模型）

针对动态shape模型。设置shape区间参数dymShape_range。根据传入的shape区间，对每个shape进行性能测试并汇总

### 性能提升

优化推理流程，提高推理性能

精确统计H2D和D2H的拷贝统计耗时。

### 接口开放

开放推理python接口。

参考https://github.com/Ascend/tools/blob/be75cf413af2238147708c46b6745dd5eee68f09/ais-bench_workload/tool/ais_infer/test/interface_sample.py

可以通过如下几行命令就完成推理操作

```python
def infer_simple():
  device_id = 0
  session = InferSession(device_id, model_path)

  *# create new numpy data according inputs info*
  barray = bytearray(session.get_inputs()[0].realsize)
  ndata = np.frombuffer(barray)

  mode = "static"
  outputs = session.infer([ndata], mode)
  print("outputs:{} type:{}".format(outputs, type(outputs)))
    
  print("static infer avg:{} ms".format(np.mean(session.sumary().exec_time_list)))
```



```
def infer_dymshape():
  device_id = 0
  session = InferSession(device_id, model_path)
  ndata = np.zeros([1,3,224,224], dtype=np.float32)

  mode = "dymshape"
  outputs = session.infer([ndata], mode, custom_sizes=100000)
  print("outputs:{} type:{}".format(outputs, type(outputs)))
  print("dymshape infer avg:{} ms".format(np.mean(session.sumary().exec_time_list)))
```



### 接口变更与兼容：

**增加warmup_count   display_all_summary  dymShape_range   auto_set_dymdims_mode**

**去除infer_queue_count 参数。当前程序已不需要设置队列个数。**

**建议更新aclruntime和ais_bench版本。如果不更新aclruntime版本。执行保证兼容性。但会有warning提示。**

```
[WARNING] aclruntime version:0.0.1 is lower please update aclruntime follow any one method
[WARNING] 1. visit https://github.com/Ascend/tools/tree/master/ais-bench_workload/tool/ais_infer to install
[WARNING] 2. or run cmd: pip3  install -v --force-reinstall 'git+https://github.com/Ascend/tools.git#egg=aclruntime&subdirectory=ais-bench_workload/tool/ais_infer/backend' to install
```

