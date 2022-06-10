#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves tf common function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2022
"""
import os
import numpy as np
import tensorflow as tf
import subprocess
from common import utils
from common.utils import AccuracyCompareException

DTYPE_MAP = {
    tf.float32: np.float32,
    tf.float64: np.float64,
    tf.int64: np.int64,
    tf.int32: np.int32,
    tf.int16: np.int16,
    tf.int8: np.int8,
    tf.uint8: np.uint8,
    tf.bool: np.bool_,
    tf.complex64: np.complex64
}

TF_DEBUG_TIMEOUT = 3600
VERSION_TF2X = "2."
VERSION_TF1X = "1."


def check_tf_version(version):
    tf_version = tf.__version__
    if tf_version.startswith(version):
        return True


def execute_command(cmd: str):
    """ Execute shell command
    :param cmd: command
    :return: status code
    """
    if cmd is None:
        utils.print_error_log("Command is None.")
        return -1
    utils.print_info_log("[Run CMD]: %s" % cmd)
    complete_process = subprocess.run(cmd, shell=True)
    return complete_process.returncode


def convert_to_numpy_type(tensor_type):
    """
    Function Description:
        convert to numpy type
    Parameter:
        tensor_type:the tensor type
    Return Value:
        numpy type
    Exception Description:
        When tensor type not in DTYPE_MAP throw exception
    """
    np_type = DTYPE_MAP.get(tensor_type)
    if np_type is not None:
        return np_type
    utils.print_error_log("unsupported tensor type: {},".format(tensor_type))
    raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_TENSOR_TYPE_ERROR)


def convert_tensor_shape(tensor_shape):
    """
    Function Description:
        convert tensor shape
    Parameter:
        tensor_shape:the tensor shape
    Return Value:
        shape tuple
    Exception Description:
        When tensor dim is none throw exception
    """
    tensor_shape_list = tensor_shape.as_list()
    for i in range(len(tensor_shape_list)):
        if tensor_shape_list[i] is None:
            utils.print_error_log("The dynamic shape %s are not supported. "
                                  "Please set '-s' or '--input-shape' to fix the dynamic shape." % tensor_shape)
            raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_NOT_SUPPORT_ERROR)
    return tuple(tensor_shape_list)


def verify_and_adapt_dynamic_shape(input_shapes, op_name, tensor):
    """
    verify and adapt dynamic shape
    """
    try:
        model_shape = list(tensor.shape)
    except ValueError:
        tensor.set_shape(input_shapes.get(op_name))
        return tensor
    if op_name in input_shapes:
        fixed_tensor_shape = input_shapes.get(op_name)
        message = "The fixed input tensor dim not equal to model input dim." \
                  "tensor_name:%s, %s vs %s" % (op_name, str(fixed_tensor_shape), str(model_shape))
        if len(fixed_tensor_shape) != len(model_shape):
            utils.print_error_log(message)
            raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)
        for index, dim in enumerate(model_shape):
            fixed_tensor_dim = int(fixed_tensor_shape[index])
            if dim is not None and fixed_tensor_dim != dim:
                utils.print_error_log(message)
                raise utils.AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)
            model_shape[index] = fixed_tensor_dim
        utils.print_info_log("Fix dynamic input shape of %s to %s" % (op_name, model_shape))
    tensor.set_shape(model_shape)
    return tensor


def get_inputs_tensor(global_graph, input_shape_str):
    """
    get input tensor
    """
    input_shapes = utils.parse_input_shape(input_shape_str)
    inputs_tensor = []
    tensor_index = {}
    operations = global_graph.get_operations()
    op_names = [op.name for op in operations if "Placeholder" == op.type]
    print(op_names)
    for _, tensor_name in enumerate(input_shapes):
        utils.check_input_name_in_model(op_names, tensor_name)
    for op in operations:
        # the operator with the 'Placeholder' type is the input operator of the model
        if "Placeholder" == op.type:
            op_name = op.name
            if op_name in tensor_index:
                tensor_index[op_name] += 1
            else:
                tensor_index[op_name] = 0
            tensor = global_graph.get_tensor_by_name(op.name + ":" + str(tensor_index[op_name]))
            tensor = verify_and_adapt_dynamic_shape(input_shapes, op.name, tensor)
            inputs_tensor.append(tensor)
    utils.print_info_log("model inputs tensor:\n{}\n".format(inputs_tensor))
    return inputs_tensor


def get_inputs_data(inputs_tensor, input_paths):
    inputs_map = {}
    input_path = input_paths.split(",")
    for index, tensor in enumerate(inputs_tensor):
        try:
            input_data = np.fromfile(input_path[index], convert_to_numpy_type(tensor.dtype))
            if tensor.shape:
                input_data = input_data.reshape(tensor.shape)
            inputs_map[tensor] = input_data
            utils.print_info_log("load file name: {}, shape: {}, dtype: {}".format(
                os.path.basename(input_path[index]), input_data.shape, input_data.dtype))
        except Exception as err:
            utils.print_error_log("Failed to load data %s. %s" % (input_path[index], err))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_BIN_FILE_ERROR)
    return inputs_map
