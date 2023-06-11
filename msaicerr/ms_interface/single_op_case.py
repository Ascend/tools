#!/usr/bin/env python
# coding=utf-8
"""
Function:
This file mainly involves the common function.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import re
import os
from time import sleep
import time
import chardet
import numpy as np
from ms_interface import utils
from ms_interface.constant import Constant
from ms_interface.dump_data_parser import DumpDataParser
from ms_interface.single_op_test_frame.common.ascend_tbe_op import AscendOpKernel, AscendOpKernelRunner


class SingleOpCase:

    def __init__(self, collection) -> None:
        self.collection = collection

    @staticmethod
    def _check_file_content(kernel_name, content):
        error_strings = [
            "there is an aivec error exception",
            "there is an aicore error exception",
            "aicore exception"
        ]
        for s in error_strings:
            if s in content and kernel_name in content:
                return True
        return False
 
    @staticmethod
    def _wait_for_log_stabilization(log_path):
        log_size = os.path.getsize(log_path)
        while True:
            sleep(0.2)
            current_log_size = os.path.getsize(log_path)
            if current_log_size == log_size:
                break
            log_size = current_log_size

    @staticmethod
    def search_aicerr_log(kernel_name, path):
        for root, _, files in os.walk(path):
            for file in files:
                if not file.endswith(".log"):
                    continue
                log_path = os.path.abspath(os.path.join(root, file))
                utils.print_info_log(f"The find single op log {log_path}")
                SingleOpCase._wait_for_log_stabilization(log_path)
                with open(log_path, "r") as f:
                    content = f.read()
                if SingleOpCase._check_file_content(kernel_name, content):
                    return True
        return False

    def generate_config(self):
        config_file_list = []
        kernel_path = self.collection.collect_kernel_path

        encoding = chardet.detect(self.collection.tiling_list[1])["encoding"]
        if encoding:
          tiling_data = self.collection.tiling_list[1].decode(encoding)
        else:
          tiling_data = ""

        for kernel_name in self.collection.kernel_name_list:
            data = {
                "cce_file": self.get_cce_file(),
                "bin_path": os.path.join(kernel_path, f"{kernel_name}.o"),
                "json_path": os.path.join(kernel_path, f"{kernel_name}.json"),
                "tiling_data": tiling_data,
                "tiling_key": self.collection.tiling_list[0],
                "block_dim": self.collection.tiling_list[2],
                "input_file_list": self.collection.input_list,
                "output_file_list": self.collection.output_list,
                "kernel_name": kernel_name
            }
            config_file_list.append(data)
        return config_file_list

    @staticmethod
    def get_soc_version_from_cce(cce_file):
        with open(cce_file, 'r') as f:
            content = f.read()
        soc_version_ret = re.findall(r'//.*?(Ascend.*?)"', content)
        if soc_version_ret:
            utils.print_info_log(f"get soc_version {soc_version_ret[0]} from cce file {cce_file}")
            return soc_version_ret[0]
        else:
            utils.print_warn_log('Can not get soc_version from cce file {cce_file}')
            return "Ascend310"

    def get_cce_file(self):
        kernel_path = self.collection.collect_kernel_path
        kernel_name = self.collection.kernel_name_list[0]
        tiling_key = self.collection.tiling_list[0]
        cce_file = os.path.join(kernel_path, kernel_name + ".cce")
        if not os.path.exists(cce_file):
            cce_file = os.path.join(kernel_path, f"{kernel_name}_{tiling_key}.cce")
            if not os.path.exists(cce_file):
                utils.print_warn_log(f"The cce file:{cce_file} does not exist. Set soc version Ascend310")
                return "Ascend310"
        return cce_file

    @staticmethod
    def run_dirty_ub(soc_version):
        try:
            SingleOpCase.dirty_ub(soc_version, kernel_name=f"dirty_ub_{soc_version}")
        except Exception as e:
            utils.print_warn_log("compile diry_ub op failed, skip dirty ub")
            return
        find_path_cmd = ["find", "./", "-name", f"dirty_ub_{soc_version}*"]
        regexp = r"([_\-/0-9a-zA-Z.]{1,}\.json|[_\-/0-9a-zA-Z.]{1,}\.o|[_\-/0-9a-zA-Z.]{1,}\.cce)"
        kernel_file_list = utils.get_inquire_result(find_path_cmd, regexp)
        if not kernel_file_list:
            utils.print_warn_log(f"The dirty_ub_{soc_version} file path cannot be found.")
        for file in kernel_file_list:
            if file.endswith(".o"):
              bin_path = file
            elif file.endswith(".json"):
              json_path = file
            else:
              continue
        if not os.path.exists(bin_path) or not os.path.exists(json_path):
            utils.print_info_log(f"Can not find bin_file  and json_file ")
            
            return 
        utils.print_info_log(f"Find bin_file {bin_path} and json_file {json_path}")
        op_kernel = AscendOpKernel(bin_path, json_path)
        runner = AscendOpKernelRunner()
        output_info = {}
        output_info["size"] = 4
        output_info["dtype"] = "float32"
        output_info["shape"] = (1,)
        runner.run(op_kernel, inputs=[], actual_output_info=(output_info,))
        
    @staticmethod
    def dirty_ub(soc_version, kernel_name="dirty_ub"):
        try:
            from te import tik
            from tbe.common import platform as cce
            from tbe.common.platform import set_current_compile_soc_info as te_set_version
        except ImportError as e:
            utils.print_warn_log("failed to import te or tbe to compile op dirty_ub, skipped it. error:", e)
            return 
        te_set_version(soc_version)
        ub_size = cce.get_soc_spec("UB_SIZE")
        
        tik_instance = tik.Tik()
        
        output_gm = tik_instance.Tensor("float32", (1,), name="output_gm", scope=tik.scope_gm)
        all_ub = tik_instance.Tensor("float32", (ub_size // 4,), name="all_ub", scope=tik.scope_ubuf)
        with tik_instance.for_range(0, ub_size // 256)  as loop_idx:
            tik_instance.vec_dup(64, all_ub[loop_idx * 64], 1.7976931348623157e+30, 1, 8)
        tik_instance.BuildCCE(kernel_name=kernel_name, inputs=[], outputs=[output_gm])

        return tik_instance

    @staticmethod
    def run_kernel(data):
        runner = AscendOpKernelRunner()
        
        bin_path = data["bin_path"]
        json_path = data["json_path"]
        tiling_data = data["tiling_data"].encode("utf-8")
        tiling_key = data["tiling_key"]
        block_dim = data["block_dim"]
        input_file_list = data["input_file_list"]
        output_file_list = data["output_file_list"]

        input_data_list = []
        for file in input_file_list:
            input_data = np.load(file)
            input_data_list.append(input_data)

        output_info_list = []
        for file in output_file_list:
            output_info = {}
            np_data = np.load(file)
            output_info["size"] = np_data.nbytes
            output_info["dtype"] = str(np_data.dtype)
            output_info["shape"] = np_data.shape
            output_info_list.append(output_info)

        op_kernel = AscendOpKernel(bin_path, json_path)
        runner.run(op_kernel,
                   inputs=input_data_list,
                   tiling_data=tiling_data,
                   block_dim=block_dim,
                   tiling_key=tiling_key,
                   actual_output_info=output_info_list)

    @staticmethod
    def run(configs: dict):
        # set single op log path
        date_string = time.strftime("%Y%m%d%H%M%S", time.localtime(int(time.time())))
        single_op_log_path =  f"single_op_log_{date_string}"
        os.environ['ASCEND_PROCESS_LOG_PATH'] = single_op_log_path
        os.environ['ASCEND_SLOG_PRINT_TO_STDOUT'] = "0"
        utils.print_info_log(f"The single_op_log_path is {single_op_log_path}")
        soc_version = SingleOpCase.get_soc_version_from_cce(configs.get("cce_file"))
        SingleOpCase.run_dirty_ub(soc_version)
        SingleOpCase.run_kernel(configs)

        return not SingleOpCase.search_aicerr_log(configs.get("kernel_name"), os.path.join(single_op_log_path, "debug"))
