#!/usr/bin/env python
# coding=utf-8
"""
Function:
RemoteCollection class. This file mainly involves the collect function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import os
import re
from ms_interface import utils
from ms_interface.constant import Constant
from ms_interface.collection import Collection


def collect_remote_file(report_path: str, key: str, collect_path: str) -> str:
    """
    collect local file:
    :param report_path: the local report path
    :param key: the key in slog_conf_path
    :param collect_path: the collect path
    :return: the local path
    """
    collect_target_path = os.path.join(collect_path,
                                       os.path.basename(report_path))
    utils.check_path_valid(collect_target_path, isdir=True, output=True)
    if key == Constant.DIR_SLOG:
        slog_report_path = os.path.join(report_path, "log", "device", "firmware")
        if os.path.exists(slog_report_path) and \
                os.path.isdir(slog_report_path):
            copy_file_to_dest(slog_report_path, key, collect_target_path,
                              report_path)
        else:
            utils.print_error_log(
                'There is no %s in %s.' % (key, report_path))
    elif key == 'MNTN_PATH':
        hisi_report_path = os.path.join(report_path, "log", "device", "system")
        if os.path.exists(hisi_report_path) and \
                os.path.isdir(hisi_report_path):
            copy_file_to_dest(hisi_report_path, Constant.DIR_BBOX,
                              collect_target_path, report_path)
        else:
            utils.print_warn_log(
                'There is no hisi_logs in %s.' % report_path)
    elif key == Constant.DIR_PLOG:
        plog_path = os.path.join(report_path, "log", "host", "cann")
        debug_plog_path = os.path.join(report_path, "log", "host", "cann", "debug")
        if os.path.exists(debug_plog_path) and \
                os.path.isdir(debug_plog_path):
            copy_file_to_dest(debug_plog_path, Constant.DIR_PLOG,
                              collect_target_path, report_path)
        elif os.path.exists(plog_path) and \
                os.path.isdir(plog_path):
            copy_file_to_dest(plog_path, Constant.DIR_PLOG,
                              collect_target_path, report_path)
        else:
            utils.print_warn_log(
                'There is no plog in %s.' % report_path)
    return collect_target_path


def copy_file_to_dest(log_path: str, target: str, collect_target_path: str, report_path: str) -> None:
    """
    copy file to dest:
    :param log_path: the local log path
    :param target: the target in log
    :param collect_target_path: the collect path
    :param report_path: the local report path
    """
    match = False
    for top, _, files in os.walk(log_path):
        for name in files:
            src = os.path.join(top, name)
            dest = os.path.join(collect_target_path,
                                top[len(report_path) + 1:], name)
            utils.copy_file(src, dest)
            match = True
    if not match:
        utils.print_warn_log(
            'There is no %s file in %s.' % (target, report_path))


class RemoteCollection(Collection):
    """
    The RemoteCollection class. collect local info
    """

    def check_argument_valid(self: any) -> None:
        """
        check argument valid
        """
        utils.check_path_valid(self.report_path, isdir=True)
        utils.check_path_valid(self.output_path, isdir=True, output=True)

    @staticmethod
    def collect_slog_file(report_path: str, collect_path: str) -> str:
        """
        collect slog file
        :param report_path: the slog conf file
        :param collect_path: the collect path
        """
        return collect_remote_file(report_path, Constant.DIR_SLOG, collect_path)

    @staticmethod
    def collect_plog_file(self: any, collect_path: str) -> None:
        """
        collect plog file
        :param collect_path: the collect path
        """
        return collect_remote_file(self.report_path, Constant.DIR_PLOG, collect_path)

    @staticmethod
    def collect_bbox_file(report_path: str, collect_path: str) -> str:
        """
        collect bbox file
        :param report_path: the bbox conf file
        :param collect_path: the collect path
        """
        return collect_remote_file(report_path, 'MNTN_PATH', collect_path)

    def collect_dump_file(self: any, collect_path: str, op_name_list: list) -> str:
        """
        collect dump file
        :param collect_path: the collect path
        :param op_name_list: the op name list
        """
        # dump files are in report_path
        dump_path = os.path.join(self.report_path, "extra-info", "data-dump")
        utils.check_path_valid(dump_path, isdir=True)
        collect_dump_path = os.path.join(collect_path, 'dump')
        utils.check_path_valid(collect_dump_path, isdir=True, output=True)
        copy_dump_file_status = False
        for op_name in op_name_list:
            copy_dump_file_status = utils.copy_dump_file(dump_path,
                                                         collect_dump_path,
                                                         op_name)

        if copy_dump_file_status:
            utils.print_info_log(
                'The dump file is saved in %s.' % collect_dump_path)

        return collect_dump_path

    def collect_compile_file(self: any, collect_path: str, kernel_name_list: list) -> str:
        """
        collect compile file
        :param collect_path: the collect path
        :param kernel_name_list: the kernel name list
        """
        utils.check_path_valid(self.report_path, isdir=True)
        collect_compile_path = os.path.join(collect_path, 'compile')
        utils.check_path_valid(collect_compile_path, isdir=True, output=True)

        copy_kernel_meta_status = False

        for kernel_name in kernel_name_list:
            copy_kernel_meta_status = self.copy_kernel_meta(
                self.report_path, collect_compile_path, kernel_name)
        copy_proto_file_status = self.copy_proto_file(self.report_path,
                                                       collect_compile_path)

        if copy_kernel_meta_status or copy_proto_file_status:
            utils.print_info_log(
                'The compile file is saved in %s.' % collect_compile_path)

        return collect_compile_path


    def copy_kernel_meta(self, report_path: str, collect_compile_path: str, kernel_name: str) -> bool:
        """
        collect local dump file:
        :param report_path: the local compile path
        :param collect_compile_path: the collect compile path
        :param kernel_name: the kernel name
        """
        match = False
        kernel_meta_path = os.path.join(self.report_path, "extra-info", "ops")
        if os.path.exists(kernel_meta_path):
            for root, _, names in os.walk(kernel_meta_path):
                for name in names:
                    if name.startswith(kernel_name):
                        src = os.path.join(root, name)
                        collect_kernel_meta_path = os.path.join(
                            collect_compile_path, "kernel_meta")
                        utils.check_path_valid(collect_kernel_meta_path, isdir=True,
                                        output=True)
                        dest = os.path.join(collect_kernel_meta_path, name)
                        utils.copy_file(src, dest)
                        match = True

        if not match:
            utils.print_warn_log('There is no kernel_meta file for "%s" in %s.'
                        % (kernel_name, report_path))
        return match


    def copy_proto_file(self, report_path: str, collect_compile_path: str) -> bool:
        """
        copy proto file:
        :param report_path: the local compile path
        :param collect_compile_path: the collect compile path
        """
        match = False
        proto_path = os.path.join(self.report_path, "extra-info", "graph")
        for root, _, names in os.walk(report_path):
            for name in names:
                file_name_pattern = re.compile(Constant.BUILD_PROTO_FILE_PATTERN)
                pattern_match = file_name_pattern.match(name)
                if pattern_match:
                    src = os.path.join(root, name)
                    dest = os.path.join(collect_compile_path, name)
                    utils.copy_file(src, dest)
                    match = True

        if not match:
            utils.print_warn_log('There is no graph file in %s.' % report_path)

        return match
