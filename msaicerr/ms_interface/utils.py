#!/usr/bin/env python
# coding=utf-8
"""
Function:
This file mainly involves the common function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import os
import os.path
import shutil
import subprocess
import sys
import tempfile
import time
import re
import stat

from datetime import datetime

from ms_interface.constant import Constant


class AicErrException(Exception):
    """
    The class for Op Gen Exception
    """

    def __init__(self: any, error_info: int) -> None:
        super().__init__(error_info)
        self.error_info = error_info


def _print_log(level: str, msg: str) -> None:
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    pid = os.getpid()
    print(current_time + " (" + str(pid) + ") - [" + level + "] " + msg)
    sys.stdout.flush()


def print_info_log(info_msg: str) -> None:
    """
    print info log
    @param info_msg: the info message
    @return: none
    """
    _print_log("INFO", info_msg)


def print_warn_log(warn_msg: str) -> None:
    """
    print warn log
    @param warn_msg: the warn message
    @return: none
    """
    _print_log("WARNING", warn_msg)


def print_error_log(error_msg: str) -> None:
    """
    print error log
    @param error_msg: the error message
    @return: none
    """
    _print_log("ERROR", error_msg)


def check_path_special_character(path: str) -> None:
    """
    Function Description: check path special character
    @param path: the path to check
    """
    if path == "":
        print_error_log("The path is empty. Please enter a valid path.")
        raise AicErrException(Constant.MS_AICERR_INVALID_PARAM_ERROR)
    if " " in path:
        print_error_log("The path can not contain space.")
        raise AicErrException(Constant.MS_AICERR_INVALID_PARAM_ERROR)
    grep_str = "[\';*?`!#$%^&+=<>{}]|~\""
    if set(path) & set(grep_str):
        print_error_log(
            "The path is not allowed with special characters " + grep_str + ".")
        raise AicErrException(Constant.MS_AICERR_INVALID_PARAM_ERROR)


def check_path_valid(path: str, isdir: bool = False, output: bool = False) -> None:
    """
    Function Description: check path valid
    @param path: the path to check
    @param isdir: the path is dir or file
    @param output: the path is output
    """
    check_path_special_character(path)
    path = os.path.realpath(path)
    if output and isdir and not os.path.exists(path):
        try:
            os.makedirs(path, mode=Constant.DIRECTORY_MASK)
        except OSError as ex:
            print_error_log(f'Failed to create {path}. '
                            f'Please check that the path is accessible or the disk space is enough. {str(ex)}')
            raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR) from ex
        finally:
            pass
    if not os.path.exists(path):
        print_error_log(f'The path {path} does not exist. Please check that the path exists.')
        raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)

    if not os.access(path, os.R_OK):
        print_error_log(f'The path {path} does not have permission to read. Please check that the path is readable.')
        raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)

    if isdir and not os.access(path, os.W_OK):
        print_error_log(f'The path {path} does not have permission to write. Please check that the path is writeable.')
        raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)

    if isdir:
        if not os.path.isdir(path):
            print_error_log(f'The path {path} is not a directory. Please check the path.')
            raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)
    else:
        if not os.path.isfile(path):
            print_error_log(f'The path {path} is not a file. Please check the path.')
            raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)


def execute_command(cmd: list, file_out: str = None) -> tuple:
    """
    execute command
    :param cmd: the command to execute
    :param file_out: the stdout file
    :return: status and data
    """
    try:
        with tempfile.SpooledTemporaryFile() as out_temp:
            file_no = out_temp.fileno()
            if file_out is None:
                process = subprocess.Popen(cmd, shell=False, stdout=file_no,
                                           stderr=file_no)
            else:
                with os.fdopen(os.open(file_out, Constant.WRITE_FLAGS, Constant.WRITE_MODES), 'w') as output_file:
                    process = subprocess.Popen(cmd, shell=False, stdout=output_file, stderr=file_no)
                    os.chmod(file_out, stat.S_IRUSR)
            process.wait()
            status = process.returncode
            out_temp.seek(0)
            data = out_temp.read().decode('utf-8')
        return status, data
    except FileNotFoundError as error:
        print_error_log('Failed to execute cmd %s. %s' % (cmd, error))
        raise AicErrException(Constant.MS_AICERR_EXECUTE_COMMAND_ERROR) from error
    finally:
        pass


def __copy_file(src: str, dest: str) -> None:
    """
    copy file from src to dest
    :param src: the src path
    :param dest: the dest path
    """
    shutil.copy2(src, dest)


def copy_src_to_dest(src_file_list: list, dest_path: str):
    """
    copy file form src_file_list to dest_path
    :param src_file_list: the source file list
    :param dest_path: the dest path
    """
    check_path_valid(dest_path, isdir=True, output=True)
    for file in src_file_list:
        dest_file = os.path.join(dest_path, os.path.basename(file))
        # 文件夹
        if os.path.isdir(file):
            original_files = [os.path.join(file, name) for name in os.listdir(file)]
            copy_src_to_dest(original_files, dest_file)
        else:
            try:
                __copy_file(file, dest_file)
            except (OSError, IOError) as error:
                print_error_log(f"Failed to copy {file} to {dest_file}. {error}.")
                raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR) from error


def write_file(output_path: str, file_content: str, write_mode="w") -> None:
    """
    write text to output file
    :param output_path: the output path
    :param file_content: the file content
    """
    dest_dir = os.path.dirname(output_path)
    check_path_valid(dest_dir, isdir=True, output=True)
    try:
        with os.fdopen(os.open(output_path, Constant.WRITE_FLAGS, Constant.WRITE_MODES), write_mode) as output_file:
            output_file.write(file_content)
        os.chmod(output_path, stat.S_IRUSR)
    except IOError as io_error:
        print_error_log(
            'Failed to write file %s. %s' % (output_path, io_error))
        raise AicErrException(Constant.MS_AICERR_OPEN_FILE_ERROR) from io_error
    finally:
        pass

def get_str_value(value_str: str) -> int:
    """
    get value by string
    """
    if not value_str:
        return -1
    value_str = value_str.strip()
    if value_str.startswith("0x"):
        return int(value_str, 16)
    else:
        return int(value_str)

def get_hexstr_value(hexstr: str) -> int:
    """
    get hex by string
    """
    hexstr = hexstr.strip()
    if hexstr == "0":
        return 0
    return int(hexstr, 16)


def hexstr_to_list_bin(hexstr: str) -> list:
    """
    convert hex str to list
    """
    value = get_hexstr_value(hexstr)
    binstr = bin(value)
    binstr_size = len(binstr)
    ret = []
    for i, bin_value in enumerate(binstr):
        if bin_value == '1':
            ret.append(binstr_size - i - 1)
    return ret


def get_01_from_hexstr(hexstr: str, high_bit: int, low_bit: int) -> str:
    """
    get 0 or 1 by hex string
    """
    ret = hexstr_to_list_bin(hexstr)
    code = ""
    for i in range(high_bit, low_bit - 1, -1):
        code += "1" if i in ret else "0"
    return code


def strplogtime(str_time: str):
    temp_list = str_time.split(".")
    if len(temp_list) != 3:
        print_warn_log("str_time[{}] does not match %Y-%m-%d-%H:%M:%S.%f1.%f2, please check".format(str_time))
        return datetime.strptime(str_time, '%Y-%m-%d-%H:%M:%S')
    new_str = "{}.{}{}".format(temp_list[0], temp_list[1], temp_list[2])
    return datetime.strptime(new_str, '%Y-%m-%d-%H:%M:%S.%f')


def get_inquire_result(grep_cmd, regexp):
    status, data = execute_command(grep_cmd)
    if status != 0:
        print_warn_log(f"Failed to execute command:{grep_cmd}.")
        return None
    ret = re.findall(regexp, data, re.M | re.S)
    if len(ret) == 0:
        print_warn_log(f"Log info does not macth:{regexp} in command result.")
        return None
    return ret
