#!/usr/bin/env python
# coding=utf-8
"""
Function:
Collection class. This file mainly involves the collect function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import os

from ms_interface import utils
from ms_interface.log_parser import HostLogParser
from ms_interface.constant import Constant


class Collection:
    """
    Collection class
    """

    def __init__(self: any, report_path: str, output_path: str) -> None:
        self.report_path = os.path.realpath(report_path)
        self.output_path = os.path.realpath(output_path)
        self.collect_plog_path = None
        self.collect_dump_path = None
        self.collect_kernel_path = None
        self.ai_core_error_list = []
        self.kernel_name_list = []
        self.node_name_list = []
        self.input_list = []
        self.output_list = []
        self.tiling_list = []

    def check_argument_valid(self: any) -> None:
        """
        check argument valid
        """
        utils.check_path_valid(self.report_path, isdir=True)
        utils.check_path_valid(self.output_path, isdir=True, output=True)

    def collect(self: any):
        """
        collect info
        """
        self.check_argument_valid()
        collect_path = os.path.join(self.output_path, 'collection')
        utils.check_path_valid(collect_path, isdir=True, output=True)
        utils.print_info_log('******************Collection******************')

        collect_target_path = os.path.join(collect_path, os.path.basename(self.report_path))
        utils.check_path_valid(collect_target_path, isdir=True, output=True)

        # collect plog
        utils.print_info_log(f'Start to collect {Constant.DIR_PLOG} file.')
        plog_dest_path = self.collect_file(Constant.DIR_PLOG, collect_target_path)
        utils.print_info_log(f'The {Constant.DIR_PLOG} file is saved in {plog_dest_path}.')

        # parse ai core
        utils.print_info_log('Start to parse ai core error only by plog file.')
        log_parser = HostLogParser(plog_dest_path)
        self.ai_core_error_list, self.node_name_list, self.kernel_name_list = log_parser.get_op_info()
        utils.print_info_log(f'The ai core error occurs in {self.node_name_list}.')

        # collect compile
        utils.print_info_log('Start to collect compile file.')
        kernel_dest_path = self.collect_file("kernel", collect_path)
        utils.print_info_log(f"The ops file is saved in {kernel_dest_path}.")
        proto_dest_path = self.collect_file("proto", collect_path)
        utils.print_info_log(f"The graph file is saved in {proto_dest_path}.")

        # collect dump
        utils.print_info_log('Start to collect dump file.')
        dump_dest_path = self.collect_file("dump", collect_path)
        utils.print_info_log(f'The dump file is saved in {dump_dest_path}.')

    def collect_file(self, key: str, collect_target_path: str):
        """
        collect file
        :param key:the key
        :param collect_target_path: the collect path
        :return: the local path
        """
        original_files = []
        if key == Constant.DIR_PLOG:
            find_path_cmd = ['grep', \
                'there is an fftsplus aicore error|there is an aicore error|there is an .*aivec.* error exception', \
                '-inrE', self.report_path]
            find_path_regexp = r"([_\-/0-9a-zA-Z.]{1,}.log):"
            plog_path_ret = utils.get_inquire_result(find_path_cmd, find_path_regexp)
            if plog_path_ret and Constant.DIR_PLOG in plog_path_ret[0]:
                original_path = plog_path_ret[0].split(Constant.DIR_PLOG)[0]
            else:
                utils.print_error_log(
                    f"Plog file cannot be collected, \
                        the {Constant.DIR_PLOG} log path cannot be found in {self.report_path}.")
                raise utils.AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)
            dest_path = os.path.join(collect_target_path, original_path.split(self.report_path)[1][1:])
            utils.check_path_valid(dest_path, isdir=True, output=True)
            self.collect_plog_path = dest_path
            original_files = [os.path.join(original_path, name) for name in os.listdir(original_path)]
        elif key == "kernel":
            for kernel_name in self.kernel_name_list:
                find_path_cmd = ['find', self.report_path, '-name', f"{kernel_name}*"]
                regexp = r"([_\-/0-9a-zA-Z.]{1,}\.json|[_\-/0-9a-zA-Z.]{1,}\.o|[_\-/0-9a-zA-Z.]{1,}\.cce)"
                kernel_file_list = utils.get_inquire_result(find_path_cmd, regexp)
                if not kernel_file_list:
                    utils.print_warn_log(f"The {kernel_name} file path cannot be found in {self.report_path}.")
                    continue
                original_files.extend(kernel_file_list)
            if not original_files:
                utils.print_error_log(
                    f"Kernel file cannot be collected, the kernel file cannot be found in {self.report_path}.")
                raise utils.AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)
            collect_compile_path = os.path.join(collect_target_path, "compile")
            utils.check_path_valid(collect_compile_path, isdir=True, output=True)
            dest_path = os.path.join(collect_compile_path, "kernel_meta")
            utils.check_path_valid(dest_path, isdir=True, output=True)
            self.collect_kernel_path = dest_path
        elif key == "proto":
            find_path_cmd = ['find', self.report_path, '-name', "ge_proto_*_Build.txt"]
            regexp = r"([_\-/0-9a-zA-Z.]{1,}_Build.txt)"
            graph_file_list = utils.get_inquire_result(find_path_cmd, regexp)
            if not graph_file_list:
                utils.print_error_log(
                    f"Graph file cannot be collected, the graph file cannot be found in {self.report_path}.")
                raise utils.AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)
            original_files = graph_file_list
            dest_path = os.path.join(collect_target_path, "compile")
            utils.check_path_valid(dest_path, isdir=True, output=True)
        elif key == "dump":
            for node_name in self.node_name_list:
                find_path_cmd = ['find', self.report_path, '-name',
                                 f"*.{node_name.replace('/', '_').replace('.', '_')}.*"]
                regexp = r"[_\.\-/0-9a-zA-Z.]{1,}"
                dump_file_list = utils.get_inquire_result(find_path_cmd, regexp)
                if not dump_file_list:
                    utils.print_warn_log(f"The {node_name} file path cannot be found in {self.report_path}.")
                    continue
                original_files.extend(dump_file_list)
            if not original_files:
                utils.print_error_log(
                    f"Dump file cannot be collected, the dump file cannot be found in {self.report_path}.")
                raise utils.AicErrException(Constant.MS_AICERR_INVALID_PATH_ERROR)
            dest_path = os.path.join(collect_target_path, "dump")
            utils.check_path_valid(dest_path, isdir=True, output=True)
            self.collect_dump_path = dest_path
        utils.copy_src_to_dest(original_files, dest_path)
        return dest_path
