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
op ut case info,
apply info classes: UTCaseFileInfo, OpUTSuite, CaseUsage, OpUTCase, OpUTStageResult, OpUTCaseTrace
"""
from enum import Enum
from op_test_frame.common import op_status
from op_test_frame.common import precision_info


class UTCaseFileInfo:  # 'pylint: disable=too-few-public-methods
    """
    UT case file info, contains case_file and op_module_name
    """

    def __init__(self, case_file, op_module_name):
        self.case_file = case_file
        self.op_module_name = op_module_name


class CaseUsage(Enum):
    """
    case usage Enum
    """
    IMPL = "compile"
    CHECK_SUPPORT = "check_support"
    SELECT_FORMAT = "op_select_format"
    CFG_COVERAGE_CHECK = "op_config_coverage_check"
    PRECISION = "precision"
    CUSTOM = "custom"
    DIRECT = "direct"

    def to_str(self):
        """
        get case usage string
        :return: string type case usage
        """
        return self.value

    @staticmethod
    def parser_str(type_str):
        """
        parser str to CaseUsage Enum
        :param type_str: string type case usage
        :return: CaseUsage Enum
        """
        str_enum_map = {
            "compile": CaseUsage.IMPL,
            "check_support": CaseUsage.CHECK_SUPPORT,
            "op_select_format": CaseUsage.SELECT_FORMAT,
            "op_config_coverage_check": CaseUsage.CFG_COVERAGE_CHECK,
            "precision": CaseUsage.PRECISION,
            "custom": CaseUsage.CUSTOM
        }
        if not type_str or type_str not in str_enum_map.keys():
            return None

        return str_enum_map[type_str]


class OpUTBaseCase:
    """
    Op ut base case info
    """

    def __init__(self, support_soc=None, op_type=None, case_name=None,  # 'pylint: disable=too-many-arguments
                 case_usage: CaseUsage = CaseUsage.IMPL, case_file=None, case_line_num=None):
        self.support_soc = support_soc
        self.op_type = op_type
        self.case_name = case_name
        self.case_usage = case_usage
        self.case_file = case_file
        self.case_line_num = case_line_num

    def check_support_soc(self, soc_version: str):
        """
        check this case if support the soc

        Parameters
        ----------
        soc_version: str
            soc_version which need to check if support

        Returns
        -------
        True or False
        """
        if isinstance(self.support_soc, str):
            if self.support_soc.lower() == "all":
                return True
            if self.support_soc == soc_version:
                return True
        if isinstance(self.support_soc, (tuple, list)):
            if soc_version in self.support_soc:
                return True
            if "all" in self.support_soc:
                return True
        return False

    def to_json_obj(self):
        """
        convert to json object
        :return: json object
        """
        return {
            "support_soc": self.support_soc,
            "op_type": self.op_type,
            "case_name": self.case_name,
            "case_usage": self.case_usage.to_str(),
            "case_file": self.case_file,
            "case_line_num": self.case_line_num
        }

    @staticmethod
    def parser_json_obj(json_obj):
        """
        convert json object to OpUTBaseCase object
        :param json_obj: json object
        :return: OpUTBaseCase object
        """
        if not json_obj:
            return None
        case_usage = CaseUsage.parser_str(json_obj["case_usage"])
        if case_usage == CaseUsage.CUSTOM:
            return OpUTCustomCase.parser_json_obj(json_obj)

        return OpUTCase.parser_json_obj(json_obj)


class OpUTCase(OpUTBaseCase):  # 'pylint: disable=too-many-instance-attributes
    """
    op ut case
    """

    def __init__(self, support_soc=None, op_type=None, case_name=None,  # 'pylint: disable=too-many-arguments
                 op_params=None, expect=None, case_usage: CaseUsage = CaseUsage.IMPL,
                 expect_out_fn=None, case_file=None, case_line_num=None,
                 precision_standard: precision_info.PrecisionStandard = None,
                 op_imply_type="static", addition_params=None, bin_path=None):
        super().__init__(support_soc=support_soc, op_type=op_type, case_name=case_name, case_usage=case_usage,
                         case_file=case_file, case_line_num=case_line_num)

        self.op_params = op_params
        self.expect = expect
        self.expect_out_fn = expect_out_fn
        self.precision_standard = precision_standard
        self.op_imply_type = op_imply_type
        self.addition_params = addition_params
        self.bin_path = bin_path

    def to_json_obj(self):
        """
        convert to json object
        :return: json object
        """

        def _build_op_param_json(op_params):
            json_list = []
            for op_param in op_params:
                if isinstance(op_param, (tuple, list)):
                    if not op_param:
                        json_list.append(op_param)
                        continue
                    if isinstance(op_param[0], dict) and "shape" in op_param[0].keys():
                        # this is input or output
                        json_param = []
                        for sub_param in op_param:
                            json_param.append({
                                "dtype": sub_param.get("dtype"),
                                "shape": sub_param.get("shape"),
                                "format": sub_param.get("format"),
                                "ori_shape": sub_param.get("ori_shape"),
                                "ori_format": sub_param.get("ori_format"),
                                "data_path": sub_param.get("data_path"),
                                "expect_data_path": sub_param.get("expect_data_path"),
                                "range": sub_param.get("range")
                            })
                        json_list.append(json_param)
                    else:
                        json_list.append(op_param)
                elif isinstance(op_param, dict):
                    if "shape" in op_param.keys():
                        json_list.append({
                            "dtype": op_param.get("dtype"),
                            "shape": op_param.get("shape"),
                            "format": op_param.get("format"),
                            "ori_shape": op_param.get("ori_shape"),
                            "ori_format": op_param.get("ori_format"),
                            "data_path": op_param.get("data_path"),
                            "expect_data_path": op_param.get("expect_data_path"),
                            "range": op_param.get("range")
                        })
                else:
                    json_list.append(op_param)
            return json_list

        return {
            "support_soc": self.support_soc,
            "op_type": self.op_type,
            "case_name": self.case_name,
            "op_params": _build_op_param_json(self.op_params),
            "addition_params": self.addition_params,
            "expect": self.expect if isinstance(self.expect, str) else self.expect.__class__.__name__,
            "case_usage": self.case_usage.to_str(),
            "case_file": self.case_file,
            "case_line_num": self.case_line_num,
            "precision_standard": self.precision_standard.to_json_obj() if self.precision_standard else None,
            "op_imply_type": self.op_imply_type
        }

    @staticmethod
    def parser_json_obj(json_obj):
        """
        convert json object to OpUTCase object
        :param json_obj: json object
        :return: OpUTCase object
        """
        if not json_obj:
            return None
        return OpUTCase(support_soc=json_obj["support_soc"],
                        op_type=json_obj["op_type"],
                        case_name=json_obj["case_name"],
                        op_params=json_obj["op_params"],
                        expect=json_obj["expect"],
                        case_usage=CaseUsage.parser_str(json_obj["case_usage"]),
                        case_file=json_obj.get("case_file"),
                        case_line_num=json_obj.get("case_line_num"),
                        precision_standard=precision_info.PrecisionStandard.parse_json_obj(
                            json_obj.get("precision_standard")),
                        op_imply_type=json_obj.get("op_imply_type"),
                        addition_params=json_obj.get("addition_params"),
                        bin_path=json_obj.get("bin_path"))


class OpUTCustomCase(OpUTBaseCase):
    """
    op custom ut case
    """

    def __init__(self, support_soc=None, op_type=None, case_name=None,  # 'pylint: disable=too-many-arguments
                 case_usage: CaseUsage = CaseUsage.CUSTOM, case_file=None, case_line_num=None,
                 test_func_name=None, test_func=None):
        super().__init__(support_soc, op_type, case_name, case_usage, case_file, case_line_num)
        self.test_func_name = test_func_name
        self.test_func = test_func

    def to_json_obj(self):
        """
        convert to json object
        :return: json object
        """
        json_obj = super().to_json_obj()
        json_obj["test_func_name"] = self.test_func_name
        return json_obj

    @staticmethod
    def parser_json_obj(json_obj):
        """
        convert json object to OpUTCustomCase object
        :param json_obj: json object
        :return: OpUTCustomCase object
        """
        if not json_obj:
            return None
        return OpUTCustomCase(support_soc=json_obj["support_soc"],
                              op_type=json_obj["op_type"],
                              case_name=json_obj["case_name"],
                              case_usage=CaseUsage.parser_str(json_obj["case_usage"]),
                              case_file=json_obj.get("case_file"),
                              case_line_num=json_obj.get("case_line_num"),
                              test_func_name=json_obj.get("test_func_name"))


# 'pylint: disable=too-few-public-methods
class Constant:
    """
    This class for Constant.
    """
    STAGE_COMPILE = "ut_compile"
    STAGE_RUN = "ut_run_on_model"
    STAGE_COMPARE_PRECISION = "ut_compare_precision"
    STAGE_CUST_FUNC = "ut_cust_func"


class OpUTStageResult:
    """
    op ut run stage result info
    """

    def __init__(self, status, stage_name=None, result=None,  # 'pylint: disable=too-many-arguments
                 err_msg=None, err_trace=None):
        self.status = status
        self.result = result
        self.err_msg = err_msg
        self.err_trace = err_trace
        self.stage_name = stage_name

    def is_success(self):
        """
        check stage status is success
        :return: True or False
        """
        return self.status == op_status.SUCCESS

    def to_json_obj(self):
        """
        convert to json object
        :return: json object
        """
        return {
            "status": self.status,
            "result": self.result,
            "err_msg": self.err_msg,
            "stage_name": self.stage_name,
            "err_trace": self.err_trace
        }

    @staticmethod
    def parser_json_obj(json_obj):
        """
        convert json object to OpUTStageResult object
        :param json_obj: json object
        :return: OpUTStageResult object
        """
        return OpUTStageResult(json_obj["status"], json_obj["stage_name"], json_obj["result"], json_obj["err_msg"],
                               json_obj["err_trace"])


class OpUTCaseTrace:
    """
    op ut case run trace
    """

    def __init__(self, soc_version, ut_case_info: OpUTBaseCase):
        self.ut_case_info = ut_case_info
        self.stage_result = []
        self.run_soc = soc_version

    def add_stage_result(self, stage_res: OpUTStageResult):
        """
        add a stage result into trace
        :param stage_res: stage result
        :return: None
        """
        self.stage_result.append(stage_res)

    def to_json_obj(self):
        """
        convert to json object
        :return: json object
        """
        return {
            "run_soc": self.run_soc,
            "ut_case_info": self.ut_case_info.to_json_obj(),
            "stage_result": [stage_obj.to_json_obj() for stage_obj in self.stage_result],
        }

    @staticmethod
    def parser_json_obj(json_obj):
        """
        convert json object to OpUTCaseTrace object
        :param json_obj: json object
        :return: OpUTCaseTrace object
        """
        if not json_obj:
            return None
        res = OpUTCaseTrace(json_obj["run_soc"], OpUTBaseCase.parser_json_obj(json_obj["ut_case_info"]))
        res.stage_result = [OpUTStageResult.parser_json_obj(stage_obj) for stage_obj in json_obj["stage_result"]]
        return res
