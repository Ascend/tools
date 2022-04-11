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
the op ut test main class: OpUT, BroadcaseOpUT, ElementwiseOpUT, ReduceOpUT
"""
import os
import sys
import ast
import stat
import json
import inspect
import traceback
from enum import Enum
from typing import List
from typing import Dict
from typing import Any
from typing import Union

import numpy as np

from ms_interface.single_op_test_frame.config import llt_config
from ms_interface.single_op_test_frame.common import logger
from ms_interface.single_op_test_frame.common import op_status
from ms_interface.single_op_test_frame.common import precision_info
from ms_interface.single_op_test_frame.common import data_generator
from ms_interface.single_op_test_frame.utils import shape_utils
from ms_interface.single_op_test_frame.utils import precision_compare_util
from ms_interface.single_op_test_frame.utils import op_param_util
from ms_interface.single_op_test_frame.utils import file_util
from ms_interface.single_op_test_frame.ut import op_ut_case_info
from ms_interface.single_op_test_frame.ut import ut_report
from ms_interface.single_op_test_frame.common.ascend_tbe_op import AscendOpKernel
from ms_interface.single_op_test_frame.common.ascend_tbe_op import AscendOpKernelRunner


# 'pylint: disable=too-many-lines,too-many-branches,too-many-locals,invalid-name,no-self-use
class OpFuncType(Enum):
    """
    Op Func Type Enum, contains INTF_FUNC, SELECT_FORMAT_FUNC, CHECK_SUPPORT_TYPE
    """
    INTF_FUNC = "INTF_FUNC"
    SELECT_FORMAT_FUNC = "SELECT_FORMAT_FUNC"
    CHECK_SUPPORT_TYPE = "CHECK_SUPPORT_TYPE"


class OpImplyType(Enum):
    """
    op imply type Enum, contains STATIC_SHAPE, DYNAMIC_SHAPE
    """
    PRE_STATIC = "pre_static"
    STATIC = "static"
    DYNAMIC = "dynamic"


class FuncCache:
    """
    op func cache object struct, contains: status, func_type, func, err_msg
    """

    def __init__(self, status, func_type, func, err_msg=None):
        self.status = status
        self.func_type = func_type
        self.func = func
        self.err_msg = err_msg

    def get_status(self):
        """
        :return: self.status
        """
        return self.status

    def get_func_type(self):
        """
        :return: self.func_type
        """
        return self.func_type

    def get_func(self):
        """
        :return: self.func
        """
        return self.func

    def get_err_msg(self):
        """
        :return: self.err_msg
        """
        return self.err_msg


# 'pylint: disable=too-few-public-methods
class Constant:
    """
    This class for Constant.
    """
    DATA_FILE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    DATA_FILE_MODES = stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP
    DATA_DIR_MODES = stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP


def get_trace_info() -> str:
    """
    get exception trace info
    :return: exception trace info str
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    trace_info = traceback.format_exception(exc_type, exc_value, exc_traceback)
    if not trace_info:
        return "None exception."
    return "".join(trace_info)


