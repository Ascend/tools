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
import tarfile

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
    current_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                 time.localtime(int(time.time())))
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
            print_error_log(
                'Failed to create %s. Please check that the path is accessible'
                ' or the disk space is enough. %s ' % (path, str(ex)))
            raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)
        finally:
            pass
    if not os.path.exists(path):
        print_error_log(
            'The path %s does not exist. Please check that the path exists.' % path)
        raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)

    if not os.access(path, os.R_OK):
        print_error_log('The path %s does not have permission to read.'
                        ' Please check that the path is readable.' % path)
        raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)

    if isdir and not os.access(path, os.W_OK):
        print_error_log('The path %s does not have permission to write.'
                        ' Please check that the path is writeable.' % path)
        raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)

    if isdir:
        if not os.path.isdir(path):
            print_error_log(
                'The path %s is not a directory. Please check the path.' % path)
            raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)
    else:
        if not os.path.isfile(path):
            print_error_log(
                'The path %s is not a file. Please check the path.' % path)
            raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)


def copy_kernel_meta(report_path: str, collect_compile_path: str, kernel_name: str) -> bool:
    """
    collect local dump file:
    :param report_path: the local compile path
    :param collect_compile_path: the collect compile path
    :param kernel_name: the kernel name
    """
    match = False
    kernel_meta_path = os.path.join(report_path, "kernel_meta")
    if os.path.exists(kernel_meta_path):
        for name in os.listdir(kernel_meta_path):
            if name.startswith(kernel_name):
                src = os.path.join(kernel_meta_path, name)
                collect_kernel_meta_path = os.path.join(
                    collect_compile_path, "kernel_meta")
                check_path_valid(collect_kernel_meta_path, isdir=True,
                                 output=True)
                dest = os.path.join(collect_kernel_meta_path, name)
                copy_file(src, dest)
                match = True

    if not match:
        print_warn_log('There is no kernel_meta file for "%s" in %s.'
                       % (kernel_name, report_path))
    return match


def copy_proto_file(report_path: str, collect_compile_path: str) -> bool:
    """
    copy proto file:
    :param report_path: the local compile path
    :param collect_compile_path: the collect compile path
    """
    match = False
    for name in os.listdir(report_path):
        file_name_pattern = re.compile(Constant.BUILD_PROTO_FILE_PATTERN)
        pattern_match = file_name_pattern.match(name)
        if pattern_match:
            src = os.path.join(report_path, name)
            dest = os.path.join(collect_compile_path, name)
            copy_file(src, dest)
            match = True

    if not match:
        print_warn_log('There is no graph file in %s.' % report_path)

    return match


def copy_dump_file(dump_path: str, collect_dump_path: str, op_name: str) -> bool:
    """
    collect local dump file:
    :param dump_path: the local dump path
    :param collect_dump_path: the collect dump path
    :param op_name: the op name
    """
    match_name = op_name.replace('/', '_').replace('.', '_')
    match = False
    for root, _, names in os.walk(dump_path):
        for name in names:
            if "".join(['.', match_name, '.']) in name:
                src = os.path.join(root, name)
                dest = os.path.join(collect_dump_path, name)
                copy_file(src, dest)
                match = True

    if not match:
        print_warn_log(
            'There is no dump file for "%s" in %s.' % (op_name, dump_path))

    return match


def execute_command(cmd: list, file_out: str = None) -> (int, str):
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
                with os.fdopen(os.open(file_out, Constant.WRITE_FLAGS,
                                       Constant.WRITE_MODES),
                               'w') as output_file:
                    process = subprocess.Popen(cmd, shell=False,
                                               stdout=output_file,
                                               stderr=file_no)
                    os.chmod(file_out, stat.S_IRUSR)
            process.wait()
            status = process.returncode
            out_temp.seek(0)
            data = out_temp.read().decode('utf-8')
        return status, data
    except (FileNotFoundError,) as error:
        print_error_log('Failed to execute cmd %s. %s' % (cmd, error))
        raise AicErrException(Constant.MS_AICERR_EXECUTE_COMMAND_ERROR)
    finally:
        pass


def copy_file(src: str, dest: str) -> None:
    """
    copy file from src to dest
    :param src: the src path
    :param dest: the dest path
    """
    dest_dir = os.path.dirname(dest)
    check_path_valid(dest_dir, isdir=True, output=True)
    try:
        shutil.copy2(src, dest)
    except (OSError, IOError) as error:
        print_error_log('Failed to copy %s to %s. %s' % (src, dest, error))
        raise AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)
    finally:
        pass


def write_file(output_path: str, file_content: str, write_mode="w") -> None:
    """
    write text to output file
    :param output_path: the output path
    :param file_content: the file content
    """
    dest_dir = os.path.dirname(output_path)
    check_path_valid(dest_dir, isdir=True, output=True)
    try:
        with os.fdopen(os.open(output_path, Constant.WRITE_FLAGS,
                               Constant.WRITE_MODES), write_mode) \
                as output_file:
            output_file.write(file_content)
        os.chmod(output_path, stat.S_IRUSR)
    except IOError as io_error:
        print_error_log(
            'Failed to write file %s. %s' % (output_path, io_error))
        raise AicErrException(Constant.MS_AICERR_OPEN_FILE_ERROR)
    finally:
        pass


def get_hexstr_value(hexstr: str) -> int:
    """
    get hex by string
    """
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


def untar(tar_file: str, dirs: str) -> None:
    """
    extract tar.gz file
    :param tar_file: the tar.gz file
    :param dirs: the dirs
    """
    try:
        current_size = 0
        src_file = tarfile.open(tar_file)
        flag = True
        for info in src_file.getmembers():
            current_size += info.size
            if current_size >= Constant.MAX_TAR_SIZE:
                print_warn_log("Failed to extract file %s" % tar_file)
                flag = False
                break
        if flag:
            src_file.extractall(path=dirs)
    except (ValueError, tarfile.ExtractError) as err:
        print_warn_log("Failed to untar file %s. %s" % (tar_file, err))
    finally:
        pass


def rm_path(path: str, base_path: str, isdir: bool = False) -> None:
    """
    delete directory
    :param path: the file or directory to delete
    :param base_path: the base path
    :param isdir: is directory or not
    """
    try:
        if os.path.exists(path) and os.path.realpath(path).startswith(
                os.path.realpath(base_path)):
            if isdir:
                shutil.rmtree(path)
            else:
                os.remove(path)
    except (OSError, PermissionError) as err:
        print_warn_log("Failed to delete path %s. %s" % (path, err))
    finally:
        pass


def strplogtime(str_time: str):
    temp_list = str_time.split(".")
    if len(temp_list) != 3:
        print_warn_log("str_time[{}] does not match %Y-%m-%d-%H:%M:%S.%f1.%f2, please check".format(str_time))
        return datetime.strptime(str_time, '%Y-%m-%d-%H:%M:%S')
    new_str = "{}.{}{}".format(temp_list[0], temp_list[1], temp_list[2])
    return datetime.strptime(new_str, '%Y-%m-%d-%H:%M:%S.%f')
