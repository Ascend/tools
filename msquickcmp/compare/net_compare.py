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
import stat
import re
import sys
import subprocess

from common import utils
from common.utils import AccuracyCompareException

MSACCUCMP_DIR_PATH = "toolkit/tools/operator_cmp/compare"
MSACCUCMP_FILE_NAME = ["msaccucmp.py", "msaccucmp.pyc"]
PYC_FILE_TO_PYTHON_VERSION = "3.7.5"
INFO_FLAG = "[INFO]"
WRITE_FLAGS = os.O_WRONLY | os.O_CREAT
WRITE_MODES = stat.S_IWUSR | stat.S_IRUSR
# index of each member in compare result_*.csv file
NPU_DUMP_TAG = "NPUDump"
GROUND_TRUTH_TAG = "GroundTruth"
MIN_ELEMENT_NUM = 3
ADVISOR_ARGS = "-advisor"


class NetCompare(object):
    """
    Class for compare the entire network
    """

    def __init__(self, npu_dump_data_path, cpu_dump_data_path, output_json_path, arguments):
        self.npu_dump_data_path = npu_dump_data_path
        self.cpu_dump_data_path = cpu_dump_data_path
        self.output_json_path = output_json_path
        self.arguments = arguments
        self.msaccucmp_command_dir_path = os.path.join(self.arguments.cann_path, MSACCUCMP_DIR_PATH)
        self.msaccucmp_command_file_path = self._check_msaccucmp_file(self.msaccucmp_command_dir_path)
        self.python_version = sys.executable.split('/')[-1]

    def accuracy_network_compare(self):
        """
        Function Description:
            invoke the interface for network-wide comparsion
        Exception Description:
            when invalid  msaccucmp command throw exception
        """
        self._check_pyc_to_python_version(self.msaccucmp_command_file_path, self.python_version)
        msaccucmp_cmd = [self.python_version, self.msaccucmp_command_file_path, "compare", "-m",
                         self.npu_dump_data_path, "-g",
                         self.cpu_dump_data_path, "-f", self.output_json_path, "-out", self.arguments.out_path]
        if self._check_msaccucmp_compare_support_advisor():
            msaccucmp_cmd.append(ADVISOR_ARGS)
        utils.print_info_log("msaccucmp command line: %s " % " ".join(msaccucmp_cmd))
        status_code, _ = self.execute_msaccucmp_command(msaccucmp_cmd)
        if status_code == 2 or status_code == 0:
            utils.print_info_log("Finish compare the files in directory %s with those in directory %s." % (
                self.npu_dump_data_path, self.cpu_dump_data_path))
        else:
            utils.print_error_log("Failed to execute command: %s" % " ".join(msaccucmp_cmd))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)

    def net_output_compare(self, npu_net_output_data_path, golden_net_output_info):
        """
        net_output_compare
        """
        if not golden_net_output_info:
            return
        npu_dump_file = {}
        file_index = 0
        utils.print_info_log("=================================compare Node_output=================================")
        utils.print_info_log("start to compare the Node_output at now, compare result is:")
        utils.print_warn_log("The comparison of Node_output may be incorrect in certain scenarios. If the precision"
                             " is abnormal, please check whether the mapping between the comparison"
                             " data is correct.")
        for dir_path, subs_paths, files in os.walk(npu_net_output_data_path):
            for each_file in sorted(files):
                if each_file.endswith(".npy"):
                    npu_dump_file[file_index] = os.path.join(dir_path, each_file)
                    msaccucmp_cmd = [self.python_version, self.msaccucmp_command_file_path, "compare", "-m",
                                     npu_dump_file.get(file_index), "-g", golden_net_output_info.get(file_index)]
                    status, compare_result = self.execute_msaccucmp_command(msaccucmp_cmd, True)
                    if status == 2 or status == 0:
                        self.save_net_output_result_to_csv(npu_dump_file.get(file_index),
                                                           golden_net_output_info.get(file_index),
                                                           compare_result)
                        utils.print_info_log("Compare Node_output:{} completely.".format(file_index))
                    else:
                        utils.print_error_log("Failed to execute command: %s" % " ".join(msaccucmp_cmd))
                        raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_DATA_ERROR)
                    file_index += 1
        return

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
                    cosine_similarity = item.get("CosineSimilarity")
                    if cosine_similarity and float(cosine_similarity) < 0.9:
                        return item
        except IOError as csv_file_except:
            utils.print_error_log('Failed to open"' + result_file_path + '", ' + str(csv_file_except))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_OPEN_FILE_ERROR)
        return None

    def _process_result_one_line(self, fp_write, fp_read, npu_file_name, golden_file_name, result):
        writer = csv.writer(fp_write)
        # write header to file
        table_header_info = next(fp_read)
        header_list = table_header_info.strip().split(',')
        writer.writerow(header_list)
        npu_dump_index = header_list.index(NPU_DUMP_TAG)
        ground_truth_index = header_list.index(GROUND_TRUTH_TAG)

        result_reader = csv.reader(fp_read)
        # update result data
        new_content = []
        for line in result_reader:
            if len(line) < MIN_ELEMENT_NUM:
                utils.print_warn_log('The content of line is {}'.format(line))
                continue
            if line[npu_dump_index] != "Node_Output":
                writer.writerow(line)
            else:
                new_content = [line[0], "NaN", "Node_Output", "NaN", "NaN",
                               npu_file_name, "NaN", golden_file_name, "[]"]
                if self._check_msaccucmp_compare_support_advisor():
                    new_content.append("NaN")
                new_content.extend(result)
                new_content.extend([""])
                if line[ground_truth_index] != "*":
                    writer.writerow(line)
        writer.writerow(new_content)

    def save_net_output_result_to_csv(self, npu_file, golden_file, result):
        """
        save_net_output_result_to_csv
        """
        result_file_path = None
        result_file_backup_path = None
        npu_file_name = os.path.basename(npu_file)
        golden_file_name = os.path.basename(golden_file)
        for dir_path, subs_paths, files in os.walk(self.arguments.out_path):
            files = [file for file in files if file.endswith("csv")]
            if files:
                result_file_path = os.path.join(dir_path, files[0])
                result_file_backup = "{}_bak.csv".format(files[0].split(".")[0])
                result_file_backup_path = os.path.join(dir_path, result_file_backup)
                break
        try:
            # read result file and write it to backup file,update the result of compare Node_output
            with open(result_file_path, "r") as fp_read:
                with os.fdopen(os.open(result_file_backup_path, WRITE_FLAGS, WRITE_MODES), 'w',
                               newline="") as fp_write:
                    self._process_result_one_line(fp_write, fp_read, npu_file_name, golden_file_name, result)
            os.remove(result_file_path)
            os.rename(result_file_backup_path, result_file_path)
        except (OSError, SystemError, ValueError, TypeError, RuntimeError, MemoryError) as error:
            utils.print_error_log('Failed to write Net_output compare result')
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_NET_OUTPUT_ERROR)
        finally:
            pass

    @staticmethod
    def _catch_compare_result(log_line, catch):
        result = []
        try:
            if catch:
                # get the compare result
                info = log_line.decode().split(INFO_FLAG)
                if len(info) > 1:
                    info_content = info[1].strip().split(" ")
                    info_content = [item for item in info_content if item != '']
                    pattern_num = re.compile(r'^([0-9]+)\.?([0-9]+)?')
                    pattern_nan = re.compile(r'NaN', re.I)
                    match = pattern_num.match(info_content[0])
                    if match:
                        result = info_content
                    if not match and pattern_nan.match(info_content[0]):
                        result = info_content
            return result
        except (OSError, SystemError, ValueError, TypeError, RuntimeError, MemoryError):
            utils.print_warn_log('Failed to parse the alg compare result!')
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_NET_OUTPUT_ERROR)
        finally:
            pass

    def execute_msaccucmp_command(self, cmd, catch=False):
        """
        Function Description:
            run the following command
        Parameter:
            cmd: command
        Return Value:
            status code
        """
        result = []
        process = self.execute_command_line(cmd)
        while process.poll() is None:
            line = process.stdout.readline().strip()
            if line:
                print(line)
                compare_result = self._catch_compare_result(line, catch)
                result = compare_result if compare_result else result
        return process.returncode, result

    @staticmethod
    def execute_command_line(cmd):
        utils.print_info_log('Execute command:%s' % cmd)
        process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return process

    def _check_msaccucmp_compare_support_args(self, compare_args):
        check_cmd = [self.python_version, self.msaccucmp_command_file_path, "compare", "-h"]
        process = self.execute_command_line(check_cmd)
        while process.poll() is None:
            line = process.stdout.readline().strip()
            if line:
                line_decode = line.decode(encoding="utf-8")
                if compare_args in line_decode:
                    return True
        else:
            utils.print_warn_log(f'Current version does not support {compare_args} function')
            return False

    def _check_msaccucmp_compare_support_advisor(self):
        return self.arguments.advisor and \
               self._check_msaccucmp_compare_support_args(ADVISOR_ARGS)
