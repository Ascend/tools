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
import time

from .advisor_const import AdvisorConst
from ..common.utils import Const
from ..common.utils import print_info_log, print_error_log


class AdvisorResult:
    """
    Class for generate advisor result
    """

    def __init__(self, node, line, message):
        self.suspect_node = node
        self.line = line
        self.advisor_message = message

    @staticmethod
    def gen_summary_file(out_path, message_list):
        file_name = 'advisor_{}.txt'.format(time.strftime("%Y%m%d%H%M%S", time.localtime(time.time())))
        result_file = os.path.join(out_path, file_name)
        try:
            with os.fdopen(os.open(result_file, Const.WRITE_FLAGS, Const.WRITE_MODES), 'w+') as output_file:
                output_file.truncate(0)
                message_list = [message + AdvisorConst.NEW_LINE for message in message_list]
                output_file.writelines(message_list)
        except IOError as io_error:
            print_error_log("Failed to save %s, the reason is %s." % (result_file, io_error))
        else:
            print_info_log("The advisor summary is saved in: %s" % result_file)

    def print_advisor_log(self):
        print_info_log("The summary of the expert advice is as follows: ")
        message_list = [AdvisorConst.LINE + AdvisorConst.COLON + str(self.line),
                        AdvisorConst.SUSPECT_NODES + AdvisorConst.COLON + self.suspect_node,
                        AdvisorConst.ADVISOR_SUGGEST + AdvisorConst.COLON + self.advisor_message]
        for message in message_list:
            print_info_log(message)
        return message_list
