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

"""op ut runner, apply run ut function"""
import importlib
import time
import os
import sys
import stat
import shutil
import multiprocessing
from typing import List
from typing import Union
from datetime import datetime
from multiprocessing import Pool
from functools import reduce

import coverage
from op_test_frame.common import logger
from op_test_frame.ut import ut_loader
from op_test_frame.ut import ut_report
from op_test_frame.ut import op_ut
from op_test_frame.utils import file_util

from op_test_frame.ut.op_ut_case_info import CaseUsage


# 'pylint: disable=too-few-public-methods
class Constant:
    """
    This class for Constant.
    """
    DATA_DIR_MODES = stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP


# 'pylint: disable=too-few-public-methods,too-many-arguments,too-many-branches,too-many-statements
class OpUTTestRunner:
    """
    Op ut runner
    """

    def __init__(self, print_summary=True, verbosity=2, simulator_mode=None, simulator_lib_path=None,
                 simulator_dump_path=None, data_dump_level=None, data_dump_dir=None):
        self.print_summary = print_summary
        self.verbosity = verbosity

        if not simulator_mode:
            simulator_mode = "pv"

        if not simulator_lib_path:
            simulator_lib_path = os.environ.get("SIMULATOR_PATH")
        if not simulator_lib_path:
            raise RuntimeError(
                "Not configured simulator path, when run simulator. "
                "Please set simulator_lib_path arg, or set ENV SIMULATOR_PATH")

        self.simulator_mode = simulator_mode
        self.simulator_lib_path = simulator_lib_path
        self.simulator_dump_path = simulator_dump_path
        self.data_dumnp_level = data_dump_level
        self.data_dumnp_dir = data_dump_dir

    def _execute_one_soc(self, op_ut_case: op_ut.OpUT, run_soc_vsersion: str,
                         case_name_list: List[str], case_usage_list: List = None) -> ut_report.OpUTReport:
        if self.simulator_mode:
            run_cfg = {"simulator_mode": self.simulator_mode,
                       "simulator_lib_path": self.simulator_lib_path,
                       "simulator_dump_path": self.simulator_dump_path,
                       "data_dump_path": self.data_dumnp_dir}
        ut_run_report = op_ut_case.run_case(run_soc_vsersion, case_name_list=case_name_list,
                                            case_usage_list=case_usage_list, run_cfg=run_cfg)
        return ut_run_report

    def run(self, run_soc_versions: Union[str, List[str]], op_ut_case: op_ut.OpUT,
            case_name_list: List[str] = None, case_usage_list: List = None) -> ut_report.OpUTReport:
        """
        run op_ut

        Parameters
        ----------
        run_soc_versions: Union[str, List[str]]
            run soc versions, like: 1) Ascend910 2) Ascend910,Ascend310 3) [Ascend910, Ascend310]
        op_ut_case: op_ut.OpUT
            the op_ut_case you need to run
        case_name_list: List[str], can be None
            can only run the cases which in case_name_list, if None means run all test cases in op_ut
        case_usage_list: List, default is None
            can only run the cases which caseusage in case_usage_list, if None means run all test cases in op_ut

        Returns
        -------
        report: ut_report.OpUTReport
            the case run report
        """
        if isinstance(run_soc_versions, str):
            if "," in run_soc_versions:
                run_soc_versions = [x.strip() for x in run_soc_versions.split(",")]
        if not isinstance(run_soc_versions, (tuple, list)):
            run_soc_versions = [run_soc_versions, ]

        report = ut_report.OpUTReport()
        start_time = time.time()
        print(">>>> start run test case")
        for run_soc_version in run_soc_versions:
            one_soc_rpt = self._execute_one_soc(op_ut_case, run_soc_version,
                                                case_name_list=case_name_list, case_usage_list=case_usage_list)
            report.merge_rpt(one_soc_rpt)
        end_time = time.time()
        time_taken = end_time - start_time
        print(">>>> end run test case, op_type:%s cost time: %d " % (op_ut_case.op_type, time_taken))
        if self.print_summary:
            report.console_print()

        return report


class RunUTCaseFileArgs:  # 'pylint: disable=too-many-instance-attributes,too-few-public-methods
    """
    run ut case file args for multiprocess run
    """

    def __init__(self, case_file, op_module_name, soc_version,  # 'pylint: disable=too-many-arguments
                 case_name, test_report, test_report_data_path,
                 cov_report, cov_data_path, simulator_mode, simulator_lib_path,
                 data_dir, dump_model_dir):
        self.case_file = case_file
        self.op_module_name = op_module_name
        self.soc_version = soc_version
        self.case_name = case_name
        self.test_report = test_report
        self.test_report_data_path = test_report_data_path
        self.cov_report = cov_report
        self.cov_data_path = cov_data_path
        self.simulator_mode = simulator_mode
        self.simulator_lib_path = simulator_lib_path
        self.data_dir = data_dir
        self.dump_model_dir = dump_model_dir


