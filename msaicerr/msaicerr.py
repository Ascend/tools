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
from ms_interface.constant import Constant
from ms_interface.remote_collection import RemoteCollection
from ms_interface.aicore_error_parser import AicoreErrorParser
from ms_interface.single_op_case import SingleOpCase

def extract_tar(tar_file, path):
    tar = tarfile.open(tar_file, "r")
    tar.extractall(path)
    tar.close()

def get_select_dir(path):
    subdir = os.listdir(path)
    if len(subdir) != 1:
        sys.exit("[ERROR] found more than one subdir in collect tar")
    report_path = os.path.join(path, subdir[0])
    return report_path

def main() -> int:
    """
    main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--report_path", dest="report_path", default="",
        help="<Optional> the tar dir from npucollector", required=False)
    parser.add_argument(
        "-f", "--tar_file", dest="tar_file", default="",
        help="<Optional> the tar.gz path from npucollector", required=False)
    parser.add_argument(
        "-out", "--output", dest="output_path", default="",
        help="<Optional> the output path")

    if len(sys.argv) <= 1:
        parser.print_usage()
        return Constant.MS_AICERR_INVALID_PARAM_ERROR
    args = parser.parse_args(sys.argv[1:])
    if (not args.report_path) and (not args.tar_file):
        utils.print_error_log(
                "report_path and tar_file must have one ")
        return Constant.MS_AICERR_INVALID_PARAM_ERROR

    try:
        collect_time = time.localtime()
        cur_time_str = time.strftime("%Y%m%d%H%M%S", collect_time)
        utils.check_path_valid(os.path.realpath(args.output_path), isdir=True, output=True)
        output_path = os.path.join(os.path.realpath(args.output_path), "info_" + cur_time_str)
        utils.check_path_valid(output_path, isdir=True, output=True)
        if args.tar_file:
            print("Start to unzip tar.gz, ")
            extract_path = "extract_" + cur_time_str
            extract_tar(args.tar_file, extract_path)
            args.report_path = get_select_dir(extract_path)

        # collect info
        collection = RemoteCollection(args.report_path, output_path)
        collection.collect()

        # clear local script.sh
        local_script = os.path.join(output_path, 'collection', Constant.SCRIPT)
        utils.rm_path(local_script, output_path, isdir=True)

        # parse ai core error
        parser = AicoreErrorParser(collection, output_path, collect_time)
        parser.parse()

        single_op_case = SingleOpCase(collection, output_path, collect_time)
        single_op_case.run()

    except utils.AicErrException as error:
        return error.error_info
    finally:
        pass
    return Constant.MS_AICERR_NONE_ERROR


if __name__ == '__main__':
    sys.exit(main())
