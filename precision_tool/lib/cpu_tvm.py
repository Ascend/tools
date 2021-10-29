import numpy as np
from tbe import tvm


class CpuTvm():
    def __init__(self, json_file, dump_input_files, dump_output_files):
        self.json_file = json_file
        self.dump_input_files = dump_input_files
        self.dump_output_files = dump_output_files
        self.input_list = []
        self.output_list = []

    def _load_schedule(self):
        with open(self.json_file, 'r') as jsonfile:
            tvm_node = tvm.load_json(jsonfile.read())
            self.output_list = tvm_node.op.attrs['output_list']
            self.input_list = tvm_node.op.attrs['input_list']
        schedule = tvm.create_schedule([res.op for res in self.output_list])
        return schedule

    def _build_tvm(self, schedule):
        tensor_list = [ele for ele in self.input_list if ele is not None]
        for ele in self.output_list:
            if ele is not None:
                tensor_list.append(ele)
        fusion_op = tvm.build(schedule, tensor_list, "c", "llvm")
        return fusion_op

    def _load_data(self, dump_files):
        ctx = tvm.cpu(0)
        data_tvm = []
        for dump_file in dump_files:
            data_temp_numpy = np.load(dump_file)
            data_temp_tvm = tvm.nd.array(data_temp_numpy, ctx)
            data_tvm.append(data_temp_tvm)
        return data_tvm

    def run_cpu_tvm(self):
        # load schedule and build tvm
        schedule = self._load_schedule()
        fusion_op = self._build_tvm(schedule)

        #load data and run cpu tvm
        data_tvm_in = self._load_data(self.dump_input_files)
        data_tvm_out = self._load_data(self.dump_output_files)
        data_tvm_in.extend(data_tvm_out)
        fusion_op(*data_tvm_in)

        #tvm format to numpy format
        data_np_out = [data.asnumpy() for data in data_tvm_out]
        return data_np_out
