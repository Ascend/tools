#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""
ut report module
"""
import os
import stat
import json
import fnmatch
from enum import Enum
from ms_interface.single_op_test_frame.common import logger
from ms_interface.single_op_test_frame.common import op_status
from ms_interface.single_op_test_frame.utils import file_util
from ms_interface.single_op_test_frame.ut.op_ut_case_info import OpUTCaseTrace


# 'pylint: disable=too-few-public-methods
class Constant:
    """
    This class for Constant.
    """
    DATA_FILE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    DATA_FILE_MODES = stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP
    DATA_DIR_MODES = stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP


class TestResultType(Enum):
    """
    Test result type Enum: UNKNOWN, SUCCESS, FAILED, ERROR
    """
    UNKNOWN = "unknown"
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


class OpUTCaseReport:
    """
    op ut case report
    """

    def __init__(self, case_run_trace: OpUTCaseTrace):
        self.op_type = case_run_trace.ut_case_info.op_type
        self.case_name = case_run_trace.ut_case_info.case_name
        self.run_soc = case_run_trace.run_soc
        stage_list = case_run_trace.stage_result
        self.status = op_status.SUCCESS
        self.err_msg = None
        self.err_trace = None
        for stage_res in stage_list:
            if not stage_res.is_success():
                self.status = op_status.FAILED
        if self.status != op_status.SUCCESS:
            err_msg = ""
            err_trace = ""
            for stage_res in stage_list:
                if not stage_res.is_success():
                    err_msg += "" if not stage_res.err_msg else stage_res.err_msg
                    err_trace += "" if not stage_res.err_trace else (stage_res.err_trace)
            self.err_msg = err_msg
            self.err_trace = err_trace

        self.trace_detail = case_run_trace

    def to_json_obj(self):
        """
        get json object info
        :return: json object
        """
        return {
            "op_type": self.op_type,
            "case_name": self.case_name,
            "run_soc": self.run_soc,
            "status": self.status,
            "err_msg": self.err_msg,
            "trace_detail": None if not self.trace_detail else self.trace_detail.to_json_obj()
        }

    def summary_txt(self):
        """
        get summary info string
        :return: summary info string
        """
        if self.status != op_status.SUCCESS:
            if not self.err_trace:
                return "%s: [%s]  %s (%s), error msg: %s\n      Case File \"%s\", line %s\n" % (
                    self.status, self.op_type, self.case_name, self.run_soc, self.err_msg,
                    self.trace_detail.ut_case_info.case_file, str(self.trace_detail.ut_case_info.case_line_num))

            summary_with_trace_str = "{status}: [{op_type}]  {case_name} ({run_soc}), error msg: {err_msg}, \n"
            summary_with_trace_str += "      Case File \"{case_file}\", line {line_no}\n"
            summary_with_trace_str += "      Error trace: \n      {trace_info}"
            return summary_with_trace_str.format_map({
                "status": self.status,
                "op_type": self.op_type,
                "case_name": self.case_name,
                "run_soc": self.run_soc,
                "err_msg": self.err_msg,
                "case_file": self.trace_detail.ut_case_info.case_file,
                "line_no": str(self.trace_detail.ut_case_info.case_line_num),
                "trace_info": self.err_trace.replace("\n", "\n      ")
            })

        return "%s: [%s]  %s (%s) (%s)" % (self.status, self.op_type, self.case_name, self.run_soc,
                                           self.trace_detail.ut_case_info.case_usage.value)

    @staticmethod
    def parser_json_obj(json_obj):
        """
        parser from json object
        :param json_obj: json object
        :return: OpUTCaseReport
        """
        if not json_obj:
            return None
        return OpUTCaseReport(OpUTCaseTrace.parser_json_obj(json_obj["trace_detail"]))


class OpUTReport:
    """
    op ut report
    """

    def __init__(self, run_cmd=None):
        self.run_cmd = run_cmd
        self.total_cnt = 0
        self.failed_cnt = 0
        self.success_cnt = 0
        self.err_cnt = 0
        self._report_list = []
        # map struct is: soc -> status['success', 'failed'] -> case_rpt list
        self._soc_report_map = {}

    def get_case_rpt_list(self):
        """
        get case report list
        :return: case report list
        """
        return self._report_list

    def add_case_report(self, case_rpt: OpUTCaseReport):
        """
        add one test case report
        :param case_rpt: case report
        :return: None
        """
        self._report_list.append(case_rpt)
        self.total_cnt += 1
        if case_rpt.status == op_status.SUCCESS:
            self.success_cnt += 1
        if case_rpt.status == op_status.FAILED:
            self.failed_cnt += 1
        if case_rpt.status == op_status.ERROR:
            self.err_cnt += 1

        if case_rpt.run_soc not in self._soc_report_map.keys():
            self._soc_report_map[case_rpt.run_soc] = {}
        if case_rpt.status not in self._soc_report_map[case_rpt.run_soc].keys():
            self._soc_report_map[case_rpt.run_soc][case_rpt.status] = []

        self._soc_report_map[case_rpt.run_soc][case_rpt.status].append(case_rpt)

    def merge_rpt(self, rpt):
        """
        merge a report(OpUTReport)
        :param rpt: another report
        :return: None
        """
        for case_rpt in rpt.get_case_rpt_list():
            self.add_case_report(case_rpt)

    def to_json_obj(self):
        """
        convert to json object
        :return: json object
        """
        return {
            "run_cmd": self.run_cmd,
            "report_list": [case_rpt.to_json_obj() for case_rpt in self._report_list]
        }

    def summary_txt(self):
        """
        get report summary string
        :return: summary string
        """
        total_txt = """========================================================================
