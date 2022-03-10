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
op ut helper, apply helper function, get case name
"""
import os
import sys
import stat
import json
import multiprocessing
from multiprocessing import Pool
from op_test_frame.ut import ut_loader
from op_test_frame.utils import file_util
from op_test_frame.common import logger



def get_case_name_from_file(params):
    """
    get case name
    :param params: param contains case_file_path and soc_version
    :return: case_file: case_name_list dict
    """
    case_file_path = params.get("case_file_path")
    soc_version = params.get("soc_version")
    try:
        case_dir = os.path.dirname(os.path.realpath(case_file_path))
        case_module_name = os.path.basename(os.path.realpath(case_file_path))[:-3]
        sys.path.insert(0, case_dir)
        __import__(case_module_name)
        case_module = sys.modules[case_module_name]
        ut_case = getattr(case_module, "ut_case", None)
        case_name_list_inner = ut_case.get_all_test_case_name(soc_version)
    except BaseException as run_err:  # 'pylint: disable=broad-except
        logger.log_err("Get case name failed, error msg: %s" % run_err.args[0])
        return None
    return {case_file_path: case_name_list_inner}


def _print_case_name_info(json_obj):
    for key, name_list in json_obj.items():
        print("Case File: %s, Case names as follows" % key)
        for idx, name in enumerate(name_list):
            print("        %d) %s" % (idx, name))


def _save_to_file(info_str, dump_file_inner):
    DATA_FILE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    DATA_FILE_MODES = stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP
    DATA_DIR_MODES = stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP
    dump_file_dir = os.path.dirname(dump_file_inner)
    if not os.path.exists(dump_file_dir):
        file_util.makedirs(dump_file_dir, mode=DATA_DIR_MODES)

    if not os.path.exists(dump_file_inner):
        with os.fdopen(os.open(dump_file_inner, DATA_FILE_FLAGS, DATA_FILE_MODES), 'w') as rpt_fout:
            rpt_fout.write(info_str)
    else:
        with open(dump_file_inner, 'w') as d_f:
            d_f.write(info_str)


def _get_case_info_by_multi(soc_version, ut_case_file_info_list):
    multi_process_args = [
        {
            "case_file_path": ut_file_info.case_file,
            "soc_version": soc_version
        } for ut_file_info in ut_case_file_info_list
    ]

    cpu_cnt = max(multiprocessing.cpu_count() - 1, 1)
    with Pool(processes=cpu_cnt) as pool:
        all_res = pool.map(get_case_name_from_file, multi_process_args)
    return all_res


def get_case_name(case_file, dump_file=None, soc_version=None):
    """
    get case name
    :param case_file: case file path
    :param dump_file: dump file path, default is None, if not None dump case info to json file
    :param soc_version: soc version, default is None, get all soc
    :return: total case info
    """

    total_case_info = {}
    ut_case_file_info_list, _ = ut_loader.load_ut_cases(case_file)

    if len(ut_case_file_info_list) > 4:
        all_res = _get_case_info_by_multi(soc_version, ut_case_file_info_list)
        for res in all_res:
            if not res:
                continue
            for key, val in res.items():
                total_case_info[key] = val
    else:
        for ut_file_info in ut_case_file_info_list:
            params = {
                "case_file_path": ut_file_info.case_file,
                "soc_version": soc_version
            }
            res = get_case_name_from_file(params)
            if not res:
                continue
            for key, val in res.items():
                total_case_info[key] = val

    if not dump_file:
        _print_case_name_info(total_case_info)
        return total_case_info

    dump_file = os.path.realpath(dump_file)
    json_str = json.dumps(total_case_info, indent=4)
    _save_to_file(json_str, dump_file)
    return total_case_info


def print_case_summary(case_file, soc_version=None):
    """
    print case summary info
    :param case_file: case file path
    :param soc_version: soc version
    :return: None
    """
    total_case_info = get_case_name(case_file, dump_file=None, soc_version=soc_version)
    case_file_list = []
    op_type_list = []
    for test_file, case_list in total_case_info.items():
        if not case_list:
            continue
        case_file_list.append(test_file)
        op_type_list.append(case_list[0].get("op_type"))
    print("Test Op Type List:")
    print(op_type_list)

    print("Test Op Count: %d" % len(op_type_list))
    print("Test File Count: %d" % len(case_file_list))
