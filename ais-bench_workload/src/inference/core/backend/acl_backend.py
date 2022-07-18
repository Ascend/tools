import time

import aclruntime
import ais_utils
import numpy as np
from backendbase import BackendBase


def get_zero_ndata(size):
    barray = bytearray(size)
    ndata = np.frombuffer(barray, dtype=np.int8)
    return ndata

# out api 创建空数据
def create_intensors_zerodata(intensors_desc, device_id):
    intensors = []
    for info in intensors_desc:
        ndata = get_zero_ndata(info.realsize)
        tensor = aclruntime.Tensor(ndata)
        tensor.to_device(device_id)
        intensors.append(tensor)
    return intensors

def warmup(session, intensors_desc, outtensors_desc, device_id):
    outputs_names = [desc.name for desc in outtensors_desc]
    n_loop = 5
    inputs = create_intensors_zerodata(intensors_desc, device_id)
    for i in range(n_loop):
        session.run(outputs_names, inputs)
    print("warm up {} times done".format(n_loop))

class BackendAcl(BackendBase):
    def __init__(self, batchsize):
        super(BackendAcl, self).__init__(batchsize)
        self.elapsedtime = 0
        self.infercount = 0
    @property
    def version(self):
        return "1.0"

    @property
    def name(self):
        return "BackendAcl"

    def load(self, model_path, inputs=None, outputs=None, device_id=0, args=None):
        self.device_id = device_id
        self.model_path = model_path
        options = aclruntime.session_options()
        #options.log_level = 1
        self.session = aclruntime.InferenceSession(model_path, device_id, options)

        self.set_options(args)

        if not inputs:
            self.inputs = [meta.name for meta in self.session.get_inputs()]
        else:
            self.inputs = inputs
        if not outputs:
            self.outputs = [meta.name for meta in self.session.get_outputs()]
        else:
            self.outputs = outputs
        warmup(self.session, self.session.get_inputs(), self.session.get_outputs(), device_id)

    def set_options(self, args):
        # 增加校验
        if args.dymBatch != 0:
            self.session.set_dynamic_batchsize(args.dymBatch)
        elif args.dymHW !=None:
            hwstr = args.dymHW.split(",")
            self.session.set_dynamic_hw((int)(hwstr[0]), (int)(hwstr[1]))
        elif args.dymDims !=None:
            self.session.set_dynamic_dims(args.dymDims)
        elif args.dymShape !=None:
            self.session.set_dynamic_shape(args.dymShape)
        else:
            self.session.set_staticbatch()

        # 设置custom out tensors size
        if args.outputSize != None:
            customsizes = [int(n) for n in args.outputSize.split(',')]
            self.session.set_custom_outsize(customsizes)

    def predict(self, inputs):
        intensors = []
        for array in inputs:
            cur_tensor = aclruntime.Tensor(array)
            cur_tensor.to_device(self.device_id)
            intensors.append(cur_tensor)
        # outtensors = self.session.run(self.outputs, intensors)
        self.session.run_setinputs(intensors)
        start = time.time()
        self.session.run_execute()
        end = time.time()
        outtensors = self.session.run_getoutputs(self.outputs)

        self.elapsedtime += (end - start)*1000
        self.infercount += self.batchsize

        outarrays = []
        for tensor in outtensors:
            tensor.to_host()
            array = np.array(tensor)
            outarrays.append(array)
        return outarrays

    def unload(self):
        return None

    def calc_lantency(self, elapsedtime, count):
        latency = 0 if count == 0 else elapsedtime/count
        return latency

    def sumary(self):
        infer_latency = self.calc_lantency(self.elapsedtime, self.infercount)
        print("acl sumary infer_latency:{} elapasedtime:{} infercount:{}".format(infer_latency, self.elapsedtime, self.infercount))
        #print("acl session sumary", self.session.sumary())
        ais_utils.set_result("inference", "infer_latency", infer_latency)