run command: %s
------------------------------------------------------------------------
- test soc: [%s]
- test case count: %d
- success count: %d
- failed count: %d
- error count: %d
------------------------------------------------------------------------
""" % (self.run_cmd, ", ".join(self._soc_report_map), self.total_cnt, self.success_cnt, self.failed_cnt, self.err_cnt)

        for soc, soc_detail in self._soc_report_map.items():
            total_txt += "Soc Version: %s\n" % soc
            for err_case in soc_detail.get(op_status.ERROR, []):
                total_txt += "    " + err_case.summary_txt() + "\n"
            for err_case in soc_detail.get(op_status.FAILED, []):
                total_txt += "    " + err_case.summary_txt() + "\n"
            for err_case in soc_detail.get(op_status.SUCCESS, []):
                total_txt += "    " + err_case.summary_txt() + "\n"
            total_txt += "------------------------------------------------------------------------\n"
        if self.failed_cnt > 0 or self.err_cnt > 0:
            total_txt += "Some test case failed. Please check your code or case!\n"
        total_txt += "========================================================================\n"
        return total_txt

    def console_print(self):
        """
        print report to console
        :return: None
        """
        if self.total_cnt > 0:
            print(self.summary_txt())
            return self.summary_txt()
        return "did not get single op test summary!"

    def txt_report(self, report_path):
        """
        txt type report, save report to txt file
        :param report_path:
        :return:
        """
        report_path = os.path.realpath(report_path)
        if not os.path.exists(report_path):
            file_util.makedirs(report_path, mode=Constant.DATA_DIR_MODES)

        rpt_txt = self.summary_txt()
        rpt_file_path = os.path.join(report_path, "ut_test_report.txt")
        if not os.path.exists(rpt_file_path):
            with os.fdopen(os.open(rpt_file_path,
                                   Constant.DATA_FILE_FLAGS, Constant.DATA_FILE_MODES), 'w') as rpt_fout:
                rpt_fout.write(rpt_txt)
        else:
            with open(rpt_file_path, 'w') as rpt_file:
                rpt_file.write(rpt_txt)

    def combine_report(self, report_paths, strict=False, file_pattern=None):
        """
        combine all report in report paths
        :param report_paths: report path
        :param strict: True is not found report will raise runtime exception
        :param file_pattern: report file pattern
        :return: None
        """

        def _add_report(rpt: OpUTReport):
            for case_rpt in rpt.get_case_rpt_list():
                self.add_case_report(case_rpt)

        if not isinstance(report_paths, (tuple, list)):
            report_paths = (report_paths,)

        find_report_list = []
        for report_path in report_paths:
            if not os.path.exists(report_path):
                logger.log_warn("combine_report report path not exist: %s" % report_path)
            if os.path.isfile(report_path):
                ut_report = OpUTReport()
                ut_report.load(report_path)
                print("load %s success, case cnt: %d" % (report_path, ut_report.total_cnt))
                _add_report(ut_report)
                continue
            for path, dir_names, file_names in os.walk(report_path):
                print(path, dir_names, file_names)
                for file_name in file_names:
                    if file_pattern and not fnmatch.fnmatch(file_name, file_pattern):
                        continue
                    report_file = os.path.join(path, file_name)
                    find_report_list.append(report_file)
                    report_file = os.path.join(path, file_name)
                    ut_report = OpUTReport()
                    ut_report.load(report_file)
                    print("load %s success, case cnt: %d" % (report_file, ut_report.total_cnt))
                    _add_report(ut_report)
        if not find_report_list and strict:
            logger.log_err("combine_report not found any report to combine in: [%s]" % ", ".join(report_paths))
            raise RuntimeError("combine_report not found any report to combine in: [%s]" % ", ".join(report_paths))

    def load(self, report_file):
        """
        load report
        :param report_file: report file path
        :return: None
        """
        with open(report_file) as r_f:
            json_str = r_f.read()
        json_obj = json.loads(json_str)
        self.run_cmd = json_obj["run_cmd"]
        for case_rpt in [OpUTCaseReport.parser_json_obj(case_obj) for case_obj in json_obj["report_list"]]:
            self.add_case_report(case_rpt)

    def save(self, report_data_path):
        """
        save report
        :param report_data_path: report data path
        :return: None
        """
        json_obj = self.to_json_obj()
        report_data_path = os.path.realpath(report_data_path)
        report_data_dir = os.path.dirname(report_data_path)
        if not os.path.exists(report_data_dir):
            file_util.makedirs(report_data_dir, mode=Constant.DATA_DIR_MODES)
        json_str = json.dumps(json_obj, indent=4)

        if not os.path.exists(report_data_path):
            with os.fdopen(os.open(report_data_path,
                                   Constant.DATA_FILE_FLAGS, Constant.DATA_FILE_MODES), 'w') as rpt_fout:
                rpt_fout.write(json_str)
        else:
            with open(report_data_path, 'w') as rpt_file:
                rpt_file.write(json_str)

    @staticmethod
    def parser_json_obj(json_obj):
        """
        parser from json object
        :param json_obj: json object
        :return: report object
        """
        rpt = OpUTReport(json_obj["run_cmd"])
        for case_rpt in [OpUTCaseReport.parser_json_obj(case_obj) for case_obj in json_obj["report_list"]]:
            rpt.add_case_report(case_rpt)
        return rpt
