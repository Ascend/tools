
import time
import aclruntime
import numpy as np

class InferSession:
    def __init__(self, device_id: int, model_path: str, acl_json_path: str = None, debug: bool = False, loop: int = 1):
        """
        init InferSession

        Args:
            device_id: device id for npu device
            model_path: om model path to load
            acl_json_path: set acl_json_path to enable profiling or dump function
            debug: enable debug log.  Default: False
            loop: loop count for one inference. Default: 1
        """
        self.device_id = device_id
        self.model_path = model_path
        self.loop = loop
        options = aclruntime.session_options()
        if acl_json_path is not None:
            options.acl_json_path = acl_json_path
        options.log_level = 1 if debug == True else 2
        options.loop = self.loop
        self.session = aclruntime.InferenceSession(self.model_path, self.device_id, options)
        self.outputs_names = [meta.name for meta in self.session.get_outputs()]

    def get_inputs(self):
        """
        get inputs info of model
        """
        self.intensors_desc = self.session.get_inputs()
        return self.intensors_desc

    def get_outputs(self):
        """
        get outputs info of model
        """
        self.outtensors_desc = self.session.get_outputs()
        return self.outtensors_desc

    def set_loop_count(self, loop):
        options = self.session.options()
        options.loop = loop

    # 默认设置为静态batch
    def set_staticbatch(self):
        self.session.set_staticbatch()

    def set_dynamic_batchsize(self, dymBatch: str):
        self.session.set_dynamic_batchsize(dymBatch)

    def set_dynamic_hw(self, w: int, h: int):
        self.session.set_dynamic_hw(w, h)

    def set_dynamic_dims(self, dym_dims: str):
        self.session.set_dynamic_dims(dym_dims)

    def set_dynamic_shape(self, dym_shape: str):
        self.session.set_dynamic_shape(dym_shape)

    def set_custom_outsize(self, custom_sizes):
        self.session.set_custom_outsize(custom_sizes)

    def create_tensor_from_fileslist(self, desc, files):
        return self.session.create_tensor_from_fileslist(desc, files)

    def create_tensor_from_arrays_to_device(self, arrays):
        tensor = aclruntime.Tensor(arrays)
        tensor.to_device(self.device_id)
        return tensor

    def convert_tensors_to_host(self, tensors):
        for tensor in tensors:
            tensor.to_host()

    def convert_tensors_to_arrays(self, tensors):
        arrays = []
        for tensor in tensors:
            # convert acltensor to numpy array
            arrays.append(np.array(tensor))
        return arrays

    def run(self, feeds, out_array=False):
        if len(feeds) > 0 and isinstance(feeds[0], np.ndarray):
            # if feeds is ndarray list, convert to baseTensor
            inputs = []
            for array in feeds:
                basetensor = aclruntime.BaseTensor(array.__array_interface__['data'][0], array.nbytes)
                inputs.append(basetensor)
        else:
            inputs = feeds
        outputs = self.session.run(self.outputs_names, inputs)
        if out_array == True:
            # convert to host tensor
            self.convert_tensors_to_host(outputs)
            # convert tensor to narray
            return self.convert_tensors_to_arrays(outputs)
        else:
            return outputs

    def reset_sumaryinfo(self):
        self.session.reset_sumaryinfo()

    def sumary(self):
        return self.session.sumary()
    def finalize(self):
        if hasattr(self.session, 'finalize'):
            self.session.finalize()

    def infer(self, feeds, mode = 'static', custom_sizes = 100000):
        '''
        Parameters:
            feeds: input data
            mode: static dymdims dymshapes
        '''
        inputs = []
        shapes = []
        torchTensorlist = ['torch.FloatTensor', 'torch.DoubleTensor', 'torch.HalfTensor',
            'torch.BFloat16Tensor', 'torch.ByteTensor', 'torch.CharTensor', 'torch.ShortTensor',
            'torch.LongTensor', 'torch.BoolTensor', 'torch.IntTensor' ]
        npTypelist = [np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.float16, np.float32, np.float64]
        for feed in feeds:
            if type(feed) is np.ndarray:
                input = feed
                shapes.append(input.shape)
            elif type(feed) in npTypelist:
                input = np.array(feed)
                shapes.append([feed.size])
            elif type(feed) is aclruntime.Tensor:
                input = feed
                shapes.append(input.shape)
            elif hasattr(feed, 'type') and feed.type() in torchTensorlist:
                input = feed.numpy()
                if not feed.is_contiguous():
                    input = np.ascontiguousarray(input)
                shapes.append(input.shape)
            else:
                raise RuntimeError('type:{} invalid'.format(type(feed)))
            inputs.append(input)

        if mode == 'dymshape' or mode == 'dymdims':
            l = []
            indesc = self.get_inputs()
            outdesc = self.get_outputs()
            for i, shape in enumerate(shapes):
                str_shape = [ str(val) for val in shape ]
                dyshape = "{}:{}".format(indesc[i].name, ",".join(str_shape))
                l.append(dyshape)
            dyshapes = ';'.join(l)
            if mode == 'dymshape':
                self.session.set_dynamic_shape(dyshapes)
                if isinstance(custom_sizes, int):
                    custom_sizes = [custom_sizes]*len(outdesc)
                elif isinstance(custom_sizes, list) == False:
                    raise RuntimeError('custom_sizes:{} type:{} invalid'.format(
                        custom_sizes, type(custom_sizes)))
                self.session.set_custom_outsize(custom_sizes)
            elif mode == 'dymdims':
                self.session.set_dynamic_dims(dyshapes)
        return self.run(inputs, out_array=True)

class MemorySummary:
    @staticmethod
    def get_H2D_time_list():
        if hasattr(aclruntime, 'MemorySummary'):
            return aclruntime.MemorySummary().H2D_time_list
        else:
            return []
    @staticmethod
    def get_D2H_time_list():
        if hasattr(aclruntime, 'MemorySummary'):
            return aclruntime.MemorySummary().D2H_time_list
        else:
            return []
    @staticmethod
    def reset():
        if hasattr(aclruntime, 'MemorySummary'):
            aclruntime.MemorySummary().reset()
