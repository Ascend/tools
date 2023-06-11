#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class is used to generate GUP dump data of the ONNX model.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2021
"""
import sys

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

from common.utils import InputShapeError

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
MAX_PROTOBUF = 2000000000


class OnnxDumpData(DumpData):
    """
    This class is used to generate GUP dump data of the ONNX model.
    """

    def __init__(self, arguments):
        self.args = arguments
        self.input_shapes = utils.parse_input_shape(self.args.input_shape)
        self.net_output = {}

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
        bytes_model = new_onnx_model.SerializeToString()
        save_as_external_data_switch = sys.getsizeof(bytes_model) > MAX_PROTOBUF
        onnx.save_model(new_onnx_model,
                        new_onnx_model_path,
                        save_as_external_data=save_as_external_data_switch,
                        location=model_dir if save_as_external_data_switch else None)
        utils.print_info_log("modify model outputs success")

        return old_onnx_model, new_onnx_model_path

    def _get_inputs_tensor_info(self, session):
        inputs_tensor_info = []
        # 'session' is a class of 'onnxruntime.InferenceSession'
        # 'input' is a class of 'onnxruntime.NodeArg'
        input_tensor_names = [item.name for item in session.get_inputs()]
        for _, tensor_name in enumerate(self.input_shapes):
            utils.check_input_name_in_model(input_tensor_names, tensor_name)
        for input_item in session.get_inputs():
            tensor_name = input_item.name
            tensor_type = input_item.type
            tensor_shape = tuple(input_item.shape)
            if utils.check_dynamic_shape(tensor_shape):
                if not self.input_shapes:
                    utils.print_error_log(
                        "The dynamic shape {} are not supported. Please "
                        "set '-s' or '--input-shape' to fix the dynamic shape.".format(tensor_shape))
                    raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            if self.input_shapes and tensor_name in self.input_shapes:
                input_shape = self.input_shapes.get(tensor_name)
                try:
                    number_shape = [int(dim) for dim in input_shape]
                except (ValueError, TypeError):
                    utils.print_error_log(utils.get_shape_not_match_message(
                        InputShapeError.FORMAT_NOT_MATCH, self.args.input_shape))
                    raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
                self._check_input_shape_fix_value(tensor_name, tensor_shape, number_shape)
                tensor_info = {"name": tensor_name, "shape": tuple(number_shape), "type": tensor_type}
                utils.print_info_log("Fix dynamic input shape of %s to %s" % (tensor_name, number_shape))
            else:
                tensor_info = {"name": tensor_name, "shape": tensor_shape, "type": tensor_type}
            inputs_tensor_info.append(tensor_info)
        utils.print_info_log("model inputs tensor info:\n{}\n".format(inputs_tensor_info))
        return inputs_tensor_info

    def _get_inputs_data(self, data_dir, inputs_tensor_info):
        inputs_map = {}
        if "" == self.args.input_path:
            for i, tensor_info in enumerate(inputs_tensor_info):
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

    def _save_dump_data(self, dump_bins, onnx_dump_data_dir, old_onnx_model, net_output_node):
        res_idx = 0
        for node in old_onnx_model.graph.node:
            for j, output in enumerate(node.output):
                file_name = node.name.replace('.', '_').replace('/', '_') + "." + str(j) + "." \
                            + str(round(time.time() * 1000000)) + ".npy"
                file_path = os.path.join(onnx_dump_data_dir, file_name)
                if output in net_output_node:
                    self.net_output[net_output_node.index(output)] = file_path
                np.save(file_path, dump_bins[res_idx])
                res_idx += 1
        for key, value in self.net_output.items():
            utils.print_info_log("net_output node is:{}, file path is {}".format(key, value))
        utils.print_info_log("dump data success")

    @staticmethod
    def _check_input_shape_fix_value(op_name, model_shape, input_shape):
        message = "fixed input tensor dim not equal to model input dim." \
                  "tensor_name:%s, %s vs %s" % (op_name, str(input_shape), str(model_shape))
        if len(model_shape) != len(input_shape):
            utils.print_error_log(message)
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)
        for index, value in enumerate(model_shape):
            if value is None or isinstance(value, str):
                continue
            if input_shape[index] != value:
                utils.print_error_log(message)
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)

    def _get_net_output_node(self):
        """
        get net output name
        """
        net_output_node = []
        session = self._load_session(self.args.model_path)
        for output_item in session.get_outputs():
            net_output_node.append(output_item.name)
        return net_output_node

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
        net_output_node = self._get_net_output_node()
        session = self._load_session(new_onnx_model_path)
        inputs_tensor_info = self._get_inputs_tensor_info(session)
        inputs_map = self._get_inputs_data(data_dir, inputs_tensor_info)
        dump_bins = self._run_model(session, inputs_map)
        self._save_dump_data(dump_bins, onnx_dump_data_dir, old_onnx_model, net_output_node)
        return onnx_dump_data_dir

    def get_net_output_info(self):
        """
        get_net_output_info
        """
        return self.net_output
