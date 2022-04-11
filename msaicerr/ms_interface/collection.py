#!/usr/bin/env python
# coding=utf-8
"""
Function:
Collection class. This file mainly involves the collect function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import os
from abc import abstractmethod
from abc import ABCMeta
from ms_interface import utils
from ms_interface.log_parser import HostLogParser, DeviceLogParser


class BaseCollection:
    """
    The abstract class for BaseCollection
    """
    __metaclass__ = ABCMeta

    def __init__(self: any, report_path: str, output_path: str) -> None:
        self.report_path = os.path.realpath(report_path)
        self.output_path = os.path.realpath(output_path)
        self.collect_slog_path = None
        self.collect_applog_path = None
        self.node_name_list = []

    def get_collect_slog_path(self: any) -> str:
        """
        get collect slog path
        """
        return self.collect_slog_path

    def get_collect_applog_path(self: any) -> str:
        """
        get collect applog path
        """
        return self.collect_applog_path


class Collection(BaseCollection):
    """
    The abstract class for Collection
    """
    __metaclass__ = ABCMeta

    def __init__(self: any, report_path: str, output_path: str) -> None:
        BaseCollection.__init__(self, report_path, output_path)
        self.collect_dump_path = None
        self.collect_bbox_path = None
        self.collect_compile_path = None
        self.ai_core_error_list = []
        self.kernel_name_list = []

    @abstractmethod
    def check_argument_valid(self: any) -> None:
        """
        check argument valid
        """

    @abstractmethod
    def collect_slog_file(self: any, report_path: str, collect_path: str) -> None:
        """
        collect slog file
        :param report_path:  the report path of slog conf file
        :param collect_path: the collect path
        """

    @abstractmethod
    def collect_plog_file(self: any, collect_path: str) -> None:
        """
        collect plog file
        :param collect_path: the collect path
        """

    @abstractmethod
    def collect_bbox_file(self: any, report_path: str, collect_path: str) -> None:
        """
        collect bbox file
        :param report_path: the report path of bbox conf file
        :param collect_path: the collect path
        """

    @abstractmethod
    def collect_dump_file(self: any, collect_path: str, op_name_list: list) -> None:
        """
        collect dump file
        :param collect_path: the collect path
        :param op_name_list: the op name list
        """

    @abstractmethod
    def collect_compile_file(self: any, collect_path: str, kernel_name_list: list) -> None:
        """
        collect compile file
        :param collect_path: the collect path
        :param kernel_name_list: the kernel name list
        """

    def collect(self: any) -> None:
        """
        collect info
        """
        self.check_argument_valid()
        collect_path = os.path.join(self.output_path, 'collection')
        utils.check_path_valid(collect_path, isdir=True, output=True)
        utils.print_info_log('******************Collection******************')

        # collect slog
        utils.print_info_log('Start to collect slog file.')
        self.collect_slog_path = self.collect_slog_file(
            self.report_path, collect_path)
        utils.print_info_log(
            'The slog file is saved in %s.' % self.collect_slog_path)

        # collect plog
        utils.print_info_log('Start to collect plog file.')
        self.collect_plog_file(self, collect_path)
        self.collect_applog_path = collect_path
        utils.print_info_log(
            'The plog file is saved in %s.' % self.collect_applog_path)

        # if os.path.exists(os.path.join(self.report_path, "log", "device")):
        #     utils.print_info_log(
        #         'Start to parse ai core error by slog and plog file.')
        #     log_parser = DeviceLogParser(self.collect_applog_path, self.collect_slog_path)
        # else:
        #     # 某些场景无法获取device日志
        utils.print_info_log(
            'Start to parse ai core error only by plog file.')
        log_parser = HostLogParser(self.collect_applog_path)
        self.ai_core_error_list, self.node_name_list, self.kernel_name_list = log_parser.get_op_info()
        utils.print_info_log(
            'The ai core error occurs in %s.' % self.node_name_list)

        # collect compile
        utils.print_info_log('Start to collect compile file.')
        self.collect_compile_path = self.collect_compile_file(
            collect_path, self.kernel_name_list)

        utils.print_info_log('Start to collect dump file.')
        self.collect_dump_path = self.collect_dump_file(
            collect_path, self.node_name_list)

        # collect bbox
        utils.print_info_log('Start to collect bbox file.')
        self.collect_bbox_path = self.collect_bbox_file(
            self.report_path, collect_path)
        utils.print_info_log(
            'The bbox file is saved in %s.' % self.collect_bbox_path)