def get_cov_relate_source(module_name: str) -> list:
    """
    get relate source to generate coverage
    Parameters:
    -----------
    module_name: related module
    Returns:
    -----------
    List related source to generate coverage
    """
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        for dir_item in sys.path:
            impl_dir = os.path.join(dir_item, "impl")
            if os.path.exists(impl_dir):
                sys.path.append(impl_dir)
        module_name = module_name.replace("impl.", "")
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        logger.log_warn("fail to find module: %s" % module_name)
        module_dir = "impl"
    else:
        module_dir = os.path.split(module_spec.origin)[0]
        if module_dir.endswith("dynamic"):
            module_dir = os.path.dirname(module_dir)
    return [module_name, module_dir]


def _run_ut_case_file(run_arg: RunUTCaseFileArgs):
    logger.log_info("start run: %s" % run_arg.case_file)
    res = True

    if run_arg.cov_report:
        cov_src = get_cov_relate_source(run_arg.op_module_name)
        ut_cover = coverage.Coverage(source=cov_src, data_file=run_arg.cov_data_path)
        ut_cover.start()

    try:
        if sys.modules.get(run_arg.op_module_name):
            print("[INFO]reload module for coverage ,moule name:", sys.modules.get(run_arg.op_module_name))
            importlib.reload(sys.modules.get(run_arg.op_module_name))
        case_dir = os.path.dirname(os.path.realpath(run_arg.case_file))
        case_module_name = os.path.basename(os.path.realpath(run_arg.case_file))[:-3]
        sys.path.insert(0, case_dir)
        __import__(case_module_name)
        case_module = sys.modules[case_module_name]
        ut_case = getattr(case_module, "ut_case", None)
        case_usage_list = [CaseUsage.IMPL, CaseUsage.CUSTOM, CaseUsage.CFG_COVERAGE_CHECK,
                           CaseUsage.CHECK_SUPPORT, CaseUsage.SELECT_FORMAT, CaseUsage.PRECISION]

        if not run_arg.simulator_mode:
            case_usage_list.remove(CaseUsage.PRECISION)

        case_runner = OpUTTestRunner(print_summary=False,
                                     simulator_mode=run_arg.simulator_mode,
                                     simulator_lib_path=run_arg.simulator_lib_path,
                                     simulator_dump_path=run_arg.dump_model_dir,
                                     data_dump_dir=run_arg.data_dir)
        if isinstance(run_arg.case_name, str):
            case_name_list = run_arg.case_name.split(",")
        else:
            case_name_list = run_arg.case_name
        ut_rpt = case_runner.run(run_arg.soc_version, ut_case, case_name_list, case_usage_list)
        ut_rpt.save(run_arg.test_report_data_path)
        del sys.modules[case_module_name]
    except BaseException as run_err:  # 'pylint: disable=broad-except
        logger.log_err("Test Failed! case_file: %s, error_msg: %s" % (run_arg.case_file, run_err.args[0]),
                       print_trace=True)
        res = False

    if run_arg.cov_report:
        ut_cover.stop()
        ut_cover.save()
    logger.log_info("end run: %s" % run_arg.case_file)
    return res




def _check_args(case_dir, test_report, cov_report):
    if not case_dir:
        logger.log_err("Not set case dir")
        return False
    if test_report and test_report not in ("json", "console"):
        logger.log_err("'test_report' only support 'json/console'.")
        return False
    if cov_report and cov_report not in ("html", "json", "xml"):
        logger.log_err("'cov_report' only support 'html/json/xml'.")
        return False
    return True


def _build_cov_data_path(cov_report_path):
    cov_combine_path = os.path.join(os.path.realpath(cov_report_path), "combine_data_path")
    if os.path.exists(cov_combine_path):
        shutil.rmtree(cov_combine_path)
    file_util.makedirs(cov_combine_path, mode=Constant.DATA_DIR_MODES)
    return cov_combine_path


def _build_report_data_path(test_report_path):
    rpt_combine_path = os.path.join(os.path.realpath(test_report_path), "combine_rpt_path")
    if os.path.exists(rpt_combine_path):
        shutil.rmtree(rpt_combine_path)
    file_util.makedirs(rpt_combine_path, mode=Constant.DATA_DIR_MODES)
    return rpt_combine_path


