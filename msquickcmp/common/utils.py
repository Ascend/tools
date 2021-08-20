#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves common function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2021
"""
import os
import re
import subprocess
import sys
import time
import enum
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
DIM_PATTERN = "^[^,][0-9,]*$"
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


class InputShapeError(enum.Enum):
    """
     Class for Input Shape Error
    """
    FORMAT_NOT_MATCH = 0
    VALUE_TYPE_NOT_MATCH = 1
    NAME_NOT_MATCH = 2


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
    dynamic_shape = False
    for item in shape:
        if item is None or isinstance(item, str):
            dynamic_shape = True
            break
    return dynamic_shape


def parse_input_shape(input_shape):
    """
    Function Description:
        parse input shape
    Parameter:
        input_shape:the input shape,this format like:tensor_name1:dim1,dim2;tensor_name2:dim1,dim2
    Return Value:
        the map type of input_shapes
    """
    input_shapes = {}
    if input_shape == '':
        return input_shapes
    _check_colon_exist(input_shape)
    tensor_list = input_shape.split(';')
    for tensor in tensor_list:
        _check_colon_exist(input_shape)
        tensor_shape_list = tensor.split(':')
        if len(tensor_shape_list) == 2:
            shape = tensor_shape_list[1]
            input_shapes[tensor_shape_list[0]] = shape.split(',')
            _check_shape_number(shape)
        else:
            print_error_log(get_shape_not_match_message(InputShapeError.FORMAT_NOT_MATCH, input_shape))
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
    return input_shapes


def _check_colon_exist(input_shape):
    if ":" not in input_shape:
        print_error_log(get_shape_not_match_message(InputShapeError.FORMAT_NOT_MATCH, input_shape))
        raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PARAM_ERROR)


def _check_shape_number(input_shape_value):
    dim_pattern = re.compile(DIM_PATTERN)
    match = dim_pattern.match(input_shape_value)
    if match is None:
        print_error_log(get_shape_not_match_message(InputShapeError.VALUE_TYPE_NOT_MATCH, input_shape_value))
        raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PARAM_ERROR)


def get_shape_not_match_message(shape_error_type, value):
    """
    Function Description:
        get shape not match message
    Parameter:
        input:the value
        shape_error_type: the shape error type
    Return Value:
        not match message
    """
    message = ""
    if shape_error_type == InputShapeError.FORMAT_NOT_MATCH:
        message = "Input shape \"{}\" format mismatch,the format like: " \
                  "input_name1:1,224,224,3;input_name2:3,300".format(value)
    if shape_error_type == InputShapeError.VALUE_TYPE_NOT_MATCH:
        message = "Input shape \"{}\" value not number".format(value)
    if shape_error_type == InputShapeError.NAME_NOT_MATCH:
        message = "Input tensor name \"{}\" not in model".format(value)
    return message


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
    op_names = [op.name for op in operations if "Placeholder" == op.type]
    for _, tensor_name in enumerate(input_shapes):
        check_input_name_in_model(op_names, tensor_name)
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
        tensor.set_shape(input_shapes.get(op_name))
        return tensor
    if op_name in input_shapes:
        fixed_tensor_shape = input_shapes.get(op_name)
        message = "The fixed input tensor dim not equal to model input dim." \
                  "tensor_name:%s, %s vs %s" % (op_name, str(fixed_tensor_shape), str(model_shape))
        if len(fixed_tensor_shape) != len(model_shape):
            print_error_log(message)
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_DATA_ERROR)
        for index, dim in enumerate(model_shape):
            fixed_tensor_dim = fixed_tensor_shape[index]
            if dim is not None and fixed_tensor_dim != dim:
                print_error_log(message)
                raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_DATA_ERROR)
            model_shape[index] = fixed_tensor_dim
        print_info_log("Fix dynamic input shape of %s to %s" % (op_name, model_shape))
    tensor.set_shape(model_shape)
    return tensor


def check_input_name_in_model(tensor_name_list, input_name):
    """
    Function Description:
        check input name in model
    Parameter:
        tensor_name_list: the tensor name list
        input_name: the input name
    Exception Description:
        When input name not in tensor name list throw exception
    """
    if input_name not in tensor_name_list:
        print_error_log(get_shape_not_match_message(InputShapeError.NAME_NOT_MATCH, input_name))
        raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
