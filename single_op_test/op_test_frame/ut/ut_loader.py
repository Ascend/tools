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
ut load for load ut cases
"""
import os
import sys
import fnmatch
import traceback
import multiprocessing
from typing import List
from multiprocessing import Pool
from op_test_frame.common import logger
from op_test_frame.ut import op_ut_case_info


def _find_all_test_case_file(case_path_list, file_name_pattern):
    case_file_list_inner = []
    for case_path in case_path_list:
        case_path_inner = os.path.realpath(case_path)
        if os.path.isfile(case_path_inner) and case_path not in case_file_list_inner:
            case_file_list_inner.append(case_path)
            continue
        for path, _, file_names in os.walk(case_path_inner):
            for file_name in file_names:
                if fnmatch.fnmatch(file_name, file_name_pattern):
                    test_case_file = os.path.join(path, file_name)
                    if test_case_file not in case_file_list_inner:
                        case_file_list_inner.append(test_case_file)
    return case_file_list_inner


def load_ut_cases(case_dir, file_name_pattern="test_*_impl.py") -> List[op_ut_case_info.UTCaseFileInfo]:
    """
    load ut cases
    :param case_dir: case diretory
    :param file_name_pattern: file name pattern, default: "test_*_impl.py"
    :return: List of UTCaseFileInfo
    """
    test_case_file_list = []
    has_error = False

    if not isinstance(case_dir, (tuple, list)):
        case_dir = [case_dir, ]

    case_file_list = _find_all_test_case_file(case_dir, file_name_pattern)
    logger.log_debug("load_ut_cases, case_file_list: %s" % ",".join(case_file_list))
    if len(case_file_list) > 4:

        cpu_cnt = max(multiprocessing.cpu_count() - 1, 1)
        with Pool(processes=cpu_cnt) as pool:
            all_res = pool.map(_get_op_module_info, case_file_list)
        for res in all_res:
            status, c_f, c_m = res
            if not status:
                has_error = True
            if not c_f or not c_m:
                continue
            test_case_file_list.append(op_ut_case_info.UTCaseFileInfo(c_f, c_m))
    else:
        for case_file in case_file_list:
            status, c_f, c_m = _get_op_module_info(case_file)
            if not status:
                has_error = True
            if not c_f or not c_m:
                continue
            test_case_file_list.append(op_ut_case_info.UTCaseFileInfo(c_f, c_m))
    logger.log_debug("load_ut_cases end, load case files total count: %d" % len(test_case_file_list))
    return test_case_file_list, has_error


def _get_op_module_info(case_file):
    logger.log_debug("_get_op_module_info start, case file: %s" % case_file)
    case_dir = os.path.dirname(case_file)
    case_module_name = os.path.basename(case_file)[:-3]
    sys.path.insert(0, case_dir)
    try:
        __import__(case_module_name)
    except BaseException as import_err:  # 'pylint: disable=broad-except
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace_info = traceback.format_exception(exc_type, exc_value, exc_traceback)
        err_trace_str = "".join(trace_info)
        logger.log_warn("import case file failed,case File \"%s\", error msg: %s, \n trace detail:\n %s"
                        "" % (case_file, import_err.args[0], err_trace_str))

        sys.path.remove(case_dir)
        logger.log_debug("_get_op_module_info end, case file: %s " % case_file)
        return False, None, None

    case_module = sys.modules[case_module_name]
    ut_case = getattr(case_module, "ut_case", None)
    if not ut_case:
        logger.log_warn("Not found ut_case in case_file: %s" % case_file)
        sys.path.remove(case_dir)
        del sys.modules[case_module_name]
        logger.log_debug("_get_op_module_info end, case file: %s " % case_file)
        return True, None, None

    op_module_name = None
    if "op_module_name" in ut_case.__dict__.keys():
        op_module_name = ut_case.op_module_name
    else:
        logger.log_warn("'ut_case' object type is not base on 'OpUT' in case_file: %s" % case_file)

    sys.path.remove(case_dir)
    del sys.modules[case_module_name]
    logger.log_debug("_get_op_module_info end, case file: %s " % case_file)
    return True, case_file, op_module_name