def run_ut(case_dir, soc_version, case_name=None,  # 'pylint: disable=too-many-arguments, too-many-locals
           test_report="json", test_report_path="./report",
           cov_report=None, cov_report_path="./cov_report",
           simulator_mode=None, simulator_lib_path=None,
           simulator_data_path="./model", test_data_path="./data",
           process_num=0):
    """
    run ut test case
    :param case_dir: a test case dir or a test case file
    :param soc_version: like "Ascend910", "Ascend310"
    :param case_name: run case name, default is None, run all test case
    :param test_report: support console/json, report format type
    :param test_report_path: test report save path
    :param cov_report: support html/json/xml type, if None means not need coverage report
    :param cov_report_path: coverage report save path
    :param simulator_mode: simulator_mode can be None/pv/ca/tm/esl
    :param simulator_lib_path: simulator library path
    :param simulator_data_path: test data directory, input, output and expect output data
    :param test_data_path: when run ca or tm mode, dump data save in this dirctory
    :param process_num: when 0 means use cpu_count, else means process count

    :return: success or failed
    """
    success = "success"
    failed = "failed"
    print("start run ops ut time: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
    if not _check_args(case_dir, test_report, cov_report):
        return failed

    case_file_info_list, load_has_err = ut_loader.load_ut_cases(case_dir)
    if not case_file_info_list:
        logger.log_err("Not found any test cases.")
        return failed

    cov_combine_dir = _build_cov_data_path(cov_report_path)
    rpt_combine_dir = _build_report_data_path(test_report_path)

    def _build_multiprocess_run_args():

        ps_count = 1
        if not isinstance(soc_version, (tuple, list)):
            soc_version_list = str(soc_version).split(",")
        else:
            soc_version_list = soc_version
        total_run_arg_list = {}
        for one_soc in soc_version_list:
            total_run_arg_list[one_soc] = []
        for case_file_info in case_file_info_list:
            case_file_tmp = os.path.basename(case_file_info.case_file)[:-3]
            for one_soc_version in soc_version_list:
                single_cov_data_path = os.path.join(cov_combine_dir, ".coverage_" + str(ps_count) + "_" + case_file_tmp)
                single_rpt_data_path = os.path.join(rpt_combine_dir,
                                                    "rpt_" + str(ps_count) + "_" + case_file_tmp + ".data")
                run_arg = RunUTCaseFileArgs(case_file=case_file_info.case_file,
                                            op_module_name=case_file_info.op_module_name,
                                            soc_version=one_soc_version,
                                            case_name=case_name,
                                            test_report=test_report,
                                            test_report_data_path=single_rpt_data_path,
                                            cov_report=cov_report,
                                            cov_data_path=single_cov_data_path,
                                            simulator_mode=simulator_mode,
                                            simulator_lib_path=simulator_lib_path,
                                            data_dir=test_data_path,
                                            dump_model_dir=simulator_data_path)
                total_run_arg_list[one_soc_version].append(run_arg)
                ps_count += 1
        return total_run_arg_list, ps_count

    multiprocess_run_args, total_count = _build_multiprocess_run_args()

    logger.log_info("multiprocess_run_args count: %d" % total_count)

    if process_num == 1:
        logger.log_info("process_num is 1, run cases one by one")
        results = []
        for _, soc_args in multiprocess_run_args.items():
            for soc_arg in soc_args:
                res = _run_ut_case_file(soc_arg)
                results.append(res)
        run_success = reduce(lambda x, y: x and y, results)
    else:
        if process_num == 0:
            cpu_count = max(multiprocessing.cpu_count() - 1, 1)
            logger.log_info("multiprocessing cpu count: %d" % cpu_count)
        else:
            cpu_count = process_num
            logger.log_info("process_num is %s" % process_num)

        if simulator_mode == "esl":
            cpu_count = 1

        if total_count < cpu_count:
            total_args = []
            for _, soc_args in multiprocess_run_args.items():
                for soc_arg in soc_args:
                    total_args.append(soc_arg)
            if len(total_args) == 1:
                res = _run_ut_case_file(total_args[0])
                results = [res, ]
            else:
                with Pool(processes=cpu_count) as pool:
                    results = pool.map(_run_ut_case_file, total_args)
            run_success = reduce(lambda x, y: x and y, results)
        else:
            results = []
            for _, soc_args in multiprocess_run_args.items():
                with Pool(processes=cpu_count) as pool:
                    one_soc_results = pool.map(_run_ut_case_file, soc_args)
                for result in one_soc_results:
                    results.append(result)
            run_success = reduce(lambda x, y: x and y, results)

    test_report = ut_report.OpUTReport()
    test_report.combine_report(rpt_combine_dir)
    report_data_path = os.path.join(test_report_path, ".ut_test_report")
    test_report.save(report_data_path)
    if test_report:
        test_report.console_print()

    if cov_report and len(multiprocess_run_args) > 0:
        _combine_coverage(cov_report_path, cov_combine_dir)

    print("end run ops ut time: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
    if load_has_err:
        logger.log_err("Has error in case files, you can see error log by key word 'import case file failed'.")
    run_result = success if run_success and not load_has_err else failed
    if test_report.err_cnt > 0 or test_report.failed_cnt > 0:
        run_result = failed
    return run_result


def _combine_coverage(cov_report_path, cov_combine_dir):
    total_cov_data_file = os.path.join(cov_report_path, ".coverage")
    cov = coverage.Coverage(source="impl", data_file=total_cov_data_file)
    combine_files = [os.path.join(cov_combine_dir, cov_file) for cov_file in os.listdir(cov_combine_dir)]
    cov.combine(combine_files)
    cov.save()
    cov.load()
    cov.html_report(directory=cov_report_path)
    os.removedirs(cov_combine_dir)
