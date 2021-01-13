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

ACCURACY_COMPARISON_INVALID_PARAM_ERROR = 1
ACCURACY_COMPARISON_INVALID_DATA_ERROR = 2
ACCURACY_COMPARISON_INVALID_PATH_ERROR = 3
ACCURACY_COMPARISON_INVALID_COMMAND_ERROR = 4
ACCURACY_COMPARISON_PYTHON_VERSION_ERROR = 5
ACCURACY_COMPARISON_MODEL_TYPE_ERROR = 6
ACCURACY_COMPARISON_LOAD_JSON_FILE_ERROR = 7
ACCURACY_COMPARISON_WRITE_JSON_FILE_ERROR = 8
ACCURACY_COMPARISON_OPEN_FILE_ERROR = 9
ACCURACY_COMPARISON_BIN_FILE_ERROR = 10
ACCURACY_COMPARISON_INVALID_KEY_ERROR = 11
ACCURACY_COMPARISON_PYTHON_COMMAND_ERROR = 12

MODEL_TYPE = ['.onnx', '.pb', '.om']


class AccuracyCompareException(Exception):
    """
    Class for Accuracy Compare Exception
    """

    def __init__(self, error_info):
        super().__init__(self)
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
    Return Value:
        none
    Exception Description:
        none
    """
    _print_log("INFO", info_msg)


def print_error_log(error_msg):
    """
    Function Description:
        print error log.
    Parameter:
        info_msg: the error message.
    Return Value:
        none
    Exception Description:
        none
    """
    _print_log("ERROR", error_msg)


def print_warn_log(warn_msg):
    """
    Function Description:
        print warn log.
    Parameter:
        info_msg: the warn message.
    Return Value:
        none
    Exception Description:
        none
    """
    _print_log("WARNING", warn_msg)


def check_file_or_directory_path(path, isdir=False):
    """
    Function Description:
        check whether the path is valid
    Parameter:
        path: the path to check
        isdir: the path is dir or file
    Return Value:
        none
    Exception Description:
        when invalid data throw exception
    """
    if isdir:
        if not os.path.isdir(path):
            print_error_log('The path {} is not a directory.Please check the path'.format(path))
            raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PATH_ERROR)
    else:
        if not os.path.isfile(path):
            print_error_log('The path {} is not a file.Please check the path'.format(path))
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
        print_error_log('{} name extension does not meet requirements.Please check file name'.format(file_name))
        raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PATH_ERROR)
    return model_name, extension


def get_dump_data_path(dump_data_dir):
    """
    Function Description:
        traverse directories and obtain the absolute path of dump data
    Parameter:
        dump_data_dir: dump data directory
    Return Value:
        dump data path,file is exist or file is not exist
    Exception Description:
        none
    """
    dump_data_path = None
    file_is_exist = True
    for dir_path, sub_paths, files in os.walk(dump_data_dir):
        if len(files) != 0:
            dump_data_path = dir_path
            file_is_exist = False
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
        none
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
    Return Value:
        none
    Exception Description:
        when invalid data throw exception
    """
    check_file_or_directory_path(dir_path, True)
    try:
        os.makedirs(dir_path, mode=0o700)
    except OSError as ex:
        print_error_log(
            'Failed to create {}.Please check the path permission or disk space .{}'.format(dir_path, str(ex)))
        raise AccuracyCompareException(ACCURACY_COMPARISON_INVALID_PATH_ERROR)


def check_input_bin_file_path(data_path):
    """
    Function Description:
        check the output bin file
    Parameter:
        data_path: data path directory
    Return Value:
        none
    Exception Description:
        none
    """
    bin_files = data_path.split(',')
    for item in bin_files:
        check_file_or_directory_path(item)