class OpUT:  # 'pylint: disable=too-many-instance-attributes
    """
        OpUT
        example:
        from ms_interface.single_op_test_frame import OpUT
        ut_case = OpUT("Add", "impl.add", "add")
        ut_case.add_precision_case(...)

        if __name__ == "__main__":
            ut_case.run("Ascend910", simulator_mode="pv", simulator_lib_path="xxx")
    """
    _case_info_map: Dict[str, Union[op_ut_case_info.OpUTCase, op_ut_case_info.OpUTCustomCase]]
    KERNEL_DIR = os.path.realpath("./kernel_meta")
    SOC_VERSION_STR = "SOC_VERSION"

    def __init__(self, op_type, op_module_name=None, op_func_name=None):

        self.op_type = op_type

        def _default_lower_op_type():
            lower_name = ""
            for ele in str(self.op_type):
                if ele.isupper():
                    lower_name += "_" + ele
                else:
                    lower_name += ele
            if lower_name.startswith("_"):
                lower_name = lower_name[1:]
                lower_name = lower_name.lower()
            return lower_name

        if not op_module_name:
            self.op_module_name = "impl." + _default_lower_op_type()
        else:
            self.op_module_name = op_module_name
        if ".dynamic." in self.op_module_name:
            self.imply_type = OpImplyType.DYNAMIC
        else:
            self.imply_type = OpImplyType.STATIC
        if not op_func_name:
            self.op_func_name = _default_lower_op_type()
        else:
            self.op_func_name = op_func_name

        self._select_format_func_name = llt_config.LLTConf.op_select_format_name
        self._check_support_func_name = llt_config.LLTConf.check_support_func_name
        self._auto_gen_case_name_count = 0
        # key: case_name, value: case_info: OpUTCase
        self._case_info_map = {}
        caller = inspect.stack()[1]
        self.case_file = caller.filename

    def add_test_cfg_cov_case(self, cfg_path_root=None):
        """
        Use less
        """
        if cfg_path_root is None:
            logger.log_err("add_test_cfg_cov_case but cfg_path_root is none.")
            return
        print("Op Type: %s, not support test cfg_cov_case now." % self.op_type)

    def _build_op_ut_case_info(self, support_soc, case,
                               case_usage: op_ut_case_info.CaseUsage = op_ut_case_info.CaseUsage.IMPL,
                               case_line_num=None) -> op_ut_case_info.OpUTCase:
        if "params" not in case.keys():
            raise RuntimeError("Not has params info in case")\
        
        if case.get("op_imply_type"):
            op_imply_type = case.get("op_imply_type")
        else:
            op_imply_type = self.imply_type.value

        case_name = case.get("case_name")
        if not case_name:
            self._auto_gen_case_name_count += 1
            case_name = "test_%s_auto_case_name_%d" % (self.op_type, self._auto_gen_case_name_count)
        case_name = "_".join([self.op_type, str(op_imply_type), case_name])
        # case_name duplicated, auto change name to xxx__1, xxx__2
        if case_name in self._case_info_map.keys():
            idx = 1
            while idx < 5000:
                tmp_name = "".join([case_name, "__%d" % idx])
                idx += 1
                if tmp_name not in self._case_info_map.keys():
                    case_name = tmp_name
                    break

        expect = case.get("expect")
        if not expect:
            expect = op_status.SUCCESS

        precision_standard = case.get("precision_standard")
        if precision_standard and not isinstance(precision_standard, precision_info.PrecisionStandard):
            raise RuntimeError("precision_standard is not ms_interface.single_op_test_frame.common.precision.PrecisionStandard type")

        return op_ut_case_info.OpUTCase(support_soc=support_soc,
                                        op_type=self.op_type,
                                        case_name=case_name,
                                        op_params=case.get("params"),
                                        expect=expect,
                                        case_usage=case_usage,
                                        expect_out_fn=case.get("calc_expect_func"),
                                        case_file=self.case_file,
                                        case_line_num=case_line_num,
                                        precision_standard=precision_standard,
                                        op_imply_type=op_imply_type,
                                        addition_params=case.get("addition_params", None),
                                        bin_path=case.get("bin_path", None))

    def add_case(self, support_soc=None, case=None):
        """
        add a only test op compile case
        :param support_soc: this case can test soc list
        :param case: case info, this is a dict.
        :return: None
        """
        if not support_soc:
            support_soc = ("all",)

        if not isinstance(support_soc, (tuple, list)):
            support_soc = (support_soc,)

        case_line_num = "unknown"
        for stack in inspect.stack():
            if not stack.filename.endswith("op_ut.py"):
                case_line_num = stack.lineno
                break

        case_info = self._build_op_ut_case_info(support_soc, case, case_line_num=case_line_num)
        self._case_info_map[case_info.case_name] = case_info

    @staticmethod
    def _gen_input_data(param_info):
        def _deal_data_path():
            input_data_path = param_info.get("data_path")
            if not isinstance(input_data_path, str):
                raise TypeError("data_path is not a str, please check your case param.")
            input_data_path = os.path.realpath(input_data_path)
            if not os.path.exists(input_data_path):
                raise IOError("data_path is not exist, please check your case param, data_path: %s" % input_data_path)
            data_type = str(param_info.get("dtype")).strip()
            data_from_file = np.fromfile(input_data_path, data_type)
            data_from_file_size = len(data_from_file)
            param_shape = param_info.get("run_shape")
            if param_shape is None:
                param_shape = param_info.get("shape")
            param_shape_size = shape_utils.calc_shape_size(param_shape)
            if data_from_file_size < param_shape_size:
                raise RuntimeError("Input data file size(%s) is len than shape size(%s), dtype is %s. " % (
                    data_from_file_size, param_shape_size, data_type))
            param_info["value"] = data_from_file[:param_shape_size].reshape(param_shape)

        def _deal_no_param_data_path():
            if "value" in param_info.keys():
                return
            distribution = param_info.get("distribution", "uniform")
            value_range = param_info.get("value_range", [0.1, 1])
            # if dynamic shape use run_shape, if static shape use shape
            shape = param_info.get("run_shape")
            if shape is None:
                shape = param_info.get("shape")
            dtype = param_info.get("dtype")
            data = data_generator.gen_data(data_shape=shape,
                                           min_value=value_range[0],
                                           max_value=value_range[1],
                                           dtype=dtype,
                                           distribution=distribution)
            param_info["value"] = data

        if "data_path" in param_info.keys():
            _deal_data_path()
        else:
            _deal_no_param_data_path()

    @staticmethod
    def _get_param_type(one_param):
        if not one_param:
            return None
        if isinstance(one_param, (tuple, list)):
            if not one_param or not isinstance(one_param[0], dict):
                return None
            return one_param[0].get("param_type", None)
        if isinstance(one_param, dict):
            return one_param.get("param_type")
        return None

    @staticmethod
    def _get_input_outputs(param_list: List):
        def _add_to_params(params: List, one_param):
            if isinstance(one_param, list):
                for sub_param in one_param:
                    params.append(sub_param)
            else:
                params.append(one_param)

        input_list = []
        output_list = []
        for arg in param_list:
            param_type = OpUT._get_param_type(arg)
            if param_type == "input":
                _add_to_params(input_list, arg)
            if param_type == "output":
                _add_to_params(output_list, arg)
        return input_list, output_list

    @staticmethod
    def _get_outputs(param_list: List):
        def _add_to_params(params: List, one_param):
            if isinstance(one_param, list):
                for sub_param in one_param:
                    params.append(sub_param)
            else:
                params.append(one_param)

        output_list = []
        for arg in param_list:
            param_type = OpUT._get_param_type(arg)
            if param_type == "output":
                _add_to_params(output_list, arg)
        return output_list

    def _build_data_file(self, file_name, run_soc_version, run_cfg: Dict = None):
        if run_cfg:
            data_root_dir = run_cfg.get("data_dump_path", "./data")
        else:
            data_root_dir = "./data"
        data_dir = os.path.join(data_root_dir, self.op_type, run_soc_version)
        data_dir = os.path.realpath(data_dir)
        if not os.path.exists(data_dir):
            file_util.makedirs(data_dir, mode=Constant.DATA_DIR_MODES)
        data_path = os.path.join(data_dir, file_name)
        if not os.path.exists(data_path):
            # create output data file with mode
            with os.fdopen(os.open(data_path, Constant.DATA_FILE_FLAGS, Constant.DATA_FILE_MODES), 'w') as fout:
                fout.write("")
        return data_path

    def _save_data(self, run_soc_version, case_info: op_ut_case_info.OpUTCase, run_cfg: Dict = None):

        def _save_input_data(one_param, idx):
            input_data_file_name = "%s_input%s.bin" % (case_info.case_name, str(idx))
            input_data_path = self._build_data_file(input_data_file_name, run_soc_version, run_cfg)
            one_param["data_path"] = input_data_path
            one_param["value"].tofile(input_data_path)

        def _save_output_data(one_param, idx):
            output_data_file_name = "%s_output%s.bin" % (case_info.case_name, str(idx))
            expect_output_data_file_name = "%s_expect_output%s.bin" % (case_info.case_name, str(idx))
            output_data_path = self._build_data_file(output_data_file_name, run_soc_version, run_cfg)
            expect_output_data_path = self._build_data_file(expect_output_data_file_name, run_soc_version, run_cfg)
            one_param["data_path"] = output_data_path
            one_param["expect_data_path"] = expect_output_data_path
            one_param["value"].tofile(output_data_path)
            one_param["expect_value"].tofile(expect_output_data_path)

        input_idx = 0
        output_idx = 0
        for arg in case_info.op_params:
            param_type = OpUT._get_param_type(arg)
            if param_type == "input":
                if isinstance(arg, list):
                    for sub_param in arg:
                        _save_input_data(sub_param, input_idx)
                        input_idx += 1
                else:
                    _save_input_data(arg, input_idx)
                    input_idx += 1
            if param_type == "output":
                if isinstance(arg, list):
                    for sub_param in arg:
                        _save_output_data(sub_param, output_idx)
                        output_idx += 1
                else:
                    _save_output_data(arg, output_idx)
                    output_idx += 1

    def add_precision_case(self, support_soc=None, case=None):
        """
        add a test op compile and precision case
        :param support_soc: support soc list
        :param case: case info
        :return: None
        """
        if not support_soc:
            support_soc = ("all",)
        if not isinstance(support_soc, (tuple, list)):
            support_soc = (support_soc,)
        case_line_num = "unknown"
        for stack in inspect.stack():
            if not stack.filename.endswith("op_ut.py"):
                case_line_num = stack.lineno
                break

        case_info = self._build_op_ut_case_info(support_soc, case,
                                                op_ut_case_info.CaseUsage.PRECISION,
                                                case_line_num=case_line_num)
        self._case_info_map[case_info.case_name] = case_info

    def add_direct_case(self, case=None):
        """
        add a test onboard case
        :param case: case info
        :return: None
        """
        support_soc = ("all",)
        case_line_num = "unknown"
        for stack in inspect.stack():
            if not stack.filename.endswith("op_ut.py"):
                case_line_num = stack.lineno
                break
        case_info = self._build_op_ut_case_info(support_soc, case,
                                                op_ut_case_info.CaseUsage.DIRECT,
                                                case_line_num=case_line_num)
        self._case_info_map[case_info.case_name] = case_info

    def _build_custom_test_case(self, support_soc, test_func, case_line_no):
        case_name = test_func.__name__
        if case_name in self._case_info_map.keys():
            idx = 1
            while idx < 5000:
                tmp_name = "".join([case_name, "__%d" % idx])
                idx += 1
                if tmp_name not in self._case_info_map.keys():
                    case_name = tmp_name
                    break
        return op_ut_case_info.OpUTCustomCase(support_soc=support_soc,
                                              op_type=self.op_type,
                                              case_name=case_name,
                                              case_usage=op_ut_case_info.CaseUsage.CUSTOM,
                                              case_file=self.case_file,
                                              case_line_num=case_line_no,
                                              test_func_name=test_func.__name__,
                                              test_func=test_func)

    def add_cust_test_func(self, support_soc=None, test_func=None):
        """
        add a custom test func
        :param support_soc: support soc version
        :param test_func: should be a func
        :return: None
        """
        if not test_func:
            raise RuntimeError("add_cust_test_func failed, test func is None")
        if not hasattr(test_func, "__call__"):
            raise RuntimeError("add_cust_test_func failed, test func is not a function.")
        if not support_soc:
            support_soc = ("all",)

        if not isinstance(support_soc, (tuple, list)):
            support_soc = (support_soc,)

        case_line_num = "unknown"
        for stack in inspect.stack():
            if not stack.filename.endswith("op_ut.py"):
                case_line_num = stack.lineno
        case_info = self._build_custom_test_case(support_soc, test_func, case_line_num)
        self._case_info_map[case_info.case_name] = case_info

    def get_all_test_case_name(self, soc=None) -> List:
        """
        get all test case name
        :param soc: soc version, if None get all test case, if not none get support this soc's test case
        :return: test case info list
        """
        soc_list = None
        if isinstance(soc, str):
            if "," in soc:
                soc_list = [soc_str.strip() for soc_str in str(soc).split(",")]
            else:
                soc_list = [soc, ]
        if isinstance(soc, (list, tuple)):
            soc_list = soc

        def _check_soc_match(case_support_soc):
            if not soc_list:
                return True
            if "all" in case_support_soc:
                return True
            for one_soc in soc_list:
                if one_soc in case_support_soc:
                    return True
            return False

        case_info_list = []
        for case_name, case_info in self._case_info_map.items():
            if not _check_soc_match(case_info.support_soc):
                continue
            case_obj = {
                "op_type": case_info.op_type,
                "case_name": case_name,
                "case_usage": case_info.case_usage.value,
                "support_soc": case_info.support_soc
            }
            case_info_list.append(case_obj)
        return case_info_list

    def _load_op_func(self):
        try:
            __import__(self.op_module_name)
        except (ImportError, ModuleNotFoundError) as _:
            # custom op and inner op both have parent dir impl，
            # so when python_path contains two impl's parent dir,
            # we need to add either impl dir to python_path
            for dir_item in sys.path:
                impl_dir = os.path.join(dir_item, "impl")
                if os.path.exists(impl_dir):
                    sys.path.append(impl_dir)
            self.op_module_name = self.op_module_name.replace("impl.", "")
            try:
                __import__(self.op_module_name)
            except (ImportError, ModuleNotFoundError) as _:
                err_msg = "Can't import op module, please check you python path"
                err_msg += ", op module name: %s" % self.op_module_name
                err_trace = get_trace_info()
                err_msg += ", err_trace: %s" % err_trace
                return None, err_msg

        op_module = sys.modules[self.op_module_name]
        op_func = getattr(op_module, self.op_func_name)
        if not op_func:
            err_msg = "can't get op function in op module,"
            err_msg += " op module name: %s, op function name: %s" % (self.op_module_name, self.op_func_name)
            return None, err_msg

        return op_func, None

    @staticmethod
    def _check_kernel_so_exist(kernel_meta_dir, kernel_name):
        bin_path = os.path.join(kernel_meta_dir, kernel_name + ".o")
        json_path = os.path.join(kernel_meta_dir, kernel_name + ".json")
        if os.path.exists(bin_path) and os.path.exists(json_path):
            return True
        return False

    @staticmethod
    def _get_kernel_name(run_soc_version: str, case_info: op_ut_case_info.OpUTCase) -> str:
        return "_".join([case_info.case_name, run_soc_version.lower()])

    @staticmethod
    def _get_compile_info_file_name(kernel_name):
        return kernel_name + "_compile_info.json"

    def _save_compile_info_json(self, kernel_name: str, compile_info: Any):
        compile_info_save_path = os.path.join(self.KERNEL_DIR, self._get_compile_info_file_name(kernel_name))
        if not os.path.exists(compile_info_save_path):
            with os.fdopen(os.open(compile_info_save_path,
                                   Constant.DATA_FILE_FLAGS, Constant.DATA_FILE_MODES), 'w') as fout:
                fout.write("")

        if isinstance(compile_info, str):
            compile_info_str = compile_info
        else:
            compile_info_str = json.dumps(compile_info, indent=4)
        with open(compile_info_save_path, "w") as info_f:
            info_f.write(compile_info_str)

    def _get_compile_info(self, kernel_name):
        compile_info_save_path = os.path.join(self.KERNEL_DIR, self._get_compile_info_file_name(kernel_name))
        with open(compile_info_save_path) as info_f:
            compile_info_str = info_f.read()
        return json.loads(compile_info_str)

    def _call_op_func(self, run_soc_version: str, op_func, case_info: op_ut_case_info.OpUTCase, check_exist=False):
        kernel_name = self._get_kernel_name(run_soc_version, case_info)
        if not case_info.addition_params:
            addition_params = {"kernel_name": kernel_name}
        else:
            addition_params = case_info.addition_params
            addition_params["kernel_name"] = kernel_name

        call_op_success = True
        err_msg = None
        try:
            # there is a bug in te, we can't import te before tensorflow, so can't import te outside
            import tbe  # 'pylint: disable=import-outside-toplevel
            import tbe.common.context.op_info as operator_info  # 'pylint: disable=import-outside-toplevel
            if case_info.op_imply_type == OpImplyType.DYNAMIC.value:
                with tbe.common.context.op_context.OpContext("dynamic"):
                    op_info = operator_info.OpInfo(self.op_type, self.op_type)
                    tbe.common.context.op_context.get_context().add_op_info(op_info)
                    # op_func(*case_info.op_params, **addition_params)
                    compile_info = tbe.common.context.get_context().get_compile_info()
                    self._save_compile_info_json(kernel_name=kernel_name, compile_info=compile_info)
            elif case_info.op_imply_type == OpImplyType.STATIC.value:
                with tbe.common.context.op_context.OpContext("static"):
                    op_info = operator_info.OpInfo(self.op_type, self.op_type)
                    op_info.inputs, op_info.outputs = self._build_tiling_args(case_info.op_params)
                    op_info.extra_params = case_info.addition_params
                    tbe.common.context.op_context.get_context().add_op_info(op_info)
                    op_func(*case_info.op_params, **addition_params)
                    compile_info = tbe.common.context.get_context().get_compile_info()
                    self._save_compile_info_json(kernel_name=kernel_name, compile_info=compile_info)
            elif case_info.op_imply_type == OpImplyType.PRE_STATIC.value:
                import tbe # 'pylint: disable=import-outside-toplevel
                if not case_info.bin_path:
                    with tbe.common.context.op_context.OpContext("pre-static"):
                        op_func(*case_info.op_params, **addition_params)
        except BaseException as run_err:  # 'pylint: disable=broad-except
            if case_info.expect != op_status.SUCCESS:
                if case_info.expect != op_status.FAILED and not isinstance(run_err, case_info.expect):
                    call_op_success = False
                    err_msg = "Call op func failed, exception class not match, expect: %s, actual: %s" % (
                        case_info.expect.__name__, run_err.__class__.__name__)
            else:
                call_op_success = False
                err_trace = get_trace_info()
                err_msg = "Call op func failed, err_trace: %s" % err_trace

        if case_info.expect == op_status.SUCCESS and call_op_success and not case_info.bin_path:
            if check_exist and not self._check_kernel_so_exist(self.KERNEL_DIR, kernel_name):
                call_op_success = False
                err_msg = "Call op func success, but no .o and .json generated."

        return call_op_success, err_msg

    def _compile_op_kernel(self, run_soc_version, case_info: op_ut_case_info.OpUTCase, check_exist=False):
        op_func, load_err_msg = self._load_op_func()
        if not op_func:
            return False, load_err_msg
        call_success, err_msg = self._call_op_func(run_soc_version=run_soc_version,
                                                   op_func=op_func,
                                                   case_info=case_info,
                                                   check_exist=check_exist)
        return call_success, err_msg

    def _run_compile_stage(self, run_soc_version,
                           case_info: op_ut_case_info.OpUTCase,
                           check_exist=False) -> op_ut_case_info.OpUTStageResult:
        compile_success, compile_err_msg = self._compile_op_kernel(run_soc_version,
                                                                   case_info=case_info,
                                                                   check_exist=check_exist)
        if not compile_success:
            stage_status = op_ut_case_info.OpUTStageResult(status=op_status.FAILED,
                                                           stage_name=op_ut_case_info.Constant.STAGE_COMPILE,
                                                           err_msg="Failed",
                                                           err_trace=compile_err_msg)
        else:
            stage_status = op_ut_case_info.OpUTStageResult(status=op_status.SUCCESS,
                                                           stage_name=op_ut_case_info.Constant.STAGE_COMPILE)
        return stage_status

    def _run_compile_case(self, run_soc_version,
                          case_info: op_ut_case_info.OpUTCase) -> ut_report.OpUTCaseReport:
        case_trace = op_ut_case_info.OpUTCaseTrace(run_soc_version, case_info)
        stage_status = self._run_compile_stage(run_soc_version, case_info)
        case_trace.add_stage_result(stage_status)
        return ut_report.OpUTCaseReport(case_trace)

    @staticmethod
    def _get_simulator_mode(run_cfg):
        if not run_cfg or not isinstance(run_cfg, dict):
            return None
        return run_cfg.get("simulator_mode")

    @staticmethod
    def _get_simulator_lib_path(run_cfg):
        if not run_cfg or not isinstance(run_cfg, dict):
            return None
        return run_cfg.get("simulator_lib_path", None)

    def _get_simulator_dump_path(self, simulator_mode, case_name, run_cfg):
        base_dir = "./model"
        if isinstance(run_cfg, dict):
            base_dir = run_cfg.get("simulator_dump_path", "./model")
        if simulator_mode:
            model_data_path = os.path.join(os.path.realpath(base_dir), simulator_mode, self.op_type, case_name)
        else:
            model_data_path = os.path.join(os.path.realpath(base_dir), self.op_type, case_name)
        if not os.path.exists(model_data_path):
            file_util.makedirs(model_data_path, Constant.DATA_DIR_MODES)
        return model_data_path

    def _do_tiling(self, run_soc_version: str, case_info: op_ut_case_info.OpUTCase,
                   input_info_list: List, output_info_list: List):
        from tbe.common.utils import op_tiling # 'pylint: disable=import-outside-toplevel
        kernel_name = self._get_kernel_name(run_soc_version, case_info)
        compile_info = self._get_compile_info(kernel_name)
        tiling_info = op_tiling.do_op_tiling(self.op_type, compile_info=compile_info,
                                             inputs=input_info_list, outputs=output_info_list)
        return tiling_info.get("block_dim"), tiling_info.get("tiling_data")

    @staticmethod
    def _get_op_param_desc_info(op_func):
        param_desc_list = []
        param_name_list = []

        def visit_function_def(node: ast.FunctionDef):
            for d in node.decorator_list:
                if isinstance(d, ast.Call):
                    name = d.func.attr if isinstance(d.func, ast.Attribute) else d.func.id
                else:
                    name = d.attr if isinstance(d, ast.Attribute) else d.id
                if name == "check_op_params":
                    for param in d.args:
                        param_desc_list.append(param.attr)
            for p in node.args.args:
                param_name_list.append(p.arg)

        node_iter = ast.NodeVisitor()
        node_iter.visit_FunctionDef = visit_function_def
        node_iter.visit(ast.parse(inspect.getsource(op_func)))

        return param_desc_list, param_name_list

    def _check_and_fix_param_desc(self, param_desc_list, op_params):

        def _check_input(param_idx, op_param_desc: str):
            if len(op_params) <= param_idx:
                raise RuntimeError("Op params in testcase not match the op interface check_op_params decorator.")
            if op_param_desc.lower().startswith("required") and (
                    not op_params[param_idx] or not isinstance(op_params[param_idx], dict)):
                raise RuntimeError("Op params in testcase not match the op interface check_op_params decorator.")
            if op_param_desc.lower().startswith("option") and not (
                    op_params[param_idx] is None or isinstance(op_params[param_idx], dict)):
                raise RuntimeError("Op params in testcase not match the op interface check_op_params decorator.")
            if op_param_desc.lower().startswith("dynamic") and not isinstance(op_params[param_idx], (tuple, list)):
                raise RuntimeError("Op params in testcase not match the op interface check_op_params decorator.")

        if param_desc_list:
            for idx, param_desc in enumerate(param_desc_list):
                if param_desc.lower().endswith("input") or param_desc.lower().endswith("output"):
                    _check_input(idx, param_desc)
        else:
            param_desc_list = []
            for idx, op_param in enumerate(op_params):
                if op_param:
                    if isinstance(op_param, dict) and op_param.get("param_type") == "input":
                        param_desc_list.append("REQUIRED_INPUT")
                    if isinstance(op_param, (tuple, list)) and op_param[0].get("param_type") == "input":
                        param_desc_list.append("DYNAMIC_INPUT")
                    if isinstance(op_param, dict) and op_param.get("param_type") == "output":
                        param_desc_list.append("REQUIRED_OUTPUT")
                    if isinstance(op_param, (tuple, list)) and op_param[0].get("param_type") == "output":
                        param_desc_list.append("DYNAMIC_OUTPUT")
                else:
                    if idx == 0:
                        param_desc_list.append("OPTION_INPUT")
                    else:
                        if isinstance(op_params[idx - 1], dict) and op_params[idx - 1].get("param_type") == "input":
                            param_desc_list.append("OPTION_INPUT")
                        else:
                            param_desc_list.append("OPTION_OUTPUT")
        return param_desc_list

    def _build_tiling_args(self, op_params):

        def _add_to_list(param, param_name, param_list):
            if isinstance(param, (tuple, list)):
                dynamic_params = []
                for one in param:
                    dynamic_param = {
                        "shape": one.get("run_shape"),
                        "dtype": one.get("dtype"),
                    }
                    if one.get("value_need_in_tiling"):
                        name = one.get("name")
                        param_name = name if name else param_name
                        dynamic_param["name"] = param_name
                        dynamic_param["const_value"] = one.get("value").tolist()
                    dynamic_params.append(dynamic_param)
                param_list.append(dynamic_params)
            elif isinstance(param, dict):
                one_param = {
                    "shape": param.get("run_shape"),
                    "dtype": param.get("dtype"),
                }
                if param.get("value_need_in_tiling"):
                    name = param.get("name")
                    param_name = name if name else param_name
                    one_param["name"] = param_name
                    one_param["const_value"] = param.get("value").tolist()
                param_list.append(one_param)

        input_list = []
        output_list = []
        op_func, _ = self._load_op_func()
        param_desc_list, param_name_list = self._get_op_param_desc_info(op_func)
        param_desc_list = self._check_and_fix_param_desc(param_desc_list, op_params)
        if len(param_name_list) < len(param_desc_list):
            raise RuntimeError("Op params in testcase not match the op interface check_op_params decorator.")
        for idx, param_desc in enumerate(param_desc_list):
            if param_desc.lower().endswith("input"):
                _add_to_list(op_params[idx], param_name_list[idx], input_list)
            elif param_desc.lower().endswith("output"):
                _add_to_list(op_params[idx], param_name_list[idx], output_list)
        return input_list, output_list

    def _run_kernel(self, run_soc_version: str, case_info: op_ut_case_info.OpUTCase, run_cfg: Dict[str, Any] = None):
        if case_info.bin_path:
            bin_path = case_info.bin_path
            json_path = case_info.bin_path.replace(".o", ".json")
        else:
            bin_path = os.path.join(OpUT.KERNEL_DIR, self._get_kernel_name(run_soc_version, case_info) + ".o")
            json_path = os.path.join(OpUT.KERNEL_DIR, self._get_kernel_name(run_soc_version, case_info) + ".json")
        input_info_list, output_info_list = self._get_input_outputs(case_info.op_params)
        input_data_list = []
        for input_info in input_info_list:
            self._gen_input_data(input_info)
            input_data_list.append(input_info.get("value"))
        op_kernel = AscendOpKernel(bin_path, json_path)
        op_kernel.set_input_info(input_info_list)
        op_kernel.set_output_info(output_info_list)
        simulator_mode = self._get_simulator_mode(run_cfg)
        simulator_dump_path = self._get_simulator_dump_path(simulator_mode, case_info.case_name, run_cfg)
        with AscendOpKernelRunner(simulator_mode=simulator_mode,
                                  soc_version=run_soc_version,
                                  simulator_lib_path=self._get_simulator_lib_path(run_cfg),
                                  simulator_dump_path=simulator_dump_path) as runner:
            if self.imply_type.value == OpImplyType.DYNAMIC.value or  self.imply_type.value == OpImplyType.STATIC.value:                
                output_data_list = runner.run(op_kernel, inputs=input_data_list,
                                              tiling=case_info.tiling_data, block_dim=case_info.block_dim)
            else:
                output_data_list = runner.run(op_kernel, inputs=input_data_list)

            if not isinstance(output_data_list, (tuple, list)):
                output_data_list = [output_data_list, ]
            for output_data in output_data_list:
                if output_data:
                    output_data.sync_from_device()

        for idx, output_info in enumerate(output_info_list):
            output_info["value"] = output_data_list[idx].get_data()

    def _run_model_run_stage(self, run_soc_version, case_info: op_ut_case_info.OpUTCase,
                             run_cfg: Dict[str, Any] = None) -> op_ut_case_info.OpUTStageResult:
        run_success = True
        err_msg = None
        try:
            self._run_kernel(run_soc_version, case_info, run_cfg)
        except BaseException as _:  # 'pylint: disable=broad-except
            run_success = False
            err_msg = get_trace_info()
        stage_status = op_ut_case_info.OpUTStageResult(status=op_status.SUCCESS if run_success else op_status.FAILED,
                                                       stage_name=op_ut_case_info.Constant.STAGE_RUN,
                                                       err_msg="Failed" if not run_success else None,
                                                       err_trace=err_msg)
        return stage_status

    def _gen_expect_data(self, case_info: op_ut_case_info.OpUTCase):
        addition_params = {}
        if case_info.addition_params:
            addition_params = case_info.addition_params
        try:
            output_tensors = case_info.expect_out_fn(*case_info.op_params, **addition_params)
        except BaseException as _:  # 'pylint: disable=broad-except
            err_trace = get_trace_info()
            return False, err_trace

        if not isinstance(output_tensors, (list, tuple)):
            output_tensors = [output_tensors, ]

        output_list = self._get_outputs(case_info.op_params)
        if len(output_list) != len(output_tensors):
            err_msg = "calc_expect_func's return tensor count(%d) not equal output dict count(%d)." % (
                len(output_tensors), len(output_list))
            return False, err_msg

        for idx, out_param in enumerate(output_list):
            out_param["expect_value"] = output_tensors[idx]

        return True, None

    def _run_gen_expect_stage(self, case_info: op_ut_case_info.OpUTCase) -> op_ut_case_info.OpUTStageResult:
        try:
            gen_success, err_msg = self._gen_expect_data(case_info)
        except BaseException as _:  # 'pylint: disable=broad-except
            gen_success = False
            err_msg = get_trace_info()
        stage_status = op_ut_case_info.OpUTStageResult(status=op_status.SUCCESS if gen_success else op_status.FAILED,
                                                       stage_name=op_ut_case_info.Constant.STAGE_RUN,
                                                       err_msg="Failed" if not gen_success else None,
                                                       err_trace=err_msg)
        return stage_status

    def _compare_output(self, case_info: op_ut_case_info.OpUTCase):
        output_list = self._get_outputs(case_info.op_params)
        err_msg = ""
        compare_success = True
        for idx, output in enumerate(output_list):
            expect_tensor = output.get("expect_value")
            actual_tensor = output.get("value")
            if expect_tensor.shape != actual_tensor.shape:
                compare_success = False
                err_msg += "output %d 's shape is not same, expect: [%s], actual: [%s]\n" % (
                    idx, ",".join([str(x) for x in expect_tensor.shape]),
                    ",".join([str(x) for x in actual_tensor.shape]))
                continue
            cmp_res = precision_compare_util.compare_precision(output.get("value"),
                                                               output.get("expect_value"),
                                                               precision_standard=case_info.precision_standard)
            if cmp_res.status != op_status.SUCCESS:
                compare_success = False
                err_msg += "output %d precision compare failed, detail msg: %s" % (idx, cmp_res.err_msg)
        return compare_success, err_msg

    def _run_data_compare_stage(self, case_info: op_ut_case_info.OpUTCase):
        compare_success, err_msg = self._compare_output(case_info)
        stage_status = op_ut_case_info.OpUTStageResult(
            status=op_status.SUCCESS if compare_success else op_status.FAILED,
            stage_name=op_ut_case_info.Constant.STAGE_COMPARE_PRECISION,
            err_msg=err_msg)
        return stage_status

    @staticmethod
    def _check_need_run_expect(run_args):
        if not run_args:
            return True

        simulator_mode = run_args.get("simulator_mode")
        return simulator_mode != "tm"

    def _run_precision_case(self, run_soc_version, case_info: op_ut_case_info.OpUTCase,
                            run_cfg: Dict[str, Any] = None) -> ut_report.OpUTCaseReport:
        case_trace = op_ut_case_info.OpUTCaseTrace(run_soc_version, case_info)
        compile_stage_status = self._run_compile_stage(run_soc_version, case_info, check_exist=True)
        case_trace.add_stage_result(compile_stage_status)
        if compile_stage_status.status != op_status.SUCCESS:
            return ut_report.OpUTCaseReport(case_trace)

        run_stage_status = self._run_model_run_stage(run_soc_version, case_info, run_cfg)
        case_trace.add_stage_result(run_stage_status)
        if run_stage_status.status != op_status.SUCCESS or not self._check_need_run_expect(run_cfg):
            return ut_report.OpUTCaseReport(case_trace)

        gen_expect_stage_status = self._run_gen_expect_stage(case_info)
        case_trace.add_stage_result(gen_expect_stage_status)
        if gen_expect_stage_status.status != op_status.SUCCESS:
            return ut_report.OpUTCaseReport(case_trace)

        compare_stage_status = self._run_data_compare_stage(case_info)
        case_trace.add_stage_result(compare_stage_status)
        self._save_data(run_soc_version, case_info, run_cfg)
        return ut_report.OpUTCaseReport(case_trace)

    def _run_direct_case(self, run_soc_version, case_info: op_ut_case_info.OpUTCase,
                         run_cfg: Dict[str, Any] = None) -> ut_report.OpUTCaseReport:
        """
        run onboard case
        """
        case_trace = op_ut_case_info.OpUTCaseTrace(run_soc_version, case_info)
        run_stage_status = self._run_model_run_stage(run_soc_version, case_info, run_cfg)
        case_trace.add_stage_result(run_stage_status)
        if run_stage_status.status != op_status.SUCCESS or not self._check_need_run_expect(run_cfg):
            return ut_report.OpUTCaseReport(case_trace)
        return ut_report.OpUTCaseReport(case_trace)

    @staticmethod
    def _run_custom_case(run_soc_version: str,
                         case_info: op_ut_case_info.OpUTCustomCase) -> ut_report.OpUTCaseReport:
        run_success = True
        err_trace = None
        try:
            import tbe # 'pylint: disable=import-outside-toplevel
            with tbe.common.context.op_context.OpContext("pre-static"):
                case_info.test_func(run_soc_version)
        except BaseException as _:  # 'pylint: disable=broad-except
            run_success = False
            err_trace = get_trace_info()
        stage_status = op_ut_case_info.OpUTStageResult(
            status=op_status.SUCCESS if run_success else op_status.FAILED,
            stage_name=op_ut_case_info.Constant.STAGE_CUST_FUNC,
            err_msg=None if run_success else "Failed",
            err_trace=err_trace)
        case_trace = op_ut_case_info.OpUTCaseTrace(run_soc_version, case_info)
        case_trace.add_stage_result(stage_status)
        return ut_report.OpUTCaseReport(case_trace)

    def _run_one_case(self, run_soc_version, case_info: op_ut_case_info.OpUTCase,
                      run_cfg: Dict[str, Any] = None) -> ut_report.OpUTCaseReport:
        try:
            case_rpt = None
            if case_info.case_usage == op_ut_case_info.CaseUsage.IMPL:
                case_rpt = self._run_compile_case(run_soc_version, case_info)
            elif case_info.case_usage == op_ut_case_info.CaseUsage.PRECISION:
                case_rpt = self._run_precision_case(run_soc_version, case_info, run_cfg)
            elif case_info.case_usage == op_ut_case_info.CaseUsage.CUSTOM:
                case_rpt = self._run_custom_case(run_soc_version, case_info)
            elif case_info.case_usage == op_ut_case_info.CaseUsage.DIRECT:
                case_rpt = self._run_direct_case(run_soc_version, case_info)
        except BaseException as _:  # 'pylint: disable=broad-except
            err_trace = get_trace_info()
            stage_status = op_ut_case_info.OpUTStageResult(
                status=op_status.ERROR,
                stage_name=op_ut_case_info.Constant.STAGE_CUST_FUNC,
                err_msg="Error",
                err_trace=err_trace)
            case_trace = op_ut_case_info.OpUTCaseTrace(run_soc_version, case_info)
            case_trace.add_stage_result(stage_status)
            case_rpt = ut_report.OpUTCaseReport(case_trace)
        return case_rpt

    @staticmethod
    def _set_run_soc(run_soc_version):
        # there is a bug in te, we can't import te before tensorflow, so can't import te outside
        from te.platform import te_set_version  # 'pylint: disable=import-outside-toplevel
        te_set_version(run_soc_version)

    def run_case(self, one_soc_version: str, case_name_list: List[str] = None,
                 case_usage_list: List = None, run_cfg: Dict[str, Any] = None) -> ut_report.OpUTReport:
        """
        run case

        Parameters
        ----------
        one_soc_version: str
            the soc need to run
        case_name_list: List[str], default is None
            only run the cases which's case name in this list, default None means run all.
        case_usage_list: List, default is None
            only run the cases which's caseusage in this list, default None means run all.
        run_cfg: Dict[str, Any]
            run configuration, like: simulator_mode, simulator_lib_path, simulator_dump_path, data_dump_path

        Returns
        -------
        run_report: ut_report.OpUTReport
            run report
        """
        self._set_run_soc(one_soc_version)
        print("%s test start running..." % self.op_type)
        case_cnt = 0
        success_cnt = 0
        fail_cnt = 0
        err_cnt = 0
        total_rpt = ut_report.OpUTReport()
        for case_name, case_info in self._case_info_map.items():
            if not case_info.check_support_soc(one_soc_version):
                continue
            if case_name_list and not case_name in case_name_list:
                continue
            if case_usage_list and not case_info.case_usage in case_usage_list:
                continue
            print("%s (%s) (%s) ... " % (case_name, self.op_type, case_info.case_usage.value), end="")
            case_cnt += 1
            case_rpt = self._run_one_case(one_soc_version, case_info, run_cfg=run_cfg)
            total_rpt.add_case_report(case_rpt)
            if case_rpt.status == op_status.SUCCESS:
                success_cnt += 1
                print("ok")
            elif case_rpt.status == op_status.FAILED:
                fail_cnt += 1
                print("fail")
            else:
                err_cnt += 1
                print("error")
        print("\n\n----------------------------------")
        summary_msg = "run %d tests, success: %d" % (case_cnt, success_cnt)
        if fail_cnt > 0:
            summary_msg += ", fail: %d" % fail_cnt
        if err_cnt > 0:
            summary_msg += ", error: %d" % err_cnt
        print(summary_msg)
        return total_rpt

    def run(self, soc=["Ascend910A"], case_name=None, simulator_mode=None, simulator_lib_path=None):
        """
        run ut
        :param soc: soc version, one soc or a soc list
        :param case_name: case name, if none will run all test case
        :param simulator_mode: support "pv", "tm"
        :param simulator_lib_path: simulator library path
        :return: None
        """
        if simulator_mode:
            if not simulator_lib_path:
                simulator_lib_path = os.environ.get("SIMULATOR_PATH")
            if not simulator_lib_path:
                raise RuntimeError("Not configured simulator path, when run simulator. "
                                   "Please set simulator_lib_path arg, or set ENV SIMULATOR_PATH")

        run_cfg = {"simulator_mode": simulator_mode,
                   "simulator_lib_path": simulator_lib_path}
          
        if isinstance(soc, str):
            soc_list = [x.strip() for x in soc.split(",")]
        if isinstance(soc, (tuple, list)):
            soc_list = soc
        run_rpt = ut_report.OpUTReport()
        for one_soc in soc_list:
            one_rpt = self.run_case(one_soc, case_name, run_cfg=run_cfg)
            run_rpt.merge_rpt(one_rpt)
        run_rpt.save("ut_report.txt")
        return run_rpt.console_print()


