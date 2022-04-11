#!/usr/bin/env python
# coding=utf-8
"""
Function:
LocalCollection class. This file mainly involves the collect function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import os
from ms_interface import utils
from ms_interface.constant import Constant
from ms_interface.collection import Collection


def collect_local_file(report_path: str, key: str, collect_path: str) -> str:
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
        slog_report_path = os.path.join(report_path, key)
        if os.path.exists(slog_report_path) and \
                os.path.isdir(slog_report_path):
            copy_file_to_dest(slog_report_path, key, collect_target_path,
                              report_path)
        else:
            utils.print_error_log(
                'There is no %s in %s.' % (key, report_path))
            raise utils.AicErrException(
                Constant.MS_AICERR_INVALID_SLOG_DATA_ERROR)
    elif key == 'MNTN_PATH':
        collect_target_path = os.path.join(collect_path,
                                           os.path.basename(report_path))
        utils.check_path_valid(collect_target_path, isdir=True, output=True)
        hisi_report_path = os.path.join(report_path, Constant.DIR_BBOX)
        if os.path.exists(hisi_report_path) and \
                os.path.isdir(hisi_report_path):
            copy_file_to_dest(hisi_report_path, Constant.DIR_BBOX,
                              collect_target_path, report_path)
        else:
            utils.print_warn_log(
                'There is no hisi_logs in %s.' % report_path)
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
            if target == 'slog' and os.path.basename(top) == 'slogd':
                continue
            src = os.path.join(top, name)
            dest = os.path.join(collect_target_path,
                                top[len(report_path) + 1:], name)
            utils.copy_file(src, dest)
            match = True
    if not match:
        utils.print_warn_log(
            'There is no %s file in %s.' % (target, report_path))


class LocalCollection(Collection):
    """
    The LocalCollection class. collect local info
    """

    def check_argument_valid(self: any) -> None:
        """
        check argument valid
        """
        utils.check_path_valid(self.report_path, isdir=True)
        utils.check_path_valid(self.compile_path, isdir=True)
        utils.check_path_valid(self.output_path, isdir=True, output=True)

    @staticmethod
    def collect_slog_file(report_path: str, collect_path: str) -> str:
        """
        collect slog file
        :param report_path: the slog conf file
        :param collect_path: the collect path
        """
        return collect_local_file(report_path, Constant.DIR_SLOG, collect_path)

    @staticmethod
    def collect_plog_file(collect_path: str) -> None:
        """
        collect plog file
        :param collect_path: the collect path
        """
        home_path = os.path.expanduser("~")
        ascend_path = os.path.join(home_path, Constant.DIR_ASCEND)
        applog_path = os.path.join(ascend_path, Constant.DIR_LOG)
        collect_target_path = os.path.join(collect_path,
                                           os.path.basename(applog_path))
        utils.check_path_valid(collect_target_path, isdir=True, output=True)
        copy_file_to_dest(applog_path, Constant.DIR_PLOG, collect_target_path,
                          applog_path)

    @staticmethod
    def collect_bbox_file(report_path: str, collect_path: str) -> str:
        """
        collect bbox file
        :param report_path: the bbox conf file
        :param collect_path: the collect path
        """
        return collect_local_file(report_path, 'MNTN_PATH', collect_path)

    def collect_dump_file(self: any, collect_path: str, op_name_list: list) -> str:
        """
        collect dump file
        :param collect_path: the collect path
        :param op_name_list: the op name list
        """
        # dump files are in compile_path
        utils.check_path_valid(self.compile_path, isdir=True)
        collect_dump_path = os.path.join(collect_path, 'dump')
        utils.check_path_valid(collect_dump_path, isdir=True, output=True)
        copy_dump_file_status = False
        for op_name in op_name_list:
            copy_dump_file_status = utils.copy_dump_file(self.compile_path,
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
        utils.check_path_valid(self.compile_path, isdir=True)
        collect_compile_path = os.path.join(collect_path, 'compile')
        utils.check_path_valid(collect_compile_path, isdir=True, output=True)

        copy_kernel_meta_status = False

        for kernel_name in kernel_name_list:
            copy_kernel_meta_status = utils.copy_kernel_meta(
                self.compile_path, collect_compile_path, kernel_name)
        copy_proto_file_status = utils.copy_proto_file(self.compile_path,
                                                       collect_compile_path)

        if copy_kernel_meta_status or copy_proto_file_status:
            utils.print_info_log(
                'The compile file is saved in %s.' % collect_compile_path)

        return collect_compile_path
