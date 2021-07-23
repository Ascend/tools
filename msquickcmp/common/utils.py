#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves common function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2021
"""
import os
import subprocess
import sys
import time
import numpy as np
import tensorflow as tf

ACCURACY_COMPARISON_INVALID_PARAM_ERROR = 1
ACCURACY_COMPARISON_INVALID_DATA_ERROR = 2
ACCURACY_COMPARISON_INVALID_PATH_ERROR = 3
ACCURACY_COMPARISON_INVALID_COMMAND_ERROR = 4
ACCURACY_COMPARISON_PYTHON_VERSION_ERROR = 5
ACCURACY_COMPARISON_MODEL_TYPE_ERROR = 6
ACCURACY_COMPARISON_PARSER_JSON_FILE_ERROR = 7
ACCURACY_COMPARISON_WRITE_JSON_FILE_ERROR = 8
ACCURACY_COMPARISON_OPEN_FILE_ERROR = 9
ACCURACY_COMPARISON_BIN_FILE_ERROR = 10
ACCURACY_COMPARISON_INVALID_KEY_ERROR = 11
ACCURACY_COMPARISON_PYTHON_COMMAND_ERROR = 12
ACCURACY_COMPARISON_TENSOR_TYPE_ERROR = 13
ACCURACY_COMPARISON_NO_DUMP_FILE_ERROR = 14
ACCURACY_COMPARISON_NOT_SUPPORT_ERROR = 15
MODEL_TYPE = ['.onnx', '.pb', '.om']

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


class AccuracyCompareException(Exception):
    """
    Class for Accuracy Compare Exception
    """

    def __init__(self, error_info):
        super(AccuracyCompareException, self).__init__()
        self.error_info = error_info


def _print_log(level, msg):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    pid = os.getgid()
    print(current_time + "(" + str(pid) + ")-[" + level + "]" + msg)
    sys.stdout.flush()


def print_info_log(info_msg):
    """
    Function Description:
        print info log.
    Parameter:
        info_msg: the info message.
    """
    _print_log("INFO", info_msg)


def print_error_log(error_msg):
    """
    Function Description:
        print error log.
    Parameter:
        error_msg: the error message.
    """
    _print_log("ERROR", error_msg)


def print_warn_log(warn_msg):
    """
    Function Description:
        print warn log.
    Parameter:
        warn_msg: the warn message.
    """
    _print_log("WARNING", warn_msg)


def check_file_or_directory_path(path, isdir=False):
    """
    Function Description:
        check whether the path is valid
    Parameter:
        path: the path to check
        isdir: the path is dir or file
    Exception Description:
        when invalid data throw exception
    """

    if isdir:
        if not os.path.isdir(path):
            print_error_log('The path {} is not a directory.Please check the path'.format(path))
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PATH_ERROR)
        if not os.access(path, os.W_OK):
            print_error_log(
                'The path{} does not have permission to write.Please check the path permission'.format(path))
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PATH_ERROR)
    else:
        if not os.path.isfile(path):
            print_error_log('The path {} is not a file.Please check the path'.format(path))
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PATH_ERROR)
        if not os.access(path, os.R_OK):
            print_error_log(
                'The path{} does not have permission to read.Please check the path permission'.format(path))
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PATH_ERROR)


def get_model_name_and_extension(offline_model_path):
    """
    Function Description:
        obtain the name and extension of the model file
    Parameter:
        offline_model_path: offline model path
    Return Value:
        model_name,extension
    Exception Description:
        when invalid data throw exception
    """
    file_name = os.path.basename(offline_model_path)
    model_name, extension = os.path.splitext(file_name)
    if extension not in MODEL_TYPE:
        print_error_log('Only model files whose names end with .pb or .onnx are supported.Please check {}'.format(
            offline_model_path))
        raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PATH_ERROR)
    return model_name, extension


def get_dump_data_path(dump_dir):
    """
    Function Description:
        traverse directories and obtain the absolute path of dump data
    Parameter:
        dump_dir: dump data directory
    Return Value:
        dump data path,file is exist or file is not exist
    """
    dump_data_path = None
    file_is_exist = False
    dump_data_dir = None
    for i in os.listdir(dump_dir):
        # Contains the dump file directory, whose name is a pure digital timestamp
        if i.isdigit():
            dump_data_dir = os.path.join(dump_dir, i)
            break

    if not dump_data_dir:
        print_error_log("The directory \"{}\" does not contain dump data".format(dump_dir))
        raise AccuracyCompareException(ACCURACY_COMPARISON_NO_DUMP_FILE_ERROR)

    for dir_path, sub_paths, files in os.walk(dump_data_dir):
        if len(files) != 0:
            dump_data_path = dir_path
            file_is_exist = True
            break
        dump_data_path = dir_path
    return dump_data_path, file_is_exist


def execute_command(cmd):
    """
    Function Description:
        run the following command
    Parameter:
        cmd: command
    Return Value:
        command output result
    Exception Description:
        when invalid command throw exception
    """
    print_info_log('Execute command:%s' % cmd)
    process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while process.poll() is None:
        line = process.stdout.readline()
        line = line.strip()
        if line:
            print(line)
    if process.returncode != 0:
        print_error_log('Failed to execute command:%s' % " ".join(cmd))
        raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_DATA_ERROR)


def create_directory(dir_path):
    """
    Function Description:
        creating a directory with specified permissions
    Parameter:
        dir_path: directory path
    Exception Description:
        when invalid data throw exception
    """
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, mode=0o700)
        except OSError as ex:
            print_error_log(
                'Failed to create {}.Please check the path permission or disk space .{}'.format(dir_path, str(ex)))
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PATH_ERROR)


def check_input_bin_file_path(input_path):
    """
    Function Description:
        check the output bin file
    Parameter:
        input_path: input path directory
    """
    input_bin_files = input_path.split(',')
    bin_file_path_array = []
    for input_item in input_bin_files:
        input_item_path = os.path.realpath(input_item)
        check_file_or_directory_path(input_item_path)
        bin_file_path_array.append(input_item_path)
    return bin_file_path_array


def check_dynamic_shape(shape):
    """
    Function Description:
        check dynamic shpae
    Parameter:
        shape:shape
    Return Value:
        False or True
    """
    for item in shape:
        if isinstance(item, str):
            print_error_log("dynamic shape {} are not supported".format(shape))
            raise AccuracyCompareException(ACCURACY_COMPARISON_NOT_SUPPORT_ERROR)


def convert_to_numpy_type(tensor_type):
    np_type = DTYPE_MAP.get(tensor_type)
    if np_type is not None:
        return np_type
    print_error_log("unsupported tensor type: {},".format(tensor_type))
    raise AccuracyCompareException(ACCURACY_COMPARISON_TENSOR_TYPE_ERROR)


def convert_tensor_shape(tensor_shape):
    tensor_shape_list = tensor_shape.as_list()
    for i in range(len(tensor_shape_list)):
        if tensor_shape_list[i] is None:
            print_error_log("The dynamic shape %s are not supported. "
                            "Please set '-s' or '--input-shape' to fix the dynamic shape." % tensor_shape)
            raise AccuracyCompareException(ACCURACY_COMPARISON_NOT_SUPPORT_ERROR)
    return tuple(tensor_shape_list)


def get_inputs_tensor(global_graph, input_shape_str):
    """
    get input tensor
    """
    input_shapes = parse_input_shape(input_shape_str)
    inputs_tensor = []
    tensor_index = {}
    operations = global_graph.get_operations()
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
    print_info_log("model inputs tensor:\n{}\n".format(inputs_tensor))
    return inputs_tensor


def verify_and_adapt_dynamic_shape(input_shapes, op_name, tensor):
    """
    verify and adapt dynamic shape
    """
    try:
        model_shape = list(tensor.shape)
    except ValueError:
        if op_name not in input_shapes:
            print_error_log("can not get model input tensor shape, and not set input shape in arguments.")
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_DATA_ERROR)
        tensor.set_shape(input_shapes[op_name])
        return tensor
    if op_name in input_shapes:
        fixed_tensor_shape = input_shapes[op_name]
        if len(fixed_tensor_shape) != len(model_shape):
            print_error_log("The fixed input tensor shape not equal to model input shape."
                            " tensor_name:%s, %s vs %s" % (op_name, str(fixed_tensor_shape),
                                                           str(model_shape)))
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_DATA_ERROR)
        for index, dim in enumerate(model_shape):
            fixed_tensor_dim = fixed_tensor_shape[index]
            if dim is not None and fixed_tensor_dim != dim:
                print_error_log("The fixed input tensor dim not equal to model input dim."
                                " tensor_name:%s, %s vs %s" % (op_name, str(fixed_tensor_shape),
                                                               str(model_shape)))
                raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_DATA_ERROR)
            model_shape[index] = fixed_tensor_dim
        print_info_log("Fix dynamic input shape of %s to %s" % (op_name, model_shape))
    tensor.set_shape(model_shape)
    return tensor


def parse_input_shape(input_shape_str):
    """self.args.input_shape should be format like: tensor_name1:dim1,dim2;tensor_name2:dim1,dim2"""
    input_shapes = {}
    if input_shape_str == '':
        return input_shapes
    tensor_list = input_shape_str.split(';')
    for tensor in tensor_list:
        tensor_shape_list = tensor.split(':')
        if len(tensor_shape_list) == 2:
            input_shapes[tensor_shape_list[0]] = tensor_shape_list[1].split(',')
    return input_shapes
