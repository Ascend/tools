#!/usr/bin/env python
# coding=utf-8
"""
Function:
This class mainly involves convert model to json function.
Copyright Information:
HuaWei Technologies Co.,Ltd. All Rights Reserved © 2021
"""
import os

from common import utils
from common.utils import AccuracyCompareException

ATC_FILE_PATH = "atc/bin/atc"


class AtcUtils(object):
    """
    Class for convert the om model to json.
    """

    def __init__(self, arguments):
        self.arguments = arguments

    def convert_model_to_json(self):
        """
        Function Description:
            convert om model to json
        Return Value:
            output json path
        Exception Description:
            when the model type is wrong throw exception
        """
        model_name, extension = utils.get_model_name_and_extension(self.arguments.offline_model_path)
        if ".om" != extension:
            utils.print_error_log('The offline model file ends with an .om file.Please check {} file.'.format(
                self.arguments.offline_model_path))
            raise AccuracyCompareException(utils.ACCURACY_COMPARISON_MODEL_TYPE_ERROR)
        utils.check_file_or_directory_path((os.path.realpath(self.arguments.cann_path)), True)
        atc_command_file_path = os.path.join(self.arguments.cann_path, ATC_FILE_PATH)
        utils.check_file_or_directory_path(atc_command_file_path)
        output_json_path = os.path.join(self.arguments.out_path, "model", model_name + ".json")
        # do the atc command to convert om to json
        utils.print_info_log('Start to converting the model to json')
        atc_cmd = [atc_command_file_path, "--mode=1", "--om=" + self.arguments.offline_model_path,
                   "--json=" + output_json_path]
        utils.print_info_log("ATC command line %s" % " ".join(atc_cmd))
        utils.execute_command(atc_cmd)
        utils.print_info_log("Complete model conversion to json %s." % output_json_path)
        return output_json_path
