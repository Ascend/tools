#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves generate npu dump data function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2021
"""
import json
import os
import re
import numpy as np

from common import utils
from common.dump_data import DumpData
from common.utils import AccuracyCompareException
from npu.om_parser import OmParser

MSAME_DIR = "msame"
BUILD_SH = "build.sh"
OUT_PATH = "out"
MSAME_COMMAND_PATH = "msame"
ACL_JSON_PATH = "out/acl.json"
NPU_DUMP_DATA_BASE_PATH = "dump_data/npu"
RESULT_DIR = "result"
INPUT = "input"


class NpuDumpData(DumpData):
    """
    Class for generate npu dump data
    """

    def __init__(self, arguments, output_json_path):
        self.arguments = arguments
        self.om_parser = OmParser(output_json_path)

    def generate_dump_data(self):
        """
        Function Description:
            compile and rum msame project
        Return Value:
            npu dump data path
        """
        self._check_input_path_param()
        msame_dir = os.path.join(os.path.realpath(".."), MSAME_DIR)
        self.msame_compile(msame_dir)
        return self.msame_run(msame_dir)

    def get_expect_output_name(self):
        """
        Function Description:
            get expect output node name in golden net
        Return Value:
            output node name in golden net
        """
        return self.om_parser.get_expect_net_output_name()

    def msame_compile(self, msame_dir):
        """
        Function Description:
            compile msame project
        Parameter:
            msame_dir: msame project directory
        """
        execute_path = os.path.join(msame_dir, OUT_PATH, MSAME_COMMAND_PATH)
        if os.path.exists(execute_path):
            utils.print_info_log("The execute file %s exist. Skip the compile step." % execute_path)
            return
        utils.print_info_log("Start to compile %s" % msame_dir)
        out_path = os.path.join(msame_dir, OUT_PATH)
        build_sh_cmd = ["sh", BUILD_SH, "g++", out_path]
        os.chdir(msame_dir)
        # do build.sh command
        utils.print_info_log("Run command line: cd %s && %s" % (msame_dir, " ".join(build_sh_cmd)))
        utils.execute_command(build_sh_cmd)
        utils.print_info_log("Finish to compile %s." % msame_dir)

    def _make_msame_cmd_for_shape_range(self, msame_cmd):
        pattern = re.compile(r'^[0-9]+$')
        count = self.om_parser.get_net_output_count()
        if self.om_parser.shape_range:
            if not self.arguments.input_shape:
                utils.print_error_log('In the dynamic shape scenario, the "-s" or "--input-shape" is mandatory.')
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            msame_cmd.append('--dymShape')
            msame_cmd.append('"%s"' % self.arguments.input_shape)
            if not self.arguments.output_size:
                if count > 0:
                    count_list = []
                    for _ in range(count):
                        count_list.append("90000000")
                    self.arguments.output_size = ",".join(count_list)
        if self.arguments.output_size:
            output_size_list = self.arguments.output_size.split(',')
            if len(output_size_list) != count:
                utils.print_error_log(
                    'The output size (%d) is not equal %d in model. Please check the "--output-size" argument.'
                    % (len(output_size_list), count))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            for item in output_size_list:
                item = item.strip()
                match = pattern.match(item)
                if match is None:
                    utils.print_error_log("The size (%s) is invalid. Please check the output size."
                                          % self.arguments.output_size)
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
                if int(item) <= 0:
                    utils.print_error_log("The size (%s) must be large than zero. Please check the output size."
                                          % self.arguments.output_size)
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PARAM_ERROR)
            msame_cmd.append('--outputSize')
            msame_cmd.append(self.arguments.output_size)

    def msame_run(self, msame_dir):
        """
        Function Description:
            run msame project
        Parameter:
            msame_dir: msame project directory
        Return Value:
            npu dump data path
        Exception Description:
            when invalid npu dump data path throw exception
        """
        self._compare_shape_vs_bin_file()
        npu_data_output_dir = os.path.join(self.arguments.out_path, NPU_DUMP_DATA_BASE_PATH)
        utils.create_directory(npu_data_output_dir)
        model_name, extension = utils.get_model_name_and_extension(self.arguments.offline_model_path)
        acl_json_path = os.path.join(msame_dir, ACL_JSON_PATH)
        if not os.path.exists(acl_json_path):
            os.mknod(acl_json_path, mode=0o600)
        self._write_content_to_acl_json(acl_json_path, model_name, npu_data_output_dir)
        msame_cmd = ["./" + MSAME_COMMAND_PATH, "--model", self.arguments.offline_model_path, "--input",
                     self.arguments.input_path, "--device", self.arguments.device, "--output", npu_data_output_dir]
        self._make_msame_cmd_for_shape_range(msame_cmd)
        os.chdir(os.path.join(msame_dir, OUT_PATH))
        # do msame command
        utils.print_info_log("Run command line: cd %s && %s" % (os.path.join(msame_dir, OUT_PATH), " ".join(msame_cmd)))
        utils.execute_command(msame_cmd)
        npu_dump_data_path, file_is_exist = utils.get_dump_data_path(npu_data_output_dir)
        if not file_is_exist:
            utils.print_error_log("The path {} dump data is not exist.".format(npu_dump_data_path))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PATH_ERROR)
        # net output data path
        npu_net_output_data_path, file_is_exist = utils.get_dump_data_path(npu_data_output_dir, True)
        if not file_is_exist:
            utils.print_error_log("The path {} net output data is not exist.".format(npu_net_output_data_path))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PATH_ERROR)
        self._convert_net_output_to_numpy(npu_net_output_data_path)
        return npu_dump_data_path, npu_net_output_data_path

    def _convert_net_output_to_numpy(self, npu_net_output_data_path):
        net_output_data = None
        npu_net_output_data_info = self.om_parser.get_net_output_data_info()
        for dir_path, sub_paths, files in os.walk(npu_net_output_data_path):
            for index, each_file in enumerate(sorted(files)):
                data_type = npu_net_output_data_info.get(index)[0]
                shape = npu_net_output_data_info.get(index)[1]
                original_net_output_data = np.fromfile(os.path.join(dir_path, each_file), data_type)
                try:
                    net_output_data = original_net_output_data.reshape(shape)
                except ValueError:
                    utils.print_warn_log(
                        "The shape of net_output data from file {} is {}.".format(
                            each_file, shape))
                    net_output_data = original_net_output_data
                file_name = os.path.basename(each_file).split('.')[0]
                numpy_file_path = os.path.join(npu_net_output_data_path, file_name)
                utils.save_numpy_data(numpy_file_path, net_output_data)

    def _check_input_path_param(self):
        if self.arguments.input_path == "":
            input_path = os.path.join(self.arguments.out_path, INPUT)
            utils.check_file_or_directory_path(os.path.realpath(input_path), True)
            input_bin_files = os.listdir(input_path)
            input_bin_files.sort(key=lambda file: int((re.findall("\\d+", file))[0]))
            bin_file_path_array = []
            for item in input_bin_files:
                bin_file_path_array.append(os.path.join(input_path, item))
            self.arguments.input_path = ",".join(bin_file_path_array)
        else:
            bin_file_path_array = utils.check_input_bin_file_path(self.arguments.input_path)
            self.arguments.input_path = ",".join(bin_file_path_array)

    def _compare_shape_vs_bin_file(self):
        shape_size_array = self.om_parser.get_shape_size()
        if self.om_parser.contain_negative_1:
            return
        bin_files_size_array = self._get_bin_file_size()
        self._shape_size_vs_bin_file_size(shape_size_array, bin_files_size_array)

    def _get_bin_file_size(self):
        bin_file_size = []
        bin_files = self.arguments.input_path.split(",")
        for item in bin_files:
            bin_file_size.append(os.path.getsize(item))
        return bin_file_size

    def _shape_size_vs_bin_file_size(self, shape_size_array, bin_files_size_array):
        if len(shape_size_array) < len(bin_files_size_array):
            utils.print_error_log("The number of input bin files is incorrect.")
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_BIN_FILE_ERROR)
        if self.om_parser.shape_range:
            for bin_file_size in bin_files_size_array:
                if bin_file_size not in shape_size_array:
                    utils.print_error_log(
                        "The size (%d) of bin file can not match the input of the model." % bin_file_size)
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_BIN_FILE_ERROR)
        else:
            for shape_size, bin_file_size in zip(shape_size_array, bin_files_size_array):
                if shape_size == 0:
                    continue
                if shape_size != bin_file_size:
                    utils.print_error_log("The shape value is different from the size of the bin file.")
                    raise AccuracyCompareException(utils.ACCURACY_COMPARISON_BIN_FILE_ERROR)

    @staticmethod
    def _write_content_to_acl_json(acl_json_path, model_name, npu_data_output_dir):
        load_dict = {
            "dump": {"dump_list": [{"model_name": model_name}], "dump_path": npu_data_output_dir, "dump_mode": "all",
                     "dump_op_switch": "off"}}
        if os.access(acl_json_path, os.W_OK):
            try:
                with open(acl_json_path, "w") as write_json:
                    try:
                        json.dump(load_dict, write_json)
                    except ValueError as write_json_except:
                        print(str(write_json_except))
                        raise AccuracyCompareException(utils.ACCURACY_COMPARISON_WRITE_JSON_FILE_ERROR)
            except IOError as acl_json_file_except:
                utils.print_error_log('Failed to open"' + acl_json_path + '", ' + str(acl_json_file_except))
                raise AccuracyCompareException(utils.ACCURACY_COMPARISON_OPEN_FILE_ERROR)
        else:
            utils.print_error_log(
                "The path {} does not have permission to write.Please check the path permission".format(acl_json_path))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_INVALID_PATH_ERROR)
