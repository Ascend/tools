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

from common import utils
from common.utils import AccuracyCompareException

MSACCUCMP_DIR_PATH = "toolkit/tools/operator_cmp/compare"
MSACCUCMP_FILE_NAME = ["msaccucmp.py", "msaccucmp.pyc"]
PYC_FILE_TO_PYTHON_VERSION = "3.7.5"


class NetCompare(object):
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
        Exception Description:
            when invalid  msaccucmp command throw exception
        """
        cmd = ["python3", "-V"]
        python_version = self._check_python_command_valid(cmd)
        msaccucmp_command_dir_path = os.path.join(self.arguments.cann_path, MSACCUCMP_DIR_PATH)
        msaccucmp_command_file_path = self._check_msaccucmp_file(msaccucmp_command_dir_path)
        self._check_pyc_to_python_version(msaccucmp_command_file_path, python_version)
        msaccucmp_cmd = ["python" + python_version, msaccucmp_command_file_path, "compare", "-m",
                         self.npu_dump_data_path, "-g",
                         self.cpu_dump_data_path, "-f", self.output_json_path, "-out", self.arguments.out_path]
        utils.print_info_log("msaccucmp command line: %s " % " ".join(msaccucmp_cmd))
        status_code = self.execute_msaccucmp_command(msaccucmp_cmd)
        if status_code == 2 or status_code == 0:
            utils.print_info_log("Finish compare the files in directory %s with those in directory %s." % (
                self.npu_dump_data_path, self.cpu_dump_data_path))
        else:
            utils.print_error_log("Failed to execute command: %s" % " ".join(msaccucmp_cmd))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)

    @staticmethod
    def _check_python_command_valid(cmd):
        try:
            output_bytes = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            output_text = output_bytes.decode("utf-8")
            if "Python 3" not in output_text:
                utils.print_error_log(
                    "The python version only supports the python 3 version family, %s" % " ".join(cmd))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_PYTHON_VERSION_ERROR)
            python_version = output_text.split(" ")[1].strip()
            return python_version
        except subprocess.CalledProcessError as check_output_except:
            print(str(check_output_except))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_PYTHON_COMMAND_ERROR)

    @staticmethod
    def _check_msaccucmp_file(msaccucmp_command_dir_path):
        for file_name in MSACCUCMP_FILE_NAME:
            msaccucmp_command_file_path = os.path.join(msaccucmp_command_dir_path, file_name)
            if os.path.exists(msaccucmp_command_file_path):
                return msaccucmp_command_file_path
            else:
                utils.print_warn_log(
                    'The path {} is not exist.Please check the file'.format(msaccucmp_command_file_path))
        utils.print_error_log(
            'Does not exist in {} directory msaccucmp.py and msaccucmp.pyc file'.format(msaccucmp_command_dir_path))
        raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PATH_ERROR)

    @staticmethod
    def _check_pyc_to_python_version(msaccucmp_command_file_path, python_version):
        if msaccucmp_command_file_path.endswith(".pyc"):
            if python_version != PYC_FILE_TO_PYTHON_VERSION:
                utils.print_error_log(
                    "The python version for executing {} must be 3.7.5".format(msaccucmp_command_file_path))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_PYTHON_VERSION_ERROR)

    def get_csv_object_by_cosine(self):
        """
        Function Description:
            get operators whose cosine value is less than 0.9
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
                    if float(item.get("CosineSimilarity")) < 0.9:
                        return item
        except IOError as csv_file_except:
            utils.print_error_log('Failed to open"' + result_file_path + '", ' + str(csv_file_except))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_OPEN_FILE_ERROR)
        return None

    def execute_msaccucmp_command(self, cmd):
        """
        Function Description:
            run the following command
        Parameter:
            cmd: command
        Return Value:
            status code
        """
        utils.print_info_log('Execute command:%s' % cmd)
        process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while process.poll() is None:
            line = process.stdout.readline()
            line = line.strip()
            if line:
                print(line)
        return process.returncode
