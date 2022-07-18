import loadgen as lg
from tqdm import tqdm


class QueryInfo:
    def __init__(self, query_id, index, valid=True):
        self.query_id = query_id
        self.index = index
        self.valid = valid

class BackendBase():
    def __init__(self, batchsize=1):
        self.batchsize = batchsize

    @property
    def version(self):
        raise NotImplementedError("Backend:version")

    @property
    def name(self):
        raise NotImplementedError("Backend:name")

    def load(self, model_path, inputs=None, outputs=None, args=None):
        raise NotImplementedError("Backend:load")

    def predict(self, feed):
        raise NotImplementedError("Backend:predict")

    def set_datasets(self, datasets):
        self.datasets = datasets

    def run_predict(self, batchsamples):
        idx_list = [query_info.index for query_info in batchsamples]
        query_id_list = [query_info.query_id for query_info in batchsamples]
        samples_data = self.datasets.get_preprocessed_data(idx_list)
        outputs_array_list = self.predict(samples_data)
        response = [lg.QuerySampleResponse(q.query_id, q.index) for q in batchsamples]
        # 注意该函数必须要调用，否则测试会运行失败，需要告知loadgen已经处理好的样本的情况
        lg.NotifyQuerySamplesComplete(response)

        # reassembled_idx_list, reassembled_outputs_array_list = self.reassemble_ouputs(batchsamples, idx_list, outputs_array_list)
        self.datasets.save_predict_result(batchsamples, idx_list, outputs_array_list)

    # 推理处理函数api 当前函数内推入线程队列中处理 快速返回不影响后续分发
    def predict_proc_func(self, query_samples):
        for x in tqdm(range(0, len(query_samples), self.batchsize),desc='Inference Processing'):
            batchsamples = query_samples[x: self.batchsize+x]
            batchsamples = [QueryInfo(q.id, q.index) for q in query_samples[x: self.batchsize+x]]

            if len(batchsamples) < self.batchsize:
                batchsamples = batchsamples + \
                    [QueryInfo(0, 0, False) for y in range(self.batchsize-len(batchsamples))]
            self.run_predict(batchsamples)
        return 0

    def sumary(self):
        print("backend sumary null impl")

def create_backend_instance(backend_type, args):
    if backend_type == "tensorflow":
        from backend_tf import BackendTensorflow
        backend = BackendTensorflow(model_path, batchsize, inputs=None, outputs=None)
        backend.load(model_path, inputs=args.inputs, outputs=args.outputs)
    elif backend_type == "onnxruntime":
        from backend.onnx_backend import BackendOnnxruntime
        backend = BackendOnnxruntime(args.batchsize)
    elif backend_type == "null":
        from backend_null import BackendNull
        backend = BackendNull()
    elif backend_type == "acl":
        from backend.acl_backend import BackendAcl
        backend = BackendAcl(args.batchsize)
        backend.load(args.model, inputs=args.inputs, outputs=args.outputs, device_id=args.device_id, args=args)
    else:
        raise ValueError("unknown backend: ", backend_type)
    return backend
