#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class is used to generate GUP dump data of the ONNX model.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2021
"""

import onnx
import onnxruntime
import numpy as np
import time
import os

from common.dump_data import DumpData
from skl2onnx.helpers.onnx_helper import enumerate_model_node_outputs
from skl2onnx.helpers.onnx_helper import select_model_inputs_outputs
from skl2onnx.helpers.onnx_helper import save_onnx_model
from common import utils
from common.utils import AccuracyCompareException

NODE_TYPE_TO_DTYPE_MAP = {
    "tensor(int)": np.int32,
    "tensor(int8)": np.int8,
    "tensor(int16)": np.int16,
    "tensor(int32)": np.int32,
    "tensor(int64)": np.int64,
    "tensor(uint8)": np.uint8,
    "tensor(uint16)": np.uint16,
    "tensor(uint32)": np.uint32,
    "tensor(uint64)": np.uint64,
    "tensor(float)": np.float32,
    "tensor(float16)": np.float16,
    "tensor(double)": np.double,
    "tensor(bool)": np.bool_,
    "tensor(complex64)": np.complex64,
    "tensor(complex128)": np.complex_
}


class OnnxDumpData(DumpData):
    """
    This class is used to generate GUP dump data of the ONNX model.
    """

    def __init__(self, arguments):
        self.args = arguments

    def _create_dir(self):
        # create input directory
        data_dir = os.path.join(self.args.out_path, "input")
        utils.create_directory(data_dir)

        # create dump_data/onnx directory
        onnx_dump_data_dir = os.path.join(self.args.out_path, "dump_data/onnx")
        utils.create_directory(onnx_dump_data_dir)

        # create model directory
        model_dir = os.path.join(self.args.out_path, "model")
        utils.create_directory(model_dir)

        return data_dir, onnx_dump_data_dir, model_dir

    def _modify_model_add_outputs_nodes(self, model_dir):
        old_onnx_model = onnx.load(self.args.model_path)
        utils.print_info_log("load model success")
        for index, node in enumerate(old_onnx_model.graph.node):
            if not node.name:
                node.name = node.op_type + "_" + str(index)
        outputs_name = [name for name in enumerate_model_node_outputs(old_onnx_model)]
        new_onnx_model = select_model_inputs_outputs(old_onnx_model, outputs_name)
        new_onnx_model_path = os.path.join(model_dir, "new_" + os.path.basename(self.args.model_path))
        save_onnx_model(new_onnx_model, new_onnx_model_path)
        utils.print_info_log("modify model outputs success")

        return old_onnx_model, new_onnx_model_path

    def _get_inputs_tensor_info(self, session):
        inputs_tensor_info = []
        # 'session' is a class of 'onnxruntime.InferenceSession'
        # 'input' is a class of 'onnxruntime.NodeArg'
        for input_item in session.get_inputs():
            tensor_info = {"name": input_item.name, "shape": tuple(input_item.shape), "type": input_item.type}
            inputs_tensor_info.append(tensor_info)
        utils.print_info_log("model inputs tensor info:\n{}\n".format(inputs_tensor_info))

        return inputs_tensor_info

    def _get_inputs_data(self, data_dir, inputs_tensor_info):
        inputs_map = {}
        if "" == self.args.input_path:
            for i, tensor_info in enumerate(inputs_tensor_info):
                utils.check_dynamic_shape(tensor_info["shape"])
                input_data = np.random.random(tensor_info["shape"]).astype(
                    self._convert_to_numpy_type(tensor_info["type"]))
                inputs_map[tensor_info["name"]] = input_data
                file_name = "input_" + str(i) + ".bin"
                input_data.tofile(os.path.join(data_dir, file_name))
                utils.print_info_log("save input file name: {}, shape: {}, dtype: {}".format(
                    file_name, input_data.shape, input_data.dtype))
        else:
            input_path = self.args.input_path.split(",")
            if len(inputs_tensor_info) != len(input_path):
                utils.print_error_log("the number of model inputs tensor_info is not equal the number of "
                                      "inputs data, inputs tensor_info is: {}, inputs data is: {}".format(
                    len(inputs_tensor_info), len(input_path)))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)
            for i, tensor_info in enumerate(inputs_tensor_info):
                utils.check_dynamic_shape(tensor_info["shape"])
                input_data = np.fromfile(input_path[i], self._convert_to_numpy_type(tensor_info["type"])).reshape(
                    tensor_info["shape"])
                inputs_map[tensor_info["name"]] = input_data
                utils.print_info_log("load input file name: {}, shape: {}, dtype: {}".format(
                    os.path.basename(input_path[i]), input_data.shape, input_data.dtype))
        return inputs_map

    def _convert_to_numpy_type(self, tensor_type):
        numpy_data_type = NODE_TYPE_TO_DTYPE_MAP.get(tensor_type)
        if numpy_data_type:
            return numpy_data_type
        else:
            utils.print_error_log(
                "unsupported tensor type: {}".format(tensor_type))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_TENSOR_TYPE_ERROR)

    def _load_session(self, new_onnx_model_path):
        return onnxruntime.InferenceSession(new_onnx_model_path)

    def _run_model(self, session, inputs_map):
        outputs_name = [node.name for node in session.get_outputs()]
        return session.run(outputs_name, inputs_map)

    def _save_dump_data(self, dump_bins, onnx_dump_data_dir, old_onnx_model):
        res_idx = 0
        for node in old_onnx_model.graph.node:
            for j, output in enumerate(node.output):
                file_name = node.name.replace('/', '_') + "." + str(j) + "." \
                            + str(round(time.time() * 1000000)) + ".npy"
                np.save(os.path.join(onnx_dump_data_dir, file_name), dump_bins[res_idx])
                res_idx += 1
        utils.print_info_log("dump data success")

    def generate_dump_data(self):
        """
        Function description:
            generate onnx model dump data
        Parameter:
            none
        Return Value:
            onnx model dump data directory
        Exception Description:
            none
        """
        data_dir, onnx_dump_data_dir, model_dir = self._create_dir()
        old_onnx_model, new_onnx_model_path = self._modify_model_add_outputs_nodes(model_dir)
        session = self._load_session(new_onnx_model_path)
        inputs_tensor_info = self._get_inputs_tensor_info(session)
        inputs_map = self._get_inputs_data(data_dir, inputs_tensor_info)
        dump_bins = self._run_model(session, inputs_map)
        self._save_dump_data(dump_bins, onnx_dump_data_dir, old_onnx_model)
        return onnx_dump_data_dir
