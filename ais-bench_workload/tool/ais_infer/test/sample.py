import sys
import numpy as np
import aclruntime

model_path = sys.argv[1]

# 最短运行样例
def infer_simple():
    device_id = 0
    options = aclruntime.session_options()
    session = aclruntime.InferenceSession(model_path, device_id, options)

    # create new numpy data according inputs info
    barray = bytearray(session.get_inputs()[0].realsize)
    ndata = np.frombuffer(barray)
    # convert numpy to pytensors in device
    tensor = aclruntime.Tensor(ndata)
    tensor.to_device(device_id)

    outnames = [ session.get_outputs()[0].name ]
    feeds = { session.get_inputs()[0].name : tensor}

    outputs = session.run(outnames, feeds)
    print("outputs:", outputs)

    for out in outputs:
        out.to_host()
    # sumary inference throughput
    print(session.sumary())

# 推理3个step阶段运行
def infer_step():
    device_id = 0
    options = aclruntime.session_options()
    options.log_level = 1
    session = aclruntime.InferenceSession(model_path, device_id, options)

    # create new numpy data according inputs info
    barray = bytearray(session.get_inputs()[0].realsize)
    ndata = np.frombuffer(barray)
    # convert numpy to pytensors in device
    tensor = aclruntime.Tensor(ndata)
    tensor.to_device(device_id)

    outnames = [ session.get_outputs()[0].name ]
    feeds = { session.get_inputs()[0].name : tensor}

    # infer three step function
    session.run_setinputs(feeds)
    session.run_execute()
    outputs = session.run_getoutputs(outnames)

    # outputs = session.run(outnames, feeds)
    print("step outputs:", outputs)

    for out in outputs:
        out.to_host()
    # sumary inference throughput
    print(session.sumary())

# 获取模型信息
def get_model_info():
    device_id = 0
    options = aclruntime.session_options()
    # 方法1设置级别为debug模式后可以打印模型信息
    options.log_level = 1
    session = aclruntime.InferenceSession(model_path, device_id, options)

    # 方法2 直接打印session 也可以获取模型信息
    print(session)

    # 方法3 也可以直接通过get接口去获取
    intensors_desc = session.get_outputs()
    for i, info in enumerate(intensors_desc):
        print("input info i:{} shape:{} type:{} val:{} realsize:{} size:{}".format(
            i, info.shape, info.datatype, int(info.datatype), info.realsize, info.size))

    intensors_desc = session.get_outputs()
    for i, info in enumerate(intensors_desc):
        print("outputs info i:{} shape:{} type:{} val:{} realsize:{} size:{}".format(
            i, info.shape, info.datatype, int(info.datatype), info.realsize, info.size))

def infer_dynamicshape():
    device_id = 0
    options = aclruntime.session_options()
    session = aclruntime.InferenceSession(model_path, device_id, options)

    # only need call this functon compare infer_simple
    session.set_dynamic_shape("actual_input_1:1,3,224,224")
    session.set_custom_outsize([10000])

    # create new numpy data according inputs info
    barray = bytearray(session.get_inputs()[0].realsize)
    ndata = np.frombuffer(barray)
    # convert numpy to pytensors in device
    tensor = aclruntime.Tensor(ndata)
    tensor.to_device(device_id)

    outnames = [ session.get_outputs()[0].name ]
    feeds = { session.get_inputs()[0].name : tensor}

    outputs = session.run(outnames, feeds)
    print("outputs:", outputs)

    for out in outputs:
        out.to_host()
    print(session.sumary())


# 传入acl文件 执行profiling或者dump
def acljson_run():
    device_id = 0
    options = aclruntime.session_options()
    options.acl_json_path = "./acl.json"
    session = aclruntime.InferenceSession(model_path, device_id, options)

# 并行运行样例
def infer_run_simultaneous():
    device_id = 0

    # one call
    options = aclruntime.session_options()
    session = aclruntime.InferenceSession(model_path, device_id, options)
    # create new numpy data according inputs info
    barray = bytearray(session.get_inputs()[0].realsize)
    ndata = np.frombuffer(barray)
    # convert numpy to pytensors in device
    tensor = aclruntime.Tensor(ndata)
    tensor.to_device(device_id)
    outnames = [ session.get_outputs()[0].name ]
    feeds = { session.get_inputs()[0].name : tensor}

    # another call
    options1 = aclruntime.session_options()
    model_path1 = sys.argv[2]
    session1 = aclruntime.InferenceSession(model_path1, device_id, options1)
    # create new numpy data according inputs info
    barray1 = bytearray(session1.get_inputs()[0].realsize)
    ndata1 = np.frombuffer(barray1)
    # convert numpy to pytensors in device
    tensor1 = aclruntime.Tensor(ndata1)
    tensor1.to_device(device_id)
    outnames1 = [ session1.get_outputs()[0].name ]
    feeds1 = { session1.get_inputs()[0].name : tensor1}

    # one run
    outputs = session.run(outnames, feeds)
    print("outputs:", outputs)

    for out in outputs:
        out.to_host()
    # sumary inference throughput
    print(session.sumary())

    # another run
    outputs1 = session1.run(outnames1, feeds1)
    print("outputs1:", outputs1)

    for out in outputs1:
        out.to_host()
    # sumary inference throughput
    print(session1.sumary())


infer_simple()
#infer_run_simultaneous()
#infer_step()
#infer_dynamicshape()
#get_model_info()
#acljson_run()
