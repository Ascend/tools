#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Copyright (C) 2022-2023. Huawei Technologies Co., Ltd. All rights reserved.
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
"""

import os
import pandas as pd

from .advisor_result import AdvisorResult
from .advisor_const import AdvisorConst
from ..common import utils
from ..common.utils import CompareException, CompareConst, Const
from ..common.utils import print_info_log, print_warn_log, print_error_log


class Advisor:
    """
    Class for generate advisor
    """

    def __init__(self, input_file, out_path=""):
        self.input_file = os.path.realpath(input_file)
        self.out_path = os.path.realpath(out_path)

    def _parse_input_file(self):
        if not self.input_file.endswith(".csv"):
            print_error_log("Advisor only support csv file from ptdbg_ascend result.")
            raise CompareException(CompareException.INVALID_FILE_ERROR)
        try:
            df = pd.read_csv(self.input_file, on_bad_lines='skip')
        except OSError as os_err:
            print_error_log('Failed to parse the input file %s. %s'
                            % (self.input_file, str(os_err)))
            raise CompareException(CompareException.PARSE_FILE_ERROR) from os_err
        data_columns = df.columns.values
        if not {CompareConst.ACCURACY, CompareConst.NPU_NAME}.issubset(data_columns):
            print_error_log('Compare result file does not contain %s, %s columns.' % (CompareConst.ACCURACY,
                                                                                      CompareConst.NPU_NAME))
            raise CompareException(CompareException.INVALID_FILE_ERROR)
        df.reset_index(inplace=True)
        # The value of index is consistent with the line number of csv, csv file first line is 2
        df.iloc[:, 0] += 2
        return df

    def _check_result_file(self):
        utils.check_file_or_directory_path(self.input_file)
        utils.check_file_size(self.input_file, Const.ONE_HUNDRED_MB)

    @staticmethod
    def filter_data(pd_data):
        """
        filter some apis cannot be fixed
        """
        result = pd_data[~pd_data[CompareConst.NPU_NAME].str.contains(AdvisorConst.BATCH_NORM)]
        return result

    @staticmethod
    def gen_advisor_message(node_name):
        if AdvisorConst.FORWARD in node_name:
            if AdvisorConst.INPUT in node_name:
                message = AdvisorConst.FORWARD_INPUT_SUGGEST
            else:
                message = AdvisorConst.FORWARD_OUTPUT_SUGGEST
        else:
            if AdvisorConst.INPUT in node_name:
                message = AdvisorConst.BACKWARD_INPUT_SUGGEST
            else:
                message = AdvisorConst.BACKWARD_OUTPUT_SUGGEST
        return message

    def gen_advisor_result(self, pd_data):
        first_failing_data = pd_data.iloc[0]
        node_name = first_failing_data[CompareConst.NPU_NAME]
        index = first_failing_data['index']
        message = self.gen_advisor_message(node_name)
        print_warn_log("Find %s accuracy not reached, the line is %s" % (node_name, index))
        result = AdvisorResult(node_name, index, message)
        return result
    
    def analyze_unmatched(self, analyze_data):
        accuracy_unmatched = analyze_data[analyze_data[CompareConst.ACCURACY] == CompareConst.ACCURACY_CHECK_UNMATCH]
        num_unmatch = len(accuracy_unmatched)
        if num_unmatch != 0:
            for i in range(len(accuracy_unmatched)):
                item = analyze_data.iloc[i]
                print_warn_log("The tensor name matches but the shape or dtype does not match: {}"\
                        .format(item[CompareConst.NPU_NAME]))

    def analysis(self):
        self._check_result_file()
        analyze_data = self._parse_input_file()
        print_info_log("Start analyzing the comparison result: %s" % self.input_file)
        self.analyze_unmatched(analyze_data)
        accuracy_not_reached = analyze_data[analyze_data[CompareConst.ACCURACY] == CompareConst.ACCURACY_CHECK_NO]
        failing_data = self.filter_data(accuracy_not_reached)
        if failing_data.empty:
            print_info_log("All data from api input/output accuracy reached")
            result = AdvisorResult(AdvisorConst.NO_ERROR_API, AdvisorConst.NO_ERROR_API, AdvisorConst.NO_ERR_SUGGEST)
        else:
            result = self.gen_advisor_result(failing_data)
        message_list = result.print_advisor_log()
        result.gen_summary_file(self.out_path, message_list)