class BroadcastOpUT(OpUT):
    """
    OpUT for broadcast op
    """

    def __init__(self, op_type, op_module_name=None, op_func_name=None):
        super().__init__(op_type, op_module_name, op_func_name)
        caller = inspect.stack()[1]
        self.case_file = caller.filename

    def add_broadcast_case(self, soc, input_1_info, input_2_info,  # 'pylint: disable=too-many-arguments
                           output_info=None, expect=op_status.SUCCESS, case_name=None):
        """
        add a only test op compile case
        :param soc: support soc list
        :param input_1_info: input info, [dtype, shape, format, ori_shape, ori_format]
        :param input_2_info: input info, [dtype, shape, format, ori_shape, ori_format]
        :param output_info: output info, [dtype, shape, format, ori_shape, ori_format]
        :param expect: test case except, default is SUCCESS
        :param case_name: case name, can be none, will auto generate a name
        :return: None
        """
        input_1 = op_param_util.build_op_param(input_1_info)
        input_2 = op_param_util.build_op_param(input_2_info)
        if output_info is None:
            output_param = op_param_util.build_op_param(input_1_info)
            b_shape = op_param_util.broadcast_shape(input_1.get("shape"), input_2.get("shape"))
            output_param["shape"] = b_shape
            b_ori_shape = op_param_util.broadcast_shape(input_1.get("ori_shape"), input_2.get("ori_shape"))
            output_param["ori_shape"] = b_ori_shape
        else:
            output_param = op_param_util.build_op_param(output_info)
        if expect == op_status.SUCCESS:
            self.add_case(soc, {"params": [input_1, input_2, output_param], "case_name": case_name})
        else:
            self.add_case(soc, {"params": [input_1, input_2, output_param], "expect": expect, "case_name": case_name})

    def add_broadcast_case_simple(self, soc, dtypes, shape1, shape2,  # 'pylint: disable=too-many-arguments
                                  expect=op_status.SUCCESS, case_name=None):
        """
        add a only test op compile case
        :param soc: support soc list
        :param dtypes: need test dtypes
        :param shape1: first input's shape
        :param shape2: second input's shape
        :param expect: test case except, default is SUCCESS
        :param case_name: case name, can be none, will auto generate a name
        :return: None
        """
        if not isinstance(dtypes, (tuple, list)):
            dtypes = (dtypes,)
        for dtype in dtypes:
            self.add_broadcast_case(soc, (dtype, shape1, "ND"), (dtype, shape2, "ND"), expect=expect,
                                    case_name=case_name)


