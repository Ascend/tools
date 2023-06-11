#!/usr/bin/env python
# coding=utf-8
"""
Function:
The file mainly involves main function of parsing input arguments.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import sys
import os
import time
import argparse
import tarfile
from ms_interface import utils
from ms_interface.collection import Collection
from ms_interface.constant import Constant
from ms_interface.aicore_error_parser import AicoreErrorParser


def extract_tar(tar_file, path):
    tar = tarfile.open(tar_file, "r")
    tar.extractall(path)
    tar.close()


def get_select_dir(path):
    subdir = os.listdir(path)
    if len(subdir) != 1:
        raise ValueError("[ERROR] found more than one subdir in collect tar")
    report_path = os.path.join(path, subdir[0])
    return report_path


def main() -> int:
    """
    main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--report_path", dest="report_path", default="",
        help="<Optional> The decompression directory of the tar package from npucollector.", required=False)
    parser.add_argument(
        "-f", "--tar_file", dest="tar_file", default="",
        help="<Optional> The tar.gz package path from npucollector.", required=False)
    parser.add_argument(
        "-out", "--output_path", dest="output_path", default="",
        help="<Optional> The output address of the analysis report.", required=False)

    if len(sys.argv) <= 1:
        parser.print_usage()
        return Constant.MS_AICERR_INVALID_PARAM_ERROR
    args = parser.parse_args(sys.argv[1:])
    # report_path、tar_file 必须存在一个
    if not args.report_path and not args.tar_file:
        utils.print_error_log("There must be one of the parameters report_path and tar_file.")
        return Constant.MS_AICERR_INVALID_PARAM_ERROR

    # 如果输入参数中没有报告地址
    if not args.output_path:
        utils.print_info_log("The tool directory will be used to as the output address of the analysis report.")
        args.output_path = os.getcwd()

    try:
        collect_time = time.localtime()
        cur_time_str = time.strftime("%Y%m%d%H%M%S", collect_time)
        utils.check_path_valid(os.path.realpath(args.output_path), isdir=True, output=True)
        output_path = os.path.join(os.path.realpath(args.output_path), "info_" + cur_time_str)
        utils.check_path_valid(output_path, isdir=True, output=True)
        # 解压路径存在就不需要再次解压了
        if not args.report_path and args.tar_file:
            utils.print_info_log("Start to unzip tar.gz package.")
            extract_path = "extract_" + cur_time_str
            extract_tar(args.tar_file, extract_path)
            args.report_path = get_select_dir(extract_path)

        # collect info
        collection = Collection(args.report_path, output_path)
        collection.collect()

        # parse ai core error
        parser = AicoreErrorParser(collection, output_path, collect_time)
        parser.parse()

        return Constant.MS_AICERR_NONE_ERROR

    except utils.AicErrException as error:
        utils.print_error_log(
            f"The aicore error analysis tool has an exception, and error code is {error.error_info}.")
        return error.error_info


if __name__ == '__main__':
    sys.exit(main())
