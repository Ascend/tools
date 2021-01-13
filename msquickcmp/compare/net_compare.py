#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves the accuracy_network_compare function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2021
"""
import csv
import os
import subprocess

from msquickcmp.common import utils
from msquickcmp.common.utils import AccuracyCompareException

MSACCUCMP_PATH = "toolchain/operator_cmp/compare/msaccucmp.pyc"


class NetCompare:
    """
    Class for compare the entire network
    """

    def __init__(self, npu_dump_data_path, cpu_dump_data_path, output_json_path, arguments):
        self.npu_dump_data_path = npu_dump_data_path
        self.cpu_dump_data_path = cpu_dump_data_path
        self.output_json_path = output_json_path
        self.arguments = arguments

    def accuracy_network_compare(self):
        """
        Function Description:
            invoke the interface for network-wide comparsion
        Parameter:
            none
        Return Value:
            none
        Exception Description:
            none
        """
        cmd = ["python3", "-V"]
        self._check_python_command_valid(cmd)
        msaccucmp_command_file_path = os.path.join(self.arguments.cann_path, MSACCUCMP_PATH)
        utils.check_file_or_directory_path(msaccucmp_command_file_path)
        msaccucmp_cmd = ["python3", msaccucmp_command_file_path, "compare", "-m", self.npu_dump_data_path, "-g",
                         self.cpu_dump_data_path, "-f", self.output_json_path, "-out", self.arguments.out_path]
        utils.print_info_log("msaccucmp command line: %s " % " ".join(msaccucmp_cmd))
        utils.execute_command(msaccucmp_cmd)

    @staticmethod
    def _check_python_command_valid(cmd):
        try:
            output_bytes = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            output_text = output_bytes.decode("utf-8")
            if "Python 3.7.5 " != output_text:
                utils.print_error_log("The Python version should be 3.7.5: %s" % " ".join(cmd))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_PYTHON_VERSION_ERROR)
        except (subprocess.CalledProcessError, FileNotFoundError) as check_output_except:
            print(check_output_except)
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_PYTHON_COMMAND_ERROR)

    def get_csv_object_by_cosine(self):
        """
        Function Description:
            get operators whose cosine value is less than 0.9
        Parameter:
            none
        Return Value:
            operators object or None
        Exception Description:
            when invalid data throw exception
        """
        result_data = os.walk(self.arguments.out_path)
        result_file_path = None
        for dir_path, subs_paths, files in result_data:
            if len(files) != 0:
                result_file_path = os.path.join(dir_path, files[0])
                break
        try:
            with open(result_file_path, "r") as csv_file:
                csv_object = csv.DictReader(csv_file)
                rows = [row for row in csv_object]
                for item in rows:
                    if float(item["CosineSimilarity"]) < 0.9:
                        return item
        except(FileNotFoundError, IOError) as csv_file_except:
            print(csv_file_except)
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_OPEN_FILE_ERROR)
        return None