class ElementwiseOpUT(OpUT):
    """
    OpUT for elementwise OpUT
    """

    def __init__(self, op_type, op_module_name=None, op_func_name=None):
        super().__init__(op_type, op_module_name, op_func_name)
        caller = inspect.stack()[1]
        self.case_file = caller.filename

    def add_elewise_case(self, soc, param_info, expect=op_status.SUCCESS, case_name=None):
        """
        :param soc: can be "Ascend910", "Ascend310" ..., and "all" means test all soc
        :param param_info:
                [dtype, shape, format, ori_shape, ori_format] or [dtype, shape, format]
                with 5 element like ["float16", [3,4,5,6], "ND", [3,4,5,6], "ND"]
                with 3 element mean ori_format and ori_shape is the same as format and shape
        :return: None
        """
        input_info = op_param_util.build_op_param(param_info)

        # elementwise op's output is the same as input
        self.add_case(soc, {"params": [input_info, input_info], "expect": expect, "case_name": case_name})

    def add_elewise_case_simple(self, soc, dtypes, shape,  # 'pylint: disable=too-many-arguments
                                expect=op_status.SUCCESS, case_name=None):
        """
        add a only test op compile case
        :param soc: support soc list
        :param dtypes: need test dtypes
        :param shape: test shape
        :param expect: test case except, default is SUCCESS
        :param case_name: case name, can be none, will auto generate a name
        :return: None
        """
        if not isinstance(dtypes, (tuple, list)):
            dtypes = (dtypes,)
        for dtype in dtypes:
            self.add_elewise_case(soc, [dtype, shape, "ND"], expect=expect, case_name=case_name)


class ReduceOpUT(OpUT):
    """
    OpUT for reduce op
    """

    def __init__(self, op_type, op_module_name=None, op_func_name=None):
        super().__init__(op_type, op_module_name, op_func_name)
        caller = inspect.stack()[1]
        self.case_file = caller.filename

    @staticmethod
    def _build_reduce_op_param(input_info, axes, keep_dim=False):
        input_param = op_param_util.build_op_param(input_info)
        output_shape = input_info[1][:]
        rank = len(output_shape)
        unique_axes = []
        if not isinstance(axes, (tuple, list)):
            axes = [axes, ]
        for axis in axes:
            if axis < -rank or axis >= rank:
                raise RuntimeError("is not in out of rank, shape is [%s], axes is: [%s]" % (
                    ",".join([str(x) for x in output_shape]), ",".join([str(x) for x in axes])))
            if axis < 0:
                axis += rank
            if axis not in unique_axes:
                unique_axes.append(axis)

        reduce_shape = []
        for idx, dim in enumerate(output_shape):
            if idx in unique_axes:
                if keep_dim:
                    reduce_shape.append(1)
            else:
                reduce_shape.append(dim)
        # elementwise op's output is the same as input
        output_info = op_param_util.build_op_param([input_info[0], reduce_shape, input_info[2]])
        return {"params": [input_param, output_info, axes, keep_dim]}

    def add_reduce_case(self, soc, input_info, axes, keep_dim=False,  # 'pylint: disable=too-many-arguments
                        expect=op_status.SUCCESS, case_name=None):
        """
        add a only test op compile case
        :param soc: support soc list
        :param input_info: input info, [dtype, shape, format, ori_shape, ori_format]
        :param axes: test reduce op's axes's value
        :param keep_dim: test reduce op's attr keep_dim's value
        :param expect: test case except, default is SUCCESS
        :param case_name: case name, can be none, will auto generate a name
        :return: None
        """
        op_params = self._build_reduce_op_param(input_info, axes, keep_dim)
        op_params["expect"] = expect
        op_params["case_name"] = case_name
        self.add_case(soc, op_params)

    def add_reduce_case_simple(self, soc, dtypes, shape, axes, keep_dim=False,  # 'pylint: disable=too-many-arguments
                               expect=op_status.SUCCESS, case_name=None):
        """
        add a only test op compile case
        :param soc: support soc list
        :param dtypes: need test dtypes
        :param shape: test shape
        :param axes: test reduce op's axes's value
        :param keep_dim: test reduce op's attr keep_dim's value
        :param expect: test case except, default is SUCCESS
        :param case_name: case name, can be none, will auto generate a name
        :return: None
        """
        if not isinstance(dtypes, (tuple, list)):
            dtypes = (dtypes,)
        for dtype in dtypes:
            self.add_reduce_case(soc, [dtype, shape, "ND"], axes, keep_dim=keep_dim, expect=expect, case_name=case_name)
